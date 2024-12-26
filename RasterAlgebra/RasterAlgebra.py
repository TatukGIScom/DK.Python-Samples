import tatukgis_pdk as pdk
import math

class RasterAlgebraForm(pdk.TGIS_PvlForm):
    SAMPLE_RESULT = "Result"

    def __init__(self, _owner):
        self.Caption = "RasterAlgebra - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Align = "Top"
        self.toolbar.Height = 120

        self.lblSrc = pdk.TGIS_PvlLabel(self.toolbar.Context)
        self.lblSrc.Place(81, 13, None, 13, None, 13)
        self.lblSrc.Caption = "Choose source:"

        self.btnPixel = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnPixel.Place(75, 23, None, 100, None, 8)
        self.btnPixel.Caption = "Open Pixel"
        self.btnPixel.OnClick = self.btnPixel_click

        self.btnGrid = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnGrid.Place(75, 23, None, 181, None, 8)
        self.btnGrid.Caption = "Open Grid"
        self.btnGrid.OnClick = self.btnGrid_click

        self.btnVector = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnVector.Place(75, 23, None, 262, None, 8)
        self.btnVector.Caption = "Open Vector"
        self.btnVector.OnClick = self.btnVector_click

        self.lblResultType = pdk.TGIS_PvlLabel(self.toolbar.Context)
        self.lblResultType.Place(63, 13, None, 12, None, 42)
        self.lblResultType.Caption = "Result type:"

        self.rbResultPixel = pdk.TGIS_PvlRadioButton(self.toolbar.Context)
        self.rbResultPixel.Place(47, 17, None, 100, None, 42)
        self.rbResultPixel.Caption = "Pixel"

        self.rbResultGrid = pdk.TGIS_PvlRadioButton(self.toolbar.Context)
        self.rbResultGrid.Place(47, 17, None, 153, None, 42)
        self.rbResultGrid.Caption = "Grid"

        self.lblResult = pdk.TGIS_PvlLabel(self.toolbar.Context)
        self.lblResult.Place(46, 13, None, 13, None, 67)
        self.lblResult.Caption = "Result ="

        self.memoFormula = pdk.TGIS_PvlMemo(self.toolbar.Context)
        self.memoFormula.Place(399, 20, None, 100, None, 65)

        self.btnExecute = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnExecute.Place(75, 23, None, 505, None, 62)
        self.btnExecute.Caption = "Execute"
        self.btnExecute.OnClick = self.btnExecute_click

        self.progress_bar = pdk.TGIS_PvlLabel(self.toolbar.Context)
        self.progress_bar.Place(564, 23, None, 16, None, 92)
        self.progress_bar.Visible = False

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 16
        self.GIS.Top = 121
        self.GIS.Width = 428
        self.GIS.Height = 333
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(130, 333, None, 450, None, 121)
        self.GIS_legend.Align = "Right"

    def btnOpen_click(self, _sender):
        pass

    @staticmethod
    def apply_ramp(lp):
        lp.GenerateRamp(
            pdk.TGIS_Color.Blue, pdk.TGIS_Color.Lime, pdk.TGIS_Color.Red,
            1.0 * math.floor(lp.MinHeight),
            (lp.MaxHeight + lp.MinHeight) / 2.0,
            1.0 * math.ceil(lp.MaxHeight), True,
            (lp.MaxHeight - lp.MinHeight) / 100.0,
            (lp.MaxHeight - lp.MinHeight) / 10.0,
            None, False
        )
        lp.Params.Pixel.GridShadow = False

    def btnPixel_click(self, _sender):
        self.GIS.Close()

        path = (pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                "World\\Countries\\USA\\States\\California\\San Bernardino\\DOQ\\37134877.jpg")

        lp = pdk.TGIS_Utils.GisCreateLayer("Pixel", path)
        self.GIS.Add(lp)
        self.GIS.FullExtent()

        self.rbResultPixel.Checked = True
        self.memoFormula.Text = "RGB(255 - pixel.R, 255 - pixel.G, 255 - pixel.B)"

    def btnGrid_click(self, _sender):
        self.GIS.Close()
        
        path = (pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                "World\\Countries\\USA\\States\\California\\San Bernardino\\NED\\w001001.adf")

        lp = pdk.TGIS_Utils.GisCreateLayer("Grid", path)
        lp.UseConfig = False
        self.GIS.Add(lp)
        self.apply_ramp(lp)
        self.GIS.FullExtent()

        self.rbResultGrid.Checked = True
        self.memoFormula.Text = "IF(grid < AVG(grid), MIN(grid), MAX(grid))"

    def btnVector_click(self, _sender):
        self.GIS.Close()

        path = (pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                "World\\Countries\\USA\\States\\California\\San Bernardino\\TIGER\\tl_2008_06071_edges_trunc.shp")

        lv = pdk.TGIS_Utils.GisCreateLayer("Vector", path)
        lv.UseConfig = False
        self.GIS.Add(lv)
        self.GIS.FullExtent()

        self.rbResultPixel.Checked = True
        self.memoFormula.Text = "IF(NODATA(vector.GIS_UID), RGB(0,255,0), RGB(255,0,0))"

    def doBusyEvent(self, _sender, pos, _end, _abort):
        if _end <= 0:
            self.progress_bar.Visible = False
        else:
            self.progress_bar.Visible = True
            self.progress_bar.Caption = 'progress: ' + str(int(pos/_end * 100)) + " %"
        self.GIS.ProcessMessages()

    def btnExecute_click(self, _sender):
        if self.GIS.IsEmpty:
            return

        if self.GIS.Get(self.SAMPLE_RESULT):
            self.GIS.Delete(self.SAMPLE_RESULT)

        gew = self.GIS.Extent.XMax - self.GIS.Extent.XMin

        src = None
        siz = 0

        for i in range(self.GIS.Items.Count):
            if isinstance(self.GIS.Items[0], pdk.TGIS_LayerPixel):
                src = self.GIS.Items.Item(i)
                lew = src.Extent.XMax - src.Extent.XMin
                w = round(gew * src.BitWidth / lew)
                siz = max(w, siz)

        dst = pdk.TGIS_LayerPixel()

        if not src:
            dst.Build(self.rbResultGrid.Checked, self.GIS.CS, self.GIS.Extent, siz, 0)
        else:
            dst.Build(self.rbResultGrid.Checked, self.GIS.CS, self.GIS.Extent, int(self.GIS.Width), 0)

        dst.Name = self.SAMPLE_RESULT
        self.GIS.Add(dst)
        ra = pdk.TGIS_RasterAlgebra()
        ra.BusyEvent = self.doBusyEvent

        for i in range(self.GIS.Items.Count):
            ra.AddLayer(self.GIS.Items.Item(i))
        try:
            ra.Execute(self.SAMPLE_RESULT + "=" + self.memoFormula.Text)

        except pdk.EGIS_Exception:
            self.GIS.Delete(self.SAMPLE_RESULT)

        if dst.IsGrid():
            self.apply_ramp(dst)

        self.GIS.InvalidateWholeMap()


def main():
    frm = RasterAlgebraForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
