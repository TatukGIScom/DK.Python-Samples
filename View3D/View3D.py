import tatukgis_pdk as pdk
import math

class View3DForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "View3D - TatukGIS DK Sample"
        self.ClientWidth = 904
        self.ClientHeight = 692

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 57, None, 12, None, 12)

        self.btnOpenBuildings = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnOpenBuildings.Place(131, 23, None, 13, None, 3)
        self.btnOpenBuildings.Caption = "Open Buildings + DTM"
        self.btnOpenBuildings.OnClick = self.btnOpenBuildings_click

        self.btn2D3D = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btn2D3D.Place(75, 23, None, 197, None, 3)
        self.btn2D3D.Caption = "3D View"
        self.btn2D3D.OnClick = self.btn2D3D_click

        self.lbl3DMode = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lbl3DMode.Place(54, 13, None, 377, None, 11)
        self.lbl3DMode.Caption = "3D Mode:"

        self.cbx3DMode = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbx3DMode.Place(107, 23, None, 437, None, 3)
        names = ("Camera Position",
                 "Camera XYZ",
                 "Camera XY",
                 "Camera Rotation",
                 "Sun Position",
                 "Zoom",
                 "Select 3D")
        for name in names:
            self.cbx3DMode.ItemsAdd(name)
        self.cbx3DMode.ItemIndex = 0
        self.cbx3DMode.OnChange = self.cbx3DMode_change

        self.btnNavigation = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnNavigation.Place(96, 23, None, 564, None, 3)
        self.btnNavigation.Caption = "Adv. Navigation"
        self.btnNavigation.OnClick = self.btnNavigation_click

        self.btnRefresh = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnRefresh.Place(81, 23, None, 671, None, 3)
        self.btnRefresh.Caption = "Lock Refresh"
        self.btnRefresh.OnClick = self.btnRefresh_click

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(75, 23, None, 278, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnTextures = pdk.TGIS_PvlButton(self.Context)
        self.btnTextures.Place(99, 23, None, 28, None, 42)
        self.btnTextures.Caption = "Show Textures"
        self.btnTextures.Enabled = False
        self.btnTextures.OnClick = self.btnTextures_click

        self.btnRoof = pdk.TGIS_PvlButton(self.Context)
        self.btnRoof.Place(63, 23, None, 11, None, 71)
        self.btnRoof.Caption = "Hide roof"
        self.btnRoof.Enabled = False
        self.btnRoof.OnClick = self.btnRoof_click

        self.btnHideWalls = pdk.TGIS_PvlButton(self.Context)
        self.btnHideWalls.Place(68, 23, None, 76, None, 71)
        self.btnHideWalls.Caption = "Hide walls"
        self.btnHideWalls.Enabled = False
        self.btnHideWalls.OnClick = self.btnHideWalls_click

        self.btnOpenVolumetricLines = pdk.TGIS_PvlButton(self.Context)
        self.btnOpenVolumetricLines.Place(132, 23, None, 10, None, 601)
        self.btnOpenVolumetricLines.Caption = "Open Volumetric Lines"
        self.btnOpenVolumetricLines.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.btnOpenVolumetricLines.OnClick = self.btnOpenVolumetricLines_click

        self.btnOpenMultipatch = pdk.TGIS_PvlButton(self.Context)
        self.btnOpenMultipatch.Place(132, 26, None, 10, None, 630)
        self.btnOpenMultipatch.Caption = "Open MultiPatch"
        self.btnOpenMultipatch.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.btnOpenMultipatch.OnClick = self.btnOpenMultipatch_click

        self.btnInvertMultipatchLights = pdk.TGIS_PvlButton(self.Context)
        self.btnInvertMultipatchLights.Place(132, 23, None, 10, None, 662)
        self.btnInvertMultipatchLights.Caption = "Invert MultiPatch Lights"
        self.btnInvertMultipatchLights.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.btnInvertMultipatchLights.Enabled = False
        self.btnInvertMultipatchLights.OnClick = self.btnInvertMultipatchLights_click

        self.Image1 = pdk.TGIS_Bitmap()
        self.Image1.LoadFromFile("Resources/pictureBox1.Image.bmp")

        self.Image2 = pdk.TGIS_Bitmap()
        self.Image2.LoadFromFile("Resources/pictureBox2.Image.bmp")

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 152
        self.GIS.Top = 48
        self.GIS.Width = 604
        self.GIS.Height = 631
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(136, 495, None, 8, None, 100)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_3D = pdk.TGIS_PvlControl3D(self.Context)
        self.GIS_3D.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_3D.GIS_Viewer = self.GIS
        self.GIS_3D.Place(136, 631, None, 764, None, 48)
        self.GIS_3D.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS_3D.Enabled = False

    def btnOpenBuildings_click(self, sender):
        self.GIS.Lock()
        try:
            if self.GIS.View3D:
                self.btn2D3D_click(sender)

            self.GIS.Close()
            self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                          + "Samples/3D/Building3D.ttkproject")
            self.cbx3DMode.ItemIndex = 0
            
        finally:
            self.GIS.Unlock()

    def btn2D3D_click(self, _sender):
        if self.GIS.IsEmpty:
            return

        self.GIS.View3D = not self.GIS.View3D

        if self.GIS.View3D:
            self.btn2D3D.Caption = "2D View"
            self.btnTextures.Enabled = True
            self.btnRoof.Enabled = True
            self.btnHideWalls.Enabled = True
            self.btnInvertMultipatchLights.Enabled = True
            self.GIS_3D.Enabled = True
        else:
            self.btn2D3D.Caption = "3D View"
            self.btnTextures.Enabled = False
            self.btnRoof.Enabled = False
            self.btnHideWalls.Enabled = False
            self.btnInvertMultipatchLights.Enabled = False
            self.GIS_3D.Enabled = False
        self.cbx3DMode.ItemIndex = 0

    def cbx3DMode_change(self, _sender):
        if not self.GIS.View3D:
            return

        if self.cbx3DMode.ItemIndex == 0:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().CameraPosition
        
        elif self.cbx3DMode.ItemIndex == 1:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().CameraXYZ

        elif self.cbx3DMode.ItemIndex == 2:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().CameraXY

        elif self.cbx3DMode.ItemIndex == 3:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().CameraRotation

        elif self.cbx3DMode.ItemIndex == 4:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().SunPosition

        elif self.cbx3DMode.ItemIndex == 5:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().Zoom

        elif self.cbx3DMode.ItemIndex == 6:
            self.GIS.Viewer3D.Mode = pdk.TGIS_Viewer3DMode().Select

    def btnTextures_click(self, _sender):
        lv = self.GIS.Get("buildings")
        if lv is None:
            return

        if lv.Params.Area.Bitmap is None:
            self.btnTextures.Caption = "Hide Textures"
            lv.Params.Area.Bitmap = self.Image1
            lv.Params.Area.OutlineBitmap = self.Image2
        else:
            self.btnTextures.Caption = "Show Textures"
            lv.Params.Area.Bitmap = None
            lv.Params.Area.OutlineBitmap = None

        self.GIS.Viewer3D.UpdateWholeMap()

    def btnRoof_click(self, _sender):
        lv = self.GIS.Get("buildings")
        if lv is None:
            return

        if lv.Params.Area.Pattern == pdk.TGIS_BrushStyle().Clear:
            self.btnRoof.Caption = "Hide roof"
            lv.Params.Area.Pattern = pdk.TGIS_BrushStyle().Solid
        else:
            lv.Params.Area.Pattern = pdk.TGIS_BrushStyle().Clear
            self.btnRoof.Caption = "Show roof"

        self.GIS.Viewer3D.UpdateWholeMap()

    def btnHideWalls_click(self, _sender):
        lv = self.GIS.Get("buildings")
        if lv is None:
            return

        if lv.Params.Area.OutlinePattern == pdk.TGIS_BrushStyle().Clear:
            self.btnHideWalls.Caption = "Hide walls"
            lv.Params.Area.OutlinePattern = pdk.TGIS_BrushStyle().Solid
        else:
            lv.Params.Area.OutlinePattern = pdk.TGIS_BrushStyle().Clear
            self.btnHideWalls.Caption = "Show walls"

        self.GIS.Viewer3D.UpdateWholeMap()

    def btnFullExtent_click(self, _sender):
        if not self.GIS.View3D:
            self.GIS.FullExtent()
        else:
            self.GIS.Viewer3D.ResetView()

    def btnOpenVolumetricLines_click(self, sender):
        self.GIS.Lock()
        try:
            self.GIS.Close()

            lv = pdk.TGIS_LayerVector()
            lv.Name = "volumetric_lines"
            self.GIS.Add(lv)

            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc, pdk.TGIS_DimensionType().XYZ)
            shp.Params.Line.Color = pdk.TGIS_Color().Red
            shp.Params.Line.Width = 450
            shp.Params.Line.OutlinePattern = pdk.TGIS_BrushStyle().Clear
            shp.Lock(pdk.TGIS_Lock().Projection)
            try:
                shp.AddPart()
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(-50, 50, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(50, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(50, 50, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(50, 50, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(100, 50, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(150, 50, 0))
            finally:
                shp.Unlock()

            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc, pdk.TGIS_DimensionType().XYZ)
            shp.Params.Line.Color = pdk.TGIS_Color().Blue
            shp.Params.Line.Width = 350
            shp.Params.Line.OutlinePattern = pdk.TGIS_BrushStyle().Clear
            shp.Lock(pdk.TGIS_Lock().Projection)
            try:
                shp.AddPart()
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(-50, 40, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, -10, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(60, -10, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(60, 40, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(60, 40, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(110, 40, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(160, 40, 0))
            finally:
                shp.Unlock()

            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc, pdk.TGIS_DimensionType().XYZ)
            shp.Params.Line.Color = pdk.TGIS_Color().Green
            shp.Params.Line.Width = 250
            shp.Params.Line.OutlinePattern = pdk.TGIS_BrushStyle().Clear
            shp.Lock(pdk.TGIS_Lock().Projection)
            try:
                shp.AddPart()
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(-50, 30, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, -20, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(70, -20, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(70, 30, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(70, 30, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(120, 30, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(170, 30, 0))
            finally:
                shp.Unlock()

            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc, pdk.TGIS_DimensionType().XYZ)
            shp.Params.Line.Color = pdk.TGIS_Color().Yellow
            shp.Params.Line.Width = 150
            shp.Params.Line.OutlinePattern = pdk.TGIS_BrushStyle().Clear
            try:
                shp.Lock(pdk.TGIS_Lock().Projection)
                shp.AddPart()
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(-50, 20, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, -30, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(80, -30, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(80, 20, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(80, 20, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(130, 20, 50))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(120, 30, 50))
            finally:
                shp.Unlock()

            self.GIS.FullExtent()
            self.btn2D3D_click(sender)
            self.GIS.Viewer3D.ShowLights = True
        finally:
            self.GIS.Unlock()

    def btnOpenMultipatch_click(self, sender):
        self.GIS.Lock()
        try:
            self.GIS.Close()

            lv = pdk.TGIS_LayerVector()
            lv.Name = "multipatch"
            lv.Params.Area.Color = pdk.TGIS_Color().Yellow
            self.GIS.Add(lv)
            shp = lv.CreateShape(pdk.TGIS_ShapeType().MultiPatch, pdk.TGIS_DimensionType().XYZ)
            shp.Lock(pdk.TGIS_Lock().Projection)
            try:
                shp.AddPart()
                shp.SetPartType(0, pdk.TGIS_PartType().TriangleFan)
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(5, 4, 10))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 8, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 8, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 5))
                shp.AddPart()
                shp.SetPartType(1, pdk.TGIS_PartType().TriangleStrip)
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 8, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 8, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 8, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 8, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 0))
                shp.AddPart()
                shp.SetPartType(2, pdk.TGIS_PartType().OuterRing)
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(4, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(4, 0, 3))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(6, 0, 3))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(6, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 0, 0))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(10, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 5))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(0, 0, 0))
                shp.AddPart()
                shp.SetPartType(3, pdk.TGIS_PartType().InnerRing)
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(1, 0, 2))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(1, 0, 4))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(3, 0, 4))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(3, 0, 2))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(1, 0, 2))
                shp.AddPart()
                shp.SetPartType(4, pdk.TGIS_PartType().InnerRing)
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(7, 0, 2))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(7, 0, 4))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(9, 0, 4))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(9, 0, 2))
                shp.AddPoint3D(pdk.TGIS_Utils.GisPoint3D(7, 0, 2))
            finally:
                shp.Unlock()

            self.GIS.FullExtent()
            self.GIS.Zoom = self.GIS.Zoom / 2
            self.btn2D3D_click(sender)
            self.GIS.Viewer3D.CameraPosition = pdk.TGIS_Utils.GisPoint3D(10*math.pi/180, 200*math.pi/180, 28)
            self.GIS.Viewer3D.ShowLights = True
            self.GIS.Viewer3D.ShowVectorEdges = False
        finally:
            self.GIS.Unlock()

    def btnInvertMultipatchLights_click(self, _sender):
        if self.GIS.View3D:
            self.GIS.Viewer3D.LightVector = not self.GIS.Viewer3D.LightVector
            self.GIS.Viewer3D.UpdateWholeMap()

    def btnNavigation_click(self, _sender):
        if not self.GIS.View3D:
            return

        if not self.GIS.Viewer3D.AdvNavigation:
            self.GIS.Viewer3D.AdvNavigation = True
            self.btnNavigation.Caption = "Std. Navigation"
            self.GIS.Viewer3D.FastMode = True
            self.btnRefresh.Caption = "Unlock Refresh"
        else:
            self.GIS.Viewer3D.AdvNavigation = False
            self.btnNavigation.Caption = "Adv. Navigation"
            self.GIS.Viewer3D.FastMode = False
            self.btnRefresh.Caption = "Lock Refresh"

    def btnRefresh_click(self, _sender):
        if not self.GIS.View3D:
            return

        if not self.GIS.Viewer3D.FastMode:
            self.GIS.Viewer3D.FastMode = True
            self.btnRefresh.Caption = "Unlock Refresh"
        else:
            self.GIS.Viewer3D.FastMode = False
            self.btnRefresh.Caption = "Lock Refresh"


def main():
    frm = View3DForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
