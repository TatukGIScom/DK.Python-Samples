import tatukgis_pdk as pdk

class IsochroneMapForm(pdk.TGIS_PvlForm):
    layerSrc: pdk.TGIS_LayerVector
    layerRoute: pdk.TGIS_LayerVector
    layerMarker: pdk.TGIS_LayerVector
    rtrObj: pdk.TGIS_IsochroneMap
    srtpObj: pdk.TGIS_ShortestPath
    costFactor: float
    numZones: int
    markerShp: pdk.TGIS_Shape

    def __init__(self, _owner):
        self.Caption = "IsochroneMap - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 510
        self.OnShow = self.form_show

        self.btnFullExtent = pdk.TGIS_PvlButton(self.Context)
        self.btnFullExtent.Place(73, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoomIn = pdk.TGIS_PvlButton(self.Context)
        self.btnZoomIn.Place(73, 22, None, 79, None, 3)
        self.btnZoomIn.Caption = "Zoom In"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.Context)
        self.btnZoomOut.Place(73, 22, None, 155, None, 3)
        self.btnZoomOut.Caption = "Zoom Out"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        self.groupBox1 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox1.Place(188, 249, None, 410, None, 0)
        self.groupBox1.Caption = "Routing parameters"
        self.groupBox1.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.lblSmallRoads = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblSmallRoads.Place(100, 13, None, 24, None, 24)
        self.lblSmallRoads.Caption = "Prefer local roads"

        self.trkSmallRoads = pdk.TGIS_PvlTrackBar(self.groupBox1.Context)
        self.trkSmallRoads.Place(161, 25, None, 16, None, 40)
        self.trkSmallRoads.Minimum = 1
        self.trkSmallRoads.Maximum = 10
        self.trkSmallRoads.Position = 1

        self.lblHighways = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblHighways.Place(90, 13, None, 24, None, 72)
        self.lblHighways.Caption = "Prefer Highway"

        self.trkHighways = pdk.TGIS_PvlTrackBar(self.groupBox1.Context)
        self.trkHighways.Place(161, 25, None, 16, None, 88)
        self.trkHighways.Minimum = 1
        self.trkHighways.Maximum = 10
        self.trkHighways.Position = 5

        self.lblDistance = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblDistance.Place(59, 13, None, 24, None, 120)
        self.lblDistance.Caption = "Distance"

        self.edtDistance = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtDistance.Place(145, 20, None, 24, None, 133)
        self.edtDistance.Text = "4000"

        self.lblZones = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblZones.Place(145, 20, None, 24, None, 162)
        self.lblZones.Caption = "Zones"

        self.edtZones = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtZones.Place(145, 20, None, 24, None, 178)
        self.edtZones.Text = "3"

        self.label1 = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.label1.Place(160, 34, None, 24, None, 212)
        self.label1.Caption = "Click on the map to set start point and generate isochrone"

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = -2
        self.GIS.Top = 28
        self.GIS.Width = 400
        self.GIS.Height = 482
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseDown = self.GIS_MouseDown

        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Place(145, 25, None, 10, None, 37)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(188, 246, None, 410, None, 255)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

    def form_show(self, _sender):
        self.GIS.Lock()
        try:
            self.GIS.Open(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                "World/Countries/USA/States/California/San Bernardino/TIGER/tl_2008_06071_edges_trunc.SHP")
            self.layerSrc = self.GIS.Items[0]

            if (not self.layerSrc or
                    not isinstance(self.layerSrc, pdk.TGIS_LayerVector)):
                return

            # update the layer parameters to show roads types
            self.layerSrc.ParamsList.Add()
            self.layerSrc.Params.Line.Width = -2
            self.layerSrc.Params.Query = "MTFCC<'S1400'"
            self.layerSrc.ParamsList.Add()
            self.layerSrc.Params.Line.Width = 1
            self.layerSrc.Params.Line.Style = pdk.TGIS_PenStyle().Dash
            self.layerSrc.Params.Query = "MTFCC='S1400'"

            self.GIS.VisibleExtent = self.layerSrc.Extent
            # self.GIS_ControlScale.Units = pdk.TGIS_CSUnitsList().ByEPSG(9035)  # mile

            # initial traversing cost
            self.costFactor = 5000.0
            self.numZones = 5

            # create route layer for result isochrone map
            self.layerRoute = pdk.TGIS_LayerVector()
            self.layerRoute.UseConfig = False
            self.layerRoute.Name = 'Isochrone map for route'
            self.layerRoute.CS = self.GIS.CS
            self.layerRoute.Params.Render.Expression = 'GIS_COST'
            self.layerRoute.Params.Render.MinVal = 0.
            self.layerRoute.Params.Render.MaxVal = self.costFactor
            self.layerRoute.Params.Render.Zones = self.numZones
            self.layerRoute.Params.Area.Color = pdk.TGIS_Color.RenderColor
            self.layerRoute.Params.Area.ShowLegend = True
            self.layerRoute.Transparency = 50
            self.GIS.Add(self.layerRoute)

            # create marker layer to show position
            self.layerMarker = pdk.TGIS_LayerVector()
            self.layerMarker.UseConfig = False
            self.layerMarker.Name = 'Current Position'
            self.layerMarker.CS = self.GIS.CS
            self.layerMarker.Params.Marker.Color = pdk.TGIS_Color.Red
            self.GIS.Add(self.layerMarker)

            self.markerShp = None

            # initialize isochrone map generator
            self.rtrObj = pdk.TGIS_IsochroneMap(self.GIS)

            # initialize the shortest path and attach events
            self.srtpObj = pdk.TGIS_ShortestPath(self.GIS)
            self.srtpObj.LinkCostEvent = None  # self.doLinkCostEvent
            self.srtpObj.LinkTypeEvent = self.doLinkType
            self.srtpObj.LinkDynamicEvent = self.doLinkDynamic
        finally:
            self.GIS.Unlock()

    @staticmethod
    def doLinkCostEvent(_sender, shape, cost, revcost):
        if isinstance(shape.Layer.CS, pdk.TGIS_CSUnknownCoordinateSystem):
            cost.Value = shape.Length
        else:
            cost.Value = shape.LengthCS
        revcost.Value = cost.Value

    @staticmethod
    def doLinkType(_sender, shape, type_):
        if shape.GetField("MTFCC") >= "S1400":
            # local roads
            type_.Value = 1
        else:
            type_.Value = 0

    def doLinkDynamic(self, _sender, uid, cost, revcost):
        if self.trkHighways.Position == 1:
            # block all highways
            shp = self.layerSrc.GetShape(uid)
            if shp.GetField("MTFCC") < "S1400":
                cost.Value = -1
                revcost.Value = -1

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        self.GIS.Zoom = self.GIS.Zoom / 2

    def generateIsochrone(self, _sender):
        self.layerRoute.RevertShapes()

        # maximum traversing cost for the isochrone map
        self.numZones = int(self.edtZones.Text)
        self.costFactor = float(self.edtDistance.Text)

        # update the renderer range
        self.layerRoute.Params.Render.MaxVal = self.costFactor
        self.layerRoute.Params.Render.Zones = self.numZones

        # calculate wages
        self.srtpObj.CostModifiers(0, 1 - 1/11 * float(self.trkHighways.Position))
        self.srtpObj.CostModifiers(1, 1 - 1/11 * float(self.trkSmallRoads.Position))

        # generate the isochrone maps
        for i in range(1, self.numZones + 1):
            self.rtrObj.Generate(self.layerSrc, self.srtpObj,
                                 self.layerRoute, pdk.TGIS_ShapeType().Polygon,
                                 self.markerShp.Centroid(), self.costFactor/i, 0)

        # smooth the result polygons shapes
        for shp in self.layerRoute.Loop():
            shp.Smooth(10, False)

        self.layerRoute.RecalcExtent()
        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerRoute.ProjectedExtent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # recreate a marker shape indicating start position
        if not self.markerShp:
            self.markerShp = self.layerMarker.CreateShape(pdk.TGIS_ShapeType().Point)
            self.markerShp.Lock(pdk.TGIS_Lock().Extent)
            self.markerShp.AddPart()
            self.markerShp.AddPoint(ptg)
            self.markerShp.Unlock()
            self.markerShp.Invalidate()
        else:
            self.markerShp.SetPosition(ptg, None, 0)

        self.generateIsochrone(self)
        

def main():
    frm = IsochroneMapForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
