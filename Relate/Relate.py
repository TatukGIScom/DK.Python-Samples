import tatukgis_pdk as pdk

class RelateForm(pdk.TGIS_PvlForm):
    shpA: pdk.TGIS_Shape = None
    shpB: pdk.TGIS_Shape = None
    curr_shape: pdk.TGIS_Shape = None
    SHAPE_A = "Shape A"
    SHAPE_B = "Shape B"

    def __init__(self, _owner):
        self.Caption = "Relate - TatukGIS DK Sample"
        self.ClientWidth = 750
        self.ClientHeight = 500

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 200
        self.GIS.Top = -100
        self.GIS.Width = 550
        self.GIS.Height = 633
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Samples/Topology/topology2.shp")
        self.GIS.FullExtent()
        self.GIS.OnMouseDown = self.GISMouseDown
        
        self.gbShapes = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbShapes.Place(176, 88, None, 10, None, 17)
        self.gbShapes.Caption = "Shapes"

        self.label1 = pdk.TGIS_PvlLabel(self.gbShapes.Context)
        self.label1.Place(58, 13, None, 26, None, 30)
        self.label1.Caption = "Shape A :"

        self.label2 = pdk.TGIS_PvlLabel(self.gbShapes.Context)
        self.label2.Place(58, 13, None, 26, None, 50)
        self.label2.Caption = "Shape B :"

        self.ShapeA = pdk.TGIS_PvlColorPreview(self.gbShapes.Context)
        self.ShapeA.Place(13, 13, None, 86, None, 30)
        self.ShapeA.Color = pdk.TGIS_Color().Gray
        # self.ShapeA.StyledSettings = []
        # self.ShapeA.CaptionSettings.FontColor = pdk.TGIS_Color().Blue

        self.ShapeB = pdk.TGIS_PvlColorPreview(self.gbShapes.Context)
        self.ShapeB.Place(13, 13, None, 86, None, 50)
        self.ShapeB.Color = pdk.TGIS_Color().Gray
        # self.ShapeB.StyledSettings = []
        # self.ShapeB.CaptionSettings.FontColor = pdk.TGIS_Color().Red

        self.gbRelation = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbRelation.Place(176, 248, None, 10, None, 119)
        self.gbRelation.Caption = "Relations between A and B"

        self.Relations = pdk.TGIS_PvlListBox(self.gbRelation.Context)
        self.Relations.Place(140, 223, None, 18, None, 16)
        self.Relations.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.btnCheck = pdk.TGIS_PvlButton(self.Context)
        self.btnCheck.Place(80, 22, None, 60, None, 400)
        self.btnCheck.Caption = "CHECK"
        self.btnCheck.OnClick = self.btnCheck_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Use left and right mouse buttons to select two shapes for relations"

    def GISMouseDown(self, _sender, button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # let's locate a shape after click
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        shp = self.GIS.Locate(ptg, 5.0/self.GIS.Zoom)

        if shp is None:
            return

        shp = shp.MakeEditable()

        if button == pdk.TGIS_PvlMouseButton().Left:
            # if selected shapeA, deselect it
            if self.shpA is not None:
                self.shpA.Params.Area.Color = pdk.TGIS_Color().FromRGB(0xC0C0C0)
                self.shpA.Params.Labels.Value = ''
                self.shpA.Invalidate()
                self.ShapeA.Color = pdk.TGIS_Color().Gray

            self.shpA = shp
            self.shpA.Params.Area.Color = pdk.TGIS_Color().Blue
            self.shpA.Params.Labels.Value = self.SHAPE_A
            self.shpA.Params.Labels.Position = [pdk.TGIS_LabelPosition().UpLeft]
            self.shpA.Invalidate()
            self.ShapeA.Color = pdk.TGIS_Color().Blue

        if button == pdk.TGIS_PvlMouseButton().Right:
            # if selected shapeB, deselect it
            if self.shpB is not None:
                self.shpB.Params.Area.Color = pdk.TGIS_Color().FromRGB(0xC0C0C0)
                self.shpB.Params.Labels.Value = ''
                self.shpB.Invalidate()
                self.ShapeB.Color = pdk.TGIS_Color().Gray

            self.shpB = shp
            self.shpB.Params.Area.Color = pdk.TGIS_Color().Red
            self.shpB.Params.Labels.Value = self.SHAPE_B
            self.shpB.Params.Labels.Position = [pdk.TGIS_LabelPosition().UpLeft]
            self.shpB.Invalidate()
            self.ShapeB.Color = pdk.TGIS_Color().Red

    def btnCheck_click(self, _sender):
        self.Relations.ItemsClear()

        if self.shpA is None or self.shpB is None:
            return

        # check all relations
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_EQUALITY()):
            self.Relations.ItemsAdd('EQUALITY')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_DISJOINT()):
            self.Relations.ItemsAdd('DISJOINT')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_INTERSECT()):
            self.Relations.ItemsAdd('INTERSECT')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_INTERSECT1()):
            self.Relations.ItemsAdd('INTERSECT1')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_INTERSECT2()):
            self.Relations.ItemsAdd('INTERSECT2')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_INTERSECT3()):
            self.Relations.ItemsAdd('INTERSECT3')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_WITHIN()):
            self.Relations.ItemsAdd('WITHIN')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_CROSS()):
            self.Relations.ItemsAdd('CROSS')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_CROSS_LINE()):
            self.Relations.ItemsAdd('CROSS_LINE')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_TOUCH()):
            self.Relations.ItemsAdd('TOUCH')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_TOUCH_INTERIOR()):
            self.Relations.ItemsAdd('TOUCH_INTERIOR')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_CONTAINS()):
            self.Relations.ItemsAdd('CONTAINS')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_OVERLAP()):
            self.Relations.ItemsAdd('OVERLAP')
        if self.shpA.Relate(self.shpB, pdk.TGIS_Utils.GIS_RELATE_OVERLAP_LINE()):
            self.Relations.ItemsAdd('OVERLAP_LINE')


def main():
    frm = RelateForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
