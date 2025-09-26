import tatukgis_pdk as pdk
import os.path

class ClassificationForm(pdk.TGIS_PvlForm):
    RENDER_TYPE_SIZE = "Size / Width"
    RENDER_TYPE_COLOR = "Color"
    RENDER_TYPE_OUTLINE_WIDTH = "Outline width"
    RENDER_TYPE_OUTLINE_COLOR = "Outline color"

    STD_INTERVAL_ONE = "1 STDEV"
    STD_INTERVAL_ONE_HALF = "1/2 STDEV"
    STD_INTERVAL_ONE_THIRD = "1/3 STDEV"
    STD_INTERVAL_ONE_QUARTER = "1/4 STDEV"

    GIS_CLASSIFY_METHOD_DI = "Defined Interval"
    GIS_CLASSIFY_METHOD_EI = "Equal Interval"
    GIS_CLASSIFY_METHOD_GI = "Geometrical Interval"
    GIS_CLASSIFY_METHOD_NB = "Natural Breaks"
    GIS_CLASSIFY_METHOD_KM = "K-Means"
    GIS_CLASSIFY_METHOD_KMS = "K-Means Spatial"
    GIS_CLASSIFY_METHOD_QN = "Quantile"
    GIS_CLASSIFY_METHOD_QR = "Quartile"
    GIS_CLASSIFY_METHOD_SD = "Standard Deviation"
    GIS_CLASSIFY_METHOD_SDC = "Standard Deviation with Central"
    GIS_CLASSIFY_METHOD_UNQ = "Unique"

    GIS_FIELD_UID = "GIS_UID"
    GIS_FIELD_AREA = "GIS_AREA"
    GIS_FIELD_LENGTH = "GIS_LENGTH"
    GIS_FIELD_CENTROID_X = "GIS_CENTROID_X"
    GIS_FIELD_CENTROID_Y = "GIS_CENTROID_Y"

    def __init__(self, _owner):
        self.Caption = "Classification - TatukGIS DK Sample"
        self.ClientWidth = 959
        self.ClientHeight = 613
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 47, None, 0, None, 0)

        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnOpen.Place(75, 21, None, 12, None, 12)
        self.btnOpen.Caption = "Open..."
        self.btnOpen.OnClick = self.btnOpen_click

        self.lblField = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lblField.Place(32, 13, None, 102, None, 16)
        self.lblField.Caption = "Field:"

        self.lblMethod = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lblMethod.Place(49, 13, None, 282, None, 16)
        self.lblMethod.Caption = "Method:"

        self.lblRenderBy = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lblRenderBy.Place(59, 13, None, 464, None, 16)
        self.lblRenderBy.Caption = "Render by:"

        self.lblClasses = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lblClasses.Place(46, 13, None, 622, None, 16)
        self.lblClasses.Caption = "Classes:"

        self.lblInterval = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lblInterval.Place(45, 13, None, 745, None, 16)
        self.lblInterval.Caption = "Interval:"

        self.cbField = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbField.Place(136, 21, None, 140, None, 13)
        self.cbField.OnChange = self.do_classify_onchange

        self.cbMethod = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbMethod.Place(121, 21, None, 337, None, 13)
        names = ("Select ...",
                 self.GIS_CLASSIFY_METHOD_DI,
                 self.GIS_CLASSIFY_METHOD_EI,
                 self.GIS_CLASSIFY_METHOD_GI,
                 self.GIS_CLASSIFY_METHOD_NB,
                 self.GIS_CLASSIFY_METHOD_KM,
                 self.GIS_CLASSIFY_METHOD_KMS,
                 self.GIS_CLASSIFY_METHOD_QN,
                 self.GIS_CLASSIFY_METHOD_QR,
                 self.GIS_CLASSIFY_METHOD_SD,
                 self.GIS_CLASSIFY_METHOD_SDC,
                 self.GIS_CLASSIFY_METHOD_UNQ)
        for name in names:
            self.cbMethod.ItemsAdd(name)
        self.cbMethod.ItemIndex = 0
        self.cbMethod.OnChange = self.cbMethod_change

        self.cbRenderBy = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbRenderBy.Place(87, 21, None, 529, None, 13)
        names = (self.RENDER_TYPE_SIZE,
                 self.RENDER_TYPE_COLOR,
                 self.RENDER_TYPE_OUTLINE_WIDTH,
                 self.RENDER_TYPE_OUTLINE_COLOR)
        for name in names:
            self.cbRenderBy.ItemsAdd(name)
        self.cbRenderBy.ItemIndex = 1
        self.cbRenderBy.OnChange = self.cbRenderBy_change

        self.cbClasses = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbClasses.Place(65, 21, None, 674, None, 13)
        for i in range(1, 10):
            self.cbClasses.ItemsAdd(str(i))
        self.cbClasses.ItemIndex = 4
        self.cbClasses.OnChange = self.do_classify_onchange

        self.cbInterval = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbInterval.Place(121, 21, None, 796, None, 13)
        names = (self.STD_INTERVAL_ONE,
                 self.STD_INTERVAL_ONE_HALF,
                 self.STD_INTERVAL_ONE_THIRD,
                 self.STD_INTERVAL_ONE_QUARTER)
        for name in names:
            self.cbInterval.ItemsAdd(name)
        self.cbInterval.ItemIndex = 0
        self.cbInterval.OnChange = self.do_classify_onchange
        self.cbInterval.Visible = False

        self.edtInterval = pdk.TGIS_PvlEdit(self.toolbar_buttons.Context)
        self.edtInterval.Place(52, 20, None, 796, None, 13)
        self.edtInterval.Text = "100"
        self.edtInterval.Enabled = False
        self.edtInterval.OnChange = self.do_classify_onchange

        self.toolbar_controls = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_controls.Place(935, 44, None, 12, None, 35)

        self.lblStartColor = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblStartColor.Place(58, 13, None, 0, None, 15)
        self.lblStartColor.Caption = "Start color:"

        self.pStartColor = pdk.TGIS_PvlColorPreview(self.toolbar_controls.Context)
        self.pStartColor.Place(23, 21, None, 58, None, 11)
        self.pStartColor.Color = pdk.TGIS_Color.FromRGB(233, 248, 237)
        self.pStartColor.OnClick = self.pStartColor_click

        self.lblEndColor = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblEndColor.Place(55, 13, None, 89, None, 15)
        self.lblEndColor.Caption = "End color:"

        self.pEndColor = pdk.TGIS_PvlColorPreview(self.toolbar_controls.Context)
        self.pEndColor.Place(23, 21, None, 142, None, 11)
        self.pEndColor.Color = pdk.TGIS_Color().Green
        self.pEndColor.OnClick = self.pEndColor_click

        self.lblStartSize = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblStartSize.Place(53, 13, None, 170, None, 15)
        self.lblStartSize.Caption = "Start size:"

        self.edtStartSize = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtStartSize.Place(48, 20, None, 225, None, 12)
        self.edtStartSize.Text = "1"
        self.edtStartSize.OnChange = self.do_classify_onchange

        self.lblEndSize = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblEndSize.Place(50, 13, None, 279, None, 15)
        self.lblEndSize.Caption = "End size:"

        self.edtEndSize = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtEndSize.Place(48, 20, None, 328, None, 12)
        self.edtEndSize.Text = "100"
        self.edtEndSize.OnChange = self.do_classify_onchange

        self.lblClassIdField = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblClassIdField.Place(71, 13, None, 389, None, 15)
        self.lblClassIdField.Caption = "Class ID field:"

        self.edtClassIdField = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtClassIdField.Place(100, 20, None, 463, None, 12)

        self.chkShowInLegend = pdk.TGIS_PvlCheckBox(self.toolbar_controls.Context)
        self.chkShowInLegend.Place(109, 17, None, 572, None, 14)
        self.chkShowInLegend.Caption = "Show in legend"
        self.chkShowInLegend.Checked = True
        self.chkShowInLegend.OnChange = self.chkShowInLegend_change

        self.chkUseColorRamp = pdk.TGIS_PvlCheckBox(self.toolbar_controls.Context)
        self.chkUseColorRamp.Place(107, 17, None, 683, None, 14)
        self.chkUseColorRamp.Caption = "Use color ramp"
        self.chkUseColorRamp.Checked = True
        self.chkUseColorRamp.OnChange = self.chkUseColorRamp_change

        self.cbColorRamp = pdk.TGIS_PvlComboBox(self.toolbar_controls.Context)
        self.cbColorRamp.Place(121, 21, None, 793, None, 11)
        self.cbColorRamp.OnChange = self.do_classify_onchange

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 229
        self.GIS.Top = 80
        self.GIS.Width = 718
        self.GIS.Height = 486
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Left = 12
        self.GIS_legend.Top = 80
        self.GIS_legend.Width = 211
        self.GIS_legend.Height = 486
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

    def do_classify_onchange(self, _sender):
        self.do_classify()

    def fill_cb_fields(self):
        lyr = self.GIS.Items[0]

        if isinstance(lyr, pdk.TGIS_LayerVector):
            lv = lyr
            self.cbField.ItemsAdd(self.GIS_FIELD_UID)
            self.cbField.ItemsAdd(self.GIS_FIELD_AREA)
            self.cbField.ItemsAdd(self.GIS_FIELD_LENGTH)
            self.cbField.ItemsAdd(self.GIS_FIELD_CENTROID_X)
            self.cbField.ItemsAdd(self.GIS_FIELD_CENTROID_Y)

            for field in lv.Fields:
                if field.FieldType == pdk.TGIS_FieldType().Number:
                    self.cbField.ItemsAdd(field.Name)
                elif field.FieldType == pdk.TGIS_FieldType().Float:
                    self.cbField.ItemsAdd(field.Name)

        elif isinstance(lyr, pdk.TGIS_LayerPixel):
            lp = lyr
            for i in range(1, lp.BandsCount + 1):
                self.cbField.ItemsAdd(i)

        self.cbField.ItemIndex = 0

    def fill_cb_color_ramps(self):
        color_ramps = pdk.TGIS_Utils().GisColorRampList
        for i in range(color_ramps.Count):
            ramp_name = color_ramps.Items(i).Name
            self.cbColorRamp.ItemsAdd(ramp_name)

            if ramp_name == "GreenBlue":
                self.cbColorRamp.ItemIndex = i

    def form_show(self, _sender):
        sample_data_dir = os.path.join(pdk.TGIS_Utils.GisSamplesDataDirDownload(),
                                       "World/Countries/USA/States/California/Counties.shp")
        self.GIS.Open(sample_data_dir)

        self.fill_cb_fields()
        self.fill_cb_color_ramps()

    def pStartColor_click(self, _sender):
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pStartColor.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return

        self.pStartColor.Color = dlg_color.Color
        self.do_classify()

    def pEndColor_click(self, _sender):
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pEndColor.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return

        self.pEndColor.Color = dlg_color.Color
        self.do_classify()

    def btnOpen_click(self, _sender):
        dlg_open = pdk.TGIS_PvlOpenDialog(self.Context)
        dlg_open.Filter = pdk.TGIS_Utils.GisSupportedFiles([pdk.TGIS_FileType().All], False)

        if not dlg_open.Execute():
            return

        self.GIS.Open(dlg_open.FileName)

        self.fill_cb_fields()
        self.fill_cb_color_ramps()

    def cbMethod_change(self, _sender):
        if self.edtInterval.Text == "":
            self.edtInterval.Text = "100"

        method = str(self.cbMethod.Text)

        if method == self.GIS_CLASSIFY_METHOD_DI:
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = True
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = False
        elif method == self.GIS_CLASSIFY_METHOD_QR:
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = False
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = False
        elif method == self.GIS_CLASSIFY_METHOD_SD or method == self.GIS_CLASSIFY_METHOD_SDC:
            self.edtInterval.Visible = False
            self.cbInterval.Visible = True
            self.cbClasses.Enabled = False
        else:
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = True
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = False

        if method == self.GIS_CLASSIFY_METHOD_UNQ:
            self.cbColorRamp.ItemIndex = self.cbColorRamp.IndexOf("Unique")
        else:
            self.cbColorRamp.ItemIndex = self.cbColorRamp.IndexOf("GreenBlue")

        self.do_classify()

    def do_classify(self):
        if self.cbMethod.ItemIndex <= 0:
            return

        lv = self.GIS.Items[0]
        if lv is None:
            return

        create_field = False
        # add "ClassIdField" if provided
        class_id_field = self.edtClassIdField.Text

        if isinstance(lv, pdk.TGIS_LayerVector):

            if len(class_id_field) > 0:
                create_field = True
            else:
                create_field = False
            if create_field and lv.FindField(class_id_field) < 0:
                lv.AddField(class_id_field, pdk.TGIS_FieldType().Number, 3, 0)

        elif not isinstance(lv, pdk.TGIS_LayerPixel):
            pdk.TGIS_PvlMessages.ShowInfo(f"Layer {lv.Name: str} is not supported.", self.Context)

        classifier = pdk.TGIS_ClassificationFactory.CreateClassifier(lv)

        # set common properties
        classifier.Target = str(self.cbField.Text)
        classifier.NumClasses = self.cbClasses.ItemIndex + 1
        classifier.StartColor = self.pStartColor.Color
        classifier.EndColor = self.pEndColor.Color
        classifier.ShowLegend = self.chkShowInLegend.Checked

        # set method
        method = str(self.cbMethod.Text)
        if method == self.GIS_CLASSIFY_METHOD_DI:
            classifier.Method = pdk.TGIS_ClassificationMethod().DefinedInterval
        elif method == self.GIS_CLASSIFY_METHOD_EI:
            classifier.Method = pdk.TGIS_ClassificationMethod().EqualInterval
        elif method == self.GIS_CLASSIFY_METHOD_GI:
            classifier.Method = pdk.TGIS_ClassificationMethod().GeometricalInterval
        elif method == self.GIS_CLASSIFY_METHOD_KM:
            classifier.Method = pdk.TGIS_ClassificationMethod().KMeans
        elif method == self.GIS_CLASSIFY_METHOD_KMS:
            classifier.Method = pdk.TGIS_ClassificationMethod().KMeansSpatial
        elif method == self.GIS_CLASSIFY_METHOD_NB:
            classifier.Method = pdk.TGIS_ClassificationMethod().NaturalBreaks
        elif method == self.GIS_CLASSIFY_METHOD_QN:
            classifier.Method = pdk.TGIS_ClassificationMethod().Quantile
        elif method == self.GIS_CLASSIFY_METHOD_QR:
            classifier.Method = pdk.TGIS_ClassificationMethod().Quartile
        elif method == self.GIS_CLASSIFY_METHOD_SD:
            classifier.Method = pdk.TGIS_ClassificationMethod().StandardDeviation
        elif method == self.GIS_CLASSIFY_METHOD_SDC:
            classifier.Method = pdk.TGIS_ClassificationMethod().StandardDeviationWithCentral
        elif method == self.GIS_CLASSIFY_METHOD_UNQ:
            classifier.Method = pdk.TGIS_ClassificationMethod().Unique
        else:
            classifier.Method = pdk.TGIS_ClassificationMethod().NaturalBreaks

        # set interval
        classifier.Interval = float(self.edtInterval.Text)

        if method == self.GIS_CLASSIFY_METHOD_SD or method == self.GIS_CLASSIFY_METHOD_SDC:
            interval = self.cbInterval.Text
            if interval == self.STD_INTERVAL_ONE:
                classifier.Interval = 1.0
            elif interval == self.STD_INTERVAL_ONE_HALF:
                classifier.Interval = 1.0 / 2
            elif interval == self.STD_INTERVAL_ONE_THIRD:
                classifier.Interval = 1.0 / 3
            elif interval == self.STD_INTERVAL_ONE_QUARTER:
                classifier.Interval = 1.0 / 4
            else:
                classifier.Interval = 1.0

        # NumClasses property is automatically calculated for methods:
        # DefinedInterval, Quartile, StandardDeviation(s)
        if self.chkUseColorRamp.Checked:
            if method == self.GIS_CLASSIFY_METHOD_UNQ:
                colormap_mode = pdk.TGIS_ColorMapMode().Discrete
            else:
                colormap_mode = pdk.TGIS_ColorMapMode().Continuous
            classifier.ColorRamp = pdk.TGIS_Utils().GisColorRampList[self.cbColorRamp.ItemIndex]
            classifier.ColorRamp.DefaultColorMapMode = colormap_mode
        else:
            classifier.ColorRampName = ""

        # vector-only params 
        if isinstance(classifier, pdk.TGIS_ClassificationVector):
            classifier_vec = classifier
            classifier_vec.StartSize = int(self.edtStartSize.Text)
            classifier_vec.EndSize = int(self.edtEndSize.Text)
            classifier_vec.ClassIdField = class_id_field

            # render type
            render_type = str(self.cbRenderBy.Text)
            if render_type == self.RENDER_TYPE_SIZE:
                classifier_vec.RenderType = pdk.TGIS_ClassificationRenderType().Size
            elif render_type == self.RENDER_TYPE_COLOR:
                classifier_vec.RenderType = pdk.TGIS_ClassificationRenderType().Color
            elif render_type == self.RENDER_TYPE_OUTLINE_WIDTH:
                classifier_vec.RenderType = pdk.TGIS_ClassificationRenderType().OutlineWidth
            elif render_type == self.RENDER_TYPE_OUTLINE_COLOR:
                classifier_vec.RenderType = pdk.TGIS_ClassificationRenderType().OutlineColor
            else:
                classifier_vec.RenderType = pdk.TGIS_ClassificationRenderType().Color

        # before the classification starts, layer statistics must be provided
        if classifier.MustCalculateStatistics():
            res = pdk.TGIS_PvlOptionDialog(self.Context)
            res.Text = "Statistics need to be calculated"
            if res.Execute() != pdk.TGIS_PvlModalResult.No:
                lv.Statistics.Calculate()
            else:
                lv.Statistics.ResetModified()
                return

        if classifier.Classify() and create_field and lv is not None:
            lv.SaveData()

        self.GIS.InvalidateWholeMap()

    def cbRenderBy_change(self, _sender):
        ll = self.GIS.Items[0]
        if ll is None:
            return

        if isinstance(ll, pdk.TGIS_LayerVector):
            ll.ParamsList.ClearAndSetDefaults()
            if (ll.DefaultShapeType == pdk.TGIS_ShapeType().Polygon
                    and self.cbRenderBy.Text == self.RENDER_TYPE_SIZE):
                pdk.TGIS_PvlMessages.ShowInfo("Method not allowed for polygons", self.Context)
                self.cbRenderBy.ItemIndex = 1

        self.do_classify()

    def chkShowInLegend_change(self, _sender):
        self.do_classify()

    def chkUseColorRamp_change(self, _sender):
        self.cbColorRamp.Enabled = self.chkUseColorRamp.Checked
        self.do_classify()

def main():
    frm = ClassificationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
