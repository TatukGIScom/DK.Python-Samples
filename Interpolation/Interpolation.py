"""
=============================================================================
This source code is a part of TatukGIS Developer Kernel.
=============================================================================

Interpolation Sample (Python / PDK edition)

Demonstrates generating a raster grid from vector point data using various
spatial interpolation methods.

This sample demonstrates:
  - Opening a TatukGIS project file (.ttkproject) containing:
      "temperatures" - a vector point layer with a numeric "TEMP" field
      "country"      - a polygon layer used for output extent and clipping
  - Setting the viewer's coordinate system to EPSG:3395 (World Mercator) so
    that distance-based interpolation calculations use consistent metre units.
  - Creating an in-memory TGIS_LayerPixel as the interpolation output,
    sized with an aspect ratio correction so pixels are square.
  - Running five vector-to-grid conversion methods:
      IDW               - Inverse Distance Weighting (weight = 1/dist^exponent)
      Kriging           - geostatistical method with a semivariogram model
      Splines           - Completely Regularized Splines (radial basis functions)
      Heat Map          - Gaussian kernel density weighted by TEMP field values
      Concentration Map - Gaussian kernel density counting points only
  - Applying a Blue->Lime->Red colour ramp via GenerateRamp.
  - Clipping the output to the country polygon via CuttingPolygon.
  - Reporting progress through a BusyEvent callback that updates a label.

Key TatukGIS API classes used:
  TGIS_ViewerWnd              - map viewer component (PDK visual form)
  TGIS_LayerVector            - source point / polygon layer
  TGIS_LayerPixel             - destination raster grid layer
  TGIS_InterpolationIDW       - IDW interpolation engine
  TGIS_InterpolationKriging   - Kriging interpolation engine
  TGIS_InterpolationSplines   - Completely Regularized Splines engine
  TGIS_GaussianHeatmap        - Gaussian heat/concentration map engine
  TGIS_CSFactory              - coordinate system factory (EPSG lookup)
  TGIS_Utils                  - utility helpers (sample data directory)

Python-specific notes:
  - TGIS_PvlRadioButton does not update its Checked state until AFTER the
    OnClick handler returns.  To read the new state inside the handler the
    sample sets _sender.Checked = True manually, reads the state, then
    resets it to False so the framework can apply the final value.
  - Progress reporting uses a TGIS_PvlLabel (not a real progress bar) because
    the PDK does not expose a native progress bar widget.
  - ProcessMessages() is called inside doBusyEvent to pump the event loop
    and keep the UI responsive during the synchronous interpolation run.
"""

import tatukgis_pdk as pdk


class InterpolationForm(pdk.TGIS_PvlForm):
    """
    Main form for the Interpolation sample application.

    Loads the project on show, provides five method radio buttons, a
    Semivariance combo (Kriging only), a Generate button and a progress label.
    """

    # Name of the attribute field in the "temperatures" point layer to interpolate
    FIELD_VALUE = "TEMP"

    # Output raster width in pixels; height is computed from the extent aspect ratio
    # so that output pixels are square in the projected coordinate system
    GRID_RESOLUTION = 400

    # References to the source/destination layers; populated in btnGenerate_click
    src = None
    dst = None

    def __init__(self, _owner):
        self.Caption = "Interpolation - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 430
        # Open the project file when the form is first displayed
        self.OnShow = self.form_show

        # --- Map viewer (right side) ----------------------------------------
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 152
        self.GIS.Top = 12
        self.GIS.Width = 420
        self.GIS.Height = 358
        # Anchor to all four sides so the viewer resizes with the form
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # --- Method selection (left side) -----------------------------------
        self.lblMethod = pdk.TGIS_PvlLabel(self.Context)
        self.lblMethod.Place(43, 13, None, 12, None, 13)
        self.lblMethod.Caption = "Method"

        # IDW radio button - default selected method
        self.rbIDW = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbIDW.Place(134, 17, None, 12, None, 30)
        self.rbIDW.Caption = "IDW Interpolation"
        self.rbIDW.Checked = True  # pre-select IDW on startup
        self.rbIDW.OnClick = self.rbAny_click

        # Kriging radio button - requires semivariance model choice
        self.rbKriging = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbKriging.Place(134, 17, None, 12, None, 53)
        self.rbKriging.Caption = "Kriging Interpolation"
        self.rbKriging.OnClick = self.rbAny_click

        # Completely Regularized Splines radio button
        self.rbSpline = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbSpline.Place(134, 17, None, 12, None, 76)
        self.rbSpline.Caption = "Spline Interpolation"
        self.rbSpline.OnClick = self.rbAny_click

        # Gaussian Heat Map radio button - uses TEMP field values
        self.rbHeatMap = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbHeatMap.Place(134, 17, None, 12, None, 99)
        self.rbHeatMap.Caption = "Heat Map"
        self.rbHeatMap.OnClick = self.rbAny_click

        # Concentration Map radio button - counts point density only
        self.rbConcentrationMap = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbConcentrationMap.Place(134, 17, None, 12, None, 122)
        self.rbConcentrationMap.Caption = "Concentration Map"
        self.rbConcentrationMap.OnClick = self.rbAny_click

        # Semivariance label and combo (shown only when Kriging is selected)
        self.lblSemivariance = pdk.TGIS_PvlLabel(self.Context)
        self.lblSemivariance.Place(71, 13, None, 12, None, 157)
        self.lblSemivariance.Caption = "Semivariance"
        self.lblSemivariance.Visible = False  # hidden until Kriging is chosen

        self.cbSemivariance = pdk.TGIS_PvlComboBox(self.Context)
        self.cbSemivariance.Place(134, 21, None, 12, None, 173)
        # Populate the semivariogram model options
        names = ("Power Law", "Exponential", "Gaussian", "Spherical", "Circular", "Linear")
        for name in names:
            self.cbSemivariance.ItemsAdd(name)
        self.cbSemivariance.ItemIndex = 0   # default: Power Law
        self.cbSemivariance.Visible = False  # hidden until Kriging is chosen

        # Generate button (anchored to bottom-left)
        self.btnGenerate = pdk.TGIS_PvlButton(self.Context)
        self.btnGenerate.Place(134, 23, None, 12, None, 376)
        self.btnGenerate.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.btnGenerate.Caption = "Generate"
        self.btnGenerate.OnClick = self.btnGenerate_click

        # Progress label - used instead of a progress bar (PDK limitation)
        # Shows "progress: N %" text during interpolation
        self.progressBar1 = pdk.TGIS_PvlLabel(self.Context)
        self.progressBar1.Place(142, 23, None, 192, None, 376)
        self.progressBar1.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.progressBar1.Visible = False  # only shown during interpolation

    def form_show(self, _sender):
        """
        Called when the form is first displayed.

        Opens the bundled TatukGIS project which provides:
          "temperatures" - point layer with TEMP attribute values
          "country"      - polygon layer used for extent and clipping

        Sets the coordinate system to EPSG:3395 (World Mercator) so that
        distance-based interpolation calculations use consistent metre units.
        """
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "Samples/Interpolation/Interpolation.ttkproject"
        )
        # World Mercator: ensures interpolation distances are in metres
        self.GIS.CS = pdk.TGIS_CSFactory.ByEPSG(3395)

    def rbAny_click(self, _sender):
        """
        Shared OnClick handler for all five method radio buttons.

        Shows the Semivariance combo only when Kriging is selected.

        Python-specific workaround: TGIS_PvlRadioButton's Checked state is
        only committed AFTER the OnClick handler returns.  To read the new
        selection inside this handler, the sample temporarily sets
        _sender.Checked = True, reads the state, then resets it so the
        framework can apply the final value on handler exit.
        """
        # Temporarily mark this button as checked so rbKriging.Checked reads True
        _sender.Checked = True
        if self.rbKriging.Checked:
            # Kriging requires a semivariogram model - reveal the selector
            self.lblSemivariance.Visible = True
            self.cbSemivariance.Visible = True
        else:
            # All other methods work without a semivariogram
            self.lblSemivariance.Visible = False
            self.cbSemivariance.Visible = False
        # Reset so the framework can commit the proper Checked state on return
        _sender.Checked = False

    def doBusyEvent(self, _sender, pos, _end, _abort):
        """
        Progress callback invoked by the interpolation engine at regular intervals.

        Updates the progress label and calls ProcessMessages() to keep the UI
        responsive during the synchronous interpolation run.

        Convention:
          pos == 0  => initialise (show 0%)
          pos < 0   => finished (show 100%)
          pos > 0   => current progress percentage
        """
        self.progressBar1.Visible = True
        if pos == 0:
            self.progressBar1.Caption = 'progress: 0 %'
        elif pos < 0:
            self.progressBar1.Caption = 'progress: 100 %'
        else:
            self.progressBar1.Caption = 'progress: ' + str(pos) + ' %'
        # Pump the event loop so the label repaint reaches the screen
        self.GIS.ProcessMessages()

    def doIDW(self):
        """
        Runs Inverse Distance Weighting (IDW) interpolation.

        IDW estimates each output cell as a weighted average of all sample
        points where the weight is 1/distance^Exponent.  An Exponent of 3.0
        produces a more localised surface with sharper peaks than the default 2.0.

        To restrict the search neighbourhood and speed up large datasets, enable
        windowed mode by setting Windowed=True and providing a search Radius.
        """
        vtg = pdk.TGIS_InterpolationIDW()
        # For windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.:
        #   vtg.Windowed = True
        #   vtg.Radius = (ext.XMax - ext.XMin) / 5.0

        # Attach the progress callback to keep the label updated
        vtg.BusyEvent = self.doBusyEvent

        # Exponent 3.0 gives sharper local peaks than the default 2.0
        vtg.Exponent = 3.0

        # Generate the IDW grid: read FIELD_VALUE from src, write to dst
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doKriging(self):
        """
        Runs Ordinary Kriging interpolation.

        Kriging models spatial autocorrelation via a semivariogram and produces
        a statistically optimal (Best Linear Unbiased) estimate at each cell.
        The semivariogram model governs the spatial dependence structure and
        should be chosen to match the data's known spatial behaviour:

          Power Law    - scale-free power relationship (default)
          Exponential  - exponential decay of spatial correlation
          Gaussian     - smooth bell-curve decay
          Spherical    - linear increase then plateau (common in geology)
          Circular     - circular model
          Linear       - simple linear model
        """
        vtg = pdk.TGIS_InterpolationKriging()

        # For windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.:
        #   vtg.Windowed = True
        #   vtg.Radius = (ext.XMax - ext.XMin) / 5.0

        # Attach the progress callback
        vtg.BusyEvent = self.doBusyEvent

        # Select the semivariogram model from the combo box
        if self.cbSemivariance.ItemIndex == 0:
            vtg.Semivariance = pdk.TGIS_SemivariancePowerLaw()
        if self.cbSemivariance.ItemIndex == 1:
            vtg.Semivariance = pdk.TGIS_SemivarianceExponential()
        elif self.cbSemivariance.ItemIndex == 2:
            vtg.Semivariance = pdk.TGIS_SemivarianceGaussian()
        elif self.cbSemivariance.ItemIndex == 3:
            vtg.Semivariance = pdk.TGIS_SemivarianceSpherical()
        elif self.cbSemivariance.ItemIndex == 4:
            vtg.Semivariance = pdk.TGIS_SemivarianceCircular()
        elif self.cbSemivariance.ItemIndex == 5:
            vtg.Semivariance = pdk.TGIS_SemivarianceLinear()

        # Generate the Kriging interpolation grid
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doSplines(self):
        """
        Runs Completely Regularized Splines (CRS) interpolation.

        CRS fits a smooth surface through the sample points using radial basis
        functions.  The Tension parameter controls surface stiffness: 1e-9 gives
        a near-minimum-curvature (very smooth) result.  Increase Tension if
        unwanted oscillations appear in data-sparse regions.
        """
        vtg = pdk.TGIS_InterpolationSplines()

        # For windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.:
        #   vtg.Windowed = True
        #   vtg.Radius = (ext.XMax - ext.XMin) / 5.0

        # Attach the progress callback
        vtg.BusyEvent = self.doBusyEvent
        # Tension=1e-9 produces a very smooth minimum-curvature surface
        vtg.Tension = 1e-9
        # Generate the Completely Regularized Splines interpolation grid
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doHeatmap(self, concentration):
        """
        Runs Gaussian Heat Map or Concentration Map generation.

        Both modes use TGIS_GaussianHeatmap; the difference is the field used:

          Heat Map (concentration=False):
            Each point spreads its TEMP value through a Gaussian kernel.
            High-value points create brighter hotspots.

          Concentration Map (concentration=True):
            Ignores the TEMP field; every point contributes equally so
            the output represents spatial point density.

        EstimateRadius computes the 3-sigma Gaussian bandwidth automatically
        from the average nearest-neighbour distance in the source layer.
        Halving the estimated radius produces a finer, more peaked result.

        Args:
            concentration: True for Concentration Map (density only);
                           False for Heat Map (field values weighted).
        """
        vtg = pdk.TGIS_GaussianHeatmap()

        # Coordinate.None_ means point centroids are used as-is (no offset)
        # Note: Python uses None_ because None is a reserved keyword
        vtg.Coordinate = pdk.TGIS_VectorToGridCoordinate().None_
        if concentration:
            # Concentration Map: empty field name so only point presence counts
            fld = ""
        else:
            fld = self.FIELD_VALUE

        # Attach the progress callback
        vtg.BusyEvent = self.doBusyEvent
        # Estimate the optimal Gaussian kernel radius from the data distribution
        vtg.EstimateRadius(self.src, self.src.Extent, self.dst)
        # Halve the estimated radius for a more localised, peaked result
        vtg.Radius = vtg.Radius / 2.0
        # Generate the Heat/Concentration Map grid
        vtg.Generate(self.src, self.src.Extent, fld, self.dst, self.dst.Extent)

    def btnGenerate_click(self, _sender):
        """
        Main Generate button handler: orchestrates the full interpolation workflow.

        Steps:
          1. Retrieve source ("temperatures") and polygon ("country") layers by name.
          2. Delete any previous "grid" layer to avoid duplicates.
          3. Compute the geographic extent and aspect ratio from the polygon layer.
          4. Create a blank in-memory TGIS_LayerPixel with square pixels.
          5. Dispatch to the selected interpolation method.
          6. Apply a Blue->Lime->Red colour ramp via GenerateRamp.
          7. Clip the output to the country polygon via CuttingPolygon.
          8. Add the grid to the viewer and zoom to full extent.
        """
        self.btnGenerate.Enabled = False

        # Retrieve named layers from the loaded project
        self.src = self.GIS.Get("temperatures")  # point data source
        plg = self.GIS.Get("country")            # polygon for extent and clip

        # Remove any previous interpolation result so we start fresh
        if self.GIS.Get("grid") is not None:
            self.GIS.Delete("Grid")

        # Use the polygon's full extent as the output domain
        # (this is larger than the scattered point bounding box)
        ext = plg.Extent

        # Compute aspect ratio so the output raster cells are square when projected
        rat = (ext.YMax - ext.YMin) / (ext.XMax - ext.XMin)

        # Create the in-memory raster output layer
        self.dst = pdk.TGIS_LayerPixel()
        self.dst.Name = "grid"
        # Build allocates the pixel buffer:
        #   True           = in-memory (not backed by a file)
        #   self.src.CS    = coordinate system from the source layer
        #   ext            = geographic extent of the output domain
        #   GRID_RESOLUTION = pixel width; rounded height keeps pixels square
        self.dst.Build(True, self.src.CS, ext, self.GRID_RESOLUTION, int(round(rat * self.GRID_RESOLUTION)))
        # Disable hill-shading because the interpolated values are not elevation
        self.dst.Params.Pixel.GridShadow = False

        # Default ramp start colour (overridden to transparent blue for heat maps)
        clr = pdk.TGIS_Color.Blue

        # Dispatch to the selected interpolation method
        if self.rbIDW.Checked:
            # Inverse Distance Weighting
            self.doIDW()
        elif self.rbKriging.Checked:
            # Geostatistical Kriging
            self.doKriging()
        elif self.rbSpline.Checked:
            # Completely Regularized Splines
            self.doSplines()
        elif self.rbHeatMap.Checked:
            # Gaussian heat map weighted by TEMP field
            self.doHeatmap(False)
            # Use a transparent blue ramp start so the basemap shows through
            # where density is zero (alpha=0 means fully transparent)
            clr = pdk.TGIS_Color.FromARGB(0, 0, 0, 255)
        elif self.rbConcentrationMap.Checked:
            # Gaussian concentration map (point density only)
            self.doHeatmap(True)
            clr = pdk.TGIS_Color.FromARGB(0, 0, 0, 255)

        # Apply a three-stop colour ramp across the full value range of the grid.
        # Arguments: start, mid, end colours, minVal, midVal, maxVal, useLog,
        #            minStep, maxStep, existingZones, clearFirst
        self.dst.GenerateRamp(
            clr, pdk.TGIS_Color().Lime, pdk.TGIS_Color().Red, self.dst.MinHeight,
            (self.dst.MaxHeight - self.dst.MinHeight) / 2.0, self.dst.MaxHeight, False,
            (self.dst.MaxHeight - self.dst.MinHeight) / 100.0,
            (self.dst.MaxHeight - self.dst.MinHeight) / 10.0,
            None, False
        )

        # Clip the grid to the country boundary so only cells within the polygon
        # are rendered.  GetShape(6) is the 7th shape (0-based) in the polygon layer;
        # CreateCopy is required because CuttingPolygon takes ownership of the shape.
        self.dst.CuttingPolygon = plg.GetShape(6).CreateCopy()

        # Add the generated grid to the viewer layer list
        self.GIS.Add(self.dst)
        # Zoom to display the full interpolated result
        self.GIS.FullExtent()
        # Hide the progress label now that the operation is complete
        self.btnGenerate.Enabled = True


def main():
    """
    Application entry point.
    Creates the InterpolationForm, displays it, and starts the PDK event loop.
    """
    frm = InterpolationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
