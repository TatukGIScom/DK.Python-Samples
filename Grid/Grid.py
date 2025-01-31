import tatukgis_pdk as pdk

class GridForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Grid - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(45, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(45, 22, None, 49, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(45, 22, None, 96, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        self.btnClear = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnClear.Place(79, 22, None, 180, None, 3)
        self.btnClear.Caption = "Clear"
        self.btnClear.OnClick = self.btnClear_click

        self.btnShadow = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnShadow.Place(89, 22, None, 260, None, 3)
        self.btnShadow.Caption = "Shadow on/off"
        self.btnShadow.OnClick = self.btnShadow_click

        self.btnUserDef = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnUserDef.Place(79, 22, None, 350, None, 3)
        self.btnUserDef.Caption = "User Defined"
        self.btnUserDef.OnClick = self.btnUserDef_click

        self.btnUserINI = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnUserINI.Place(79, 22, None, 430, None, 3)
        self.btnUserINI.Caption = "User INI"
        self.btnUserINI.OnClick = self.btnUserINI_click

        self.btnReloadINI = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnReloadINI.Place(79, 22, None, 510, None, 3)
        self.btnReloadINI.Caption = "Reload INI"
        self.btnReloadINI.OnClick = self.btnReloadINI_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblAltitude = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblAltitude.Place(300, 19, None, 3, None, 0)
        self.lblAltitude.Caption = ''

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 130
        self.GIS.Top = 30
        self.GIS.Width = 480
        self.GIS.Height = 450
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
        self.GIS.OnMouseMove = self.GIS_MouseMove

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(130, 450, None, 0, None, 30)
        # self.GIS_legend.Align = "Left"

    def GIS_MouseMove(self, _sender, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        ll = self.GIS.Items[0]

        ref_rgb_mapped = pdk.VarParameter()
        ref_rgb_mapped.Value = pdk.TGIS_Color()
        ref_natives_vals = pdk.VarParameter()
        ref_natives_vals.Value = pdk.TGIS_DoubleArray()
        ref_transparency = pdk.VarParameter()
        ref_transparency.Value = False

        txt = ""
        if ll.Locate(ptg, ref_rgb_mapped, ref_natives_vals, ref_transparency):
            natives_vals = ref_natives_vals.Value
            txt = txt + f"Altitude = {natives_vals.Value(0):.2f}"
        else:
            txt = txt + "Unknown"

        self.lblAltitude.Caption = txt

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

    def btnClear_click(self, _sender):
        ll = self.GIS.Items[0]
        ll.Params.Pixel.AltitudeMapZones.Clear()
        self.GIS.InvalidateWholeMap()

    def btnUserDef_click(self, _sender):
        ll = self.GIS.Items[0]
        ll.Params.Pixel.AltitudeMapZones.Clear()
        ll.Params.Pixel.AltitudeMapZones.Add("200, 400, OLIVE, VERY LOW")
        ll.Params.Pixel.AltitudeMapZones.Add("400, 700, OLIVE, LOW")
        ll.Params.Pixel.AltitudeMapZones.Add("700, 900, GREEN, MID")
        ll.Params.Pixel.AltitudeMapZones.Add("900, 1200, BLUE, HIGH")
        ll.Params.Pixel.AltitudeMapZones.Add("1200, 1700, RED, SKY")
        ll.Params.Pixel.AltitudeMapZones.Add("1700, 2200, YELLOW, HEAVEN")
        self.GIS.InvalidateWholeMap()

    def btnReloadINI_click(self, _sender):
        ll = self.GIS.Items[0]
        ll.ConfigName = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                         + "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
        ll.RereadConfig()
        self.GIS.InvalidateWholeMap()

    def btnShadow_click(self, _sender):
        ll = self.GIS.Items[0]
        ll.Params.Pixel.GridShadow = not ll.Params.Pixel.GridShadow
        self.GIS.InvalidateWholeMap()

    def btnUserINI_click(self, _sender):
        ll = self.GIS.Items[0]
        ll.ConfigName = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                         + "Samples/Projects/dem_ned.ini")
        ll.RereadConfig()
        self.GIS.InvalidateWholeMap()


def main():
    frm = GridForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
