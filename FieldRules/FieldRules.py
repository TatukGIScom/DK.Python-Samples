import tatukgis_pdk as pdk

GIS_FLDX_EXT = ".fldx"
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

class FieldRulesForm(pdk.TGIS_PvlForm):
    lv: pdk.TGIS_LayerVector

    def __init__(self, _owner):
        self.Caption = "FieldRules - TatukGIS DK Sample"
        self.ClientWidth = 347
        self.ClientHeight = 381
        self.OnShow = self.form_show

        self.btnField = pdk.TGIS_PvlButton(self.Context)
        self.btnField.Place(75, 22, None, 258, None, 39)
        self.btnField.Caption = "Add Field"
        self.btnField.OnClick = self.btnField_click

        self.btnAlias = pdk.TGIS_PvlButton(self.Context)
        self.btnAlias.Place(75, 22, None, 258, None, 68)
        self.btnAlias.Caption = "Add Alias"
        self.btnAlias.OnClick = self.btnAlias_click

        self.btnCheck = pdk.TGIS_PvlButton(self.Context)
        self.btnCheck.Place(75, 22, None, 258, None, 97)
        self.btnCheck.Caption = "Add Check"
        self.btnCheck.OnClick = self.btnCheck_click

        self.btnList = pdk.TGIS_PvlButton(self.Context)
        self.btnList.Place(75, 22, None, 258, None, 126)
        self.btnList.Caption = "Add List"
        self.btnList.OnClick = self.btnList_click

        self.btnDefault = pdk.TGIS_PvlButton(self.Context)
        self.btnDefault.Place(75, 22, None, 258, None, 155)
        self.btnDefault.Caption = "Add Default"
        self.btnDefault.OnClick = self.btnDefault_click

        self.btnValidate = pdk.TGIS_PvlButton(self.Context)
        self.btnValidate.Place(75, 22, None, 258, None, 184)
        self.btnValidate.Caption = "Add Validate"
        self.btnValidate.OnClick = self.btnValidate_click

        self.btnSave = pdk.TGIS_PvlButton(self.Context)
        self.btnSave.Place(75, 22, None, 258, None, 256)
        self.btnSave.Caption = "Save Rules"
        self.btnSave.OnClick = self.btnSave_click

        self.btnRead = pdk.TGIS_PvlButton(self.Context)
        self.btnRead.Place(75, 22, None, 258, None, 285)
        self.btnRead.Caption = "Read Rules"
        self.btnRead.OnClick = self.btnRead_click

        self.GIS_Attributes = pdk.TGIS_PvlControlAttributes(self.Context)
        self.GIS_Attributes.Place(215, 357, None, 12, None, 12)
        self.GIS_Attributes.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

    def form_show(self, _sender):
        self.lv = pdk.TGIS_LayerVector()
        self.lv.Name = "test_rules"
        self.lv.Open()

        self.lv.AddField("name", pdk.TGIS_FieldType().String, 1, 0)

        shp = self.lv.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(20, 20))

    def btnField_click(self, _sender):
        shp = self.lv.GetShape(1)
        shp.SetField("name", "Tom")

        self.GIS_Attributes.ShowShape(shp)

    def btnAlias_click(self, _sender):
        r = pdk.TGIS_FieldRule()
        r.ValueAliases.Aliases.Add(pdk.TGIS_FieldValueAlias("Tommy", "Tom"))

        fld = self.lv.FieldInfo(0)
        fld.Rules = r

        shp = self.lv.GetShape(1)
        shp.SetField("name", "Tom")

        self.GIS_Attributes.ShowShape(shp)

    def btnCheck_click(self, _sender):
        r = pdk.TGIS_FieldRule()
        r.ValueChecks.Checks.Add(pdk.TGIS_FieldValueCheck(
            pdk.TGIS_FieldValueCheckMode().AfterEdit,
            pdk.TGIS_FieldValueCheckFormula().Required,
            "",
            "Cannot be None")
        )

        fld = self.lv.FieldInfo(0)
        fld.Rules = r

        shp = self.lv.GetShape(1)
        try:
            shp.SetField("name", "")
        except pdk.EGIS_Exception as ex:
            pdk.TGIS_PvlMessages.ShowInfo(str(ex), self.Context)

        self.GIS_Attributes.ShowShape(shp)

    def btnList_click(self, _sender):
        r = pdk.TGIS_FieldRule()
        r.Values.Mode = pdk.TGIS_FieldValuesMode().SelectList
        r.Values.Items.Add("Ala")
        r.Values.Items.Add("Tom")
        r.Values.Items.Add("Bobby")

        fld = self.lv.FieldInfo(0)
        fld.Rules = r

        shp = self.lv.GetShape(1)
        shp.SetField("name", "Tom")

        self.GIS_Attributes.ShowShape(shp)

    def btnDefault_click(self, _sender):
        r = pdk.TGIS_FieldRule()
        r.Values.DefaultValue = "Diana"

        fld = self.lv.FieldInfo(0)
        fld.Rules = r

        shp = self.lv.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(30, 20))
        shp.SetFieldsDefaulRuleValue()

        self.GIS_Attributes.ShowShape(shp)

    def btnValidate_click(self, _sender):
        if self.lv.FindField("email") == -1:
            self.lv.AddField("email", pdk.TGIS_FieldType().String, 1, 0)
            self.GIS_Attributes.Invalidate()

        r = pdk.TGIS_FieldRule()
        r.ValueChecks.Checks.Add(pdk.TGIS_FieldValueCheck(
            pdk.TGIS_FieldValueCheckMode().AfterEdit,
            pdk.TGIS_FieldValueCheckFormula().Regex,
            EMAIL_REGEX,
            "Invalid email")
        )

        fld = self.lv.FieldInfo(1)
        fld.Rules = r

        shp = self.lv.GetShape(1)
        shp.SetField("email", "xyz@gmail.com")

        self.GIS_Attributes.ShowShape(shp)

    def btnSave_click(self, _sender):
        pdk.TGIS_FieldRulesOperations().SaveFldx("my_rules" + GIS_FLDX_EXT, self.lv)

    def btnRead_click(self, _sender):
        pdk.TGIS_FieldRulesOperations().ParseFldx("my_rules" + GIS_FLDX_EXT, self.lv)

        shp = self.lv.GetShape(1)

        self.GIS_Attributes.ShowShape(shp)


def main():
    frm = FieldRulesForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
