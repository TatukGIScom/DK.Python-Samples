import tatukgis_pdk as pdk

class InterpolationForm(pdk.TGIS_PvlForm):
    FIELD_VALUE = "TEMP"
    GRID_RESOLUTION = 400
    src = None
    dst = None

    def __init__(self, _owner):
        self.Caption = "Interpolation - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 430
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 152
        self.GIS.Top = 12
        self.GIS.Width = 420
        self.GIS.Height = 358
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.lblMethod = pdk.TGIS_PvlLabel(self.Context)
        self.lblMethod.Place(43, 13, None, 12, None, 13)
        self.lblMethod.Caption = "Method"

        self.rbIDW = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbIDW.Place(134, 17, None, 12, None, 30)
        self.rbIDW.Caption = "IDW Interpolation"
        self.rbIDW.Checked = True
        self.rbIDW.OnClick = self.rbAny_click

        self.rbKriging = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbKriging.Place(134, 17, None, 12, None, 53)
        self.rbKriging.Caption = "Kriging Interpolation"
        self.rbKriging.OnClick = self.rbAny_click

        self.rbSpline = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbSpline.Place(134, 17, None, 12, None, 76)
        self.rbSpline.Caption = "Spline Interpolation"
        self.rbSpline.OnClick = self.rbAny_click

        self.rbHeatMap = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbHeatMap.Place(134, 17, None, 12, None, 99)
        self.rbHeatMap.Caption = "Heat Map"
        self.rbHeatMap.OnClick = self.rbAny_click

        self.rbConcentrationMap = pdk.TGIS_PvlRadioButton(self.Context)
        self.rbConcentrationMap.Place(134, 17, None, 12, None, 122)
        self.rbConcentrationMap.Caption = "Concentration Map"
        self.rbConcentrationMap.OnClick = self.rbAny_click

        self.lblSemivariance = pdk.TGIS_PvlLabel(self.Context)
        self.lblSemivariance.Place(71, 13, None, 12, None, 157)
        self.lblSemivariance.Caption = "Semivariance"
        self.lblSemivariance.Visible = False

        self.cbSemivariance = pdk.TGIS_PvlComboBox(self.Context)
        self.cbSemivariance.Place(134, 21, None, 12, None, 173)
        names = ("Power Law", "Exponential", "Gaussian", "Spherical", "Circular", "Linear")
        for name in names:
            self.cbSemivariance.ItemsAdd(name)
        self.cbSemivariance.ItemIndex = 0
        self.cbSemivariance.Visible = False

        self.btnGenerate = pdk.TGIS_PvlButton(self.Context)
        self.btnGenerate.Place(134, 23, None, 12, None, 376)
        self.btnGenerate.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.btnGenerate.Caption = "Generate"
        self.btnGenerate.OnClick = self.btnGenerate_click

        self.progressBar1 = pdk.TGIS_PvlLabel(self.Context)
        self.progressBar1.Place(142, 23, None, 192, None, 376)
        self.progressBar1.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.progressBar1.Visible = False

    def form_show(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "Samples/Interpolation/Interpolation.ttkproject"
        )
        self.GIS.CS = pdk.TGIS_CSFactory.ByEPSG(3395)

    def rbAny_click(self, _sender):
        if self.rbKriging.Checked:
            self.lblSemivariance.Visible = True
            self.cbSemivariance.Visible = True
        else:
            self.lblSemivariance.Visible = False
            self.cbSemivariance.Visible = False

    def doBusyEvent(self, _sender, pos, _end, _abort):
        self.progressBar1.Visible = True
        if pos == 0:
            self.progressBar1.Caption = 'progress: 0 %'
        elif pos < 0:
            self.progressBar1.Caption = 'progress: 100 %'
        else:
            self.progressBar1.Caption = 'progress: ' + str(pos) + ' %'
        self.GIS.ProcessMessages()

    def doIDW(self):
        vtg = pdk.TGIS_InterpolationIDW()
        # for windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.
        # vtg.Windowed = True
        # vtg.Radius = (ext.XMax - ext.XMin)/5.0

        # attach the event to automatically update the progress bar
        vtg.BusyEvent = self.doBusyEvent

        # set the exponent parameter of the IDW formula (default is 2.0,
        # 3.0 gives nice results in most cases)
        vtg.Exponent = 3.0

        #  generate the Inverse Distance Squared (IDW) interpolation grid
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doKriging(self):
        vtg = pdk.TGIS_InterpolationKriging()

        # for windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.
        # vtg.Windowed = True
        # vtg.Radius = ( ext.XMax - ext.XMin )/5.0

        # attach the event to automatically update the progress bar
        vtg.BusyEvent = self.doBusyEvent

        # set Semivarinace; default is Power Law
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

        # generate the Kriging interpolation grid
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doSplines(self):
        vtg = pdk.TGIS_InterpolationSplines()

        # for windowed version of this method you need to set Windowed=True
        # and at least the Radius, e.g.
        # vtg.Windowed = True ;
        # vtg.Radius = ( ext.XMax - ext.XMin )/5.0

        # attach the event to automatically update the progress bar
        vtg.BusyEvent = self.doBusyEvent
        # set the tension parameter of Splines (value need to be adjusted for
        # the data)
        vtg.Tension = 1e-9
        # generate the Completely Regularized Splines interpolation grid
        vtg.Generate(self.src, self.src.Extent, self.FIELD_VALUE, self.dst, self.dst.Extent)

    def doHeatmap(self, concentration):
        vtg = pdk.TGIS_GaussianHeatmap()

        # for Concentration Map the coordinate must be None and source field
        # must be empty
        vtg.Coordinate = pdk.TGIS_VectorToGridCoordinate().None_
        if concentration:
            fld = ""
        else:
            fld = self.FIELD_VALUE

        # attach the event to automatically update the progress bar
        vtg.BusyEvent = self.doBusyEvent
        # estimate the 3-sigma for Gaussian (can be set manually with Radius)
        vtg.EstimateRadius(self.src, self.src.Extent, self.dst)
        # correct the Radius after estimation (if needed)
        vtg.Radius = vtg.Radius / 2.0
        # generate the Heat/Concentration Map grid
        vtg.Generate(self.src, self.src.Extent, fld, self.dst, self.dst.Extent)

    def btnGenerate_click(self, _sender):
        self.btnGenerate.Enabled = False

        # obtain a handle to the source layer
        self.src = self.GIS.Get("temperatures")
        # obtain a handle to the polygonal layer (the largest extent)
        plg = self.GIS.Get("country")

        # remove any previously created grid layer

        if self.GIS.Get("grid") is not None:
            self.GIS.Delete("Grid")

        # get the source layer extent
        ext = plg.Extent

        # calculate the height/width ratio of the extent to properly set the grid
        # resolution
        rat = (ext.YMax - ext.YMin) / (ext.XMax - ext.XMin)

        # create and initialize the destination layer
        self.dst = pdk.TGIS_LayerPixel()
        self.dst.Name = "grid"
        # tmp=int(round(rat * self.GRID_RESOLUTION))
        self.dst.Build(True, self.src.CS, ext, self.GRID_RESOLUTION, int(round(rat * self.GRID_RESOLUTION)))
        self.dst.Params.Pixel.GridShadow = False

        # choose the start color of the grid ramp
        clr = pdk.TGIS_Color.Blue

        # find out which vector-to-grid has been chosen
        if self.rbIDW.Checked:
            # perform Inverse Distance Squared (IDW) interpolation
            self.doIDW()
        elif self.rbKriging.Checked:
            # perform Kriging interpolation
            self.doKriging()
        elif self.rbSpline.Checked:
            # perform Completely Regularized Splines interpolation
            self.doSplines()
        elif self.rbHeatMap.Checked:
            # perform Heat Map generation
            self.doHeatmap(False)
            # choose the start color for the grid ramp with ALPHA=0 to make it
            clr = pdk.TGIS_Color.FromARGB(0, 0, 0, 255)
        elif self.rbConcentrationMap.Checked:
            # perform Concentration Map generation
            self.doHeatmap(True)
            # choose the start color for the grid ramp with ALPHA=0 to make it
            clr = pdk.TGIS_Color.FromARGB(0, 0, 0, 255)

        # apply color ramp to the grid layer
        self.dst.GenerateRamp(
            clr, pdk.TGIS_Color().Lime, pdk.TGIS_Color().Red, self.dst.MinHeight,
            (self.dst.MaxHeight - self.dst.MinHeight) / 2.0, self.dst.MaxHeight, False,
            (self.dst.MaxHeight - self.dst.MinHeight) / 100.0,
            (self.dst.MaxHeight - self.dst.MinHeight) / 10.0,
            None, False
        )

        # limit the grid visibility only to the pixels contained within a polygon
        self.dst.CuttingPolygon = plg.GetShape(6).CreateCopy()
        # add the grid layer to the viewer
        self.GIS.Add(self.dst)
        # update the viewer to show the grid layer
        self.GIS.FullExtent()
        # reset the progress bar
        # elf.progressBar1.Caption = 'progress: 0 %'
        self.btnGenerate.Enabled = True


def main():
    frm = InterpolationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
