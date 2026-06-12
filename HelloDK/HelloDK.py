# HelloDK - TatukGIS Developer Kernel (DK11) introductory sample (Python / PDK).
#
# Demonstrates the core DK workflow:
#   1. Opening a vector Shapefile into the map viewer.
#   2. Switching the viewer interaction mode: Zoom / Drag / Select.
#   3. Creating an in-memory editable vector layer with a transparent polygon style.
#   4. Building a polygon shape programmatically by adding explicit vertices.
#   5. Click-to-select a feature using screen-to-map coordinate conversion
#      and spatial proximity search (GIS.Locate).
#   6. Spatial containment query using the DE-9IM matrix string "T*****FF*"
#      combined with a SQL WHERE filter to find world features whose label
#      starts with 's' and that are geometrically contained within the
#      user-created polygon.
#
# Python PDK notes:
#   - Enum values are accessed as instances: pdk.TGIS_ViewerMode().Select
#   - TGIS_Color / TGIS_BrushStyle / TGIS_Lock / TGIS_ShapeType are instantiated
#     before accessing their enum members.
#   - TGIS_Utils static helpers are called on an instance: pdk.TGIS_Utils().GisPoint(x, y)
#   - Lock/Unlock around shape editing should use try/finally to ensure Unlock
#     is always called even if an exception occurs during vertex additions.

import tatukgis_pdk as pdk


class HelloDKForm(pdk.TGIS_PvlForm):
    """
    HelloDK sample — introductory demonstration of core TatukGIS DK workflows.
    Opens a world shapefile, creates an in-memory vector layer with a polygon, performs spatial containment
    queries using DE-9IM topology predicates, and switches between interaction modes (Zoom, Drag, Select).
    Demonstrates screen-to-map coordinate conversion, feature location via GIS.Locate(), and SQL filtering.
    """
    # Layer name constants used as identifiers throughout the sample
    EDIT_LAYER = "edit layer"
    WORLD = "world"

    def __init__(self, _owner):
        # Set up the main form dimensions and caption
        self.Caption = "HelloDK - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        # Toolbar panel anchored to the top of the form
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        # "Open" button - loads the sample world shapefile
        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        # "Zooming" button - enables rubber-band zoom interaction
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        # "Dragging" button - enables pan/drag interaction
        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnDrag.Place(75, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Dragging"
        self.btnDrag.OnClick = self.btnDrag_click

        # "Select" button - enables click-to-select interaction
        self.btnSelect = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnSelect.Place(75, 22, None, 231, None, 3)
        self.btnSelect.Caption = "Select"
        self.btnSelect.OnClick = self.btnSelect_click

        # "Create Shape" button - adds an editable layer with a sample polygon
        self.btnCreateShape = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnCreateShape.Place(75, 22, None, 307, None, 3)
        self.btnCreateShape.Caption = "Create Shape"
        self.btnCreateShape.OnClick = self.btnCreateShape_click

        # "Find Shape" button - runs DE-9IM spatial containment query
        self.btnFindShape = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnFindShape.Place(75, 22, None, 383, None, 3)
        self.btnFindShape.Caption = "Find Shape"
        self.btnFindShape.OnClick = self.btnFindShape_click

        # The central GIS map viewer control, filling the remaining form area
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        # Wire up the TapSimple click handler
        self.GIS.TapSimpleEvent = self.GISTapSimpleEvent

    def GISTapSimpleEvent(self, _sender, _button, _shift, x, y):
        """
        TapSimple event handler - fired on every single mouse click on the viewer.
        When the viewer is in Select mode, converts the click position from screen
        pixels to map coordinates, finds the nearest shape within a tolerance of
        5 pixels, and toggles its selection state.

        Parameters:
            x, y  - screen pixel coordinates of the mouse click
        """
        # Ignore taps when the viewer is not in Select mode
        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        # Get the world layer to manage its selection state
        lv = pdk.TGIS_LayerVector()
        lv.Name = self.WORLD
        lv.CS = self.GIS.CS  # same coordinate system as a viewer

        # Clear any previously selected shapes before applying the new selection
        lv.DeselectAll()

        # Convert screen pixel coordinates to geographic map coordinates.
        # ScreenToMap accounts for the current zoom level and pan offset.
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # Compute the hit-test tolerance: 5 screen pixels expressed in map units.
        # Dividing by Zoom converts pixels to the map's coordinate unit.
        precision = 5.0 / self.GIS.Zoom

        # Search all layers for the topmost shape within 'precision' of the click point
        shp = self.GIS.Locate(ptg, precision)

        # If no shape was found near the click point, do nothing
        if not shp:
            return

        # Toggle selection: clicking a selected shape deselects it, and vice versa
        shp.IsSelected = not shp.IsSelected

        # Repaint the map to reflect the updated selection highlight
        self.GIS.InvalidateWholeMap()

    def btnOpen_click(self, _sender):
        """
        "Open" button click handler.
        Opens the WorldDCW world Shapefile from the DK sample data directory and
        loads it into the viewer. After opening, the mode is set to Select so
        the user can immediately click on features.
        """
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/WorldDCW/world.shp")
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoom_click(self, _sender):
        """
        "Zooming" button click handler.
        Switches the viewer to Zoom mode. In this mode the left mouse button
        draws a rubber-band rectangle to zoom into a region; the right button
        zooms out.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        "Dragging" button click handler.
        Switches the viewer to Drag mode, allowing the user to pan the map
        by clicking and dragging with the mouse.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnSelect_click(self, _sender):
        """
        "Select" button click handler.
        Switches the viewer to Select mode. In this mode, mouse clicks on the map
        are handled by GISTapSimpleEvent to toggle shape selection.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnCreateShape_click(self, _sender):
        """
        "Create Shape" button click handler.
        Creates a new in-memory TGIS_LayerVector named 'edit layer', gives it a
        transparent fill with a blue outline, then adds a single quadrilateral
        polygon to it. This layer is not backed by a file.
        """
        # Guard: if the edit layer already exists, do nothing (idempotent)
        ll = self.GIS.Get(self.EDIT_LAYER)
        if ll is not None:
            return

        # Create a new in-memory vector layer and register it with the viewer
        ll = pdk.TGIS_LayerVector()
        ll.Name = self.EDIT_LAYER
        # Inherit the viewer's coordinate system so coordinates are interpreted correctly
        ll.CS = self.GIS.CS

        # Style: transparent fill (Clear pattern) with a solid blue outline,
        # so the underlying world layer remains visible through the polygon
        ll.Params.Area.OutlineColor = pdk.TGIS_Color().Blue
        ll.Params.Area.Pattern = pdk.TGIS_BrushStyle().Clear

        # Register the layer with the viewer; it will appear on top of existing layers
        self.GIS.Add(ll)
        # Re-fetch from the viewer to get the managed layer reference
        ll = self.GIS.Get(self.EDIT_LAYER)

        # Create a new Polygon shape inside the layer
        shp = ll.CreateShape(pdk.TGIS_ShapeType().Polygon)

        # Lock(Extent) batches vertex additions so the bounding box is recalculated
        # only once when Unlock is called, improving performance for bulk edits
        shp.Lock(pdk.TGIS_Lock().Extent)
        try:
            # AddPart starts the first ring of the polygon; a shape can have multiple
            # parts (e.g., islands or holes in a multi-polygon)
            shp.AddPart()

            # Add the four corner vertices of the polygon (coordinates in the map's CS)
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(10, 10))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(10, 80))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(80, 90))
            shp.AddPoint(pdk.TGIS_Utils().GisPoint(90, 10))
        finally:
            # Unlock finalises the shape geometry: recalculates extents and closes
            # the polygon ring automatically if the first and last points differ.
            # Using finally ensures Unlock is always called even if an exception occurs.
            shp.Unlock()

        # Redraw the entire map canvas to show the newly added polygon
        self.GIS.InvalidateWholeMap()

    def btnFindShape_click(self, _sender):
        """
        "Find Shape" button click handler.
        Uses DE-9IM (Dimensionally Extended 9-Intersection Model) spatial
        relationship to find all world features that are fully contained inside
        the polygon created by btnCreateShape_click.

        The DE-9IM matrix "T*****FF*" encodes the "contains" relationship:
          - 'T' at position [0]: interiors must intersect (non-empty)
          - "FF" at positions [6,7]: the query shape's boundary and exterior
            must NOT intersect the target shape's interior - i.e. the target
            lies entirely within the query polygon.

        An additional SQL LIKE filter restricts results to features whose
        'label' field starts with the letter 's'.
        """
        # The edit layer must exist (created by btnCreateShape_click) to provide
        # the selection polygon; exit early if it has not been created yet
        ll = self.GIS.Get(self.EDIT_LAYER)
        if not ll:
            return

        # Retrieve the world layer - its name is derived from the filename ('world')
        lv = self.GIS.Get(self.WORLD)

        # Clear any previous selection on the world layer before applying the new one
        lv.DeselectAll()

        # Retrieve the first (and only) shape from the edit layer to use as
        # the spatial query boundary
        sel_shp = ll.GetShape(1)  # just the first shape from the layer

        # MakeEditable pins the shape into memory so it survives the subsequent
        # iteration; file-backed shapes are otherwise evicted from cache
        sel_shp = sel_shp.MakeEditable()

        # Lock the viewer to batch all selection redraws into a single repaint
        self.GIS.Lock()

        # Loop over all shapes in the world layer whose bounding box overlaps
        # sel_shp.Extent, whose 'label' field matches the SQL pattern 's%', AND
        # whose DE-9IM relationship with sel_shp satisfies "T*****FF*" (Contains).
        # The last argument (True) enables spatial index acceleration.
        for tmp_shp in lv.Loop(sel_shp.Extent, "label LIKE 's%'", sel_shp, "T*****FF*", True):
            tmp_shp.IsSelected = True

        # Unlock releases the batched repaint and triggers a single screen refresh
        self.GIS.Unlock()

        # Force a full map redraw to show the newly selected shapes highlighted
        self.GIS.InvalidateWholeMap()


def main():
    frm = HelloDKForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
