import tatukgis_pdk as pdk

class Buffers1Form(pdk.TGIS_PvlForm):
    shp_id = None

    def __init__(self, _owner):
        self.Caption = "Buffers1 - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 422
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnMinus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnMinus.Place(22, 22, None, 10, None, 3)
        self.btnMinus.Caption = " - "
        self.btnMinus.OnClick = self.btnMinus_click

        self.trackBar1 = pdk.TGIS_PvlTrackBar(self.toolbar_buttons.Context)
        self.trackBar1.Place(169, 33, None, 33, None, 6)
        self.trackBar1.OnChange = self.trackBar1_Scroll
        self.trackBar1.Maximum = 50
        self.trackBar1.Minimum = -50

        self.btnPlus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPlus.Place(22, 22, None, 203, None, 3)
        self.btnPlus.Caption = " + "
        self.btnPlus.OnClick = self.btnPlus_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 366
        self.GIS.OnMouseDown = self.GISMouseDown
        self.GIS.OnClick = self.btnPlus_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Click on shapes to choose one for buffer creation"

    def form_show(self, _sender):
        self.shp_id = 2
        # create a layer for buffer
        lb = pdk.TGIS_LayerVector()
        lb.Name = "buffer"
        lb.Transparency = 50
        lb.Params.Area.Color = pdk.TGIS_Color().Red

        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Topology/topology.shp")
        self.GIS.Add(lb)
        self.GIS.Unlock()
        self.GIS.FullExtent()

    def GISMouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # let's locate a shape after click
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        shp = self.GIS.Locate(ptg, 5.0/self.GIS.Zoom)

        if shp is not None:
            self.shp_id = shp.Uid
            shp.Flash()

    def btnPlus_click(self, _sender):
        self.trackBar1.Position = self.trackBar1.Position + 1

    def btnMinus_click(self, _sender):
        self.trackBar1.Position = self.trackBar1.Position - 1

    def trackBar1_Scroll(self, _sender):
        ll = self.GIS.Items[0]
        if ll is None:
            return

        lb = self.GIS.Get("buffer")
        if lb is None:
            return

        shp = ll.GetShape(self.shp_id)
        if shp is None:
            return

        # create a buffer using topology
        tpl = pdk.TGIS_Topology()
        lb.RevertShapes()
        tmp = tpl.MakeBuffer(shp, self.trackBar1.Position*1000)
        if tmp is not None:
            lb.AddShape(tmp)

        # check extents
        lb.RecalcExtent()
        self.GIS.FullExtent()


def main():
    frm = Buffers1Form(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
