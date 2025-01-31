import tatukgis_pdk as pdk

class AddLayerForm(pdk.TGIS_PvlForm):
    COUNTRY = "country"
    RIVERS = "rivers"

    def __init__(self, _owner):
        self.Caption = "AddLayer - TatukGIS DK Sample"
        # self.SetBounds(200, 100, 600, 500)

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomIn.Place(75, 22, self.btnOpen, 3, None, 3)
        self.btnZoomIn.Caption = "ZoomIn"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomOut.Place(75, 22, self.btnZoomIn, 3, None, 3)
        self.btnZoomOut.Caption = "ZoomOut"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        self.chkDrag = pdk.TGIS_PvlCheckBox(self.toolbar.Context)
        self.chkDrag.Caption = "Dragging"
        self.chkDrag.Place(75, 22, self.btnZoomOut, 3, None, 3)
        self.chkDrag.OnChange = self.chkDrag_change

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def btnOpen_click(self, _sender):
        # add country layer
        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/country.shp"
        ll.Name = self.COUNTRY
        ll.Params.Area.Color = pdk.TGIS_Color.LightGray
        self.GIS.Add(ll)

        # add rivers layer, set line params
        ll = pdk.TGIS_Utils.GisCreateLayer(
            self.RIVERS,
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/lwaters.shp"
        )
        ll.Params.Line.Width = 3
        ll.Params.Line.Color = pdk.TGIS_Color.Blue
        self.GIS.Add(ll)
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def chkDrag_change(self, _sender):
        # change viewer mode
        if self.chkDrag.Checked:
            self.GIS.Mode = pdk.TGIS_ViewerMode().Drag
        else:
            self.GIS.Mode = pdk.TGIS_ViewerMode().Select


def main():
    frm = AddLayerForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
    