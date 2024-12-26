import tatukgis_pdk as pdk

class PixelLocateForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Pixel Locate - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.panel = pdk.TGIS_PvlPanel(self.Context)
        self.panel.Place(209, 500, None, 0, None, 0)
        self.panel.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        self.button1 = pdk.TGIS_PvlButton(self.panel.Context)
        self.button1.Place(75, 22, None, 20, None, 50)
        self.button1.Caption = "Open image"
        self.button1.OnClick = self.btnOpenImage_click

        self.button2 = pdk.TGIS_PvlButton(self.panel.Context)
        self.button2.Place(75, 22, None, 110, None, 50)
        self.button2.Caption = "Open grid"
        self.button2.OnClick = self.btnOpenGrid_click

        self.group_box1 = pdk.TGIS_PvlGroupBox(self.Context)
        self.group_box1.Caption = "Brightness"
        self.group_box1.Place(185, 65, None, 10, None, 99)

        self.tbBrightness = pdk.TGIS_PvlTrackBar(self.group_box1.Context)
        self.tbBrightness.Place(169, 33, None, 8, None, 24)
        self.tbBrightness.Enabled = False
        self.tbBrightness.OnChange = self.tbBrightness_scroll
        self.tbBrightness.Maximum = 100
        self.tbBrightness.Minimum = -100
        # self.tbBrightness.Frequency = 10.

        self.group_box2 = pdk.TGIS_PvlGroupBox(self.Context)
        self.group_box2.Caption = "Channels value"
        self.group_box2.Place(185, 85, None, 10, None, 179)

        self.trColor = pdk.TGIS_PvlColorPreview(self.group_box2.Context)
        self.trColor.Place(69, 17, None, 8, None, 28)
        # self.trColor.Visible = False

        self.lbRGBValueC = pdk.TGIS_PvlLabel(self.group_box2.Context)
        self.lbRGBValueC.Place(169, 27, None, 10, None, 50)
        self.lbRGBValueC.Caption = "0, 0, 0"
        # self.lbRGBValueC.Visible = False

        self.group_box3 = pdk.TGIS_PvlGroupBox(self.Context)
        self.group_box3.Caption = "Original color value"
        self.group_box3.Place(185, 186, None, 10, None, 280)

        self.memo1 = pdk.TGIS_PvlMemo(self.group_box3.Context)
        self.memo1.Text = ""
        self.memo1.Place(165, 140, None, 10, None, 34)

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 400
        self.GIS.Height = 500
        self.GIS.Left = self.panel.Width
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseMove = self.GIS_MouseMove

    def btnOpenImage_click(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/USA/States/California/San Bernardino/DOQ/37134877.jpg"
        )
        self.tbBrightness.Enabled = True
        self.tbBrightness.Position = 0

    def btnOpenGrid_click(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/USA/States/California/San Bernardino/NED/w001001.adf"
        )
        self.tbBrightness.Enabled = False
        self.tbBrightness.Position = 0

    def GIS_MouseMove(self, _sender, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        lp = self.GIS.Items[0]
        if not lp:
            return

        ref_rgb_mapped = pdk.VarParameter()
        ref_native_vals = pdk.VarParameter()
        ref_transparency = pdk.VarParameter()
        ref_rgb_mapped.Value = pdk.TGIS_Color()
        ref_native_vals.Value = pdk.TGIS_DoubleArray()
        ref_transparency.Value = False
        
        if lp.Locate(ptg, ref_rgb_mapped, ref_native_vals, ref_transparency):
            rgb_mapped = ref_rgb_mapped.Value
            native_vals = ref_native_vals.Value
            
            self.trColor.Color = pdk.TGIS_Color.FromRGB(
                rgb_mapped.R,
                rgb_mapped.G,
                rgb_mapped.B
            )
            self.lbRGBValueC.Caption = f"RGB : {rgb_mapped.R}, {rgb_mapped.G}, {rgb_mapped.B}"

            self.memo1.Clear()
            for i in range(native_vals.Length):
                self.memo1.AppendLine(f"CH{i} = {native_vals.Value(i):.2f}")

    def tbBrightness_scroll(self, _sender):
        lp = self.GIS.Items[0]
        if lp is None:
            return

        lp.Params.Pixel.Brightness = int(self.tbBrightness.Position)
        self.GIS.InvalidateWholeMap()


def main():
    frm = PixelLocateForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
