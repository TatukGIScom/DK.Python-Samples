import tatukgis_pdk as pdk
import math

GIS_MAX_SINGLE = 1e37
DEG_TO_RAD = math.pi / 180

def changeDEM(_layer, _extent,
              _source, _output,
              _width, _height,
              _minz, _maxz):

    x_size = _width
    y_size = _height
    x_scale = (_extent.XMax - _extent.XMin) / x_size
    y_scale = (_extent.YMax - _extent.YMin) / y_size
    nodata = _layer.NoDataValue

    x_res = x_scale
    y_res = y_scale
    scale = 1
    minz = GIS_MAX_SINGLE
    maxz = -GIS_MAX_SINGLE

    z_factor = 0.00002
    azimuth = 225
    altitude = 45

    sin_alt_rad = math.sin(altitude * DEG_TO_RAD)
    az_rad = azimuth * DEG_TO_RAD
    z_scale_factor = z_factor / (2 * scale)
    cos_alt_zsf = math.cos(altitude * DEG_TO_RAD) * z_scale_factor
    square_z_sf = z_scale_factor ** 2

    window = [0.0] * 9
    for i in range(2, _height-1):
        l1 = i - 2
        l2 = i - 1
        l3 = i

        for j in range(1, _width-2):
            window[0] = _source.Value(l1, j - 1)
            window[1] = _source.Value(l1, j)
            window[2] = _source.Value(l1, j + 1)
            window[3] = _source.Value(l2, j - 1)
            window[4] = _source.Value(l2, j)
            window[5] = _source.Value(l2, j + 1)
            window[6] = _source.Value(l3, j - 1)
            window[7] = _source.Value(l3, j)
            window[8] = _source.Value(l3, j + 1)

            use_alg = True
            if abs(window[4] - nodata) < 1e-10:
                use_alg = False
            else:
                for k in range(9):
                    if abs(window[k] - nodata) < 1e-10:
                        use_alg = False
                        break

            if use_alg:
                x = (window[3] - window[5]) / x_res
                y = (window[7] - window[1]) / y_res

                xx_plus_yy = x**2 + y**2
                aspect = math.atan2(y, x)
                cang = ((sin_alt_rad - cos_alt_zsf * math.sqrt(xx_plus_yy) * math.sin(aspect - az_rad)) /
                        math.sqrt(1 + square_z_sf * xx_plus_yy))

                if cang <= 0.0:
                    cang = 1.0
                else:
                    cang = 1.0 + (254.0 * cang)
                val = cang

                if _source.Value(l1, j) != nodata:
                    _output.Value(l1, j, val)

                if val < minz and val != nodata:
                    minz = val

                if val > maxz and val != nodata:
                    maxz = val

    _minz.Value = minz
    _maxz.Value = maxz


class DemOperationsForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "DemOperations - TatukGIS DK Sample"
        self.ClientWidth = 900
        self.ClientHeight = 700
        self.OnShow = self.form_show        

        # Toolbar
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Align = "Top"
        self.toolbar_buttons.Height = 29
        
        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnOpen.Place(73, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open File"
        self.btnOpen.OnClick = self.btnOpen_click

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(73, 22, None, 79, None, 3)
        self.btnFullExtent.Caption = "Full Extent"

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(73, 22, None, 155, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(73, 22, None, 231, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        self.btn3d = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btn3d.Place(73, 22, None, 307, None, 3)
        self.btn3d.Caption = "3D"
        self.btn3d.OnClick = self.btn3D_click
        
        # Left panel
        self.pnlParams = pdk.TGIS_PvlPanel(self.Context)
        self.pnlParams.Align = "Left"
        self.pnlParams.Width = 193
        
        # Show angle
        self.gbxShadow = pdk.TGIS_PvlGroupBox(self.pnlParams.Context)
        self.gbxShadow.Caption = "Shadow Angle"
        self.gbxShadow.Place(159, 65, None, 10, None, 6)

        self.tbShadow = pdk.TGIS_PvlTrackBar(self.gbxShadow.Context)
        self.tbShadow.Place(148, 33, None, 3, None, 21)
        self.tbShadow.Maximum = 360
        self.tbShadow.Minimum = 1
        self.tbShadow.Position = 90
        # self.tbShadow.Frequency = 30
        self.tbShadow.OnChange = self.tbShadow_Scroll
        
        self.cbxCustomGrid = pdk.TGIS_PvlCheckBox(self.pnlParams.Context)
        self.cbxCustomGrid.Place(1781, 17, None, 10, None, 72)
        self.cbxCustomGrid.Caption = "Attach custom grid operation"
        self.cbxCustomGrid.OnChange = self.cbxCustomGrid_change

        # Operations
        self.gbxMain = pdk.TGIS_PvlGroupBox(self.pnlParams.Context)
        self.gbxMain.Caption = "Operations"
        self.gbxMain.Place(176, 440, None, 8, None, 105)
        
        self.lblOperation = pdk.TGIS_PvlLabel(self.gbxMain.Context)
        self.lblOperation.Caption = "Operation:"
        self.lblOperation.Place(102, 13, None, 16, None, 32)

        self.cbxOperations = pdk.TGIS_PvlComboBox(self.gbxMain.Context)
        self.cbxOperations.Place(143, 21, None, 17, None, 51)
        names = (
            "Hillshade",
            "Slope",
            "Slope Hydro",
            "Aspect",
            "TRI",
            "TPI",
            "Roughness",
            "Total Curvature",
            "Matrix Gain",
            "Flow dir"
        )
        for name in names:
            self.cbxOperations.ItemsAdd(name)
        self.cbxOperations.ItemIndex = 0
        self.cbxOperations.OnChange = self.cbOperation_Change

        # Shade params
        self.gbxHillShadeParams = pdk.TGIS_PvlGroupBox(self.gbxMain.Context)
        self.gbxHillShadeParams.Place(145, 161, None, 16, None, 78)
        self.gbxHillShadeParams.Visible = True

        self.lblAzimuth = pdk.TGIS_PvlLabel(self.gbxHillShadeParams.Context)
        self.lblAzimuth.Place(73, 21, None, 9, None, 23)
        self.lblAzimuth.Caption = "Azimuth"

        self.lblAltitude = pdk.TGIS_PvlLabel(self.gbxHillShadeParams.Context)
        self.lblAltitude.Place(73, 21, None, 9, None, 57)
        self.lblAltitude.Caption = "Altitude"

        self.lblZFactor = pdk.TGIS_PvlLabel(self.gbxHillShadeParams.Context)
        self.lblZFactor.Place(73, 21, None, 9, None, 98)
        self.lblZFactor.Caption = "Z Factor"
        
        self.edtAzimuth = pdk.TGIS_PvlEdit(self.gbxHillShadeParams.Context)
        self.edtAzimuth.Place(73, 21, None, 58, None, 20)
        self.edtAzimuth.Text = "315"

        self.edtAltitude = pdk.TGIS_PvlEdit(self.gbxHillShadeParams.Context)
        self.edtAltitude.Place(73, 21, None, 58, None, 54)
        self.edtAltitude.Text = "45"

        self.edtZFactor = pdk.TGIS_PvlEdit(self.gbxHillShadeParams.Context)
        self.edtZFactor.Place(73, 21, None, 58, None, 95)
        self.edtZFactor.Text = "0.00002"

        self.cbxCombined = pdk.TGIS_PvlCheckBox(self.gbxHillShadeParams.Context)
        self.cbxCombined.Place(83, 17, None, 58, None, 128)
        self.cbxCombined.Caption = "Combined"
        
        # Slope params 
        self.gbxSlopeParams = pdk.TGIS_PvlGroupBox(self.gbxMain.Context)
        self.gbxSlopeParams.Place(145, 91, None, 16, None, 245)
        self.gbxSlopeParams.Visible = False

        self.lblMode = pdk.TGIS_PvlLabel(self.gbxSlopeParams.Context)
        self.lblMode.Place(33, 13, None, 15, None, 15)
        self.lblMode.Caption = "Mode"

        self.lblScale = pdk.TGIS_PvlLabel(self.gbxSlopeParams.Context)
        self.lblScale.Place(33, 13, None, 15, None, 55)
        self.lblScale.Caption = "Scale"

        self.cbxMode = pdk.TGIS_PvlComboBox(self.gbxSlopeParams.Context)
        self.cbxMode.Place(73, 21, None, 58, None, 12)
        for name in ("Degrees", "Percent"):
            self.cbxMode.ItemsAdd(name)
        self.cbxMode.ItemIndex = 1

        self.mmScale = pdk.TGIS_PvlMemo(self.gbxSlopeParams.Context)
        self.mmScale.Place(73, 21, None, 58, None, 52)
        self.mmScale.Text = "111120"

        self.cbxAngle = pdk.TGIS_PvlCheckBox(self.gbxMain.Context)
        self.cbxAngle.Place(154, 17, None, 18, None, 342)
        self.cbxAngle.Visible = False
        self.cbxAngle.Caption = "Angle instead of azimuth"

        # Curvature params
        self.gbxCurvature = pdk.TGIS_PvlGroupBox(self.gbxMain.Context)
        self.gbxCurvature.Place(145, 45, None, 17, None, 365)
        self.gbxCurvature.Visible = False

        self.lblCurvMode = pdk.TGIS_PvlLabel(self.gbxCurvature.Context)
        self.lblCurvMode.Place(33, 13, None, 16, None, 15)
        self.lblCurvMode.Caption = "Mode"

        self.cbCurvMode = pdk.TGIS_PvlComboBox(self.gbxCurvature.Context)
        self.cbCurvMode.Place(72, 21, None, 58, None, 12)
        for name in ("Profile", "Plan"):
            self.cbCurvMode.ItemsAdd(name)
        self.cbCurvMode.ItemIndex = 0

        # Progress
        self.progress_bar = pdk.TGIS_PvlLabel(self.Context)
        self.progress_bar.Place(177, 17, None, 10, None, 660)
        self.progress_bar.Visible = False

        # Run
        self.btnRun = pdk.TGIS_PvlButton(self.pnlParams.Context)
        self.btnRun.Place(99, 25, None, 54, None, 551)
        self.btnRun.Caption = "Run Operation"
        self.btnRun.OnClick = self.btnRun_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Align = "Right"
        self.GIS_legend.Width = 145
        
        self.open_dialog = pdk.TGIS_PvlOpenDialog(self.Context)
        supported_files = pdk.TGIS_Utils.GisSupportedFiles([pdk.TGIS_FileType().Pixel], False)
        self.open_dialog.Filter = supported_files
        self.btnFullExtent.OnClick = self.btnFullExtent_click

    def form_show(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload()
            + "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf"
        )
        self.GIS.FullExtent()

    def cbxCustomGrid_change(self, _sender):
        lp = self.GIS.Items[0]

        if not lp:
            return

        if self.cbxCustomGrid.Checked:
            lp.Params.Pixel.AltitudeMapZones.Clear()
            lp.Params.Pixel.GridShadow = False
            lp.GridOperationEvent = changeDEM
        else:
            lp.GridOperationEvent = None
            lp.Params.Pixel.GridShadow = True

        self.GIS.InvalidateWholeMap()

    def btnOpen_click(self, _sender):
        self.open_dialog.Execute()
        self.GIS.Open(self.open_dialog.FileName)

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btn3D_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.View3D = not self.GIS.View3D

    def tbShadow_Scroll(self, _sender):
        lp = self.GIS.Items[0]

        if not lp:
            return

        lp.Params.Pixel.GridShadowAngle = float(self.tbShadow.Position)

        if not self.GIS.InPaint:
            self.GIS.InvalidateWholeMap()

    def cbOperation_Change(self, _sender):
        self.gbxHillShadeParams.Visible = False
        self.gbxSlopeParams.Visible = False
        self.cbxAngle.Visible = False
        self.gbxCurvature.Visible = False
        
        # self.gbxSlopeParams.Top = self.gbxHillShadeParams.Top
        # self.gbxCurvature.Top = self.gbxHillShadeParams.Top
        # self.chkAngleAzimuth.Top = self.gbxHillShadeParams.Top
        
        if self.cbxOperations.ItemIndex == 0:
            self.gbxHillShadeParams.Visible = True
        elif self.cbxOperations.ItemIndex == 1:
            self.gbxSlopeParams.Visible = True
        elif self.cbxOperations.ItemIndex == 2:
            self.gbxSlopeParams.Visible = True
        elif self.cbxOperations.ItemIndex == 3:
            self.cbxAngle.Visible = True
        elif self.cbxOperations.ItemIndex == 7:
            self.gbxCurvature.Visible = True
            
        self.gbxMain.Height = 250

        # self.btnGenerate.Top = self.gbxMain.Top + 260

    def doBusyEvent(self, _sender, pos, end, __):
        if end <= 0:
            self.progress_bar.Visible = False
        else:
            self.progress_bar.Visible = True
            self.progress_bar.Caption = str(pos/end * 100) + "%"

        self.GIS.ProcessMessages()

    def btnRun_click(self, _sender):
        lp = self.GIS.Items[0]

        ld = pdk.TGIS_LayerPixel()
        ld.Name = 'out_'
        ld.CS = lp.CS
        ld.Build(True, lp.CS, lp.Extent, lp.BitWidth, lp.BitHeight)

        dem = pdk.TGIS_DemGenerator()

        if self.cbxOperations.ItemIndex == 0:
            dop = pdk.TGIS_DemOperationHillShade(float(self.edtZFactor.Text),
                                                 float(self.edtAzimuth.Text),
                                                 float(self.edtAltitude.Text),
                                                 self.cbxCombined.Checked)

        elif self.cbxOperations.ItemIndex == 1:
            if self.cbxMode.ItemIndex == 0:
                sm = pdk.TGIS_DemSlopeMode().Degrees
            elif self.cbxMode.ItemIndex == 1:
                sm = pdk.TGIS_DemSlopeMode().Percent
            else:
                sm = pdk.TGIS_DemSlopeMode().Degrees
            dop = pdk.TGIS_DemOperationSlope(sm, float(self.mmScale.Text))
            
        elif self.cbxOperations.ItemIndex == 2:
            if self.cbxMode.ItemIndex == 0:
                sm = pdk.TGIS_DemSlopeMode().Degrees
            elif self.cbxMode.ItemIndex == 1:
                sm = pdk.TGIS_DemSlopeMode().Percent
            else:
                sm = pdk.TGIS_DemSlopeMode().Degrees
            dop = pdk.TGIS_DemOperationSlopeHydro(sm, float(self.mmScale.Text))
        
        elif self.cbxOperations.ItemIndex == 3:
            dop = pdk.TGIS_DemOperationAspect(self.cbxAngle.Checked)
        
        elif self.cbxOperations.ItemIndex == 4:
            dop = pdk.TGIS_DemOperationTRI()
        
        elif self.cbxOperations.ItemIndex == 5:
            dop = pdk.TGIS_DemOperationTPI()
        
        elif self.cbxOperations.ItemIndex == 6:
            dop = pdk.TGIS_DemOperationRoughness()

        elif self.cbxOperations.ItemIndex == 7:
            if self.cbCurvMode.ItemIndex == 0:
                cm = pdk.TGIS_DemTotalCurvatureMode().Profile
            elif self.cbxMode.ItemIndex == 1:
                cm = pdk.TGIS_DemTotalCurvatureMode().Plan
            else:
                cm = pdk.TGIS_DemTotalCurvatureMode().Profile
            dop = pdk.TGIS_DemOperationTotalCurvature(cm)

        elif self.cbxOperations.ItemIndex == 8:
            dop = pdk.TGIS_DemOperationMatrixGain()
        
        elif self.cbxOperations.ItemIndex == 9:
            dop = pdk.TGIS_DemOperationFlowDir()
        
        else:
            dop = pdk.TGIS_DemOperation()

        ld.Name = "out_" + dop.Description()

        if self.GIS.Get(ld.Name):
            self.GIS.Delete(ld.Name)

        ld.Params.Pixel.GridShadow = self.cbxOperations.ItemIndex == 7

        self.GIS.Add(ld)

        dem.Process(lp, lp.Extent, ld, dop, self.doBusyEvent)
        self.GIS.InvalidateWholeMap()


def main():
    frm = DemOperationsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
