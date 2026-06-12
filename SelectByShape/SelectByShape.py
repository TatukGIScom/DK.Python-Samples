# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# SelectByShape sample — demonstrates how to select vector features by drawing
# an arbitrary shape (circle or rectangle) interactively on the map.
#
# Key concepts shown:
#   - Interactive rubber-band drawing of a selection shape on the GIS viewer
#     using the PDK form's mouse event callbacks and the PaintExtraEvent hook.
#   - Converting screen pixel coordinates to geographic map coordinates via
#     ScreenToMap so the drawn shape is in the layer's coordinate system.
#   - Building a circular selection area using TGIS_Topology.MakeBuffer, which
#     approximates a circle as a polygon around a point shape using a given
#     radius in map units.
#   - Building a rectangular selection polygon by manually adding four corner
#     points to a new polygon shape.
#   - Spatial query using TGIS_LayerVector.Loop with the GIS_RELATE_INTERSECT
#     DE-9IM predicate to iterate over features that share at least one point
#     with the selection shape (Loop is the Python-idiomatic alternative to the
#     FindFirst / FindNext pattern used in other language editions).
#   - Visually highlighting matched features with IsSelected and listing their
#     "name" attribute in a list box.

import tatukgis_pdk as pdk
from random import randint
import math


class SelectByShapeForm(pdk.TGIS_PvlForm):
    """
    Main application form for the SelectByShape sample.

    Hosts the TatukGIS viewer widget, two radio buttons (circle / rectangle),
    a list box that displays the names of selected features, and a status label.
    All GIS interaction is driven through the viewer's mouse event callbacks
    and the PaintExtraEvent rendering hook.
    """

    # Screen-space anchor point recorded when the left mouse button is pressed
    oldPos = pdk.TPoint()
    # Current drag-end point (rectangle second corner) updated on every MouseMove
    oldPos2 = pdk.TPoint()
    # Current radius of the rubber-band circle in screen pixels
    oldRadius = 0
    # Reference to the current in-memory layer (reused across show / mouse-up)
    ll = pdk.TGIS_LayerVector()

    def __init__(self, _owner):
        self.Caption = "SelectByShape - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        # Main map viewer widget
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 417
        self.GIS.Height = 480
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select
        # Anchoring ensures the viewer resizes with the form
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Radio buttons are mutually exclusive by their group membership;
        # only one selection mode can be active at a time
        self.btnCircle = pdk.TGIS_PvlRadioButton(self.Context)
        self.btnCircle.Place(75, 23, None, 3, None, 1)
        self.btnCircle.Caption = "By circle"

        self.btnRect = pdk.TGIS_PvlRadioButton(self.Context)
        self.btnRect.Place(76, 23, None, 85, None, 1)
        self.btnRect.Caption = "By rectangle"

        # List box on the right side that shows the names of intersecting features
        self.lbSelected = pdk.TGIS_PvlListBox(self.Context)
        self.lbSelected.Place(184, 447, None, 408, None, 0)
        self.lbSelected.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Status bar at the bottom with a short usage hint
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 447)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(300, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Use the left mouse button to select by chosen shape"

        # Wire up the viewer event callbacks
        self.GIS.PaintExtraEvent = self.GISPaintExtraEvent
        self.GIS.OnMouseDown = self.GISMouseDown
        self.GIS.OnMouseMove = self.GISMouseMove
        self.GIS.OnMouseUp = self.GISMouseUp

    def form_show(self, _sender):
        """
        Loads geospatial data the first time the form is displayed.

        Opens the base Counties shapefile and adds two empty in-memory vector
        layers that will hold visual indicators during selection:

        - "Points"  — invisible marker shapes (size 0) used only as geometry
                      containers for the MakeBuffer radius calculation.
        - "Buffers" — the rendered selection polygon (circle or rectangle).

        The viewer is locked during setup so that only one repaint fires on
        Unlock.  The viewer mode is explicitly set to Select afterwards so that
        the custom mouse handlers receive control.
        """
        self.GIS.Lock()
        # Open the base shapefile; Counties.shp supplies the features to select from
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/USA/States/California/Counties.SHP")

        # "Points" layer — invisible markers (size 0) acting as geometry placeholders
        self.ll = pdk.TGIS_LayerVector()
        self.ll.Params.Area.Color = pdk.TGIS_Color().Blue
        self.ll.Transparency = 50
        self.ll.Name = "Points"
        # Inherit the coordinate system from the viewer so all geometry is in the
        # same spatial reference and ScreenToMap conversions are correct
        self.ll.CS = self.GIS.CS
        self.GIS.Add(self.ll)

        # "Buffers" layer — holds the selection shape drawn by the user
        self.ll = pdk.TGIS_LayerVector()
        self.ll.Params.Area.Color = pdk.TGIS_Color().Blue
        self.ll.Params.Area.OutlineColor = pdk.TGIS_Color().Blue
        self.ll.Transparency = 60    # Semi-transparent so the map beneath shows through
        self.ll.Name = "Buffers"
        self.ll.CS = self.GIS.CS
        self.GIS.Add(self.ll)
        self.GIS.Unlock()
        # Ensure Select mode is active after unlock so our handlers take effect
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

        # Default to rectangle mode on startup
        self.btnRect.Checked = True

    def GISPaintExtraEvent(self, _sender, renderer, _mode):
        """
        Called by the viewer after all map layers have been drawn.

        Renders the rubber-band selection shape directly on the renderer canvas
        in screen space using the abstract renderer API.

        Using PaintExtraEvent (rather than a separate overlay widget) ensures
        the feedback is composited correctly on top of the map without flickering
        and works regardless of hardware acceleration.

        The pen colour is randomised each call to create a flickering
        "marching ants" visual effect on the outline during a drag operation.
        """
        rdr = renderer
        rdr.CanvasPen.Width = 1
        # Random colour creates the animated "marching ants" outline effect
        rdr.CanvasPen.Color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                                     randint(0, 255),
                                                     randint(0, 255))
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        # Clear brush so only the outline is drawn (no fill obscuring the map)
        rdr.CanvasBrush.Style = pdk.TGIS_BrushStyle().Clear

        if self.btnRect.Checked:
            # Do not draw until the user has actually moved the cursor (zero-size guard)
            if (self.oldPos.X == self.oldPos2.X) and (self.oldPos.Y == self.oldPos2.Y):
                return

            rct = pdk.TRect()
            rct.Left = self.oldPos.X
            rct.Top = self.oldPos.Y
            rct.Width = self.oldPos2.X - self.oldPos.X
            rct.Height = self.oldPos2.Y - self.oldPos.Y
            rdr.CanvasDrawRectangle(rct)

        if self.btnCircle.Checked:
            # CanvasDrawEllipse takes top-left corner X/Y, width, height in screen pixels.
            # The top-left is the centre minus the radius on both axes.
            rdr.CanvasDrawEllipse(
                self.oldPos.X - round(self.oldRadius),
                self.oldPos.Y - round(self.oldRadius),
                self.oldRadius * 2,
                self.oldRadius * 2
            )

    def GISMouseMove(self, _sender, shift, x, y):
        """
        Updates the rubber-band dimensions while the left mouse button is held.

        For rectangle mode the second corner follows the cursor; for circle mode
        the radius is the Euclidean pixel distance from the anchor to the cursor.
        Calling GIS.InvalidateSelection() redraws only the selection overlay rather
        than the full map, which is more efficient during rapid mouse movement.

        Args:
            _sender: The widget that triggered the event (not used).
            shift:   Sequence of active modifier / button strings (e.g. "Left").
            x, y:    Current cursor position in screen pixels.
        """
        if self.GIS.IsEmpty:
            return

        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return
        # Only update the rubber-band while the left button is pressed (dragging)
        if not ("Left" in shift):
            return

        if self.btnRect.Checked:
            # Track the second corner of the bounding rectangle
            self.oldPos2 = pdk.TPoint(int(x), int(y))

        if self.btnCircle.Checked:
            # Pythagorean distance from the anchor to the current cursor position
            self.oldRadius = round(math.sqrt(math.pow(self.oldPos.X - int(x), 2) + math.pow(self.oldPos.Y - int(y), 2)))

        # Invalidate only the selection overlay for efficiency during rapid drags
        self.GIS.InvalidateSelection()

    def GISMouseUp(self, _sender, button, _shift, _x, y):
        """
        Finalises the selection when the mouse button is released.

        Steps:
            1. Guard against empty map, zero-size drag, or right-click.
            2. Record invisible point markers in the "Points" layer as geometry
               containers for the buffer / corner calculations.
            3. Clear the "Buffers" layer and add the new selection polygon:
                 Circle    — TGIS_Topology.MakeBuffer approximates a circle as a
                             32-vertex polygon; the radius is derived by converting
                             oldRadius screen pixels into map units via ScreenToMap.
                 Rectangle — four corner points are assembled in map coordinates.
            4. Iterate the base Counties layer (GIS.Items[0]) using the Loop
               helper with GIS_RELATE_INTERSECT (a DE-9IM predicate) which yields
               each feature that shares at least one point with the selection shape.
               Loop is the Python-idiomatic replacement for FindFirst / FindNext.
            5. Mark each matched feature as selected and add its name to the list.

        Args:
            _sender: The widget that triggered the event (not used).
            button:  Which mouse button was released (TMouseButton enum value).
            _shift:  Modifier key state at release time (not used).
            _x:      Release X position in screen pixels (not used directly).
            y:       Release Y position in screen pixels (used for circle edge point).
        """
        if self.GIS.IsEmpty:
            return

        if button == pdk.TMouseButton().mbRight:
            # Right-click: restore Select mode (reversed the right-click zoom set in MouseDown)
            self.GIS.Mode = pdk.TGIS_ViewerMode.Select
            return

        # Guard: if the drag produced no movement, ignore (avoids zero-size shapes)
        if self.btnRect.Checked:
            if (self.oldPos.X == self.oldPos2.X) and (self.oldPos.Y == self.oldPos2.Y):
                return

        if self.btnCircle.Checked:
            if self.oldRadius == 0:
                return

        # --- Add invisible marker(s) to the "Points" layer ---
        # Marker.Size = 0 hides them from the renderer; they exist only to
        # supply geometry for MakeBuffer (circle) or as placeholders (rectangle).
        self.ll = self.GIS.Get("Points")
        self.ll.Lock()

        tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)

        ptg, ptg1 = None, None
        if self.btnCircle.Checked:
            # Convert the anchor screen pixel to a map coordinate (centre of circle)
            ptg = self.GIS.ScreenToMap(self.oldPos)
            tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
            tmp.Params.Marker.Size = 0
            # Lock with Extent so the layer's spatial extent is updated automatically
            tmp.Lock(pdk.TGIS_Lock().Extent)
            tmp.AddPart()
            tmp.AddPoint(ptg)
            tmp.Unlock()
            self.ll.Unlock()
            # Convert a point that is exactly oldRadius pixels to the right of centre;
            # the map-unit X difference between ptg1 and ptg is the circle radius
            ptg1 = self.GIS.ScreenToMap(pdk.TPoint(self.oldPos.X + int(self.oldRadius), int(y)))

        if self.btnRect.Checked:
            # Record the first corner as an invisible marker
            ptg = self.GIS.ScreenToMap(self.oldPos)
            tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
            tmp.Params.Marker.Size = 0
            tmp.Lock(pdk.TGIS_Lock().Extent)
            tmp.AddPart()
            tmp.AddPoint(ptg)
            tmp.Unlock()
            # Record the second corner (drag endpoint) as an invisible marker
            ptg = self.GIS.ScreenToMap(self.oldPos2)
            tmp.AddPoint(ptg)
            self.ll.Unlock()
            # Re-convert the first corner for use during rectangle construction below
            ptg1 = self.GIS.ScreenToMap(self.oldPos)

        buf = self.ll.CreateShape(pdk.TGIS_ShapeType().Unknown)

        # --- Rebuild the "Buffers" layer with the new selection shape ---
        self.ll = self.GIS.Get("Buffers")
        # RevertShapes clears all shapes added since the last commit, effectively
        # resetting the layer to empty so previous selections are discarded
        self.ll.RevertShapes()

        if self.btnCircle.Checked:
            if ptg is None or ptg1 is None:
                return
            # The map-unit radius is the horizontal distance from centre to edge point
            distance = ptg1.X - ptg.X

            tpl = pdk.TGIS_Topology()
            # MakeBuffer approximates a circle as a 32-vertex polygon around tmp.
            # The last parameter (True) closes the ring automatically.
            buf = tpl.MakeBuffer(tmp, distance, 32, True)
            # AddShape transfers ownership of the geometry to the Buffers layer
            buf = self.ll.AddShape(buf)

        if self.btnRect.Checked:
            # Build a closed rectangle polygon from the two diagonally opposite corners
            ptg2 = self.GIS.ScreenToMap(self.oldPos2)
            buf = self.ll.CreateShape(pdk.TGIS_ShapeType().Polygon)
            buf.AddPart()
            # Wind the four corners in order (top-left, top-right, bottom-right, bottom-left)
            buf.AddPoint(ptg1)
            buf.AddPoint(pdk.TGIS_Utils.GisPoint(ptg1.X, ptg2.Y))
            buf.AddPoint(ptg2)
            buf.AddPoint(pdk.TGIS_Utils.GisPoint(ptg2.X, ptg1.Y))

        # --- Perform the spatial query on the base Counties layer (Items[0]) ---
        self.ll = self.GIS.Items[0]
        if self.ll is None:
            self.GIS.InvalidateWholeMap()
            return

        # Clear any previously selected features before the new selection pass
        self.ll.DeselectAll()

        self.lbSelected.ItemsClear()

        self.GIS.InvalidateWholeMap()
        self.GIS.Lock()
        # Loop is the Python-idiomatic equivalent of FindFirst / FindNext.
        # It yields each TGIS_Shape whose geometry satisfies the GIS_RELATE_INTERSECT
        # DE-9IM predicate against buf — i.e. shares at least one point with the
        # selection shape — within the bounding box buf.Extent as a first-pass filter.
        for tmp in self.ll.Loop(buf.Extent, "", buf, pdk.TGIS_Utils.GIS_RELATE_INTERSECT()):
            # This feature intersects the selection polygon: highlight it and record its name
            self.lbSelected.ItemsAdd(str(tmp.GetField("name")))
            tmp.IsSelected = True

        self.GIS.Unlock()

    def GISMouseDown(self, _sender, button, _shift, x, y):
        """
        Records the anchor point when the user begins a drag.

        Right-click switches to the viewer's built-in Zoom mode so the user
        can pan or zoom without permanently leaving the custom Select mode.

        Args:
            _sender: The widget that triggered the event (not used).
            button:  Which mouse button was pressed (TMouseButton enum value).
            _shift:  Modifier key state (not used).
            x, y:    Mouse-down position in screen pixels.
        """
        if self.GIS.IsEmpty:
            return
        if button == pdk.TMouseButton().mbRight:
            # Right-click: hand control back to the viewer's built-in zoom/pan behaviour
            self.GIS.Mode = pdk.TGIS_ViewerMode.Zoom
            return

        # Initialise both anchor and drag-end to the same pixel so the shape starts
        # with zero size (prevents stale values from a previous selection)
        self.oldPos = pdk.TPoint(int(x), int(y))
        self.oldPos2 = pdk.TPoint(int(x), int(y))
        self.oldRadius = 0

    # def btnCircle_click(self, _sender):
    #     self.btnRect.Checked = not self.btnCircle.Checked
    #
    # def btnRect_click(self, _sender):
    #     self.btnCircle.Checked = not self.btnRect.Checked


def main():
    frm = SelectByShapeForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
