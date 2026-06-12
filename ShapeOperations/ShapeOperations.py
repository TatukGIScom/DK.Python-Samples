# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# ShapeOperations sample - Interactive affine transformation of vector shapes.
#
# This sample demonstrates how to interactively apply affine geometric
# transformations to individual vector shapes using the TatukGIS PDK API:
#
#   Rotate:    Spins the selected shape around its centroid.  Horizontal mouse
#              movement maps to rotation angle (1 pixel = 1 degree).
#   Scale:     Grows or shrinks the shape by comparing the current mouse
#              position to the previous one (ratio-based per axis).
#   Move:      Translates the shape by the map-coordinate delta between
#              consecutive mouse-move events.
#
# The sample uses a two-layer approach:
#   1. The original shapefile layer holds the real data.
#   2. An in-memory TGIS_LayerVector (edtLayer) renders a live preview of the
#      shape being edited.  CachedPaint = False makes it a "tracking" layer so
#      InvalidateTopmost triggers an immediate repaint.
# On commit (second mouse-up), the edited geometry is written back to the
# source shape via CopyGeometry, and the preview layer is cleared.
#
# Data: Samples/3D/buildings.shp
# =============================================================================

import tatukgis_pdk as pdk
import math


class ShapeOperationsForm(pdk.TGIS_PvlForm):
    """
    Main form for the ShapeOperations sample.

    Manages the two-layer edit workflow:
    - First click selects a shape and starts the live-preview session.
    - Mouse movement applies incremental rotate/scale/translate transforms
      to the preview copy of the shape.
    - Second click commits the final geometry back to the original layer.
    """

    # Flag that enables transform dragging.
    # Toggled by the first mouse-up (select) and cleared by the second (commit).
    handleMouseMove = None

    # Map-coordinate position from the previous mouse event.
    # Used to compute the translation delta in map units.
    prevPtg = pdk.TGIS_Point()

    # Screen-pixel coordinates from the previous mouse event.
    # Used to derive the rotation angle and scale ratios.
    prevX = None
    prevY = None

    # In-memory overlay layer used as a live edit preview.
    # CachedPaint = False makes it bypass the tile cache so InvalidateTopmost
    # causes an immediate redraw on every incremental transform step.
    edtLayer = None

    # The original shape in the source layer, placed in editable state via
    # MakeEditable.  CopyGeometry writes the final geometry back here on commit.
    currShape = None

    # Working copy of currShape that lives in edtLayer and receives all
    # intermediate transform calls during the drag session.
    edtShape = None

    def __init__(self, _owner):
        """Build the form layout and register event handlers."""
        self.Caption = "ShapeOperations - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        # Toolbar panel holding the mode radio buttons and hint label
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 40, None, 0, None, 0)

        # Rotate mode radio button
        self.rbRotate = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbRotate.Place(57, 25, None, 12, None, 7)
        self.rbRotate.Caption = "Rotate"
        self.rbRotate.Checked = True
        self.rbRotate.OnChange = self.rbRotate_change

        # Scale mode radio button
        self.rbScale = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbScale.Place(56, 25, None, 75, None, 7)
        self.rbScale.Caption = "Scale"
        self.rbScale.OnChange = self.rbScale_change

        # Move (translate) mode radio button
        self.rbMove = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbMove.Place(56, 25, None, 133, None, 7)
        self.rbMove.Caption = "Move"
        self.rbMove.OnChange = self.rbMove_change

        # Status/hint label
        self.lbHint = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lbHint.Place(400, 25, None, 197, None, 7)
        self.lbHint.Caption = "Select shape on the map to start transform"

        # Bottom status bar (shows altitude / extra info)
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblAltitude = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblAltitude.Place(300, 19, None, 3, None, 0)
        self.lblAltitude.Caption = ""

        # Main map viewer control
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 35
        self.GIS.Width = 600
        self.GIS.Height = 440
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseMove = self.GIS_MouseMove
        self.GIS.OnMouseUp = self.GIS_MouseUp

    def form_show(self, _sender):
        """
        Called when the form first becomes visible.

        Opens the sample buildings shapefile, creates the in-memory preview
        layer, and zooms in to a comfortable starting extent.
        """
        self.GIS.Lock()  # Suspend repaints while loading/configuring layers

        # GisSamplesDataDirDownload resolves the shared sample data folder
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/3D/buildings.shp")

        # Zoom in 4x from the default extent so buildings are visible
        self.GIS.Zoom = self.GIS.Zoom * 4

        # Create the in-memory edit/preview overlay layer.
        # CachedPaint = False marks it as a "tracking" layer: the tile cache
        # is bypassed so InvalidateTopmost redraws it immediately on each step.
        self.edtLayer = pdk.TGIS_LayerVector()
        self.edtLayer.CS = self.GIS.CS                            # Match viewer CRS
        self.edtLayer.CachedPaint = False                         # Tracking layer
        self.edtLayer.Params.Area.Pattern = pdk.TGIS_BrushStyle().Clear   # Transparent fill
        self.edtLayer.Params.Area.OutlineColor = pdk.TGIS_Color().Red     # Red outline

        self.GIS.Add(self.edtLayer)
        self.GIS.Unlock()

    # -------------------------------------------------------------------------
    # Affine transform helpers
    # -------------------------------------------------------------------------

    def TransformSelectedShape(self, shp, xx, yx, xy, yy, dx, dy):
        """
        Core affine transform applied to a shape's geometry.

        Applies a 3x3 affine matrix centred on the shape's centroid so that
        rotate and scale operations appear to happen around the shape itself
        rather than around the map coordinate origin.

        Matrix convention::

            x' = x*xx + y*xy + dx
            y' = x*yx + y*yy + dy
            z' = z  (z is preserved)

        Passing the centroid as the pivot tells the DK to translate the shape
        to the origin, apply the matrix, then translate back.

        After updating the geometry, ``InvalidateTopmost`` redraws only the
        topmost (preview) layer, which avoids a costly full-map repaint.

        :param shp: The shape to transform (lives in edtLayer).
        :param xx:  Matrix element [0,0] - x-to-x factor.
        :param yx:  Matrix element [1,0] - x-to-y factor.
        :param xy:  Matrix element [0,1] - y-to-x factor.
        :param yy:  Matrix element [1,1] - y-to-y factor.
        :param dx:  Translation along X in map units.
        :param dy:  Translation along Y in map units.
        """
        if shp is None:
            return

        # Compute the geometric centroid so the transform pivots at the shape centre
        centroid = shp.Centroid()

        # Apply the affine matrix:
        # x' = x*xx + y*xy + dx
        # y' = x*yx + y*yy + dy
        # z' = z
        shp.Transform(pdk.TGIS_Utils.GisPoint3DFrom2D(centroid),
                      xx, yx, 0,   # row 0 of 3x3 matrix
                      xy, yy, 0,   # row 1
                      0,  0, 1,    # row 2 (z pass-through)
                      dx, dy, 0,   # translation vector
                      False)       # do not recalculate layer extent yet

        # Refresh only the preview layer for performance
        self.GIS.InvalidateTopmost()

    def RotateSelectedShape(self, shp, angle):
        """
        Rotates the shape by *angle* radians around its centroid.

        Standard 2-D rotation matrix::

            | cos(a)  sin(a) |
            |-sin(a)  cos(a) |

        A positive angle rotates counter-clockwise in standard map orientation.

        :param shp:   The shape to rotate.
        :param angle: Rotation angle in radians.
        """
        self.TransformSelectedShape(
            shp,
            math.cos(angle), math.sin(angle),   # row 0
            -math.sin(angle), math.cos(angle),  # row 1
            0, 0                                 # no additional translation
        )

    def ScaleSelectedShape(self, shp, x, y):
        """
        Scales the shape by independent factors along each axis.

        Values greater than 1 enlarge; values between 0 and 1 shrink.
        The centroid is used as the pivot so the shape stays centred.

        :param shp: The shape to scale.
        :param x:   Scale factor along X.
        :param y:   Scale factor along Y.
        """
        self.TransformSelectedShape(
            shp,
            x, 0,   # x scale on diagonal
            0, y,   # y scale on diagonal
            0, 0    # no translation
        )

    def TranslateSelectedShape(self, shp, x, y):
        """
        Translates (moves) the shape by the given map-coordinate offset.

        The identity submatrix leaves all coordinates unchanged; only the
        translation vector (dx, dy) produces movement.

        :param shp: The shape to move.
        :param x:   Translation along X in map units.
        :param y:   Translation along Y in map units.
        """
        self.TransformSelectedShape(
            shp,
            1, 0,  # identity: x unchanged
            0, 1,  # identity: y unchanged
            x, y   # pure translation
        )

    # -------------------------------------------------------------------------
    # Mouse event handlers
    # -------------------------------------------------------------------------

    def GIS_MouseMove(self, _sender, _shift, x, y):
        """
        Responds to mouse movement over the viewer.

        While ``handleMouseMove`` is True (a shape is selected), dispatches
        incremental affine transforms to the preview shape in ``edtLayer``.

        - Rotate:    horizontal pixel delta -> radians (pi/180 * deltaX).
        - Scale:     current screen position / previous screen position per axis.
        - Translate: map-coordinate delta since the last event.
        """
        if self.edtShape is None:
            return

        if self.handleMouseMove:
            # Convert current screen position to map coordinates
            ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

            if self.rbRotate.Checked:
                # 1 pixel of horizontal movement = 1 degree of rotation
                self.RotateSelectedShape(self.edtShape, math.pi / 180 * (int(x) - self.prevX))

            elif self.rbScale.Checked:
                # Guard against division-by-zero at the very first event
                if (self.prevX != 0) and (self.prevY != 0):
                    # Scale factor = current position / previous position (per axis)
                    self.ScaleSelectedShape(self.edtShape, float(x / self.prevX), float(y / self.prevY))

            elif self.rbMove.Checked:
                # Delta in map units between this event and the last
                self.TranslateSelectedShape(self.edtShape, (ptg.X - self.prevPtg.X), (ptg.Y - self.prevPtg.Y))

            # Update previous-position tracking for the next incremental step
            self.prevPtg.X = ptg.X
            self.prevPtg.Y = ptg.Y
            self.prevX = x
            self.prevY = y

    def GIS_MouseUp(self, _sender, _button, _shift, x, y):
        """
        Handles both the shape-selection click (first mouse-up) and the
        geometry-commit click (second mouse-up).

        **First click (currShape is None):**
          - ``GIS.Locate`` finds the nearest shape within a 5-pixel tolerance.
          - ``MakeEditable`` returns a writable proxy of the source shape.
          - A copy is placed in the preview layer for live editing.
          - ``handleMouseMove`` is toggled to start processing transform events.

        **Second click (currShape is not None):**
          - ``CopyGeometry`` writes the final geometry back to the source shape.
          - ``RevertAll`` clears the preview layer.
          - ``InvalidateWholeMap`` forces a full repaint.
        """
        self.lbHint.Caption = "No selected shape. Select shape"

        # --- COMMIT path: a shape was already selected and being edited ---
        if self.currShape:
            # Write the transformed preview geometry back to the real layer
            self.currShape.CopyGeometry(self.edtShape)

            # Discard all shapes in the preview layer
            self.edtLayer.RevertAll()

            self.currShape = None
            self.edtShape = None

            # Full repaint to show the committed shape in its real layer style
            self.GIS.InvalidateWholeMap()
            self.handleMouseMove = False
            return

        # Guard: no layers or wrong interaction mode
        if self.GIS.IsEmpty:
            return
        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        # --- SELECT path: pick a shape from the map ---

        # Convert screen click to map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # Locate the nearest shape; tolerance = 5 screen pixels in map units
        shp = self.GIS.Locate(ptg, 5 / self.GIS.Zoom)
        if shp is None:
            return

        # MakeEditable returns a proxy that allows geometry modification
        self.currShape = shp.MakeEditable()

        # Place a copy of the shape into the overlay layer for live editing
        self.edtShape = self.edtLayer.AddShape(self.currShape.CreateCopy())

        self.lbHint.Caption = f"Selected shape: {self.currShape.Uid}. Click to commit changes"

        # Seed previous-position state for the first incremental delta
        self.prevPtg.X = ptg.X
        self.prevPtg.Y = ptg.Y
        self.prevX = x
        self.prevY = y

        # Toggle: start accepting mouse-move transforms
        self.handleMouseMove = not self.handleMouseMove

    # -------------------------------------------------------------------------
    # Radio button change handlers (mode switching)
    # -------------------------------------------------------------------------

    def rbRotate_change(self, _sender):
        """
        Switches to Rotate mode.  If a shape is currently being edited,
        cancels the edit session so the user starts fresh in the new mode.
        """
        if not self.rbRotate.Checked:
            return

        self.lbHint.Caption = 'Select shape to start rotating'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False

    def rbScale_change(self, _sender):
        """
        Switches to Scale mode.  Cancels any in-progress edit session.
        """
        if not self.rbScale.Checked:
            return

        self.lbHint.Caption = 'Select shape to start scaling'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False

    def rbMove_change(self, _sender):
        """
        Switches to Move (translate) mode.  Cancels any in-progress edit session.
        """
        if not self.rbMove.Checked:
            return

        self.lbHint.Caption = 'Select shape to start moving'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False


def main():
    """Application entry point: create and run the form."""
    frm = ShapeOperationsForm(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
