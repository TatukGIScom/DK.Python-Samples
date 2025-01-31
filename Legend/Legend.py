import tatukgis_pdk as pdk

class LegendForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Legend - TatukGIS DK Sample"
        self.ClientHeight = 500
        self.ClientWidth = 600

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.btnFullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "Zoom Mode"
        self.button2.OnClick = self.btnZoom_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 156, None, 3)
        self.button3.Caption = "Drag Mode"
        self.button3.OnClick = self.btnDrag_click
        
        self.button4 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button4.Place(75, 22, None, 233, None, 3)
        self.button4.Caption = "Save config"
        self.button4.OnClick = self.btnSaveConfig_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.label = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.label.Place(200, 19, None, 3, None, 0)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.VisibleExtentChangeEvent = self.VisibleExtentChange
        self.GIS.Left = 140
        self.GIS.Top = 29
        self.GIS.Width = 452
        self.GIS.Height = 452
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/Poland/DCW/poland.ttkproject"
        )

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(160, 447, None, 0, None, 29)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        self.toolbar_select = pdk.TGIS_PvlPanel(self.GIS_legend.Context)
        self.toolbar_select.Place(592, 29, None, 0, None, 0)
        self.toolbar_select.Align = "Bottom"

        self.button5 = pdk.TGIS_PvlButton(self.toolbar_select.Context)
        self.button5.Place(75, 22, None, 3, None, 3)
        self.button5.Caption = "Layers"
        self.button5.OnClick = self.btnLayers_click

        self.button6 = pdk.TGIS_PvlButton(self.toolbar_select.Context)
        self.button6.Place(75, 22, None, 82, None, 3)
        self.button6.Caption = "Groups"
        self.button6.OnClick = self.btnGroups_click

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnSaveConfig_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.SaveAll()

    def btnLayers_click(self, _sender):
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers

    def btnGroups_click(self, _sender):
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Groups

    def VisibleExtentChange(self, _sender):
        if self.GIS.IsEmpty:
            return

        self.label.Caption = "Scale: " + self.GIS.ScaleAsText


def main():
    frm = LegendForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
