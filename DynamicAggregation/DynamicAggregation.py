import tatukgis_pdk as pdk

class DynamicAggregationForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "DynamicAggregation - TatukGIS DK Sample"
        self.ClientWidth = 981
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 218
        self.GIS.Top = 12
        self.GIS.Width = 751
        self.GIS.Height = 442
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        self.lblMethod = pdk.TGIS_PvlLabel(self.Context)
        self.lblMethod.Place(105, 13, None, 6, None, 3)
        self.lblMethod.Caption = "Aggregation method:"

        self.cbxMethod = pdk.TGIS_PvlComboBox(self.Context)
        self.cbxMethod.Place(194, 21, None, 6, None, 16)
        self.cbxMethod.ItemIndex = 5
        self.cbxMethod.OnChange = self.cbxMethod_change

        self.lblRadius = pdk.TGIS_PvlLabel(self.Context)
        self.lblRadius.Place(43, 13, None, 6, None, 40)
        self.lblRadius.Caption = "Radius:"

        self.cbxRadius = pdk.TGIS_PvlComboBox(self.Context)
        self.cbxRadius.Place(194, 21, None, 6, None, 56)
        radiuses = (5, 10, 20, 40, 80)
        for radius in radiuses:
            self.cbxRadius.ItemsAdd(f"{radius} pt")
        self.cbxRadius.ItemIndex = 3
        self.cbxRadius.OnChange = self.cbxRadius_change

        self.lblThreshold = pdk.TGIS_PvlLabel(self.Context)
        self.lblThreshold.Place(63, 13, None, 6, None, 80)
        self.lblThreshold.Caption = "Threshold:"

        self.cbxThreshold = pdk.TGIS_PvlComboBox(self.Context)
        self.cbxThreshold.Place(194, 21, None, 6, None, 96)
        thresholds = (0, 1, 2, 5, 10)
        for threshold in thresholds:
            self.cbxThreshold.ItemsAdd(str(threshold))
        self.cbxThreshold.ItemIndex = 5
        self.cbxThreshold.OnChange = self.cbxRadius_change

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Aggregation/Aggregation.ttkproject")
        self.cbxMethod.ItemsAdd("Off")

        for name in pdk.TGIS_DynamicAggregatorFactory().Names:
            self.cbxMethod.ItemsAdd(name)

        self.cbxMethod.ItemIndex = 0
        self.cbxThreshold.ItemIndex = 1

        self.cbxRadius.Enabled = False
        self.cbxThreshold.Enabled = False

    def read_default_values(self):
        if self.cbxMethod.Text == "ShapeReduction":
            self.cbxRadius.ItemIndex = 0
        else:
            self.cbxRadius.ItemIndex = 3

    def change_aggregation(self):
        dyn_agg_name = self.cbxMethod.Text
        lv = self.GIS.Get("cities")
        lv.Transparency = 70

        if dyn_agg_name == "Off":
            self.cbxRadius.Enabled = False
            self.cbxThreshold.Enabled = False
            lv.DynamicAggregator = None
        else:
            self.cbxRadius.Enabled = True
            self.cbxThreshold.Enabled = True
            lv.DynamicAggregator = pdk.TGIS_DynamicAggregatorFactory.CreateInstance(dyn_agg_name, lv)
            lv.DynamicAggregator.RadiusAsText = "SIZE: " + self.cbxRadius.Text
            lv.DynamicAggregator.Threshold = int(self.cbxThreshold.Text)

        self.GIS.InvalidateWholeMap()

    def cbxMethod_change(self, _sender):
        self.read_default_values()
        self.change_aggregation()

    def cbxRadius_change(self, _sender):
        self.change_aggregation()

    def cbxThreshold_change(self, _sender):
        self.change_aggregation()


def main():
    frm = DynamicAggregationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
