import tatukgis_pdk as pdk

class HelloDKForm(pdk.TGIS_PvlForm):
    EDIT_LAYER = "edit layer"
    WORLD = "world"

    def __init__(self, _owner):
        self.Caption = "HelloDK - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnDrag.Place(75, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Dragging"
        self.btnDrag.OnClick = self.btnDrag_click

        self.btnSelect = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnSelect.Place(75, 22, None, 231, None, 3)
        self.btnSelect.Caption = "Select"
        self.btnSelect.OnClick = self.btnSelect_click

        self.btnCreateShape = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnCreateShape.Place(75, 22, None, 307, None, 3)
        self.btnCreateShape.Caption = "Create Shape"
        self.btnCreateShape.OnClick = self.btnCreateShape_click

        self.btnFindShape = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnFindShape.Place(75, 22, None, 383, None, 3)
        self.btnFindShape.Caption = "Find Shape"
        self.btnFindShape.OnClick = self.btnFindShape_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.TapSimpleEvent = self.GISTapSimpleEvent

    def GISTapSimpleEvent(self, _sender, _button, _shift, x, y):
        # ignore clicking if mode is other than select
        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        # create a new layer and add it to the viewer
        lv = pdk.TGIS_LayerVector()
        lv.Name = self.WORLD
        lv.CS = self.GIS.CS  # same coordinate system as a viewer

        # deselect all shapes on the layer
        lv.DeselectAll()

        # convert screen coordinates to map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # calculate precision of location as 5 pixels
        precision = 5.0 / self.GIS.Zoom

        # let's try to locate a selected shape on the map
        shp = self.GIS.Locate(ptg, precision)

        # not found?
        if not shp:
            return

        # mark shape as selected
        shp.IsSelected = not shp.IsSelected

        # and refresh a map
        self.GIS.InvalidateWholeMap()

    def btnOpen_click(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/WorldDCW/world.shp")
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnSelect_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnCreateShape_click(self, _sender):
        # find if such layer already exists
        ll = self.GIS.Get(self.EDIT_LAYER)
        if ll is not None:
            return

        # create a new layer and add it to the viewer
        ll = pdk.TGIS_LayerVector()
        ll.Name = self.EDIT_LAYER
        ll.CS = self.GIS.CS  # same coordinate system as a viewer

        ll.Params.Area.OutlineColor = pdk.TGIS_Color().Blue
        ll.Params.Area.Pattern = pdk.TGIS_BrushStyle().Clear

        # add layer to the viewer
        self.GIS.Add(ll)
        ll = self.GIS.Get(self.EDIT_LAYER)

        # create a shape and add it to polygon
        shp = ll.CreateShape(pdk.TGIS_ShapeType().Polygon)

        # we group operation together
        shp.Lock(pdk.TGIS_Lock().Extent)
        try:
            shp.AddPart()
            # add some vertices
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(10, 10))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(10, 80))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(80, 90))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(90, 10))
        finally:
            # unlock operation, close shape if necessary
            shp.Unlock()

        # and now refresh map
        self.GIS.InvalidateWholeMap()

    def btnFindShape_click(self, _sender):

        # get layer from the viewer
        ll = self.GIS.Get(self.EDIT_LAYER)
        if not ll:
            return

        # get a layer with world shape
        lv = self.GIS.Get(self.WORLD)

        # deselect selected shapes
        lv.DeselectAll()

        # and we need a created shape, with we want
        # to use as selection shape
        sel_shp = ll.GetShape(1)  # just a first shape form the layer

        # for file based layer we should pin shape to memory
        # otherwise it should be discarded
        sel_shp = sel_shp.MakeEditable()

        # Group all future screen updates into one drawing operation
        self.GIS.Lock()

        # so now we search for all shapes with DE9-IM relationship
        # which labels starts with 's' (with use of SQL syntax)
        # in this case we find "T*****FF*" contains relationship
        # which means that we will find only shapes inside the polygon
        for tmp_shp in lv.Loop(sel_shp.Extent, "label LIKE 's%'", sel_shp, "T*****FF*", True):
            tmp_shp.IsSelected = True
            
        # unlock operation, close shape if necessary
        self.GIS.Unlock()

        # and now refresh map
        self.GIS.InvalidateWholeMap()


def main():
    frm = HelloDKForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
