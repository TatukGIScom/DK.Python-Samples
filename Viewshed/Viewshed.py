import tatukgis_pdk as pdk

class ViewshedForm(pdk.TGIS_PvlForm):
    SAMPLE_VIEWSHED_NAME = "Viewshed"
    SAMPLE_AGL_NAME = "Above-Ground-Level"

    lTerrain = None
    lObservers = None
    lViewshed = None
    lAGL = None

    def __init__(self, _owner):
        self.Caption = "Viewshed - TatukGIS DK Sample"
        self.ClientWidth = 800
        self.ClientHeight = 393
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 190
        self.GIS.Top = 28
        self.GIS.Width = 560
        self.GIS.Height = 340
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().UserDefined
        self.GIS.OnMouseDown = self.GIS_MouseDown
        self.GIS.OnMouseMove = self.GIS_MouseMove

        self.btnFullExtent = pdk.TGIS_PvlButton(self.Context)
        self.btnFullExtent.Place(168, 23, None, 12, None, 12)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnReset = pdk.TGIS_PvlButton(self.Context)
        self.btnReset.Place(168, 23, None, 12, None, 41)
        self.btnReset.Caption = "Reset"
        self.btnReset.OnClick = self.btnReset_click

        self.gbMapMode = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbMapMode.Place(168, 69, None, 12, None, 70)
        self.gbMapMode.Caption = "Map Mode"

        self.rbZoom = pdk.TGIS_PvlRadioButton(self.gbMapMode.Context)
        self.rbZoom.Place(52, 17, None, 16, None, 19)
        self.rbZoom.Caption = "Zoom"
        self.rbZoom.Group = "G1"
        self.rbZoom.OnChange = self.rbZoom_change

        self.rbAddObserver = pdk.TGIS_PvlRadioButton(self.gbMapMode.Context)
        self.rbAddObserver.Place(90, 17, None, 16, None, 42)
        self.rbAddObserver.Caption = "Add Observer"
        self.rbAddObserver.Checked = True
        self.rbAddObserver.Group = "G1"
        self.rbAddObserver.OnChange = self.rbAddObserver_change

        self.gbVisibleLayer = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbVisibleLayer.Place(168, 94, None, 12, None, 145)
        self.gbVisibleLayer.Caption = "Visible Layer"

        self.rbViewshedBinary = pdk.TGIS_PvlRadioButton(self.gbVisibleLayer.Context)
        self.rbViewshedBinary.Place(140, 17, None, 16, None, 19)
        self.rbViewshedBinary.Caption = "Viewshed (binary)"
        self.rbViewshedBinary.Checked = True
        self.rbViewshedBinary.OnChange = self.setLayerActive

        self.rbViewshedFreq = pdk.TGIS_PvlRadioButton(self.gbVisibleLayer.Context)
        self.rbViewshedFreq.Place(140, 17, None, 16, None, 42)
        self.rbViewshedFreq.Caption = "Viewshed (frequency)"
        self.rbViewshedFreq.OnChange = self.setLayerActive

        self.rbAGL = pdk.TGIS_PvlRadioButton(self.gbVisibleLayer.Context)
        self.rbAGL.Place(140, 17, None, 16, None, 65)
        self.rbAGL.Caption = "Above-Ground-Level"
        self.rbAGL.OnChange = self.setLayerActive

        self.lblHint = pdk.TGIS_PvlLabel(self.Context)
        self.lblHint.Place(600, 16, None, 190, None, 9)
        self.lblHint.Caption = "Click on the map to add an observer."

        self.lblObserverElevation = pdk.TGIS_PvlLabel(self.Context)
        self.lblObserverElevation.Place(147, 13, None, 12, None, 242)
        self.lblObserverElevation.Caption = "Observer Elevation (meters)"

        self.edtObserverElevation = pdk.TGIS_PvlEdit(self.Context)
        self.edtObserverElevation.Place(158, 20, None, 12, None, 258)
        self.edtObserverElevation.Text = "30"

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(753, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)

    def form_show(self, _sender):
        self.GIS.Lock()
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf"
        )
        self.GIS.FullExtent()

        # obtain the DEM layer
        self.lTerrain = self.GIS.Get("w001001")
        self.lTerrain.Params.Pixel.AltitudeMapZones.Clear()

        # create a layer for storing the observer locations
        self.lObservers = pdk.TGIS_LayerVector()
        self.lObservers.Name = "Observers"
        self.lObservers.CS = self.lTerrain.CS
        self.lObservers.Open()

        # add a symbol to represent observers
        self.lObservers.Params.Marker.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
            "LIBSVG:std:TowerCommunication01"
        )
        self.lObservers.Params.Marker.Color = pdk.TGIS_Color().White
        self.lObservers.Params.Marker.OutlineColor = pdk.TGIS_Color().White
        self.lObservers.Params.Marker.Size = -32

        self.GIS.Add(self.lObservers)
        self.GIS.Unlock()
        self.GIS.FullExtent()

    def showComment(self):
        if self.rbViewshedBinary.Checked:
            self.lblHint.Caption = "Green - area of visibility."
        elif self.rbViewshedFreq.Checked:
            self.lblHint.Caption = "Visibility frequency"\
                                " | Red - one observer is visible"\
                                " | Green - all observers are visible."
        elif self.rbAGL.Checked and self.lAGL:
            self.lblHint.Caption = "Minimum height that must be added to a" \
                                "non-visible cell to make it visible by at least" \
                                f"one observer | Red = {(round(self.lAGL.MaxHeight))} m"

    def makeViewshedRamp(self):
        if not self.GIS.Get(self.SAMPLE_VIEWSHED_NAME):
            return

        self.lViewshed.Transparency = 50
        self.lViewshed.Params.Pixel.GridShadow = False
        self.lViewshed.Params.Pixel.AltitudeMapZones.Clear()

        if self.rbViewshedBinary.Checked:
            self.lViewshed.GenerateRamp(
                pdk.TGIS_Color().FromARGB(127, 0, 255, 0),
                pdk.TGIS_Color().None_,
                pdk.TGIS_Color().FromARGB(127, 0, 255, 0),
                self.lViewshed.MinHeight, 0.01,
                self.lViewshed.MaxHeight, False,
                (self.lViewshed.MaxHeight - self.lViewshed.MinHeight) / 100,
                (self.lViewshed.MaxHeight - self.lViewshed.MinHeight) / 10,
                None, False
            )
        elif self.rbViewshedFreq.Checked:
            self.lViewshed.GenerateRamp(
                pdk.TGIS_Color().FromARGB(127, 255, 0, 0),
                pdk.TGIS_Color().None_,
                pdk.TGIS_Color().FromARGB(127, 0, 255, 0),
                0, 0,
                self.lViewshed.MaxHeight, False,
                (self.lViewshed.MaxHeight - self.lViewshed.MinHeight) / 100,
                (self.lViewshed.MaxHeight - self.lViewshed.MinHeight) / 10,
                None, False
            )

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        if self.GIS.Mode == pdk.TGIS_ViewerMode().UserDefined:
            try:
                elev = float(self.edtObserverElevation.Text)
            except ValueError:
                self.lblMsg.Caption = f"{self.edtObserverElevation.Text}"\
                                    "is not a valid floating point value."
                return

            self.GIS.Lock()
            try:
                # check if the point lays within the DEM area
                ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

                if not pdk.TGIS_Utils.GisIsPointInsideExtent(ptg, self.lTerrain.Extent):
                    return

                # add observer to the observer layer
                shp = self.lObservers.CreateShape(pdk.TGIS_ShapeType().Point, pdk.TGIS_DimensionType().XY)
                shp.AddPart()
                shp.AddPoint(ptg)

                # remove previous viewshed/AGL layers
                if self.GIS.Get(self.SAMPLE_VIEWSHED_NAME):
                    self.GIS.Delete(self.lAGL.Name)
                    self.lAGL = None
                    self.GIS.Delete(self.lViewshed.Name)
                    self.lViewshed = None

                # create and set up the layer to host viewshed
                self.lViewshed = pdk.TGIS_LayerPixel()
                self.lViewshed.Build(
                    True,
                    self.lTerrain.CS,
                    self.lTerrain.Extent,
                    self.lTerrain.BitWidth,
                    self.lTerrain.BitHeight
                )
                self.lViewshed.Name = self.SAMPLE_VIEWSHED_NAME
                self.lViewshed.Open()

                # create and set up the layer to host above-ground-level
                self.lAGL = pdk.TGIS_LayerPixel()
                self.lAGL.Build(
                    True,
                    self.lTerrain.CS,
                    self.lTerrain.Extent,
                    self.lTerrain.BitWidth,
                    self.lTerrain.BitHeight
                )
                self.lAGL.Name = self.SAMPLE_AGL_NAME
                self.lAGL.Open()

                # create viewshed tool
                vs = pdk.TGIS_Viewshed()
                # set the base observer elevation to be read from the DEM layer
                vs.ObserverElevation = pdk.TGIS_ViewshedObserverElevation().OnDem
                # turn on the correction for earth curvature and refractivity
                vs.CurvedEarth = True

                vs.Generate(self.lTerrain, self.lObservers,
                            self.lViewshed, self.lAGL,
                            0.0, "", elev)

                self.lViewshed.Active = not self.rbAGL.Checked
                self.lAGL.Active = self.rbAGL.Checked

                self.GIS.Add(self.lAGL)
                self.GIS.Add(self.lViewshed)
                self.lAGL.Transparency = 50
                self.lViewshed.Transparency = 50
                self.lObservers.Move(-2)

                # apply (binary or frequency) color ramp to the viewshed layer
                self.makeViewshedRamp()

                # apply color ramp to the AGL layer
                self.lAGL.Params.Pixel.GridShadow = False
                self.lAGL.GenerateRamp(
                      pdk.TGIS_Color().FromARGB(127, 0, 255, 0),
                      pdk.TGIS_Color().None_,
                      pdk.TGIS_Color().FromARGB(127, 255, 0, 0),
                      0, 1,
                      self.lAGL.MaxHeight, False,
                      (self.lAGL.MaxHeight - self.lAGL.MinHeight) / 100,
                      (self.lAGL.MaxHeight - self.lAGL.MinHeight) / 10,
                      None, False)

                self.GIS.InvalidateWholeMap()
            finally:
                self.GIS.Unlock()

            self.showComment()

    def GIS_MouseMove(self, _sender, _shift, x, y):
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        ref_rgb_mapped = pdk.VarParameter()
        ref_rgb_mapped.Value = pdk.TGIS_Color()
        ref_natives_vals = pdk.VarParameter()
        ref_natives_vals.Value = pdk.TGIS_DoubleArray()
        ref_transparency = pdk.VarParameter()
        ref_transparency.Value = False

        txt = ""
        if self.lViewshed and self.lViewshed.Locate(ptg,
                                                    ref_rgb_mapped,
                                                    ref_natives_vals,
                                                    ref_transparency):
            val = ref_natives_vals.Value.Value(0)
            if val != self.lViewshed.NoDataValue:
                txt += f"Frequency: {val}"
        if self.lAGL and self.lAGL.Locate(ptg,
                                          ref_rgb_mapped,
                                          ref_natives_vals,
                                          ref_transparency):
            val = ref_natives_vals.Value.Value(0)
            if val != self.lAGL.NoDataValue:
                txt += f"Above-Ground-Level: {val}"
        self.lblMsg.Caption = txt

    def setLayerActive(self, _sender):
        self.GIS.Lock()
        try:
            self.makeViewshedRamp()
            if self.GIS.Get(self.SAMPLE_VIEWSHED_NAME):
                self.lViewshed.Active = not self.rbAGL.Checked
                self.lAGL.Active = self.rbAGL.Checked
                self.GIS.InvalidateWholeMap()
        finally:
            self.GIS.Unlock()
        self.showComment()

    def rbAddObserver_change(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().UserDefined

    def rbZoom_change(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        
    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnReset_click(self, _sender):
        self.GIS.Lock()
        try:
            if self.GIS.Get(self.SAMPLE_VIEWSHED_NAME):
                self.GIS.Delete(self.lAGL.Name)
                self.lAGL = None
                self.GIS.Delete(self.lViewshed.Name)
                self.lViewshed = None
            self.lObservers.RevertAll()
            self.GIS.FullExtent()
        finally:
            self.GIS.Unlock()


def main():
    frm = ViewshedForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
