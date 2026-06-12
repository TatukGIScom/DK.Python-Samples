# DragLabel sample — demonstrates interactive draggable feature labels on maps (Python PDK).
#
# What the sample shows:
#   - Two parallel in-memory vector layers: realpoints (features) and sidekicks (labels)
#   - Realpoints layer with visible CGM ship symbols rendered as point markers
#   - Storing ship name attributes for use as label text
#   - Disabling cached painting to ensure real-time shape repositioning
#   - Sidekicks layer with invisible ghost points carrying floating labels
#   - UID matching between realpoints and sidekicks for efficient lookups
#   - Custom label rendering via PaintShapeLabelEvent callback
#   - Drawing connecting leader line from real position to label position
#   - Manual editor control for drag-to-reposition interaction
#   - Converting screen click positions to map coordinates with ScreenToMap
#   - Setting sidekick shape position during drag operation
#   - Programmatic movement loop demonstrating simultaneous realpoint/sidekick translation
#
# Key TatukGIS API concepts shown here:
#   TGIS_ViewerWnd                      - main visual map control widget
#   TGIS_LayerVector                    - in-memory vector layer for features
#   TGIS_Shape                          - individual geographic feature
#   PaintShapeLabelEvent (callback)     - per-shape label rendering hook
#   TGIS_RendererAbstract               - platform-agnostic drawing interface
#   GIS.Locate()                        - hit-test to find shape at point
#   GIS.MapToScreen()                   - convert geographic coords to screen pixels
#   GIS.ScreenToMap()                   - convert screen pixels to geographic coordinates
#   GIS.Editor.MouseBegin()             - start manual shape editing/dragging
#   TGIS_Shape.SetPosition()            - reposition shape in geographic space
#   CanvasDrawLine()                    - draw connecting leader line
#   DrawLabel()                         - render text label at shape position
#   TGIS_PvlForm                        - base class for PDK forms

import tatukgis_pdk as pdk
from random import randint
from time import sleep


class DragLabelForm(pdk.TGIS_PvlForm):
    """
    Main application form for the DragLabel sample.

    Class-level constants:
        NAME_REALPOINTS: Layer name for the visible ship-symbol points.
        NAME_SIDEKICKS:  Layer name for the invisible draggable label anchors.
        FIELD_NAME:      Attribute field name storing the ship label text.
        LABEL_TEXT:      Prefix prepended to the ship UID to form the label.

    Instance state:
        currShape: The sidekick currently being dragged, or None when idle.
        GIS:       The TGIS_ViewerWnd viewer control.
        toolbar_buttons, button1, status_bar, status_label: UI widgets.
    """

    NAME_REALPOINTS = "realpoints"
    NAME_SIDEKICKS = "sidekicks"
    FIELD_NAME = "name"
    LABEL_TEXT = "Ship"
    currShape = None   # sidekick being dragged; None when no drag is active

    def __init__(self, _owner):
        """
        Constructs the form layout.

        The form defers all GIS initialisation to form_show (via OnShow) so
        that the viewer has a valid size before any extent operations are called.
        Mouse events on the GIS viewer are wired here to the three drag handlers.
        """
        self.Caption = "Drag Label - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        # Defer layer setup until the form is shown so GIS has a valid size
        self.OnShow = self.form_show

        # Toolbar panel housing the Animate button
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        # "Animate" button: starts a 90-step programmatic movement loop
        self.button1 = pdk.TGIS_PvlButton(self.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Animate"
        self.button1.OnClick = self.animate_click

        # Status bar panel at the bottom of the form
        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(592, 19, None, 0, None, 454)

        # Status label inside the status bar
        self.status_label = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.status_label.Place(100, 19, None, 3, None, 0)

        # Main GIS viewer: fills the remaining client area
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        # Wire the three drag interaction handlers
        self.GIS.OnMouseDown = self.GIS_MouseDown
        self.GIS.OnMouseMove = self.GIS_MouseMove
        self.GIS.OnMouseUp = self.GIS_MouseUp

    def is_gis_empty(self) -> bool:
        """
        Returns True and shows an info message if the GIS viewer has no layers.
        Used as a guard in mouse event handlers to prevent null-reference errors
        when the map is not yet populated.
        """
        if self.GIS.IsEmpty:
            pdk.TGIS_PvlMessages.ShowInfo("Create a layer first !", self.Context)
            return True
        return False

    def doLabelPaint(self, _sender, _shape):
        """
        PaintShapeLabelEvent callback - fired by the "sidekicks" layer for
        each sidekick shape during every repaint pass.

        _shape is the sidekick being painted.  Its Uid matches the corresponding
        realpoint in the "realpoints" layer, which is accessed via Items[0]
        (the first layer added to the viewer, i.e. "realpoints").

        Steps:
          1. Retrieve the matching realpoint by UID from Items[0].
          2. Convert both geographic positions to screen pixels with MapToScreen.
             MapToScreen(TGIS_Point) -> TPoint in screen pixels relative to viewer.
          3. Configure the pen on the abstract renderer and draw the blue leader
             line from the real symbol position (pt_a) to the label anchor (pt_b).
          4. Copy the "name" field value to the sidekick's label parameter and
             call DrawLabel() to render the text at the sidekick's position using
             the layer's configured label style.

        Args:
            _sender: The object that fired the event (the sidekicks layer).
            _shape:  The sidekick TGIS_Shape currently being painted.
        """
        # Retrieve the realpoints layer (always index 0 in this sample)
        ll = self.GIS.Items[0]
        # Find the matching realpoint by UID
        shp = ll.GetShape(_shape.Uid)

        # MapToScreen converts geographic coordinates to screen pixels.
        # Viewer.Ref gives access to coordinate transformation utilities.
        pt_a = _shape.Viewer.Ref.MapToScreen(shp.GetPoint(0, 0))   # real symbol
        pt_b = _shape.Viewer.Ref.MapToScreen(_shape.GetPoint(0, 0)) # label anchor

        # Obtain the renderer from the shape's layer.
        # TGIS_RendererAbstract provides a backend-agnostic drawing API.
        rdr = _shape.Layer.Renderer

        # Draw the blue leader line connecting the real position to the label
        rdr.CanvasPen.Color = pdk.TGIS_Color.Blue
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rdr.CanvasPen.Width = 1
        rdr.CanvasDrawLine(pt_a.X, pt_a.Y, pt_b.X, pt_b.Y)

        # Set the label text from the real feature's "name" field and render it
        # at the sidekick's geographic position using the layer's label style.
        _shape.Params.Labels.Value = shp.GetField(self.FIELD_NAME)
        _shape.DrawLabel()

    def form_show(self, _sender):
        """
        OnShow handler - builds the two-layer data model and populates 20 ships.

        Called when the form becomes visible.  At this point the viewer has a
        valid size, so GIS.Zoom is meaningful for the 15/Zoom offset calculation.

        "realpoints" layer:
          CachedPaint = False so moving shapes are always redrawn from scratch.
          A CGM ship symbol is loaded.  A "name" string field stores each ship's
          label text (LABEL_TEXT + UID).

        "sidekicks" layer:
          Invisible markers (Marker.Size = 0).
          PaintShapeLabelEvent = doLabelPaint for leader-line drawing.
          Labels.Allocator = False keeps labels at the exact sidekick position.
          CachedPaint = False so repositioned sidekicks are always redrawn.

          Each sidekick is offset from its realpoint by 15 / GIS.Zoom map units
          so the label starts visually displaced from the ship symbol.

        Args:
            _sender: The form object (unused).
        """
        # --- "realpoints" layer ---
        ll = pdk.TGIS_LayerVector()
        symbol_list = pdk.TGIS_Utils().SymbolList
        # SymbolList.Prepare caches the compiled CGM symbol for fast rendering.
        ll.Params.Marker.Symbol = symbol_list.Prepare(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Symbols/2267.cgm"
        )
        ll.Name = self.NAME_REALPOINTS
        # Disable tile cache - positions change at runtime so always redraw fresh.
        ll.CachedPaint = False

        self.GIS.Add(ll)
        ll.AddField(self.FIELD_NAME, pdk.TGIS_FieldType().String, 100, 0)
        # World-spanning extent so all random points fall within the layer.
        ll.Extent = pdk.TGIS_Utils.GisExtent(-180, -180, 180, 180)

        # --- "sidekicks" layer (draggable label anchors) ---
        ll = pdk.TGIS_LayerVector()
        ll.Name = self.NAME_SIDEKICKS
        ll.Params.Marker.Size = 0                                      # invisible marker
        ll.Params.Labels.Position = [pdk.TGIS_LabelPosition().MiddleCenter]
        ll.CachedPaint = False

        self.GIS.Add(ll)
        # Register the custom label painter.  PaintShapeLabelEvent fires once
        # per sidekick per repaint, replacing the layer's default label rendering.
        ll.PaintShapeLabelEvent = self.doLabelPaint
        # Disable auto label-placement so labels stay exactly at the sidekick.
        ll.Params.Labels.Allocator = False

        # --- Populate both layers with 20 random ship points ---
        shp_type = pdk.TGIS_ShapeType().Point
        lv = self.GIS.Items[0]                            # "realpoints" layer
        lv_sidekicks = self.GIS.Get(self.NAME_SIDEKICKS)  # "sidekicks" layer

        for _ in range(20):
            # Random geographic position in WGS-84 world coordinates
            ptg = pdk.TGIS_Utils.GisPoint(randint(0, 360) - 180,
                                          randint(0, 180) - 90)

            color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                           randint(0, 255),
                                           randint(0, 255))

            # Create and configure the visible realpoint shape.
            # Lock(Extent)/Unlock prevents the layer from auto-expanding its
            # stored extent during AddPoint.  try/finally ensures Unlock.
            shp = lv.CreateShape(shp_type)
            shp.Lock(pdk.TGIS_Lock().Extent)
            try:
                shp.AddPart()
                shp.AddPoint(ptg)
                # Unique rotation per ship so they face different directions.
                shp.Params.Marker.SymbolRotate = float(shp.Uid)
                shp.Params.Marker.Color = color
                shp.Params.Marker.Size = 250
                shp.Params.Marker.OutlineColor = color
                # Store label text as "Ship<UID>"
                shp.SetField(self.FIELD_NAME, self.LABEL_TEXT + f"{shp.Uid}")
            finally:
                shp.UnLock()

            # Create the matching sidekick, offset by 15 pixels in map units.
            # 15 / GIS.Zoom converts 15 screen pixels to the current map-unit
            # scale so the offset is constant in screen space regardless of zoom.
            shp = lv_sidekicks.CreateShape(shp_type)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            ptg.X = ptg.X + 15/self.GIS.Zoom
            ptg.Y = ptg.Y + 15/self.GIS.Zoom
            shp.AddPoint(ptg)
            shp.Unlock()

        # Fit the viewer to the full extent of all layers
        self.GIS.FullExtent()

    def synchroMove(self, _shp, _x, _y):
        """
        Moves the given realpoint shape and its matching sidekick by (_x, _y)
        map units simultaneously.

        The sidekick is located by matching _shp.Uid.  Both shapes are moved
        by the same displacement so the leader line length is preserved.

        A TGIS_Extent covering both post-move positions is computed for
        optional selective invalidation; currently SetPosition triggers the
        viewer repaint internally, so no explicit invalidation is needed.

        Args:
            _shp: The realpoint TGIS_Shape to move.
            _x:   Horizontal displacement in map units.
            _y:   Vertical displacement in map units.
        """
        # Shift the realpoint
        ptg_a = _shp.GetPoint(0, 0)
        ptg_a.X = ptg_a.X + _x
        ptg_a.Y = ptg_a.Y + _y
        _shp.SetPosition(ptg_a, None, 0)

        # Locate and shift the matching sidekick by the same displacement
        ll = self.GIS.Get(self.NAME_SIDEKICKS)
        shp = ll.GetShape(_shp.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ptg_b.X = ptg_b.X + _x
        ptg_b.Y = ptg_b.Y + _y
        shp.SetPosition(ptg_b, None, 0)

        # Bounding extent of both positions for optional selective invalidation
        ex = pdk.TGIS_Extent()
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

    def animate_click(self, _sender):
        """
        "Animate" button click handler.

        Moves shape UID=5 (first realpoint layer) and its sidekick for 90 steps
        of (+2, +1) map units per step with a 0.1-second sleep between steps.
        GIS.ProcessMessages() keeps the UI responsive during the loop so the
        animation is visible and the form remains interactive.

        Args:
            _sender: The button that fired the click (unused).
        """
        lv = self.GIS.Items[0]   # "realpoints" layer
        shp = lv.GetShape(5)     # the shape with UID=5
        for _ in range(90):
            self.synchroMove(shp, 2, 1)
            sleep(0.1)
            # Pump the PDK event loop so the map repaints between steps
            self.GIS.ProcessMessages()

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        """
        Begins a label drag when the user clicks near a sidekick shape.

        GIS.IsEmpty guards prevent starting a drag when no layers are loaded.
        Locate searches the sidekicks layer for the nearest shape within a
        100-pixel tolerance converted to map units (100 / GIS.Zoom).

        GIS.Editor.MouseBegin is called without switching GIS.Mode to Edit,
        so normal viewer pan/zoom behaviour is not globally disabled and we
        retain full control over what gets moved.

        Args:
            _sender: The viewer that fired the event.
            _button: Mouse button identifier.
            _shift:  Keyboard modifier state.
            x, y:    Mouse position in screen pixels.
        """
        if self.GIS.IsEmpty:
            return

        # Locate the nearest sidekick within 100 pixels (in map units)
        ll = self.GIS.Get(self.NAME_SIDEKICKS)
        pt = pdk.TPoint(int(x), int(y))
        # ScreenToMap converts screen pixel coordinates to geographic map coordinates.
        ptg = self.GIS.ScreenToMap(pt)
        shp = ll.Locate(ptg, 100/self.GIS.Zoom)
        self.currShape = shp

        if not self.currShape:
            return

        # We are not switching GIS.Mode to TGIS_ViewerMode.Edit because we
        # want full control over editing.  Instead we call MouseBegin, and will
        # call SetPosition directly in GIS_MouseMove.
        self.GIS.Editor.MouseBegin(pt, True)

    def GIS_MouseMove(self, _sender, _shift, x, y):
        """
        Repositions the tracked sidekick shape to follow the mouse cursor.

        Pre- and post-move bounding extents are computed for the sidekick
        and its realpoint.  SetPosition already triggers a viewer repaint,
        but the extent values could be passed to GIS.InvalidateExtent for
        more efficient partial repaints in high-density scenes.

        ScreenToMap converts the pixel mouse position to geographic map
        coordinates.  GisIsPointInsideExtent prevents the label from being
        dragged outside the viewer's valid geographic extent.

        Args:
            _sender: The viewer that fired the event.
            _shift:  Keyboard modifier state.
            x, y:    Current mouse position in screen pixels.
        """
        if self.GIS.IsEmpty:
            return
        if not self.currShape:
            return

        # Pre-move extent: union of sidekick and its realpoint positions
        ptg_a = self.currShape.GetPoint(0, 0)
        ll = self.GIS.Get(self.NAME_REALPOINTS)
        shp = ll.GetShape(self.currShape.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ex = pdk.TGIS_Extent()
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

        # Convert mouse pixel position to geographic map coordinates
        ptg_a = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        # Only reposition if the target coordinate is within the map extent
        if pdk.TGIS_Utils.GisIsPointInsideExtent(ptg_a, self.GIS.Extent):
            self.currShape.SetPosition(ptg_a, None, 0)

        # Post-move extent (for optional selective invalidation)
        ptg_a = self.currShape.GetPoint(0, 0)
        shp = ll.GetShape(self.currShape.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

    def GIS_MouseUp(self, _sender, _button, _shift, _x, _y):
        """
        Ends the current label drag by clearing the tracked shape reference.
        Subsequent GIS_MouseMove calls will be ignored until the next
        GIS_MouseDown finds a new sidekick to track.

        Args:
            _sender:       The viewer that fired the event.
            _button:       Mouse button identifier.
            _shift:        Keyboard modifier state.
            _x, _y:        Mouse release position (not used here).
        """
        if self.GIS.IsEmpty:
            return
        self.currShape = None


def main():
    """
    Application entry point.  Creates the DragLabelForm, shows it, and
    starts the PDK event loop.
    """
    frm = DragLabelForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
