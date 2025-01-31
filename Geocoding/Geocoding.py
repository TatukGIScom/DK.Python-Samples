import tatukgis_pdk as pdk

def doLinkType(_sender, shape, ttype):
    if shape.GetField('MTFCC') >= 'S1400':
        # local roads
        ttype.Value = 1
    else:
        ttype.Value = 0

class GeocodingForm(pdk.TGIS_PvlForm):
    layerSrc: pdk.TGIS_LayerVector
    layerRoute: pdk.TGIS_LayerVector
    rtrObj: pdk.TGIS_ShortestPath
    geoObj = pdk.TGIS_Geocoding

    def __init__(self, _owner):
        self.Caption = "Geocoding - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

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

        self.lblAddrFrom = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblAddrFrom.Place(59, 13, None, 24, None, 120)
        self.lblAddrFrom.Caption = "From"

        self.edtAddrFrom = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtAddrFrom.Place(145, 20, None, 24, None, 133)
        self.edtAddrFrom.Text = "Chrys 1345"

        self.btnResolve = pdk.TGIS_PvlButton(self.groupBox1.Context)
        self.btnResolve.Place(75, 23, None, 94, None, 155)
        self.btnResolve.Caption = "Find Address"
        self.btnResolve.OnClick = self.btnResolve_click

        self.lblAddrTo = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblAddrTo.Place(145, 20, None, 24, None, 172)
        self.lblAddrTo.Caption = "To"

        self.edtAddrTo = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtAddrTo.Place(145, 20, None, 24, None, 188)
        self.edtAddrTo.Text = "wash"

        self.btnRoute = pdk.TGIS_PvlButton(self.groupBox1.Context)
        self.btnRoute.Place(75, 22, None, 94, None, 210)
        self.btnRoute.Caption = "Find Route"
        self.btnRoute.OnClick = self.btnRoute_click

        self.memRoute = pdk.TGIS_PvlMemo(self.groupBox1.Context)
        self.memRoute.Place(188, 227, None, 3, None, 240)
        self.memRoute.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 414
        self.GIS.Height = 480
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Place(145, 25, None, 8, None, 8)

    def form_show(self, _sender):
        self.GIS.Lock()

        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Projects/California.TTKPROJECT")
        self.layerSrc = self.GIS.Get("streets")

        if self.layerSrc is None:
            return

        self.GIS.VisibleExtent = self.layerSrc.Extent

        # create route layer
        self.layerRoute = pdk.TGIS_LayerVector()
        self.layerRoute.UseConfig = False

        self.layerRoute.Params.Line.Color = pdk.TGIS_Color().Red
        self.layerRoute.Params.Line.Width = -2
        self.layerRoute.Params.Marker.OutlineWidth = 1
        self.layerRoute.Name = 'RouteDisplay'
        self.layerRoute.CS = self.GIS.CS
        self.GIS.Add(self.layerRoute)

        # create geocoding object, set fields for routing
        self.geoObj = pdk.TGIS_Geocoding(self.layerSrc)
        self.geoObj.Offset = 0.0001
        self.geoObj.RoadName = "FULLNAME"
        self.geoObj.LFrom = "LFROMADD"
        self.geoObj.LTo = "LTOADD"
        self.geoObj.RFrom = "RFROMADD"
        self.geoObj.RTo = "RTOADD"

        # initialize the shortest path and attach events
        self.rtrObj = pdk.TGIS_ShortestPath(self.GIS)
        self.rtrObj.LinkTypeEvent = doLinkType
        self.rtrObj.LoadTheData(self.layerSrc)
        self.rtrObj.RoadName = "FULLNAME"

        self.GIS.Unlock()
        # self.GIS_ControlScale.Units = pdk.TGIS_Utils().CSUnitsList.ByEPSG(9035)

    def btnRoute_click(self, _sender):
        # calculate wages
        self.rtrObj.CostModifiers(0, 1 - 1/11.0 * self.trkHighways.Position)
        self.rtrObj.CostModifiers(1, 1 - 1/11.0 * self.trkSmallRoads.Position)

        # locate shapes meeting query
        res = self.geoObj.Parse(self.edtAddrFrom.Text, True, True)
        # if not found, ask for more details
        if res <= 0:
            self.edtAddrFrom.Caption = " ???"

        # remember starting point
        if res <= 0:
            return
        pt_a = self.geoObj.Point(0)

        res = self.geoObj.Parse(self.edtAddrTo.Text, True, True)
        if res > 0:
            self.edtAddrTo.Text = self.geoObj.Query(0)
        else:
            self.edtAddrTo.Text = "???"

        # remember ending point
        if res <= 0:
            return
        pt_b = self.geoObj.Point(0)

        # set starting and ending position
        self.rtrObj.UpdateTheData()
        self.rtrObj.Find(self.layerRoute.Unproject(pt_a), self.layerRoute.Unproject(pt_b))

        self.memRoute.Clear()
        old_name = ""

        # display directions
        ang = ""
        for i in range(self.rtrObj.ItemsCount-1):
            item = self.rtrObj.Items(i)

            if item.Compass == 0:
                ang = "FWD  "
            if item.Compass == 1:
                ang = "RIGHT"
            if item.Compass == 2:
                ang = "RIGHT"
            if item.Compass == 3:
                ang = "RIGHT"
            if item.Compass == 4:
                ang = "BACK "
            if item.Compass == -1:
                ang = "LEFT "
            if item.Compass == -2:
                ang = "LEFT "
            if item.Compass == -3:
                ang = "LEFT "
            if item.Compass == -4:
                ang = "BACK "

            if old_name == item.Name:
                continue
                
            old_name = item.Name
            ang = ang + " " + item.Name
            self.memRoute.AppendLine(ang)

        self.layerRoute.RevertShapes()

        # add shapes of our path to route layer (red)
        for i in range(self.rtrObj.ItemsCount - 1):
            item = self.rtrObj.Items(i)

            shp = item.Layer.GetShape(item.Uid)
            if shp is None:
                continue
            self.layerRoute.AddShape(shp)
            if i == 0:
                self.layerRoute.Extent = shp.Extent

        # mark starting point as green square
        shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pt_a)
        shp.Params.Marker.Color = pdk.TGIS_Color().Green
        shp.Unlock()

        # mark starting point as red square
        shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pt_b)
        shp.Unlock()

        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerRoute.Extent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()

    def btnResolve_click(self, _sender):

        if self.geoObj is None:
            return

        self.layerRoute.RevertShapes()

        # locate shapes meeting query
        r = self.geoObj.Parse(self.edtAddrFrom.Text, True, True) - 1
        if r < 0:
            self.edtAddrFrom.Caption = "???"

        for i in (0, r):
            self.edtAddrFrom.Text = self.geoObj.Query(i)
            self.GIS.ProcessMessages()

            # add found shape to route layer (red color)
            shp = self.layerSrc.GetShape(self.geoObj.Uid(i))
            self.layerRoute.AddShape(shp)

            if i == 0:
                self.layerRoute.Extent = shp.ProjectedExtent

            shp = self.layerSrc.GetShape(self.geoObj.UidEx(i))
            if shp is not None:
                self.layerRoute.AddShape(shp)

            # mark address as green square
            shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            shp.AddPoint(self.layerRoute.CS.FromCS(self.layerSrc.CS, self.geoObj.Point(i)))
            shp.Params.Marker.Color = pdk.TGIS_Color().Green
            shp.Unlock()

        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerRoute.ProjectedExtent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()


def main():
    frm = GeocodingForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
