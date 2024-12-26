import tatukgis_pdk as pdk

class LanguagesForm(pdk.TGIS_PvlForm):
    TXT_ENGLISH = "Welcome"
    TXT_CHINESE = "欢迎"
    TXT_JAPANESE = "ようこそ"
    TXT_HEBREW = "ברוך הבא"
    TXT_GREEK = "Καλώς ήλθατε"
    TXT_ARABIC = "أهلا بك"

    def __init__(self, _owner):
        self.Caption = "Languages - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 27, None, 0, None, 0)

        self.comboBox1 = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.comboBox1.Place(145, 21, None, 0, None, 2)
        names = ["English", "Chinese", "Japanese", "Arabic", "Hebrew", "Greek"]
        for name in names:
            self.comboBox1.ItemsAdd(name)
        self.comboBox1.OnChange = self.comboBox1_change

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 437

    def form_show(self, _sender):
        ll = pdk.TGIS_LayerVector()
        ll.Name = "points"
        ll.Params.Labels.Position = [pdk.TGIS_LabelPosition().UpLeft]
        ll.Params.Labels.Allocator = False

        self.GIS.Add(ll)
        ll.Extent = pdk.TGIS_Utils.GisExtent(-180, -90, 180, 90)

        shp = ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils().GisPoint(-45, -45))

        ll = pdk.TGIS_LayerVector()
        ll.Name = "lines"
        ll.AddField("name", pdk.TGIS_FieldType().String, 256, 0)
        ll.Params.Labels.Alignment = pdk.TGIS_LabelAlignment().Follow
        ll.Params.Labels.Color = pdk.TGIS_Color().Black
        ll.Params.Labels.Font.Size = 12
        ll.Params.Labels.FontColor = pdk.TGIS_Color().Black
        ll.Params.Labels.Allocator = False

        self.GIS.Add(ll)
        ll.Extent = pdk.TGIS_Utils.GisExtent(-180, -90, 180, 90)

        shp = ll.CreateShape(pdk.TGIS_ShapeType().Arc)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils().GisPoint(-90, 90))
        shp.AddPoint(pdk.TGIS_Utils().GisPoint(180, -90))

        self.GIS.FullExtent()
        self.comboBox1.ItemIndex = 0

    def comboBox1_change(self, _sender):
        if self.comboBox1.ItemIndex == 1:  # Chinese
            txt = self.TXT_CHINESE
        elif self.comboBox1.ItemIndex == 2:  # Japanese
            txt = self.TXT_JAPANESE
        elif self.comboBox1.ItemIndex == 3:  # Arabic
            txt = self.TXT_ARABIC
        elif self.comboBox1.ItemIndex == 4:  # Hebrew
            txt = self.TXT_HEBREW
        elif self.comboBox1.ItemIndex == 5:  # Greek
            txt = self.TXT_GREEK
        else:  # English
            txt = self.TXT_ENGLISH

        ll = self.GIS.Get("points")
        ll.Params.Labels.Value = f"{txt} 1"

        ll = self.GIS.Get("lines")
        ll.Params.Labels.Value = f"{txt} 2"

        self.GIS.InvalidateWholeMap()


def main():
    frm = LanguagesForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
