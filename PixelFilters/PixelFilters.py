import tatukgis_pdk as pdk

class PixelFiltersForm(pdk.TGIS_PvlForm):
    bFirst = None

    def __init__(self, _owner):
        self.Caption = "PixelFilters - TatukGIS DK Sample"
        self.ClientWidth = 674
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 174
        self.GIS.Top = 12
        self.GIS.Width = 488
        self.GIS.Height = 442
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        self.lblFilters = pdk.TGIS_PvlLabel(self.Context)
        self.lblFilters.Place(34, 13, None, 10, None, 12)
        self.lblFilters.Caption = "Filters"

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

        self.lblMask = pdk.TGIS_PvlLabel(self.Context)
        self.lblMask.Place(33, 13, None, 12, None, 247)
        self.lblMask.Caption = "Mask Size"
        self.lblMask.Visible = False
        self.lblMask.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.lblMaskSize = pdk.TGIS_PvlLabel(self.Context)
        self.lblMaskSize.Place(56, 13, None, 10, None, 247)
        self.lblMaskSize.Caption = "Mask Size"
        self.lblMaskSize.Visible = False
        self.lblMaskSize.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.tbMaskSize = pdk.TGIS_PvlTrackBar(self.Context)
        self.tbMaskSize.Place(121, 45, None, 10, None, 263)
        self.tbMaskSize.Maximum = 12
        self.tbMaskSize.Position = 1
        self.tbMaskSize.Visible = False
        self.tbMaskSize.OnChange = self.tbMaskSize_change
        self.tbMaskSize.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.lblMaskSizeValue = pdk.TGIS_PvlLabel(self.Context)
        self.lblMaskSizeValue.Place(40, 13, None, 130, None, 267)
        self.lblMaskSizeValue.Caption = "3x3"
        self.lblMaskSizeValue.Visible = False
        self.lblMaskSizeValue.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

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

        self.lblStructuring = pdk.TGIS_PvlLabel(self.Context)
        self.lblStructuring.Place(104, 13, None, 10, None, 295)
        self.lblStructuring.Caption = "Structuring Elements"
        self.lblStructuring.Visible = False
        self.lblStructuring.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

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

        self.btnExecute = pdk.TGIS_PvlButton(self.Context)
        self.btnExecute.Place(75, 23, None, 12, None, 338)
        self.btnExecute.Caption = "Execute"
        self.btnExecute.OnClick = self.btnExecute_click
        self.btnExecute.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.btnReset = pdk.TGIS_PvlButton(self.Context)
        self.btnReset.Place(75, 23, None, 93, None, 338)
        self.btnReset.Caption = "Reset"
        self.btnReset.OnClick = self.btnReset_click
        self.btnReset.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.progress_bar = pdk.TGIS_PvlLabel(self.Context)
        self.progress_bar.Place(156, 23, None, 12, None, 431)
        self.progress_bar.Caption = ''
        self.progress_bar.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(156, 58, None, 12, None, 367)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

    def open(self):
        self.GIS.Close()
        path = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                + r"World\Countries\USA\States\California\San Bernardino\NED\w001001.adf")
        ll = pdk.TGIS_Utils.GisCreateLayer("input", path)
        ll.Open()
        ll.Params.Pixel.AltitudeMapZones.Clear()
        ll.Params.Pixel.GridShadow = False

        self.GIS.Add(ll)
        self.GIS.FullExtent()

        self.bFirst = True

    def on_change(self):
        if self.lbFilters.ItemIndex == 0 or self.lbFilters.ItemIndex == 1 or self.lbFilters.ItemIndex == 2:
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

                self.cbStructuring.Visible = True
                self.lblStructuring.Visible = True
                self.lblMask.Visible = True
                self.cbMask.Visible = True
                self.lblMaskSize.Visible = True
                self.lblMaskSizeValue.Visible = True
                self.tbMaskSize.Visible = True
            else:
                self.cbStructuring.Visible = False
                self.lblStructuring.Visible = False
                self.lblMask.Visible = False
                self.cbMask.Visible = False
                self.lblMaskSize.Visible = False
                self.lblMaskSizeValue.Visible = False
                self.tbMaskSize.Visible = False

            if self.lbFilters.ItemIndex == 3:
                self.cbMask.Visible = True
                self.lblMask.Visible = True
                self.lblMaskSize.Visible = False
                self.lblMaskSizeValue.Visible = False
                self.tbMaskSize.Visible = False
            else:
                self.cbMask.Visible = False
                self.lblMask.Visible = False
                self.lblMaskSize.Visible = True
                self.lblMaskSizeValue.Visible = True
                self.tbMaskSize.Visible = True

    def form_show(self, _sender):
        self.lbFilters.ItemIndex = 0
        self.cbStructuring.ItemIndex = 0
        self.cbMask.ItemIndex = 0

        self.on_change()
        self.open()

    def do_busy_event(self, _sender, pos, end, _abort):
        if end <= 0:
            self.progress_bar.Visible = False
        else:
            self.progress_bar.Visible = True
            self.progress_bar.Caption = 'progress: ' + str(int(pos/end * 100)) + " %"

        self.GIS.ProcessMessages()

    def lbFilters_change(self, _sender):
        self.on_change()

    def tbMaskSize_change(self, _sender):
        i = int(2 * self.tbMaskSize.Position + 1)
        self.lblMaskSizeValue.Caption = str(i) + "x" + str(i)

    def btnReset_click(self, _sender):
        self.open()

    def btnExecute_click(self, _sender):
        input_layer = self.GIS.Items[0]

        if self.bFirst:
            output_layer = pdk.TGIS_LayerPixel()
            output_layer.Name = "Result"
            output_layer.Build(True, input_layer.CS, input_layer.Extent, input_layer.BitWidth, input_layer.BitHeight)
            output_layer.Open()
        else:
            output_layer = input_layer

        block = int(2 * self.tbMaskSize.Position + 1)

        px_filter = None
        if self.lbFilters.ItemIndex == 0:
            px_filter = pdk.TGIS_PixelFilterThreshold()
            px_filter.Threshold = float((input_layer.MinHeight + input_layer.MaxHeight) * 0.3)

        elif self.lbFilters.ItemIndex == 1:
            px_filter = pdk.TGIS_PixelFilterNoiseSaltPepper()
            px_filter.Amount = 10.0

        elif self.lbFilters.ItemIndex == 2:
            px_filter = pdk.TGIS_PixelFilterNoiseGaussian()
            px_filter.Amount = 10.0

        elif self.lbFilters.ItemIndex == 3:
            px_filter = pdk.TGIS_PixelFilterConvolution()

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

        elif self.lbFilters.ItemIndex == 4:
            px_filter = pdk.TGIS_PixelFilterSobelMagnitude()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 5:
            px_filter = pdk.TGIS_PixelFilterRange()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 6:
            px_filter = pdk.TGIS_PixelFilterMidpoint()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 7:
            px_filter = pdk.TGIS_PixelFilterMinimum()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 8:
            px_filter = pdk.TGIS_PixelFilterMaximum()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 9:
            px_filter = pdk.TGIS_PixelFilterArithmeticMean()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 10:
            px_filter = pdk.TGIS_PixelFilterAlphaTrimmedMean()
            px_filter.BlockSize = block
 
        elif self.lbFilters.ItemIndex == 11:
            px_filter = pdk.TGIS_PixelFilterContraHarmonicMean()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 12:
            px_filter = pdk.TGIS_PixelFilterGeometricMean()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 13:
            px_filter = pdk.TGIS_PixelFilterHarmonicMean()
            px_filter.BlockSize = block
 
        elif self.lbFilters.ItemIndex == 14:
            px_filter = pdk.TGIS_PixelFilterWeightedMean()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 15:
            px_filter = pdk.TGIS_PixelFilterYpMean()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 16:
            px_filter = pdk.TGIS_PixelFilterMajority()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 17:
            px_filter = pdk.TGIS_PixelFilterMinority()
            px_filter.BlockSize = block
 
        elif self.lbFilters.ItemIndex == 18:
            px_filter = pdk.TGIS_PixelFilterMedian()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 19:
            px_filter = pdk.TGIS_PixelFilterWeightedMedian()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 20:
            px_filter = pdk.TGIS_PixelFilterSum()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 21:
            px_filter = pdk.TGIS_PixelFilterStandardDeviation()
            px_filter.BlockSize = block
 
        elif self.lbFilters.ItemIndex == 22:
            px_filter = pdk.TGIS_PixelFilterUniqueCount()
            px_filter.BlockSize = block

        elif self.lbFilters.ItemIndex == 23:
            px_filter = pdk.TGIS_PixelFilterErosion()

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
            px_filter = pdk.TGIS_PixelFilterDilation()

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
            px_filter = pdk.TGIS_PixelFilterOpening()

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
            px_filter = pdk.TGIS_PixelFilterClosing()

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
            px_filter = pdk.TGIS_PixelFilterTopHat()

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
            px_filter = pdk.TGIS_PixelFilterBottomHat()

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
            return

        px_filter.SourceLayer = input_layer
        px_filter.DestinationLayer = output_layer
        px_filter.Band = 1
        px_filter.ColorSpace = pdk.TGIS_PixelFilterColorSpace().HSL
        px_filter.BusyEvent = self.do_busy_event
        px_filter.Execute()

        output_layer.Params.Pixel.GridShadow = False
        output_layer.ApplyAntialiasSettings(True)

        if self.bFirst:
            self.GIS.Delete(input_layer.Name)
            self.GIS.Add(output_layer)
            self.bFirst = False

        self.GIS.InvalidateWholeMap()


def main():
    frm = PixelFiltersForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
