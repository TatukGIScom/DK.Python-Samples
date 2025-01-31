import tatukgis_pdk as pdk

def changePixels(_layer, _extent, source, output, _width, _height):
    pix_val = pdk.TGIS_Color()

    r_max_val = -1000
    r_min_val = 1000
    g_max_val = -1000
    g_min_val = 1000
    b_max_val = -1000
    b_min_val = 1000

    for j in range(source.Length):
        pix_val.ARGB = source.Value(j)

        r = pix_val.R
        g = pix_val.G
        b = pix_val.B

        if r > r_max_val:
            r_max_val = r
        if g > g_max_val:
            g_max_val = g
        if b > b_max_val:
            b_max_val = b

        if r < r_min_val:
            r_min_val = r
        if g < g_min_val:
            g_min_val = g
        if b < b_min_val:
            b_min_val = b

    r_delta = max(1, r_max_val - r_min_val)
    g_delta = max(1, g_max_val - g_min_val)
    b_delta = max(1, b_max_val - b_min_val)

    for j in range(source.Length):
        pix_val.ARGB = source.Value(j)

        r = pix_val.R
        g = pix_val.G
        b = pix_val.B
        r = int(((r - r_min_val) / r_delta) * 255)
        g = int(((g - g_min_val) / g_delta) * 255)
        b = int(((b - b_min_val) / b_delta) * 255)
        pix_val = pdk.TGIS_Color.FromRGB(r, g, b)
        output.Value(j, pix_val.ARGB)

    return True


class PixelOperationsForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "PixelOperations - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Align = "Top"
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnOpen = pdk.TGIS_PvlButton(self.Context)
        self.btnOpen.Place(73, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open File"
        self.btnOpen.OnClick = self.btnOpen_click

        self.btnFullExtent = pdk.TGIS_PvlButton(self.Context)
        self.btnFullExtent.Place(73, 22, None, 79, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoom = pdk.TGIS_PvlButton(self.Context)
        self.btnZoom.Place(73, 22, None, 155, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.Context)
        self.btnDrag.Place(73, 22, None, 231, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        self.check_box = pdk.TGIS_PvlCheckBox(self.toolbar_buttons.Context)
        self.check_box.Caption = "Change pixels"
        self.check_box.Place(100, 22, None, 330, None, 3)
        self.check_box.OnChange = self.chkChangePixels_change

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(169, 347, None, 480, None, 29)
        self.GIS_legend.Align = "Right"

    def form_show(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/USA/States/California/San Bernardino/DOQ/37134877.jpg"
        )

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

    def chkChangePixels_change(self, _sender):
        if self.GIS.IsEmpty:
            return
        lp = self.GIS.Items[0]

        if self.check_box.Checked:
            lp.PixelOperationEvent = changePixels
        else:
            lp.PixelOperationEvent = None

        self.GIS.InvalidateWholeMap()

    def btnOpen_click(self, _sender):
        self.open_dialog = pdk.TGIS_PvlOpenDialog(self.Context)
        self.open_dialog.Execute()
        self.GIS.Open(self.open_dialog.FileName)


def main():
    frm = PixelOperationsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
