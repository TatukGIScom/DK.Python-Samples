import tatukgis_pdk as pdk

class Buffers2Form(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Buffers2 - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
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
        self.trackBar1.Maximum = 200
        self.trackBar1.Minimum = 0

        self.btnPlus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPlus.Place(22, 22, None, 203, None, 3)
        self.btnPlus.Caption = " + "
        self.btnPlus.OnClick = self.btnPlus_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 477
        self.GIS.Height = 448
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.lbSelected = pdk.TGIS_PvlListBox(self.Context)
        self.lbSelected.Place(120, 448, None, 480, None, 29)
        self.lbSelected.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

    def tmp(self):
        ll = self.GIS.Get("counties")
        if not ll:
            return

        lb = self.GIS.Get("buffer")
        if not lb:
            return

        shp = ll.FindFirst(pdk.TGIS_Utils.GisWholeWorld(), "name='Merced'")
        if not shp:
            return

        # create a buffer using topology
        tpl = pdk.TGIS_Topology()
        lb.RevertShapes()
        tmp = tpl.MakeBuffer(shp, self.trackBar1.Position/100.0)
        if tmp is not None:
            buf = lb.AddShape(tmp)
        else:
            return

        ll = self.GIS.Get("counties")
        ll.IgnoreShapeParams = False
        if ll is None:
            return

        ll.RevertShapes()
        self.lbSelected.ItemsClear()

        # check all shapes
        tmp = ll.FindFirst(buf.Extent)
        while tmp is not None:
            # if any has a common point with buffer mark it as blue
            if buf.IsCommonPoint(tmp):
                tmp = tmp.MakeEditable()
                self.lbSelected.ItemsAdd(str(tmp.GetField("name")))
                tmp.Params.Area.Color = pdk.TGIS_Color().Blue
            tmp = ll.FindNext()

        self.GIS.InvalidateWholeMap()

    def form_show(self, _sender):
        self.GIS.Lock()

        la = pdk.TGIS_Utils.GisCreateLayer(
            "counties",
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/USA/States/California/Counties.shp"
        )
        self.GIS.Add(la)

        lb = pdk.TGIS_LayerVector()
        lb.Name = "buffer"
        lb.Transparency = 70
        lb.Params.Area.Color = pdk.TGIS_Color().Yellow
        lb.CS = self.GIS.CS

        self.GIS.Add(lb)
        self.GIS.Unlock()
        self.GIS.FullExtent()
        self.tmp()

    def btnPlus_click(self, _sender):
        self.trackBar1.Position = self.trackBar1.Position + 25
        self.tmp()

    def btnMinus_click(self, _sender):
        self.trackBar1.Position = self.trackBar1.Position - 25
        self.tmp()

    def trackBar1_Scroll(self, _sender):
        self.lblMsg.Caption = str(self.trackBar1.Position) + ' km'
        self.tmp()


def main():
    frm = Buffers2Form(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
