import tatukgis_pdk as pdk

class LayerStatisticsForm(pdk.TGIS_PvlForm):
    BUTTON_CALCULATE = "Calculate statistics"
    BUTTON_CANCEL = "Cancel"
    GIS_BAND_DEFAULT = "0"
    GIS_BAND_GRID = "Value"
    GIS_BAND_A = "A"
    GIS_BAND_R = "R"
    GIS_BAND_G = "G"
    GIS_BAND_B = "B"
    GIS_BAND_H = "H"
    GIS_BAND_S = "S"
    GIS_BAND_L = "L"
    STATISTICS_STANDARD = ("Average", "Count", "CountMissings", "Max", "Median",
                           "Min", "Range", "StandardDeviation", "Sum", "Variance")
    STATISTICS_BASIC = ("Average", "Count", "Max", "Min", "Sum")

    def __init__(self, _owner):
        self.Caption = "LayerStatistics - TatukGIS DK Sample"
        self.ClientWidth = 1219
        self.ClientHeight = 726

        self.gbSelectLayer = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbSelectLayer.Caption = "Select layer"
        self.gbSelectLayer.Place(190, 116, None, 12, None, 12)

        self.rbVector = pdk.TGIS_PvlRadioButton(self.gbSelectLayer.Context)
        self.rbVector.Place(56, 17, None, 6, None, 19)
        self.rbVector.Caption = "Vector"
        self.rbVector.OnChange = self.rbVector_change

        self.rbGrid = pdk.TGIS_PvlRadioButton(self.gbSelectLayer.Context)
        self.rbGrid.Place(56, 17, None, 6, None, 42)
        self.rbGrid.Caption = "Grid"
        self.rbGrid.OnChange = self.rbGrid_change

        self.rbPixel = pdk.TGIS_PvlRadioButton(self.gbSelectLayer.Context)
        self.rbPixel.Place(56, 17, None, 6, None, 65)
        self.rbPixel.Caption = "Pixel"
        self.rbPixel.OnChange = self.rbPixel_change

        self.rbCustom = pdk.TGIS_PvlRadioButton(self.gbSelectLayer.Context)
        self.rbCustom.Place(63, 17, None, 6, None, 88)
        self.rbCustom.Caption = "Custom"
        self.rbCustom.OnChange = self.rbCustom_change

        self.btnOpen = pdk.TGIS_PvlButton(self.gbSelectLayer.Context)
        self.btnOpen.Place(75, 23, None, 80, None, 85)
        self.btnOpen.Caption = "Open"
        self.btnOpen.Enabled = False
        self.btnOpen.OnClick = self.btnOpen_click

        self.gbSelectStatistics = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbSelectStatistics.Caption = "Select statistics"
        self.gbSelectStatistics.Place(190, 230, None, 12, None, 134)

        self.btnBasicStats = pdk.TGIS_PvlButton(self.gbSelectStatistics.Context)
        self.btnBasicStats.Place(56, 23, None, 6, None, 19)
        self.btnBasicStats.Caption = "Basic"
        self.btnBasicStats.OnClick = self.btnBasicStats_click

        self.btnStandardStats = pdk.TGIS_PvlButton(self.gbSelectStatistics.Context)
        self.btnStandardStats.Place(64, 23, None, 68, None, 19)
        self.btnStandardStats.Caption = "Standard"
        self.btnStandardStats.OnClick = self.btnStandardStats_click

        self.btnAllStats = pdk.TGIS_PvlButton(self.gbSelectStatistics.Context)
        self.btnAllStats.Place(46, 23, None, 138, None, 19)
        self.btnAllStats.Caption = "All"
        self.btnAllStats.OnClick = self.btnAllStats_click

        self.cblStats = pdk.TGIS_PvlPanel(self.gbSelectStatistics.Context)
        self.cblStats.Scrollable = True
        self.cblStats.Place(178, 169, None, 6, None, 48)

        self.chbCount = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbCount.Caption = 'Count'
        self.chbCount.Place(125, 20, None, 10, None, 0)

        self.chbCountMissings = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbCountMissings.Caption = 'CountMissings'
        self.chbCountMissings.Place(125, 20, None, 10, None, 20)

        self.chbSum = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbSum.Caption = 'Sum'
        self.chbSum.Place(125, 20, None, 10, None, 40)

        self.chbAverage = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbAverage.Caption = 'Average'
        self.chbAverage.Place(125, 20, None, 10, None, 60)

        self.chbStandardDeviation = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbStandardDeviation.Caption = 'StandardDeviation'
        self.chbStandardDeviation.Place(125, 20, None, 10, None, 80)

        self.chbSample = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbSample.Caption = 'Sample'
        self.chbSample.Place(125, 20, None, 10, None, 100)

        self.chbVariance = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbVariance.Caption = 'Variance'
        self.chbVariance.Place(125, 20, None, 10, None, 120)

        self.chbMedian = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbMedian.Caption = 'Median'
        self.chbMedian.Place(125, 20, None, 10, None, 140)

        self.chbMin = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbMin.Caption = 'Min'
        self.chbMin.Place(125, 20, None, 10, None, 160)

        self.chbMax = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbMax.Caption = 'Max'
        self.chbMax.Place(125, 20, None, 10, None, 180)

        self.chbRange = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbRange.Caption = 'Range'
        self.chbRange.Place(125, 20, None, 10, None, 200)

        self.chbMinority = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbMinority.Caption = 'Minority'
        self.chbMinority.Place(125, 20, None, 10, None, 220)

        self.chbMajority = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbMajority.Caption = 'Majority'
        self.chbMajority.Place(125, 20, None, 10, None, 240)

        self.chbVariety = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbVariety.Caption = 'Variety'
        self.chbVariety.Place(125, 20, None, 10, None, 260)

        self.chbUnique = pdk.TGIS_PvlCheckBox(self.cblStats.Context)
        self.chbUnique.Caption = 'Unique'
        self.chbUnique.Place(125, 20, None, 10, None, 280)

        self.gbSelectDefs = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbSelectDefs.Caption = "Select bands"
        self.gbSelectDefs.Place(190, 260, None, 12, None, 370)

        self.btnSelectAllDefs = pdk.TGIS_PvlButton(self.gbSelectDefs.Context)
        self.btnSelectAllDefs.Place(88, 23, None, 6, None, 19)
        self.btnSelectAllDefs.Caption = "Select All"
        self.btnSelectAllDefs.OnClick = self.btnSelectAllDefs_click

        self.btnDeselectAllDefs = pdk.TGIS_PvlButton(self.gbSelectDefs.Context)
        self.btnDeselectAllDefs.Place(84, 23, None, 100, None, 19)
        self.btnDeselectAllDefs.Caption = "Deselect All"
        self.btnDeselectAllDefs.OnClick = self.btnDeselectAllDefs_click

        self.cblDefs = pdk.TGIS_PvlPanel(self.gbSelectDefs.Context)
        self.cblDefs.Place(178, 205, None, 6, None, 48)

        self.chb_1 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_1.Place(125, 20, None, 10, None, 0)

        self.chb_2 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_2.Place(125, 20, None, 10, None, 20)

        self.chb_3 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_3.Place(125, 20, None, 10, None, 40)

        self.chb_4 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_4.Place(125, 20, None, 10, None, 60)

        self.chb_5 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_5.Place(125, 20, None, 10, None, 80)

        self.chb_6 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_6.Place(125, 20, None, 10, None, 100)

        self.chb_7 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_7.Place(125, 20, None, 10, None, 120)

        self.chb_8 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_8.Place(125, 20, None, 10, None, 140)

        self.chb_9 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_9.Place(125, 20, None, 10, None, 160)

        self.chb_10 = pdk.TGIS_PvlCheckBox(self.cblDefs.Context)
        self.chb_10.Place(125, 20, None, 10, None, 180)

        self.cbBessel = pdk.TGIS_PvlCheckBox(self.gbSelectDefs.Context)
        self.cbBessel.Place(145, 17, None, 16, None, 641)
        self.cbBessel.Caption = "Use Bessel's correction"

        self.cbFastStats = pdk.TGIS_PvlCheckBox(self.Context)
        self.cbFastStats.Place(136, 17, None, 16, None, 665)
        self.cbFastStats.Caption = "Fast statistics"
        self.cbFastStats.Checked = True

        self.btnCalculate = pdk.TGIS_PvlButton(self.Context)
        self.btnCalculate.Place(190, 23, None, 12, None, 691)
        self.btnCalculate.Caption = "Calculate statistics"
        self.btnCalculate.OnClick = self.btnCalculate_click

        self.progress_bar = pdk.TGIS_PvlLabel(self.Context)
        self.progress_bar.Place(714, 23, None, 208, None, 691)
        self.progress_bar.Caption = ''

        self.gbResults = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbResults.Caption = "Results"
        self.gbResults.Place(273, 702, None, 934, None, 12)

        self.memoResult = pdk.TGIS_PvlMemo(self.gbResults.Context)
        self.memoResult.Place(261, 648, None, 6, None, 19)

        self.btnLoadStats = pdk.TGIS_PvlButton(self.gbResults.Context)
        self.btnLoadStats.Place(120, 23, None, 6, None, 673)
        self.btnLoadStats.Caption = "Load *.ttkstats"
        self.btnLoadStats.OnClick = self.btnLoadStats_click

        self.btnSaveStats = pdk.TGIS_PvlButton(self.gbResults.Context)
        self.btnSaveStats.Place(120, 23, None, 147, None, 673)
        self.btnSaveStats.Caption = "Save *.ttkstats"
        self.btnSaveStats.OnClick = self.btnSaveStats_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 208
        self.GIS.Top = 12
        self.GIS.Width = 714
        self.GIS.Height = 670
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        self.GIS.BusyEvent = self.doBusyEvent

        self.open_dialog = pdk.TGIS_PvlOpenDialog(self.Context)
        # self.open_dialog.Filter = pdk.TGIS_Utils.GisSupportedFiles([pdk.TGIS_FileType.All], False)
        self.open_dialog.Filter = "SHP files (*.SHP)|*.SHP"

        # open sample vector layer
        self.rbVector.Checked = True
        self.rbVector_change(self)

        # set common functions
        self.checkPredefined(self.STATISTICS_STANDARD)

    def doBusyEvent(self, _sender, pos, _end, _abort):
        self.progress_bar.Visible = True
        if pos == 0:
            self.progress_bar.Caption = 'progress: 0 %'
        elif pos < 0:
            self.progress_bar.Caption = 'progress: 100 %'
        else:
            self.progress_bar.Caption = 'progress: ' + str(pos) + ' %'
        self.GIS.ProcessMessages()

    def checkPredefined(self, predefined):
        for i in range(self.cblStats.Context.Controls.Count):
            self.cblStats.Context.Controls.Item(i).Checked = False
        for stat_fun in predefined:
            for i in range(self.cblStats.Context.Controls.Count):
                if self.cblStats.Context.Controls.Item(i).Caption == stat_fun:
                    self.cblStats.Context.Controls.Item(i).Checked = True
                    break

    # depending on layer's type prepare list of available statistics definitions
    # field names for vector layers; band names for pixel layers
    def prepareStatisticsDefinitions(self, layer):
        for i in range(self.cblDefs.Context.Controls.Count):
            self.cblDefs.Context.Controls.Item(i).Checked = False
        i = 0
        if isinstance(layer, pdk.TGIS_LayerVector):
            lv = layer
            self.gbSelectDefs.Caption = "Select fields"

            # fill with layer field names
            for i in range(lv.Fields.Count):
                self.cblDefs.Context.Controls.Item(i).Caption = lv.Fields[i].Name
                self.cblDefs.Context.Controls.Item(i).Checked = True

        elif isinstance(layer, pdk.TGIS_LayerPixel):
            lp = layer
            self.gbSelectDefs.Caption = "Select bands"

            # fill with appropriate band names
            if lp.IsGrid():
                self.cblDefs.Context.Controls.Item(i).Caption = self.GIS_BAND_DEFAULT
                i += 1

            for j in range(lp.BandsCount):
                self.cblDefs.Context.Controls.Item(i).Caption = str(j + 1)
                i += 1

            if lp.IsGrid():
                self.cblDefs.Context.Controls.Item(i).Caption = self.GIS_BAND_GRID
                self.cblDefs.Context.Controls.Item(i).Checked = True
                i += 1
            else:
                self.cblDefs.Context.Controls.Item(i).Caption = self.GIS_BAND_A
                self.cblDefs.Context.Controls.Item(i+1).Caption = self.GIS_BAND_R
                self.cblDefs.Context.Controls.Item(i+1).Checked = True
                self.cblDefs.Context.Controls.Item(i+2).Caption = self.GIS_BAND_G
                self.cblDefs.Context.Controls.Item(i+2).Checked = True
                self.cblDefs.Context.Controls.Item(i+3).Caption = self.GIS_BAND_B
                self.cblDefs.Context.Controls.Item(i+3).Checked = True
                self.cblDefs.Context.Controls.Item(i+4).Caption = self.GIS_BAND_H
                self.cblDefs.Context.Controls.Item(i+5).Caption = self.GIS_BAND_S
                self.cblDefs.Context.Controls.Item(i+6).Caption = self.GIS_BAND_L
                i += 7

        for j in range(i):
            self.cblDefs.Context.Controls.Item(j).Visible = True
        for i in range(i, self.cblDefs.Context.Controls.Count):
            self.cblDefs.Context.Controls.Item(i).Visible = False

    def openLayerAndStats(self, path):
        self.GIS.Open(path)
        ll = self.GIS.Items[0]
        self.prepareStatisticsDefinitions(ll)
        self.showResults(ll.Statistics, True)

    def btnLoadStats_click(self, _layer):
        ll = self.GIS.Items[0]
        if not ll.Statistics.LoadFromFile():
            pdk.TGIS_PvlMessages.ShowInfo("Loading failed.", self.Context)

        self.showResults(ll.Statistics, True)

    def btnSaveStats_click(self, _layer):
        ll = self.GIS.Items[0]
        ll.Statistics.SaveToFile()

    def rbVector_change(self, _sender):
        if not self.rbVector.Checked:
            return
        
        self.openLayerAndStats(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                               "/World/Countries/USA/States/California/Counties.shp")
        self.btnOpen.Enabled = False

    def rbGrid_change(self, _sender):
        if not self.rbGrid.Checked:
            return

        self.openLayerAndStats(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                                "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
        self.btnOpen.Enabled = False

    def rbPixel_change(self, _sender):
        if not self.rbPixel.Checked:
            return
        
        self.openLayerAndStats(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                               "/World/Countries/USA/States/California/San Bernardino/DOQ/37134877.jpg")
        self.btnOpen.Enabled = False

    def rbCustom_change(self, _sender):
        if not self.rbCustom.Checked:
            return
        
        self.btnOpen.Enabled = True

    def btnOpen_click(self, _sender):
        self.open_dialog.Execute()
        self.openLayerAndStats(self.open_dialog.FileName)

    def btnBasicStats_click(self, _sender):
        self.checkPredefined(self.STATISTICS_BASIC)

    def btnStandardStats_click(self, _sender):
        self.checkPredefined(self.STATISTICS_STANDARD)

    def btnAllStats_click(self, _sender):
        for i in range(self.cblStats.Context.Controls.Count):
            self.cblStats.Context.Controls.Item(i).Checked = True

    def btnSelectAllDefs_click(self, _sender):
        for i in range(self.cblDefs.Context.Controls.Count):
            self.cblDefs.Context.Controls.Item(i).Checked = True

    def btnDeselectAllDefs_click(self, _sender):
        for i in range(self.cblDefs.Context.Controls.Count):
            self.cblDefs.Context.Controls.Item(i).Checked = False

    def prepareFunctions(self, funcs):
        res = False
        funcs.Value = pdk.TGIS_StatisticalFunctions.EmptyStatistics()

        for i in range(self.cblStats.Context.Controls.Count):
            if self.cblStats.Context.Controls.Item(i).Checked:
                res = True
                if self.cblStats.Context.Controls.Item(i).Caption == "Average":
                    funcs.Value.Average = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Count":
                    funcs.Value.Count = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "CountMissings":
                    funcs.Value.CountMissings = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Max":
                    funcs.Value.Max = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Majority":
                    funcs.Value.Majority = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Median":
                    funcs.Value.Median = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Min":
                    funcs.Value.Min = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Minority":
                    funcs.Value.Minority = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Range":
                    funcs.Value.Range = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "StandardDeviation":
                    funcs.Value.StandardDeviation = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Sample":
                    funcs.Value.Sample = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Sum":
                    funcs.Value.Sum = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Variance":
                    funcs.Value.Variance = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Variety":
                    funcs.Value.Variety = True
                elif self.cblStats.Context.Controls.Item(i).Caption == "Unique":
                    funcs.Value.Unique = True
        return res

    def showResults(self, stats_engine, clear):
        dashed_line = "----------------------------------------"

        if clear:
            self.memoResult.Clear()

        for i in range(stats_engine.AvailableResults.Count):
            self.memoResult.AppendLine(dashed_line)
            self.memoResult.AppendLine(stats_engine.AvailableResults.Item(i))
            self.memoResult.AppendLine(dashed_line)

            stats_result = stats_engine.Get(stats_engine.AvailableResults.Item(i))
            stats_available = stats_result.AvailableStatistics

            for j in range(stats_available.Count):
                item_name = stats_available.Item(j).Name
                item_value = stats_available.Item(j).ToString()
                node_string = f"    + {item_name} = {item_value}"
                self.memoResult.AppendLine(node_string)

    def btnCalculate_click(self, _sender):
        # cancel calculation
        if self.btnCalculate.Caption == self.BUTTON_CANCEL:
            self.btnCalculate.Caption = self.BUTTON_CALCULATE
            return

        self.btnCalculate.Caption = self.BUTTON_CANCEL
        try:
            funcs = pdk.VarParameter()
            if not self.prepareFunctions(funcs):
                pdk.TGIS_PvlMessages.ShowInfo("Select at least one statistical function", self.Context)
                return

            ll = self.GIS.Items[0]
            ll.Statistics.Reset()

            # use Bessel's correction
            # if True, calculate "sample" standard deviation and variance;
            # if False, calculate "population" version (this is default)
            ll.Statistics.UseBesselCorrection = self.cbBessel.Checked

            # collect statistics definitions (fields or bands)
            for i in range(self.cblDefs.Context.Controls.Count):
                if self.cblDefs.Context.Controls.Item(i).Checked:
                    ll.Statistics.Add(self.cblDefs.Context.Controls.Item(i).Caption, funcs.Value)

            if ll.Statistics.DefinedResults.Count == 0:
                pdk.TGIS_PvlMessages.ShowInfo("Select at least one field for vector layer or band for pixel layer", self.Context)
                return

            # Here the calculations starts

            # statistics class can calculate statistics for a given extent;
            # for filtering data: "extent", "shape", "de9im" and only for vector layers:
            # "query", "useSelected" parameters can be used

            # "Fast Statistics" works only for pixel layers (by default);
            # big pixel layers are resampled to avoid long calculation;
            # the results are approximate with high accuracy
            ll.Statistics.Calculate(self.GIS.VisibleExtent, None, "", self.cbFastStats.Checked)

            # print results on TMemo control
            self.showResults(ll.Statistics, True)

        finally:
            self.btnCalculate.Caption = self.BUTTON_CALCULATE


def main():
    frm = LayerStatisticsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
