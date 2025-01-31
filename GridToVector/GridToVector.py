import tatukgis_pdk as pdk

class GridToVectorForm(pdk.TGIS_PvlForm):
    LV_FIELD = "vector"
    LV_NAME = "polygons"

    def __init__(self, _owner):
        self.Caption = "GridToVector - TatukGIS DK Sample"
        self.ClientWidth = 774
        self.ClientHeight = 658
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 227
        self.GIS.Top = -5
        self.GIS.Width = 545
        self.GIS.Height = 633
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select
        self.GIS.OnMouseDown = self.GIS_MouseDown
        
        self.gbxLoadData = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbxLoadData.Place(200, 88, None, 10, None, 17)
        self.gbxLoadData.Caption = "Load data"

        self.btnLoadLand = pdk.TGIS_PvlButton(self.gbxLoadData.Context)
        self.btnLoadLand.Place(180, 23, None, 7, None, 22)
        self.btnLoadLand.Caption = "Land Cover"
        self.btnLoadLand.OnClick = self.btnLoadLand_click

        self.btnLoadDEM = pdk.TGIS_PvlButton(self.gbxLoadData.Context)
        self.btnLoadDEM.Place(180, 23, None, 7, None, 51)
        self.btnLoadDEM.Caption = "DEM"
        self.btnLoadDEM.OnClick = self.btnLoadDEM_click

        self.gbxCommon = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbxCommon.Place(200, 62, None, 10, None, 119)
        self.gbxCommon.Caption = "Common parameters"

        self.lblTolerance = pdk.TGIS_PvlLabel(self.gbxCommon.Context)
        self.lblTolerance.Place(58, 13, None, 6, None, 20)
        self.lblTolerance.Caption = "Tolerance:"

        self.edtTolerance = pdk.TGIS_PvlEdit(self.gbxCommon.Context)
        self.edtTolerance.Place(110, 20, None, 70, None, 20)
        self.edtTolerance.Text = "1"

        self.chkIgnoreNoData = pdk.TGIS_PvlCheckBox(self.gbxCommon.Context)
        self.chkIgnoreNoData.Place(124, 17, None, 8, None, 40)
        self.chkIgnoreNoData.Caption = "Ignore No Data"
        self.chkIgnoreNoData.Checked = False

        self.gbGridToPolygon = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbGridToPolygon.Place(200, 76, None, 11, None, 202)
        self.gbGridToPolygon.Caption = "Grid To Polygon"

        self.chkSplit = pdk.TGIS_PvlCheckBox(self.gbGridToPolygon.Context)
        self.chkSplit.Place(83, 17, None, 8, None, 19)
        self.chkSplit.Caption = "Split shapes"
        self.chkSplit.Checked = True

        self.btnGridToPolygon = pdk.TGIS_PvlButton(self.gbGridToPolygon.Context)
        self.btnGridToPolygon.Place(180, 23, None, 6, None, 42)
        self.btnGridToPolygon.Caption = "Generate"
        self.btnGridToPolygon.OnClick = self.btnGridToPolygon_click

        self.gbxGridToPoint = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbxGridToPoint.Place(200, 82, None, 11, None, 300)
        self.gbxGridToPoint.Caption = "Grid To Point"

        self.lblPointSpacing = pdk.TGIS_PvlLabel(self.gbxGridToPoint.Context)
        self.lblPointSpacing.Place(74, 19, None, 6, None, 22)
        self.lblPointSpacing.Caption = "Point spacing:"

        self.edtPointSpacing = pdk.TGIS_PvlEdit(self.gbxGridToPoint.Context)
        self.edtPointSpacing.Place(100, 20, None, 86, None, 20)
        self.edtPointSpacing.Text = "1000"

        self.btnGridToPoint = pdk.TGIS_PvlButton(self.gbxGridToPoint.Context)
        self.btnGridToPoint.Place(180, 23, None, 6, None, 48)
        self.btnGridToPoint.Caption = "Generate"
        self.btnGridToPoint.OnClick = self.btnGridToPoint_click

        self.progressBar = pdk.TGIS_PvlLabel(self.Context)
        self.progressBar.Place(545, 23, None, 227, None, 634)
        self.progressBar.Caption = ''
        self.progressBar.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.progressBar.Visible = True
        
        self.gbxShapeInfo = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbxShapeInfo.Place(200, 250, None, 10, None, 400)
        self.gbxShapeInfo.Caption = "Shape info"

        self.GIS_ControlAttributes = pdk.TGIS_PvlControlAttributes(self.gbxShapeInfo.Context)
        self.GIS_ControlAttributes.Align = "Client"
        
    def form_show(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "World/Countries/Luxembourg/CLC2018_CLC2018_V2018_20_Luxembourg.tif"
        )
        
    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        shp = self.GIS.Locate(ptg, 5/self.GIS.Zoom)
        
        if shp is None:
            return

        shp.Layer.DeselectAll()
        shp.IsSelected = True
        self.GIS_ControlAttributes.ShowShape(shp)

    def btnLoadLand_click(self, _sender):
        self.form_show(self)
        
        self.edtTolerance.Text = "1"
        self.edtPointSpacing.Text = "1000"

    def btnLoadDEM_click(self, _sender):
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "Samples/3D/elevation.grd"
        )
        lp = self.GIS.Items[0]
        lp.GenerateRamp(
            pdk.TGIS_Color.Blue,
            pdk.TGIS_Color.Lime,
            pdk.TGIS_Color.Red,
            lp.MinHeight,
            (lp.MinHeight + lp.MaxHeight) / 2,
            lp.MaxHeight,
            True,
            (lp.MaxHeight - lp.MinHeight) / 100,
            (lp.MaxHeight - lp.MinHeight) / 10,
            None,
            True,
            pdk.TGIS_ColorInterpolationMode().HSL
        )
        lp.Params.Pixel.GridSmoothColors = True
        
        self.GIS.InvalidateWholeMap()

        self.edtTolerance.Text = "10"
        self.edtPointSpacing.Text = "200"

    def doBusyEvent(self, _sender, pos, end, _abort):
        if pos == 0:
            self.progressBar.Caption = 'progress: 0 %'
        elif pos < 0:
            self.progressBar.Caption = 'progress: 100 %'
        else:
            self.progressBar.Caption = 'progress: ' + str(pos) + ' %'
        self.GIS.ProcessMessages()

    def btnGridToPolygon_click(self, _sender):
        lp = self.GIS.Items[0]
        if self.GIS.Get(self.LV_NAME):
            self.GIS.Delete(self.LV_NAME)

        lv = pdk.TGIS_LayerVector()
        lv.Name = self.LV_NAME
        lv.Open()
        lv.CS = lp.CS
        lv.DefaultShapeType = pdk.TGIS_ShapeType().Polygon
        lv.AddField(self.LV_FIELD, pdk.TGIS_FieldType().Float, 0, 0)
        lv.Transparency = 50
        lv.Params.Area.OutlineColor = pdk.TGIS_Color.Black

        polygonizer = pdk.TGIS_GridToPolygon()
        polygonizer.Tolerance = float(self.edtTolerance.Text)
        polygonizer.SplitShapes = self.chkSplit.Checked
        polygonizer.BusyEvent = self.doBusyEvent
        polygonizer.Generate(lp, lv, self.LV_FIELD)

        self.GIS.Add(lv)
        self.GIS.InvalidateWholeMap()

    def btnGridToPoint_click(self, _sender):
        lp = self.GIS.Items[0]
        if self.GIS.Get(self.LV_NAME):
            self.GIS.Delete(self.LV_NAME)

        lv = pdk.TGIS_LayerVector()
        lv.Name = self.LV_NAME
        lv.Open()
        lv.CS = lp.CS
        lv.DefaultShapeType = pdk.TGIS_ShapeType().Point
        lv.AddField(self.LV_FIELD, pdk.TGIS_FieldType().Float, 0, 0)
        lv.Params.Marker.Color = pdk.TGIS_Color.Black
        lv.Params.Marker.Style = pdk.TGIS_MarkerStyle().Circle
        lv.Params.Marker.SizeAsText = "SIZE:4pt"
        lv.Transparency = 75

        grid_to_point = pdk.TGIS_GridToPoint()
        grid_to_point.IgnoreNoData = self.chkIgnoreNoData.Checked
        grid_to_point.Tolerance = float(self.edtTolerance.Text)
        grid_to_point.PointSpacing = float(self.edtPointSpacing.Text)
        grid_to_point.BusyEvent = self.doBusyEvent
        grid_to_point.Generate(lp, lv, self.LV_FIELD)

        self.GIS.Add(lv)
        self.GIS.InvalidateWholeMap()


def main():
    frm = GridToVectorForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
