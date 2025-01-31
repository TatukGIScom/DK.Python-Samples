import tatukgis_pdk as pdk

class RendererForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Renderer - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnDrag.Place(75, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Dragging"
        self.btnDrag.OnClick = self.btnDrag_click
        
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def btnOpen_click(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      "Samples/Projects/renderer.ttkproject")
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        # change viewer mode
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag


def main():
    frm = RendererForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
