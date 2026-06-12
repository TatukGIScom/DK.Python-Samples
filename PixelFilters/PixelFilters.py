"""
PixelFilters - demonstrates how to apply image-processing filters to raster
(pixel) layers using TatukGIS (Python PDK edition).

The sample loads a DEM (Digital Elevation Model) in ESRI ADF format and lets
the user pick a filter from a list, configure its parameters, and execute it.
The filtered result replaces the input layer in the viewer.

Supported filter categories:
  - Intensity / threshold  : Threshold, Salt-and-Pepper Noise, Gaussian Noise
  - Convolution kernels    : Low-Pass, High-Pass, Gaussian, Laplacian, Gradient
                             direction, Point Detector, Line Detectors
  - Rank / statistical     : Sobel Magnitude, Range, Midpoint, Minimum, Maximum,
                             Arithmetic Mean, Alpha-Trimmed Mean,
                             Contra-Harmonic Mean, Geometric Mean, Harmonic Mean,
                             Weighted Mean, Yp Mean, Majority, Minority, Median,
                             Weighted Median, Sum, Standard Deviation, Unique Count
  - Morphological          : Erosion, Dilation, Opening, Closing, Top-Hat, Bottom-Hat

Key TatukGIS API concepts shown here:
  - TGIS_LayerPixel             : base class for raster layers; the filter input
  - TGIS_PixelFilterAbstract    : abstract base for all pixel filters; set
                                  SourceLayer, DestinationLayer, Band, ColorSpace,
                                  BusyEvent, then call Execute()
  - TGIS_PixelFilterConvolution : applies a predefined kernel matrix; kernel type
                                  set via MaskType (TGIS_PixelFilterMaskType enum)
  - TGIS_PixelFilterStructuringElementType : structuring element shape for
                                  morphological operations (Square, Diamond, Disk,
                                  line variants)
  - TGIS_PixelFilterColorSpace  : colour space in which the filter operates;
                                  HSL here so the filter acts on luminance
  - TGIS_LayerPixel.Build()     : creates an in-memory output layer matching the
                                  input layer's CRS and pixel dimensions
  - filter.BusyEvent            : progress callback during Execute(); used here
                                  to update a label instead of a native progress bar
  - bFirst flag                 : True on the first Execute; a fresh output layer is
                                  created and swapped in.  Subsequent runs are
                                  in-place (output_layer = input_layer)
  - TGIS_Utils.GisSamplesDataDirDownload() : resolves the sample-data root path
"""

import tatukgis_pdk as pdk


class PixelFiltersForm(pdk.TGIS_PvlForm):
    """
    Main form for the PixelFilters sample.
    Provides a filter list, parameter controls (block size, kernel type,
    structuring element), Execute and Reset buttons, a progress label, and a
    map viewer wired to a legend panel.
    """

    # bFirst: True until the first Execute call creates and swaps in the output layer
    bFirst = None

    def __init__(self, _owner):
        self.Caption = "PixelFilters - TatukGIS DK Sample"
        self.ClientWidth = 674
        self.ClientHeight = 466
        # Wire the OnShow event so we initialise the viewer after layout is complete
        self.OnShow = self.form_show

        # --- TatukGIS map viewer (anchored to fill the right portion of the form) ---
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 174
        self.GIS.Top = 12
        self.GIS.Width = 488
        self.GIS.Height = 442
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        # --- "Filters" label ---
        self.lblFilters = pdk.TGIS_PvlLabel(self.Context)
        self.lblFilters.Place(34, 13, None, 10, None, 12)
        self.lblFilters.Caption = "Filters"

        # --- Filter list box (all 29 filter types) ---
        self.lbFilters = pdk.TGIS_PvlListBox(self.Context)
        self.lbFilters.Place(156, 212, None, 12, None, 28)
        names = ("Threshold",
                 "Salt-And-Pepper Noise",
                 "Gaussian Noise",
                 "Convolution",
                 "Sobel Magnitude",
                 "Range",
                 "Midpoint",
                 "Minimum",
                 "Maximum",
                 "Arithmetic Mean",
                 "Alpha-Trimmed Mean",
                 "Contra-Harmonic Mean",
                 "Geometric Mean",
                 "Harmonic Mean",
                 "Weighted Mean",
                 "Yp Mean",
                 "Majority",
                 "Minority",
                 "Median",
                 "Weighted Median",
                 "Sum",
                 "Standard Deviation",
                 "Unique Count",
                 "Erosion",
                 "Dilatation",
                 "Opening",
                 "Closing",
                 "Top-Hat",
                 "Bottom-Hat")
        for name in names:
            self.lbFilters.ItemsAdd(name)
        self.lbFilters.ItemIndex = 0
        self.lbFilters.OnClick = self.lbFilters_change
        self.lbFilters.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        # --- Mask size label (hidden until a block-based filter is selected) ---
        self.lblMask = pdk.TGIS_PvlLabel(self.Context)
        self.lblMask.Place(33, 13, None, 12, None, 247)
        self.lblMask.Caption = "Mask Size"
        self.lblMask.Visible = False
        self.lblMask.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- "Mask Size" label ---
        self.lblMaskSize = pdk.TGIS_PvlLabel(self.Context)
        self.lblMaskSize.Place(56, 13, None, 10, None, 247)
        self.lblMaskSize.Caption = "Mask Size"
        self.lblMaskSize.Visible = False
        self.lblMaskSize.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Block-size track bar (hidden until a block-based filter is selected) ---
        # Odd sizes only: block = 2 * Position + 1
        self.tbMaskSize = pdk.TGIS_PvlTrackBar(self.Context)
        self.tbMaskSize.Place(121, 45, None, 10, None, 263)
        self.tbMaskSize.Maximum = 12
        self.tbMaskSize.Position = 1   # Default: position=1 -> block size 3x3
        self.tbMaskSize.Visible = False
        self.tbMaskSize.OnChange = self.tbMaskSize_change
        self.tbMaskSize.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Block-size value label (e.g. "3x3") ---
        self.lblMaskSizeValue = pdk.TGIS_PvlLabel(self.Context)
        self.lblMaskSizeValue.Place(40, 13, None, 130, None, 267)
        self.lblMaskSizeValue.Caption = "3x3"
        self.lblMaskSizeValue.Visible = False
        self.lblMaskSizeValue.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Convolution kernel type combo box (shown only for Convolution filter) ---
        self.cbMask = pdk.TGIS_PvlComboBox(self.Context)
        self.cbMask.Place(157, 21, None, 11, None, 263)
        names = ("Low-Pass 3x3",
                 "Low-Pass 5x5",
                 "Low-Pass 7x7",
                 "High-Pass 3x3",
                 "High-Pass 5x5",
                 "High-Pass 7x7",
                 "Gaussian 3x3",
                 "Gaussian 5x5",
                 "Gaussian 7x7",
                 "Laplacian 3x3",
                 "Laplacian 5x5",
                 "GradientNorth",
                 "GradientEast",
                 "GradientSouth",
                 "GradientWest",
                 "GradientNorthwest",
                 "GradientNortheast",
                 "GradientSouthwest",
                 "GradientSoutheast",
                 "PointDetector",
                 "LineDetectorHorizontal",
                 "LineDetectorVertical",
                 "LineDetectorLeftDiagonal",
                 "LineDetectorRightDiagonal")
        for name in names:
            self.cbMask.ItemsAdd(name)
        self.cbMask.ItemIndex = 0
        self.cbMask.Visible = False
        self.cbMask.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Structuring element label (shown only for morphological filters) ---
        self.lblStructuring = pdk.TGIS_PvlLabel(self.Context)
        self.lblStructuring.Place(104, 13, None, 10, None, 295)
        self.lblStructuring.Caption = "Structuring Elements"
        self.lblStructuring.Visible = False
        self.lblStructuring.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Structuring element type combo box (shown only for morphological filters) ---
        self.cbStructuring = pdk.TGIS_PvlComboBox(self.Context)
        self.cbStructuring.Place(156, 21, None, 12, None, 311)
        names = ["Square",
                 "Diamond",
                 "Disk",
                 "Horizontal Line",
                 "Vertical Line",
                 "Left Diagonal Line",
                 "Right Diagonal Line"]
        for name in names:
            self.cbStructuring.ItemsAdd(name)
        self.cbStructuring.ItemIndex = 0
        self.cbStructuring.Visible = False
        self.cbStructuring.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Execute button: applies the selected filter ---
        self.btnExecute = pdk.TGIS_PvlButton(self.Context)
        self.btnExecute.Place(75, 23, None, 12, None, 338)
        self.btnExecute.Caption = "Execute"
        self.btnExecute.OnClick = self.btnExecute_click
        self.btnExecute.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Reset button: reloads the original raster ---
        self.btnReset = pdk.TGIS_PvlButton(self.Context)
        self.btnReset.Place(75, 23, None, 93, None, 338)
        self.btnReset.Caption = "Reset"
        self.btnReset.OnClick = self.btnReset_click
        self.btnReset.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Progress label: text-based substitute for a native progress bar ---
        self.progress_bar = pdk.TGIS_PvlLabel(self.Context)
        self.progress_bar.Place(156, 23, None, 12, None, 431)
        self.progress_bar.Caption = ''
        self.progress_bar.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # --- Layer legend panel docked to the bottom-left ---
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(156, 58, None, 12, None, 367)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

    def open(self):
        """
        Loads (or reloads) the sample DEM raster layer into the viewer.
        The ADF file is a DEM covering part of San Bernardino County, California.
        AltitudeMapZones are cleared and GridShadow is disabled so the layer
        renders as a plain grey-scale elevation image, making filter effects easy
        to observe.  bFirst is reset to True so the next Execute creates a fresh
        output layer rather than filtering in-place.
        """
        self.GIS.Close()
        # GisCreateLayer() infers the layer type from the file extension/format
        path = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                + r"World\Countries\USA\States\California\San Bernardino\NED\w001001.adf")
        ll = pdk.TGIS_Utils.GisCreateLayer("input", path)
        ll.Open()
        ll.Params.Pixel.AltitudeMapZones.Clear()  # Remove colour zones for a plain grey view
        ll.Params.Pixel.GridShadow = False         # Disable hillshade shadow

        self.GIS.Add(ll)
        self.GIS.FullExtent()

        self.bFirst = True  # Next Execute() must create a fresh output layer

    def on_change(self):
        """
        Adjusts the visibility of parameter controls based on the selected filter.

        - Filters 0-2 (noise/threshold): no configurable parameters; all controls hidden.
        - Filter 3 (Convolution): show only the kernel-type combo box (cbMask).
        - Filters 4-22 (rank/statistical): show only the block-size track bar.
        - Filters 23-28 (morphological): show both block size and structuring element.
        """
        if self.lbFilters.ItemIndex == 0 or self.lbFilters.ItemIndex == 1 or self.lbFilters.ItemIndex == 2:
            # Noise/threshold filters have no user-adjustable parameters
            self.cbStructuring.Visible = False
            self.lblStructuring.Visible = False
            self.lblMask.Visible = False
            self.cbMask.Visible = False
            self.lblMaskSize.Visible = False
            self.lblMaskSizeValue.Visible = False
            self.tbMaskSize.Visible = False
        else:
            if self.lbFilters.ItemIndex == 23 or \
                    self.lbFilters.ItemIndex == 24 or \
                    self.lbFilters.ItemIndex == 25 or \
                    self.lbFilters.ItemIndex == 26 or \
                    self.lbFilters.ItemIndex == 27 or \
                    self.lbFilters.ItemIndex == 28:
                # Morphological filters need both block size and structuring element
                self.cbStructuring.Visible = True
                self.lblStructuring.Visible = True
                self.lblMask.Visible = True
                self.cbMask.Visible = True
                self.lblMaskSize.Visible = True
                self.lblMaskSizeValue.Visible = True
                self.tbMaskSize.Visible = True
            else:
                # Rank/statistical filters: only block size is relevant
                self.cbStructuring.Visible = False
                self.lblStructuring.Visible = False
                self.lblMask.Visible = False
                self.cbMask.Visible = False
                self.lblMaskSize.Visible = False
                self.lblMaskSizeValue.Visible = False
                self.tbMaskSize.Visible = False

            if self.lbFilters.ItemIndex == 3:
                # Convolution filter: show only the kernel-type combo box
                self.cbMask.Visible = True
                self.lblMask.Visible = True
                self.lblMaskSize.Visible = False
                self.lblMaskSizeValue.Visible = False
                self.tbMaskSize.Visible = False
            else:
                # All other parameterised filters: show only the block-size slider
                self.cbMask.Visible = False
                self.lblMask.Visible = False
                self.lblMaskSize.Visible = True
                self.lblMaskSizeValue.Visible = True
                self.tbMaskSize.Visible = True

    def form_show(self, _sender):
        """
        Called when the form first becomes visible.
        Sets default selections and loads the raster into the viewer.
        """
        self.lbFilters.ItemIndex = 0     # Default: Threshold filter
        self.cbStructuring.ItemIndex = 0 # Default SE shape: Square
        self.cbMask.ItemIndex = 0        # Default kernel: Low-Pass 3x3

        self.on_change()  # Initialise parameter-control visibility
        self.open()       # Load the DEM

    def do_busy_event(self, _sender, pos, end, _abort):
        """
        Progress callback invoked during filter Execute().
        Updates a text label to show percentage progress.
        end <= 0 hides the label when the filter is finished.
        GIS.ProcessMessages() keeps the UI responsive during long operations.
        """
        if end <= 0:
            self.progress_bar.Visible = False  # Filter complete; hide the label
        else:
            self.progress_bar.Visible = True
            self.progress_bar.Caption = 'progress: ' + str(int(pos/end * 100)) + " %"

        self.GIS.ProcessMessages()  # Allow the UI to repaint during the filter run

    def lbFilters_change(self, _sender):
        """Updates visible parameter controls when a different filter is selected."""
        self.on_change()

    def tbMaskSize_change(self, _sender):
        """
        Updates the block-size label when the track bar moves.
        Block size is always odd: 2 * Position + 1 (e.g. Position=1 -> 3x3).
        """
        i = int(2 * self.tbMaskSize.Position + 1)
        self.lblMaskSizeValue.Caption = str(i) + "x" + str(i)

    def btnReset_click(self, _sender):
        """Reloads the original raster, clearing any previously applied filters."""
        self.open()

    def btnExecute_click(self, _sender):
        """
        Constructs the selected filter, configures its parameters, wires it to
        the source and destination layers, and calls Execute().

        On the first run (bFirst=True) a new in-memory TGIS_LayerPixel is created
        with Build() matching the input's CRS and pixel dimensions.  The input is
        then removed from the viewer and the output is added in its place.
        Subsequent runs filter the layer in-place (output_layer = input_layer).

        The block size is always odd: block = 2 * tbMaskSize.Position + 1.
        The filter operates on Band=1 in HSL colour space so it acts on the
        luminance channel rather than individual RGB components.

        For morphological filters (Erosion, Dilation, Opening, Closing, Top-Hat,
        Bottom-Hat) the structuring element type is also set from cbStructuring.
        """
        input_layer = self.GIS.Items[0]  # The raster currently loaded in the viewer

        if self.bFirst:
            # First run: create a fresh in-memory output layer matching the input
            output_layer = pdk.TGIS_LayerPixel()
            output_layer.Name = "Result"
            # Build(inMemory, CS, Extent, pixelWidth, pixelHeight)
            output_layer.Build(True, input_layer.CS, input_layer.Extent, input_layer.BitWidth, input_layer.BitHeight)
            output_layer.Open()
        else:
            output_layer = input_layer  # In-place filtering for subsequent runs

        # Derive an odd block/kernel size from the track bar position
        block = int(2 * self.tbMaskSize.Position + 1)

        # Construct the selected filter object and set filter-specific parameters
        px_filter = None

        # --- Threshold ---
        # Binarises: pixels above threshold -> max, others -> 0.
        # Threshold = 30 % of the data range is a reasonable default.
        if self.lbFilters.ItemIndex == 0:
            px_filter = pdk.TGIS_PixelFilterThreshold()
            px_filter.Threshold = float((input_layer.MinHeight + input_layer.MaxHeight) * 0.3)

        # --- Salt-and-Pepper Noise ---
        # Adds random white/black pixels; Amount = percentage of pixels replaced.
        elif self.lbFilters.ItemIndex == 1:
            px_filter = pdk.TGIS_PixelFilterNoiseSaltPepper()
            px_filter.Amount = 10.0

        # --- Gaussian Noise ---
        # Adds normally distributed noise; Amount = standard deviation.
        elif self.lbFilters.ItemIndex == 2:
            px_filter = pdk.TGIS_PixelFilterNoiseGaussian()
            px_filter.Amount = 10.0

        # --- Convolution ---
        # Applies a predefined kernel matrix selected via cbMask.
        elif self.lbFilters.ItemIndex == 3:
            px_filter = pdk.TGIS_PixelFilterConvolution()

            # Map the cbMask selection to a TGIS_PixelFilterMaskType constant
            if self.cbMask.ItemIndex == 0:
                mask = pdk.TGIS_PixelFilterMaskType().LowPass3x3
            elif self.cbMask.ItemIndex == 1:
                mask = pdk.TGIS_PixelFilterMaskType().LowPass5x5
            elif self.cbMask.ItemIndex == 2:
                mask = pdk.TGIS_PixelFilterMaskType().LowPass7x7
            elif self.cbMask.ItemIndex == 3:
                mask = pdk.TGIS_PixelFilterMaskType().HighPass3x3
            elif self.cbMask.ItemIndex == 4:
                mask = pdk.TGIS_PixelFilterMaskType().HighPass5x5
            elif self.cbMask.ItemIndex == 5:
                mask = pdk.TGIS_PixelFilterMaskType().HighPass7x7
            elif self.cbMask.ItemIndex == 6:
                mask = pdk.TGIS_PixelFilterMaskType().Gaussian3x3
            elif self.cbMask.ItemIndex == 7:
                mask = pdk.TGIS_PixelFilterMaskType().Gaussian5x5
            elif self.cbMask.ItemIndex == 8:
                mask = pdk.TGIS_PixelFilterMaskType().Gaussian7x7
            elif self.cbMask.ItemIndex == 9:
                mask = pdk.TGIS_PixelFilterMaskType().Laplacian3x3
            elif self.cbMask.ItemIndex == 10:
                mask = pdk.TGIS_PixelFilterMaskType().Laplacian5x5
            elif self.cbMask.ItemIndex == 11:
                mask = pdk.TGIS_PixelFilterMaskType().GradientNorth
            elif self.cbMask.ItemIndex == 12:
                mask = pdk.TGIS_PixelFilterMaskType().GradientEast
            elif self.cbMask.ItemIndex == 13:
                mask = pdk.TGIS_PixelFilterMaskType().GradientSouth
            elif self.cbMask.ItemIndex == 14:
                mask = pdk.TGIS_PixelFilterMaskType().GradientWest
            elif self.cbMask.ItemIndex == 15:
                mask = pdk.TGIS_PixelFilterMaskType().GradientNorthwest
            elif self.cbMask.ItemIndex == 16:
                mask = pdk.TGIS_PixelFilterMaskType().GradientNortheast
            elif self.cbMask.ItemIndex == 17:
                mask = pdk.TGIS_PixelFilterMaskType().GradientSouthwest
            elif self.cbMask.ItemIndex == 18:
                mask = pdk.TGIS_PixelFilterMaskType().GradientSoutheast
            elif self.cbMask.ItemIndex == 19:
                mask = pdk.TGIS_PixelFilterMaskType().PointDetector
            elif self.cbMask.ItemIndex == 20:
                mask = pdk.TGIS_PixelFilterMaskType().LineDetectorHorizontal
            elif self.cbMask.ItemIndex == 21:
                mask = pdk.TGIS_PixelFilterMaskType().LineDetectorVertical
            elif self.cbMask.ItemIndex == 22:
                mask = pdk.TGIS_PixelFilterMaskType().LineDetectorLeftDiagonal
            elif self.cbMask.ItemIndex == 23:
                mask = pdk.TGIS_PixelFilterMaskType().LineDetectorHorizontal
            else:
                mask = None

            px_filter.MaskType = mask

        # --- Rank / statistical filters (4-22) ---
        # All use BlockSize to define the neighbourhood window.
        elif self.lbFilters.ItemIndex == 4:
            px_filter = pdk.TGIS_PixelFilterSobelMagnitude()    # Edge magnitude via Sobel
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 5:
            px_filter = pdk.TGIS_PixelFilterRange()             # Local value range (max - min)
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 6:
            px_filter = pdk.TGIS_PixelFilterMidpoint()          # (local min + max) / 2
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 7:
            px_filter = pdk.TGIS_PixelFilterMinimum()           # Local minimum
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 8:
            px_filter = pdk.TGIS_PixelFilterMaximum()           # Local maximum
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 9:
            px_filter = pdk.TGIS_PixelFilterArithmeticMean()    # Box/averaging filter
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 10:
            px_filter = pdk.TGIS_PixelFilterAlphaTrimmedMean()  # Mean after trimming extremes
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 11:
            px_filter = pdk.TGIS_PixelFilterContraHarmonicMean() # Robust weighted mean
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 12:
            px_filter = pdk.TGIS_PixelFilterGeometricMean()     # Nth root of product
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 13:
            px_filter = pdk.TGIS_PixelFilterHarmonicMean()      # Reciprocal of mean of reciprocals
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 14:
            px_filter = pdk.TGIS_PixelFilterWeightedMean()      # Distance-weighted mean
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 15:
            px_filter = pdk.TGIS_PixelFilterYpMean()            # Generalised power-mean
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 16:
            px_filter = pdk.TGIS_PixelFilterMajority()          # Most frequent value in block
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 17:
            px_filter = pdk.TGIS_PixelFilterMinority()          # Least frequent value in block
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 18:
            px_filter = pdk.TGIS_PixelFilterMedian()            # Median value (good for S&P noise)
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 19:
            px_filter = pdk.TGIS_PixelFilterWeightedMedian()    # Distance-weighted median
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 20:
            px_filter = pdk.TGIS_PixelFilterSum()               # Sum of block values
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 21:
            px_filter = pdk.TGIS_PixelFilterStandardDeviation() # Local standard deviation
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 22:
            px_filter = pdk.TGIS_PixelFilterUniqueCount()       # Count of distinct values
            px_filter.BlockSize = block

        # --- Morphological filters (23-28) ---
        # Each requires a structuring element type selected via cbStructuring.
        elif self.lbFilters.ItemIndex == 23:
            px_filter = pdk.TGIS_PixelFilterErosion()           # Shrinks bright regions

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 24:
            px_filter = pdk.TGIS_PixelFilterDilation()          # Expands bright regions

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 25:
            px_filter = pdk.TGIS_PixelFilterOpening()           # Erosion then Dilation

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 26:
            px_filter = pdk.TGIS_PixelFilterClosing()           # Dilation then Erosion

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 27:
            px_filter = pdk.TGIS_PixelFilterTopHat()            # Original minus Opening

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 28:
            px_filter = pdk.TGIS_PixelFilterBottomHat()         # Closing minus original

            if self.cbStructuring.ItemIndex == 0:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Square
            elif self.cbStructuring.ItemIndex == 1:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Diamond
            elif self.cbStructuring.ItemIndex == 2:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().Disk
            elif self.cbStructuring.ItemIndex == 3:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineHorizontal
            elif self.cbStructuring.ItemIndex == 4:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineVertical
            elif self.cbStructuring.ItemIndex == 5:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineLeftDiagonal
            elif self.cbStructuring.ItemIndex == 6:
                struct_elem_type = pdk.TGIS_PixelFilterStructuringElementType().LineRightDiagonal
            else:
                struct_elem_type = None

            px_filter.StructuringElementType = struct_elem_type
            px_filter.BlockSize = block

        if px_filter is None:
            return  # No valid filter selected; nothing to do

        # Wire up the common filter properties shared by all filter types
        px_filter.SourceLayer      = input_layer    # Read pixel values from here
        px_filter.DestinationLayer = output_layer   # Write filtered values here
        px_filter.Band             = 1              # Process band 1 (single-band DEM)
        px_filter.ColorSpace       = pdk.TGIS_PixelFilterColorSpace().HSL  # Operate on luminance
        px_filter.BusyEvent        = self.do_busy_event  # Progress callback
        px_filter.Execute()  # Run the filter (may take several seconds for large rasters)

        # Post-process: disable altitude shadow and apply anti-alias to the output
        output_layer.Params.Pixel.GridShadow = False
        output_layer.ApplyAntialiasSettings(True)

        if self.bFirst:
            # First run only: swap input out, add output
            self.GIS.Delete(input_layer.Name)
            self.GIS.Add(output_layer)
            self.bFirst = False  # Subsequent Execute() calls will filter in-place

        self.GIS.InvalidateWholeMap()  # Force a repaint to display the filtered result


def main():
    """Creates the PixelFilters form, shows it, and starts the PDK event loop."""
    frm = PixelFiltersForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
