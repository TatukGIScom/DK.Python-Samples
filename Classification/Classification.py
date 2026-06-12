# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Classification sample (Python PDK edition) — demonstrates thematic data
# classification of vector and raster (pixel) layers using the TatukGIS PDK
# (Python Developer Kernel) TGIS_ClassificationAbstract API.
#
# Key concepts shown:
#   - Loading a layer with TGIS_ViewerWnd.Open
#   - Building a PDK UI programmatically with TGIS_PvlForm, TGIS_PvlPanel,
#     TGIS_PvlButton, TGIS_PvlComboBox, TGIS_PvlEdit, TGIS_PvlCheckBox, and
#     TGIS_PvlColorPreview widgets
#   - Creating a classifier with TGIS_ClassificationFactory.CreateClassifier,
#     which returns the appropriate subclass for the layer type
#     (TGIS_ClassificationVector or TGIS_ClassificationPixel)
#   - Setting the classification target field (numeric attribute or band index)
#   - Choosing a classification method from TGIS_ClassificationMethod:
#       DefinedInterval, EqualInterval, GeometricalInterval,
#       NaturalBreaks, KMeans, KMeansSpatial, Quantile, Quartile,
#       StandardDeviation, StandardDeviationWithCentral, Unique
#   - Controlling the visual output via:
#       StartColor / EndColor           — color gradient endpoints
#       NumClasses                      — number of class breaks (auto for some)
#       Interval                        — interval size (DefinedInterval/StdDev)
#       ColorRamp / ColorRampName       — named palette from GisColorRampList
#       ColorRamp.DefaultColorMapMode   — Continuous or Discrete color mapping
#   - Vector-specific properties via TGIS_ClassificationVector:
#       RenderType      — Color, Size, OutlineWidth, or OutlineColor
#       StartSize / EndSize — symbol size range for the Size render type
#       ClassIdField    — optional attribute field to store class index per feature
#   - Managing layer statistics:
#       MustCalculateStatistics — check whether stats are needed
#       layer.Statistics.Calculate — explicit statistics computation
#   - Adding the classification result to TGIS_PvlControlLegend
#   - Refreshing the map with GIS.InvalidateWholeMap
#
# The sample opens the California Counties shapefile from the TatukGIS sample
# dataset by default (via TGIS_Utils.GisSamplesDataDirDownload), but the user
# can open any supported file with the "Open…" button.
# =============================================================================

import tatukgis_pdk as pdk
import os.path


class ClassificationForm(pdk.TGIS_PvlForm):
    """
    Main PDK form for the Classification sample.

    Builds and hosts a TGIS_ViewerWnd map component, a TGIS_PvlControlLegend
    panel, and two toolbar rows of PDK widgets for controlling all classification
    parameters.  Any change to any control immediately calls do_classify() so the
    map updates in real time.

    Class-level string constants define the display strings used in combo-box
    items; they are compared against selected text to map UI choices to
    TGIS_ClassificationMethod and TGIS_ClassificationRenderType enum values.
    """

    # -----------------------------------------------------------------------
    # Render-type display strings (must match cbRenderBy items exactly)
    # -----------------------------------------------------------------------
    RENDER_TYPE_SIZE          = "Size / Width"   # Vary symbol size by class
    RENDER_TYPE_COLOR         = "Color"           # Vary fill color by class
    RENDER_TYPE_OUTLINE_WIDTH = "Outline width"   # Vary outline stroke width
    RENDER_TYPE_OUTLINE_COLOR = "Outline color"   # Vary outline stroke color

    # Standard deviation interval fraction display strings
    STD_INTERVAL_ONE         = "1 STDEV"
    STD_INTERVAL_ONE_HALF    = "1/2 STDEV"
    STD_INTERVAL_ONE_THIRD   = "1/3 STDEV"
    STD_INTERVAL_ONE_QUARTER = "1/4 STDEV"

    # Classification method display strings (must match cbMethod items exactly)
    GIS_CLASSIFY_METHOD_DI  = "Defined Interval"                # Fixed-width interval classes
    GIS_CLASSIFY_METHOD_EI  = "Equal Interval"                  # Equal data-range intervals
    GIS_CLASSIFY_METHOD_GI  = "Geometrical Interval"            # Geometrically progressing breaks
    GIS_CLASSIFY_METHOD_NB  = "Natural Breaks"                  # Jenks natural breaks
    GIS_CLASSIFY_METHOD_KM  = "K-Means"                         # K-means clustering
    GIS_CLASSIFY_METHOD_KMS = "K-Means Spatial"                 # Spatially aware K-means
    GIS_CLASSIFY_METHOD_QN  = "Quantile"                        # Equal-count quantile classes
    GIS_CLASSIFY_METHOD_QR  = "Quartile"                        # Four quartile classes
    GIS_CLASSIFY_METHOD_SD  = "Standard Deviation"              # Std-dev symmetric classes
    GIS_CLASSIFY_METHOD_SDC = "Standard Deviation with Central" # Std-dev with centre class
    GIS_CLASSIFY_METHOD_UNQ = "Unique"                          # One class per unique value

    # Virtual field name constants — always available on vector layers;
    # computed on-the-fly by the engine without a real attribute column.
    GIS_FIELD_UID       = "GIS_UID"        # Unique feature identifier
    GIS_FIELD_AREA      = "GIS_AREA"       # Feature area (polygon layers)
    GIS_FIELD_LENGTH    = "GIS_LENGTH"     # Feature perimeter / line length
    GIS_FIELD_CENTROID_X = "GIS_CENTROID_X"  # Centroid X coordinate
    GIS_FIELD_CENTROID_Y = "GIS_CENTROID_Y"  # Centroid Y coordinate

    def __init__(self, _owner):
        """
        Build the entire PDK UI programmatically.

        Sets the form caption, size, and OnShow handler, then creates two
        toolbar panels (toolbar_buttons on the top row, toolbar_controls on the
        second row) and the main TGIS_ViewerWnd / TGIS_PvlControlLegend pair.

        All widget positions are specified in pixels using Place(width, height,
        right_anchor, left, bottom_anchor, top).
        """
        self.Caption = "Classification - TatukGIS DK Sample"
        self.ClientWidth = 959
        self.ClientHeight = 613
        # form_show loads the default sample layer once the window is visible
        self.OnShow = self.form_show

        # ------------------------------------------------------------------
        # First toolbar row: Open button, field / method / render selectors
        # ------------------------------------------------------------------
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

        # Target-field picker — populated in fill_cb_fields() after layer load
        self.cbField = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbField.Place(136, 21, None, 140, None, 13)
        self.cbField.OnChange = self.do_classify_onchange

        # Classification method selector — index 0 is a "Select …" placeholder
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

        # Render type picker (Color, Size, Outline Width, Outline Color)
        self.cbRenderBy = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbRenderBy.Place(87, 21, None, 529, None, 13)
        names = (self.RENDER_TYPE_SIZE,
                 self.RENDER_TYPE_COLOR,
                 self.RENDER_TYPE_OUTLINE_WIDTH,
                 self.RENDER_TYPE_OUTLINE_COLOR)
        for name in names:
            self.cbRenderBy.ItemsAdd(name)
        self.cbRenderBy.ItemIndex = 1  # Default to Color
        self.cbRenderBy.OnChange = self.cbRenderBy_change

        # Number-of-classes selector (1–9); ignored for auto-count methods
        self.cbClasses = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbClasses.Place(65, 21, None, 674, None, 13)
        for i in range(1, 10):
            self.cbClasses.ItemsAdd(str(i))
        self.cbClasses.ItemIndex = 4  # Default: 5 classes
        self.cbClasses.OnChange = self.do_classify_onchange

        # Std-dev interval fraction picker (hidden unless SD/SDC is selected)
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
        self.cbInterval.Visible = False  # Shown only for StandardDeviation methods

        # Fixed interval text field (used by DefinedInterval; disabled for others)
        self.edtInterval = pdk.TGIS_PvlEdit(self.toolbar_buttons.Context)
        self.edtInterval.Place(52, 20, None, 796, None, 13)
        self.edtInterval.Text = "100"
        self.edtInterval.Enabled = False  # Enabled only when DefinedInterval is selected
        self.edtInterval.OnChange = self.do_classify_onchange

        # ------------------------------------------------------------------
        # Second toolbar row: color swatches, size, ClassIdField, legend,
        # and color-ramp controls
        # ------------------------------------------------------------------
        self.toolbar_controls = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_controls.Place(935, 44, None, 12, None, 35)

        self.lblStartColor = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblStartColor.Place(58, 13, None, 0, None, 15)
        self.lblStartColor.Caption = "Start color:"

        # Color swatch for the lowest-value (start) class color
        self.pStartColor = pdk.TGIS_PvlColorPreview(self.toolbar_controls.Context)
        self.pStartColor.Place(23, 21, None, 58, None, 11)
        self.pStartColor.Color = pdk.TGIS_Color.FromRGB(233, 248, 237)
        self.pStartColor.OnClick = self.pStartColor_click

        self.lblEndColor = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblEndColor.Place(55, 13, None, 89, None, 15)
        self.lblEndColor.Caption = "End color:"

        # Color swatch for the highest-value (end) class color
        self.pEndColor = pdk.TGIS_PvlColorPreview(self.toolbar_controls.Context)
        self.pEndColor.Place(23, 21, None, 142, None, 11)
        self.pEndColor.Color = pdk.TGIS_Color().Green
        self.pEndColor.OnClick = self.pEndColor_click

        self.lblStartSize = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblStartSize.Place(53, 13, None, 170, None, 15)
        self.lblStartSize.Caption = "Start size:"

        # Minimum symbol size used when RenderType is Size or OutlineWidth
        self.edtStartSize = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtStartSize.Place(48, 20, None, 225, None, 12)
        self.edtStartSize.Text = "1"
        self.edtStartSize.OnChange = self.do_classify_onchange

        self.lblEndSize = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblEndSize.Place(50, 13, None, 279, None, 15)
        self.lblEndSize.Caption = "End size:"

        # Maximum symbol size used when RenderType is Size or OutlineWidth
        self.edtEndSize = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtEndSize.Place(48, 20, None, 328, None, 12)
        self.edtEndSize.Text = "100"
        self.edtEndSize.OnChange = self.do_classify_onchange

        self.lblClassIdField = pdk.TGIS_PvlLabel(self.toolbar_controls.Context)
        self.lblClassIdField.Place(71, 13, None, 389, None, 15)
        self.lblClassIdField.Caption = "Class ID field:"

        # Optional name for a new numeric field added to the layer schema to
        # store the assigned class index per feature.  Leave blank to skip.
        self.edtClassIdField = pdk.TGIS_PvlEdit(self.toolbar_controls.Context)
        self.edtClassIdField.Place(100, 20, None, 463, None, 12)

        # Toggle whether classification classes appear in the layer legend panel
        self.chkShowInLegend = pdk.TGIS_PvlCheckBox(self.toolbar_controls.Context)
        self.chkShowInLegend.Place(109, 17, None, 572, None, 14)
        self.chkShowInLegend.Caption = "Show in legend"
        self.chkShowInLegend.Checked = True
        self.chkShowInLegend.OnChange = self.chkShowInLegend_change

        # Toggle color ramp override; when unchecked, StartColor/EndColor gradient is used
        self.chkUseColorRamp = pdk.TGIS_PvlCheckBox(self.toolbar_controls.Context)
        self.chkUseColorRamp.Place(107, 17, None, 683, None, 14)
        self.chkUseColorRamp.Caption = "Use color ramp"
        self.chkUseColorRamp.Checked = True
        self.chkUseColorRamp.OnChange = self.chkUseColorRamp_change

        # Named color ramp picker — populated from TGIS_Utils().GisColorRampList
        self.cbColorRamp = pdk.TGIS_PvlComboBox(self.toolbar_controls.Context)
        self.cbColorRamp.Place(121, 21, None, 793, None, 11)
        self.cbColorRamp.OnChange = self.do_classify_onchange

        # ------------------------------------------------------------------
        # Map viewer and legend
        # ------------------------------------------------------------------
        # TGIS_ViewerWnd is the core map display component; all loaded layers
        # are accessible via GIS.Items[]
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 229
        self.GIS.Top = 80
        self.GIS.Width = 718
        self.GIS.Height = 486
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # TGIS_PvlControlLegend displays an interactive layer legend.
        # Setting GIS_Viewer links it to the viewer so it shows the active layers.
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Left = 12
        self.GIS_legend.Top = 80
        self.GIS_legend.Width = 211
        self.GIS_legend.Height = 486
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                                   pdk.TGIS_PvlAnchor().Bottom)

    def do_classify_onchange(self, _sender):
        """
        Generic OnChange handler for controls that simply re-trigger classification.
        Delegates immediately to do_classify().
        """
        self.do_classify()

    def fill_cb_fields(self):
        """
        Populate cbField with the classifiable fields of the currently loaded layer.

        For vector layers (TGIS_LayerVector):
          - Always adds virtual fields first: GIS_UID, GIS_AREA, GIS_LENGTH,
            GIS_CENTROID_X, GIS_CENTROID_Y.  These are computed on-the-fly by
            the engine without needing a real attribute column.
          - Then adds numeric attribute fields of type Number or Float from
            the layer schema.

        For raster layers (TGIS_LayerPixel):
          - Adds one entry per band (band index as integer) since bands are the
            classifiable "fields" for pixel data.
        """
        lyr = self.GIS.Items[0]

        if isinstance(lyr, pdk.TGIS_LayerVector):
            lv = lyr
            # Virtual fields — always available; computed by the engine on the fly
            self.cbField.ItemsAdd(self.GIS_FIELD_UID)
            self.cbField.ItemsAdd(self.GIS_FIELD_AREA)
            self.cbField.ItemsAdd(self.GIS_FIELD_LENGTH)
            self.cbField.ItemsAdd(self.GIS_FIELD_CENTROID_X)
            self.cbField.ItemsAdd(self.GIS_FIELD_CENTROID_Y)

            # Add numeric attribute fields from the layer schema
            for field in lv.Fields:
                if field.FieldType == pdk.TGIS_FieldType().Number:
                    self.cbField.ItemsAdd(field.Name)
                elif field.FieldType == pdk.TGIS_FieldType().Float:
                    self.cbField.ItemsAdd(field.Name)

        elif isinstance(lyr, pdk.TGIS_LayerPixel):
            # For raster layers each band index is the classifiable "field"
            lp = lyr
            for i in range(1, lp.BandsCount + 1):
                self.cbField.ItemsAdd(i)

        self.cbField.ItemIndex = 0

    def fill_cb_color_ramps(self):
        """
        Populate cbColorRamp from the global GisColorRampList registry.

        Iterates TGIS_Utils().GisColorRampList and adds each ramp's Name to the
        combo box.  Pre-selects "GreenBlue" as the default ramp.
        """
        color_ramps = pdk.TGIS_Utils().GisColorRampList
        for i in range(color_ramps.Count):
            ramp_name = color_ramps.Items(i).Name
            self.cbColorRamp.ItemsAdd(ramp_name)

            if ramp_name == "GreenBlue":
                self.cbColorRamp.ItemIndex = i  # Pre-select GreenBlue as default

    def form_show(self, _sender):
        """
        OnShow handler — runs once when the form becomes visible.

        Opens the default California Counties shapefile via
        TGIS_Utils.GisSamplesDataDirDownload() so the map is populated
        immediately, then refreshes the field and color-ramp pickers.
        """
        sample_data_dir = os.path.join(pdk.TGIS_Utils.GisSamplesDataDirDownload(),
                                       "World/Countries/USA/States/California/Counties.shp")
        self.GIS.Open(sample_data_dir)

        self.fill_cb_fields()      # Populate field list for the loaded layer
        self.fill_cb_color_ramps() # Populate ramp list from the global registry

    def pStartColor_click(self, _sender):
        """
        OnClick handler for the start-color swatch.

        Opens TGIS_ControlColor (a TatukGIS PDK color-picker dialog) pre-filled
        with the current start color.  If the user confirms, updates pStartColor
        and re-classifies.  StartColor maps to the lowest-value class.
        """
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pStartColor.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return  # User cancelled; leave color unchanged

        self.pStartColor.Color = dlg_color.Color
        self.do_classify()

    def pEndColor_click(self, _sender):
        """
        OnClick handler for the end-color swatch.

        Opens TGIS_ControlColor pre-filled with the current end color.  If the
        user confirms, updates pEndColor and re-classifies.  EndColor maps to
        the highest-value class.
        """
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pEndColor.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return  # User cancelled; leave color unchanged

        self.pEndColor.Color = dlg_color.Color
        self.do_classify()

    def btnOpen_click(self, _sender):
        """
        OnClick handler for the "Open…" button.

        Shows a TGIS_PvlOpenDialog filtered to all TatukGIS-supported file types
        (via TGIS_Utils.GisSupportedFiles).  If the user selects a file, loads it
        into the viewer and refreshes the field and color-ramp pickers for the
        new layer.
        """
        dlg_open = pdk.TGIS_PvlOpenDialog(self.Context)
        dlg_open.Filter = pdk.TGIS_Utils.GisSupportedFiles([pdk.TGIS_FileType().All], False)

        if not dlg_open.Execute():
            return  # User cancelled the dialog

        self.GIS.Open(dlg_open.FileName)

        self.fill_cb_fields()      # Refresh field list for the newly opened layer
        self.fill_cb_color_ramps() # Ramp list is global but refresh for consistency

    def cbMethod_change(self, _sender):
        """
        OnChange handler for the classification method combo box.

        Updates optional control visibility and defaults based on the newly
        selected method, then calls do_classify():

        - DefinedInterval   : enables edtInterval (fixed class width); hides cbClasses
        - Quartile          : disables both edtInterval and cbClasses (always 4 classes)
        - StandardDeviation : shows cbInterval (fraction of std dev); hides cbClasses
          / SDC
        - Unique            : switches to Unique color ramp (one color per value)
        - All others        : enables cbClasses; disables edtInterval

        Methods that determine their own class count automatically do not expose
        cbClasses to avoid user confusion.
        """
        if self.edtInterval.Text == "":
            self.edtInterval.Text = "100"  # Reset to a safe default if blank

        method = str(self.cbMethod.Text)

        if method == self.GIS_CLASSIFY_METHOD_DI:
            # DefinedInterval: user supplies the class width; class count is auto
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = True
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = False
        elif method == self.GIS_CLASSIFY_METHOD_QR:
            # Quartile: always exactly 4 classes; interval not applicable
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = False
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = False
        elif method == self.GIS_CLASSIFY_METHOD_SD or method == self.GIS_CLASSIFY_METHOD_SDC:
            # StandardDeviation: Interval is a fraction of one std dev; class count is auto
            self.edtInterval.Visible = False
            self.cbInterval.Visible = True
            self.cbClasses.Enabled = False
        else:
            # All other methods: user specifies the number of classes
            self.cbInterval.Visible = False
            self.cbClasses.Enabled = True
            self.edtInterval.Visible = True
            self.edtInterval.Enabled = False

        # Switch default color ramp for Unique method; reset to GreenBlue otherwise
        if method == self.GIS_CLASSIFY_METHOD_UNQ:
            self.cbColorRamp.ItemIndex = self.cbColorRamp.IndexOf("Unique")
        else:
            self.cbColorRamp.ItemIndex = self.cbColorRamp.IndexOf("GreenBlue")

        self.do_classify()

    def do_classify(self):
        """
        Core classification routine — called whenever any classification parameter
        changes.  Assembles a fully configured TGIS_ClassificationAbstract (or its
        TGIS_ClassificationVector subclass) and calls Classify() to write rendering
        parameters to the layer.

        Workflow:
        1. Validate that a method is selected (cbMethod.ItemIndex > 0) and a layer
           is loaded (GIS.Items[0] is not None).
        2. Optionally add a ClassIdField to the vector layer schema if a name is
           provided in edtClassIdField.
        3. Create a classifier via TGIS_ClassificationFactory.CreateClassifier,
           which inspects the layer type and returns the appropriate subclass.
        4. Set common properties: Target, NumClasses, StartColor, EndColor,
           ShowLegend, Method, Interval.
        5. Set ColorRamp or clear it (use StartColor/EndColor gradient) based on
           chkUseColorRamp.  For Unique method, force Discrete colormap mode.
        6. Set vector-only properties: StartSize, EndSize, ClassIdField, RenderType.
        7. Check statistics: prompt with TGIS_PvlOptionDialog if they are required.
        8. Call classifier.Classify(); if a ClassIdField was requested, call
           SaveData() to persist the IDs.
        9. Call GIS.InvalidateWholeMap() to repaint the viewer.
        """
        # Guard: only classify when the user has actively selected a method
        if self.cbMethod.ItemIndex <= 0:
            return

        lv = self.GIS.Items[0]
        if lv is None:
            return

        create_field = False
        # Check whether the user wants to persist class IDs to an attribute field
        class_id_field = self.edtClassIdField.Text

        if isinstance(lv, pdk.TGIS_LayerVector):
            if len(class_id_field) > 0:
                create_field = True
            else:
                create_field = False
            # Add the ClassIdField column to the layer schema if it does not exist yet
            if create_field and lv.FindField(class_id_field) < 0:
                lv.AddField(class_id_field, pdk.TGIS_FieldType().Number, 3, 0)

        elif not isinstance(lv, pdk.TGIS_LayerPixel):
            # Only vector and pixel layers are supported by the classification API
            pdk.TGIS_PvlMessages.ShowInfo(f"Layer {lv.Name: str} is not supported.", self.Context)

        # TGIS_ClassificationFactory.CreateClassifier inspects the layer type and
        # returns TGIS_ClassificationVector or TGIS_ClassificationPixel accordingly.
        classifier = pdk.TGIS_ClassificationFactory.CreateClassifier(lv)

        # ---------------------------------------------------------------
        # Common classifier properties
        # ---------------------------------------------------------------

        # Target: attribute field name (vector) or band index string (pixel)
        classifier.Target = str(self.cbField.Text)

        # NumClasses is ignored (auto-calculated) for: DefinedInterval, Quartile,
        # StandardDeviation, and StandardDeviationWithCentral.
        classifier.NumClasses = self.cbClasses.ItemIndex + 1

        # Color gradient endpoints: StartColor = lowest-value class, EndColor = highest
        classifier.StartColor = self.pStartColor.Color
        classifier.EndColor = self.pEndColor.Color

        # ShowLegend: controls whether class entries appear in the layer legend
        classifier.ShowLegend = self.chkShowInLegend.Checked

        # ---------------------------------------------------------------
        # Classification method
        # ---------------------------------------------------------------
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

        # ---------------------------------------------------------------
        # Interval
        # ---------------------------------------------------------------
        # For DefinedInterval: the fixed class width parsed from edtInterval.
        # For StandardDeviation methods: overridden below with a fraction value.
        classifier.Interval = float(self.edtInterval.Text)

        if method == self.GIS_CLASSIFY_METHOD_SD or method == self.GIS_CLASSIFY_METHOD_SDC:
            # Express Interval as a fraction of one standard deviation
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

        # ---------------------------------------------------------------
        # Color ramp
        # NumClasses is automatically calculated for: DefinedInterval,
        # Quartile, StandardDeviation, StandardDeviationWithCentral.
        # ---------------------------------------------------------------
        if self.chkUseColorRamp.Checked:
            # Unique method requires Discrete mode (one solid color per class);
            # all other methods use Continuous (smooth gradient across classes).
            if method == self.GIS_CLASSIFY_METHOD_UNQ:
                colormap_mode = pdk.TGIS_ColorMapMode().Discrete
            else:
                colormap_mode = pdk.TGIS_ColorMapMode().Continuous
            classifier.ColorRamp = pdk.TGIS_Utils().GisColorRampList[self.cbColorRamp.ItemIndex]
            classifier.ColorRamp.DefaultColorMapMode = colormap_mode
        else:
            # Clear the ramp so the plain StartColor → EndColor gradient is used instead
            classifier.ColorRampName = ""

        # ---------------------------------------------------------------
        # Vector-only parameters (TGIS_ClassificationVector subclass only)
        # ---------------------------------------------------------------
        if isinstance(classifier, pdk.TGIS_ClassificationVector):
            classifier_vec = classifier
            classifier_vec.StartSize = int(self.edtStartSize.Text)  # Min symbol size
            classifier_vec.EndSize   = int(self.edtEndSize.Text)    # Max symbol size
            classifier_vec.ClassIdField = class_id_field            # Field for class IDs

            # Map the render-type string to the TGIS_ClassificationRenderType enum
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

        # ---------------------------------------------------------------
        # Statistics management
        # Classification algorithms (NaturalBreaks, KMeans, etc.) require layer
        # statistics (min, max, mean, std dev) before they can run.
        # MustCalculateStatistics() returns True when they are missing or stale.
        # ---------------------------------------------------------------
        if classifier.MustCalculateStatistics():
            res = pdk.TGIS_PvlOptionDialog(self.Context)
            res.Text = "Statistics need to be calculated"
            if res.Execute() != pdk.TGIS_PvlModalResult.No:
                lv.Statistics.Calculate()       # Compute statistics now
            else:
                lv.Statistics.ResetModified()   # Discard the stale-statistics flag
                return

        # Run the classification and, if a ClassIdField was requested, persist the IDs
        if classifier.Classify() and create_field and lv is not None:
            lv.SaveData()

        # Repaint the viewer so the newly classified colours are rendered immediately
        self.GIS.InvalidateWholeMap()

    def cbRenderBy_change(self, _sender):
        """
        OnChange handler for the render-type combo box.

        Before switching render type, resets all per-feature rendering parameters
        via ParamsList.ClearAndSetDefaults() so the previous classification styling
        does not bleed through.  Prevents the Size render type from being used with
        polygon layers (not meaningful for filled areas).
        """
        ll = self.GIS.Items[0]
        if ll is None:
            return

        if isinstance(ll, pdk.TGIS_LayerVector):
            # ClearAndSetDefaults resets any styling applied by the previous
            # classification so the new render type starts from a clean slate.
            ll.ParamsList.ClearAndSetDefaults()
            if (ll.DefaultShapeType == pdk.TGIS_ShapeType().Polygon
                    and self.cbRenderBy.Text == self.RENDER_TYPE_SIZE):
                pdk.TGIS_PvlMessages.ShowInfo("Method not allowed for polygons", self.Context)
                self.cbRenderBy.ItemIndex = 1  # Fall back to Color

        self.do_classify()

    def chkShowInLegend_change(self, _sender):
        """
        OnChange handler for the "Show in legend" checkbox.
        Re-classifies so the ShowLegend property takes effect immediately.
        """
        self.do_classify()

    def chkUseColorRamp_change(self, _sender):
        """
        OnChange handler for the "Use color ramp" checkbox.

        Enables or disables the color-ramp picker (cbColorRamp) in sync with the
        checkbox, then re-classifies.  When unchecked the plain StartColor/EndColor
        gradient is used instead of a named ramp.
        """
        self.cbColorRamp.Enabled = self.chkUseColorRamp.Checked
        self.do_classify()


def main():
    """
    Application entry point.

    Creates the ClassificationForm, calls Show() to make it visible (which
    triggers form_show via OnShow to load the default layer), then hands control
    to the TatukGIS PDK event loop via pdk.RunPvl().
    """
    frm = ClassificationForm(None)
    frm.Show()
    pdk.RunPvl(frm)  # Start the PDK message/event loop


if __name__ == '__main__':
    main()
