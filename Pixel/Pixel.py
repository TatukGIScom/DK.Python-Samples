import tatukgis_pdk as pdk

class PixelForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Pixel - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.btnFullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "Zoom"
        self.button2.OnClick = self.btnZoom_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 156, None, 3)
        self.button3.Caption = "Drag"
        self.button3.OnClick = self.btnDrag_click

        self.ComboProject = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.ComboProject.Place(175, 22, None, 300, None, 3)
        names = ("Normal.ttkproject",
                 "Normal with histogram.ttkproject",
                 "Grayscale.ttkproject",
                 "Colorize.ttkproject",
                 "Inversion.ttkproject",
                 "Inversion by RGB.ttkproject")
        for name in names:
            self.ComboProject.ItemsAdd(name)
        self.ComboProject.OnChange = self.Project_Change

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def form_show(self, _sender):
        self.ComboProject.ItemIndex = 0

    def btnFullExtent_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def Project_Change(self, _sender):
        project = self.ComboProject.Text
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "Samples/Projects/" + project)


def main():
    frm = PixelForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
