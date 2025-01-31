import tatukgis_pdk as pdk

class SQLLayerForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "SQLLayer - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 26, None, 0, None, 0)

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(73, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(73, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(73, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/SQLLayers/gistest.ttkls")

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()


def main():
    frm = SQLLayerForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
