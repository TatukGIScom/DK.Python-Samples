# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Measure Sample - TatukGIS DK11 Python (PDK)
#
# Demonstrates how to interactively measure distance (polyline length) and
# area (polygon area) on a map using the built-in shape editor.
#
# Key concepts shown:
#   - Building a cross-platform UI with TGIS_PvlForm and TGIS_PvlButton/Panel
#     widgets (the TatukGIS Python Visual Layer, which abstracts the OS GUI).
#   - Creating an in-memory TGIS_LayerVector (named "Measure") to hold the
#     temporary measurement shape rendered on top of the background basemap.
#   - Using GIS.Editor to create and track Arc (polyline) and Polygon shapes
#     as the user places vertices with the mouse.
#   - Assigning GIS.EditorChangeEvent and GIS.OnMouseDown callbacks to respond
#     to editor updates and to initiate new shapes on the first click.
#   - Retrieving the measurement layer by name via GIS.Get("Measure") in the
#     mouse handler, which avoids holding a stale reference.
#   - Using TGIS_CSUnits.AsLinear / AsAreal to format raw metre /
#     square-metre values into human-readable strings (e.g. "12.3 km").
#   - EPSG 904201 = TatukGIS standard metric unit set. The unit instance is
#     resolved per EditorChangeEvent call to keep the function self-contained.
#   - EPSG 4326 (WGS-84 geographic) assigned to the drawing layer ensures
#     that LengthCS() / AreaCS() return geodetically correct values.
#   - GIS.Mode transitions:
#       Select  - waiting for the first click that anchors the shape
#       Edit    - the editor is collecting additional vertices
#       Drag    - idle / panning (default)
# =============================================================================

import tatukgis_pdk as pdk


class MeasureForm(pdk.TGIS_PvlForm):
    """Main application window for the Measure sample.

    Inherits from TGIS_PvlForm which provides the cross-platform window and
    coordinate-system-aware layout helpers (Place).
    """

    # Class-level mode flags — exactly one should be True while measuring.
    isLine = False    # Polyline (distance) measurement is active
    isPolygon = False # Polygon (area) measurement is active

    def __init__(self, _owner):
        # --- Window setup ---
        self.Caption = "Measure - TatukGIS DK Sample"
        self.ClientWidth = 686
        self.ClientHeight = 466
        # Show event wires up the map after the window is fully constructed.
        self.OnShow = self.form_show

        # --- Toolbar panel (top strip) ---
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(662, 33, None, 12, None, 5)

        # "By line" button: activates polyline distance measurement.
        self.btnLine = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnLine.Place(75, 23, None, 16, None, 5)
        self.btnLine.Caption = "By line"
        self.btnLine.OnClick = self.btnLine_click

        # "By Polygon" button: activates polygon area measurement.
        self.btnPolygon = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPolygon.Place(75, 23, None, 100, None, 5)
        self.btnPolygon.Caption = "By Polygon"
        self.btnPolygon.OnClick = self.btnPolygon_click

        # "Clear" button: discards the current shape and returns to drag mode.
        self.btnClear = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnClear.Place(75, 23, None, 184, None, 5)
        self.btnClear.Caption = "Clear"
        self.btnClear.OnClick = self.btnClear_click

        # --- Results panel (right side) ---
        # Anchored to the top, right, and bottom so it stays visible on resize.
        self.panel_controls = pdk.TGIS_PvlPanel(self.Context)
        self.panel_controls.Place(200, 400, None, 474, None, 45)
        self.panel_controls.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Length output widgets
        self.lblLength = pdk.TGIS_PvlLabel(self.panel_controls.Context)
        self.lblLength.Place(43, 13, None, 3, None, 16)
        self.lblLength.Caption = "Length:"

        self.edtLength = pdk.TGIS_PvlEdit(self.panel_controls.Context)
        self.edtLength.Place(191, 20, None, 6, None, 32)

        # Area output widgets (only populated in polygon mode)
        self.lblArea = pdk.TGIS_PvlLabel(self.panel_controls.Context)
        self.lblArea.Place(43, 13, None, 3, None, 83)
        self.lblArea.Caption = "Area:"

        self.edtArea = pdk.TGIS_PvlEdit(self.panel_controls.Context)
        self.edtArea.Place(191, 20, None, 6, None, 99)

        # --- TatukGIS viewer ---
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 15
        self.GIS.Top = 45
        self.GIS.Width = 453
        self.GIS.Height = 396
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        # EditorChangeEvent fires after every vertex placement; used to refresh
        # the measurement display.
        self.GIS.EditorChangeEvent = self.GIS_EditorChangeEvent
        # OnMouseDown fires on the initial click to start a new shape.
        self.GIS.OnMouseDown = self.GIS_MouseDown

        # --- Status bar (bottom strip) ---
        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(600, 23, None, 0, None, 443)
        self.status_bar.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.lblMsg.Place(300, 19, None, 12, None, 0)
        self.lblMsg.Caption = "Use left mouse button to measure"

    def form_show(self, _sender):
        """Loads the basemap and prepares the in-memory measurement layer.

        Called once when the form first becomes visible.  Uses a try/finally
        block to ensure Unlock() is always called even if Open() raises an
        exception.
        """
        # Lock suspends rendering while we make multiple changes.
        self.GIS.Lock()
        try:
            # Load the world outline shapefile as the background basemap.
            self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                          + "/World/WorldDCW/world.shp")

            # Create an in-memory vector layer to hold the measurement shape.
            # The name "Measure" allows GIS_MouseDown to retrieve it later via
            # GIS.Get("Measure") without keeping a stale reference.
            ll = pdk.TGIS_LayerVector()
            ll.Name = "Measure"
            ll.Params.Line.Color = pdk.TGIS_Color.Red  # Red for high visibility
            ll.Params.Line.Width = 25                   # Thick line for easy reading

            # Assign WGS-84 geographic CS (EPSG 4326).
            # With a geographic CS, LengthCS() and AreaCS() compute geodetically
            # correct distances on the Earth's surface.
            ll.SetCSByEPSG(4326)

            self.GIS.Add(ll)
            # Restrict scrolling to the initial full-world extent.
            self.GIS.RestrictedExtent = self.GIS.Extent
        finally:
            self.GIS.Unlock()

        # Widen the rubber-band preview line for better visibility.
        self.GIS.Editor.EditingLinesStyle.PenWidth = 10
        # AfterActivePoint draws a live preview segment from the last placed
        # vertex to the current cursor position.
        self.GIS.Editor.Mode = pdk.TGIS_EditorMode().AfterActivePoint

    def btnLine_click(self, _sender):
        """Activates polyline distance measurement mode.

        Discards any in-progress shape, clears output fields, and sets the
        viewer to Select mode so the next click starts a new Arc shape.
        """
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        # Only the length field will be updated; area field stays empty.
        self.isPolygon = False
        self.isLine = True

        # Waiting for the first click that anchors the polyline's initial vertex.
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnPolygon_click(self, _sender):
        """Activates polygon area measurement mode.

        Discards any in-progress shape, clears output fields, and sets the
        viewer to Select mode so the next click starts a new Polygon shape.
        """
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        # Both perimeter length and enclosed area will be displayed.
        self.isPolygon = True
        self.isLine = False

        # Waiting for the first click that anchors the polygon's initial vertex.
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnClear_click(self, _sender):
        """Clears the current measurement shape and returns to drag/pan mode."""
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        self.isLine = False
        self.isPolygon = False

        # Return to normal pan/zoom interaction.
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def GIS_EditorChangeEvent(self, _sender):
        """Recomputes and displays the current measurement after every editor change.

        Fired by the shape editor after each vertex placement or cursor move.
        Resolves the unit formatter on each call so units could easily be made
        switchable without maintaining additional state.
        """
        # Resolve metric unit formatter: EPSG 904201 = km / km².
        unit = pdk.TGIS_Utils().CSUnitsList.ByEPSG(904201)

        if self.GIS.Editor.CurrentShape is not None:
            if self.isLine:
                # LengthCS() returns the geodetic cumulative length in metres.
                # AsLinear formats it with the unit label (e.g. "5.3 km").
                self.edtLength.Text = unit.AsLinear(self.GIS.Editor.CurrentShape.LengthCS(), True)
            elif self.isPolygon:
                # For a polygon, LengthCS() is the perimeter.
                self.edtLength.Text = unit.AsLinear(self.GIS.Editor.CurrentShape.LengthCS(), True)
                # AreaCS() returns the geodetic enclosed area in square metres.
                # "%s²" inserts the unit abbreviation followed by a superscript 2.
                self.edtArea.Text = unit.AsAreal(self.GIS.Editor.CurrentShape.AreaCS(), True, "%s²")

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        """Handles the first mouse press that starts a new measurement shape.

        Parameters
        ----------
        _sender : object
            The viewer control (unused).
        _button : int
            Mouse button identifier (unused; left click is assumed).
        _shift  : int
            Shift/Ctrl/Alt modifier flags (unused).
        x, y    : float
            Screen pixel coordinates of the mouse press.

        Once the shape is created the viewer switches to Edit mode and all
        subsequent vertex placements are handled internally by the editor.
        """
        # If the editor is already active, do not create a second shape.
        if self.GIS.Mode == pdk.TGIS_ViewerMode().Edit:
            return

        # Retrieve the measurement layer by name; bail out if it is not yet loaded.
        ll = self.GIS.Get("Measure")
        if ll is None:
            return

        # Convert the screen pixel position to geographic map coordinates.
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        if self.isLine:
            # Arc = polyline; LengthCS() sums all segment lengths geodetically.
            self.GIS.Editor.CreateShape(ll, ptg, pdk.TGIS_ShapeType().Arc)
        elif self.isPolygon:
            # Polygon; both AreaCS() and LengthCS() (perimeter) are available.
            self.GIS.Editor.CreateShape(ll, ptg, pdk.TGIS_ShapeType().Polygon)

        # Hand vertex control to the editor for all subsequent mouse events.
        self.GIS.Mode = pdk.TGIS_ViewerMode().Edit


def main():
    """Entry point: creates the form and starts the GUI event loop."""
    frm = MeasureForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
