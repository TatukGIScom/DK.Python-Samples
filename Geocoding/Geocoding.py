# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# GeoCoding Sample - Python (TatukGIS PDK)
# =========================================
# Demonstrates address geocoding and shortest-path routing using TatukGIS DK11.
#
# Geocoding translates a human-readable address string (e.g. "Chrysler 1345")
# into geographic coordinates by matching it against street-range attribute
# fields stored in a vector layer.  The TGIS_Geocoding class performs this
# matching entirely on the client side using the loaded shapefile — no
# external service is needed.
#
# Routing finds the shortest path between two geocoded points using
# TGIS_ShortestPath, which builds an in-memory Dijkstra graph from the road
# network.  The resulting path segments are visualised by copying them into a
# separate in-memory "RouteDisplay" layer rendered in red, with green/red
# point markers for the start and end positions.
#
# Key concepts shown:
#   - Creating a TGIS_PvlForm-based application window with the PDK UI toolkit
#   - Opening a TatukGIS project (.ttkproject) and retrieving a named layer
#   - Constructing TGIS_Geocoding with TIGER/Line address-range field mappings
#   - Using TGIS_Geocoding.Parse to resolve typed addresses to coordinates
#   - Building a TGIS_ShortestPath graph with per-link-type cost modifiers
#   - Providing a doLinkType callback to classify road segments by MTFCC code
#   - Drawing route results and address markers into a TGIS_LayerVector overlay
#   - Displaying a TGIS_PvlControlScale bar linked to the viewer
#
# Data used:
#   California.TTKPROJECT — a TatukGIS project referencing US Census TIGER/Line
#   street data.  Relevant attribute fields:
#     FULLNAME  — full street name
#     LFROMADD  — address range start, left side of street
#     LTOADD    — address range end, left side of street
#     RFROMADD  — address range start, right side of street
#     RTOADD    — address range end, right side of street
#     MTFCC     — MAF/TIGER Feature Class Code; "S1400"+ = local/residential road
# =============================================================================

import tatukgis_pdk as pdk  # TatukGIS Python Developer Kernel


def doLinkType(_sender, shape, ttype):
    """
    Classifies a road segment as highway (link type 0) or local road (link type 1).

    Called by TGIS_ShortestPath for every arc during graph construction.
    The US Census MTFCC code "S1400" and above identifies local/residential
    streets, alleys, and service roads.  Codes below "S1400" are interstates,
    US routes, state routes, and other major roads.

    The routing engine multiplies each segment's traversal cost by
    CostModifiers[linkType].  A slider value of 10 for highways makes major roads
    nearly free, routing the path onto them preferentially.

    Parameters:
        _sender: event source (unused)
        shape:   the arc (road segment) being classified
        ttype:   a mutable wrapper; set ttype.Value to the link type integer
    """
    if shape.GetField('MTFCC') >= 'S1400':
        # MTFCC >= "S1400" → local/residential road
        ttype.Value = 1
    else:
        # MTFCC < "S1400" → highway or major road
        ttype.Value = 0


class GeocodingForm(pdk.TGIS_PvlForm):
    """
    Main application window for the GeoCoding & Routing sample.

    Inherits from TGIS_PvlForm which provides a cross-platform windowing
    abstraction used by TatukGIS Python samples.  The window hosts a
    TGIS_ViewerWnd map viewer on the left and a controls panel on the right.

    Instance variables set during __init__:
        layerSrc   -- source streets layer loaded from the project file
        layerRoute -- in-memory layer used to display the computed route
        rtrObj     -- TGIS_ShortestPath Dijkstra routing engine
        geoObj     -- TGIS_Geocoding address-to-coordinate engine
    """

    layerSrc: pdk.TGIS_LayerVector
    layerRoute: pdk.TGIS_LayerVector
    rtrObj: pdk.TGIS_ShortestPath
    geoObj = pdk.TGIS_Geocoding

    def __init__(self, _owner):
        # Configure the form window dimensions and title.
        self.Caption = "Geocoding - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466

        # Register the form_show callback; called when the window first becomes
        # visible, deferring heavy data loading until after the UI is ready.
        self.OnShow = self.form_show

        # ------------------------------------------------------------------
        # Routing parameters group box — occupies the right-hand side.
        # Anchors keep it attached to the top-right corner on resize.
        # ------------------------------------------------------------------
        self.groupBox1 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox1.Place(188, 249, None, 410, None, 0)
        self.groupBox1.Caption = "Routing parameters"
        self.groupBox1.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Local-roads preference slider (1 = neutral, 10 = strongly prefer local).
        self.lblSmallRoads = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblSmallRoads.Place(100, 13, None, 24, None, 24)
        self.lblSmallRoads.Caption = "Prefer local roads"

        self.trkSmallRoads = pdk.TGIS_PvlTrackBar(self.groupBox1.Context)
        self.trkSmallRoads.Place(161, 25, None, 16, None, 40)
        self.trkSmallRoads.Minimum = 1
        self.trkSmallRoads.Maximum = 10
        self.trkSmallRoads.Position = 1  # Default: slight preference for local roads

        # Highway preference slider (5 = moderate, 10 = strongly prefer highways).
        self.lblHighways = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblHighways.Place(90, 13, None, 24, None, 72)
        self.lblHighways.Caption = "Prefer Highway"

        self.trkHighways = pdk.TGIS_PvlTrackBar(self.groupBox1.Context)
        self.trkHighways.Place(161, 25, None, 16, None, 88)
        self.trkHighways.Minimum = 1
        self.trkHighways.Maximum = 10
        self.trkHighways.Position = 5  # Default: moderate highway preference

        # From address input — the start point for geocoding and routing.
        self.lblAddrFrom = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblAddrFrom.Place(59, 13, None, 24, None, 120)
        self.lblAddrFrom.Caption = "From"

        self.edtAddrFrom = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtAddrFrom.Place(145, 20, None, 24, None, 133)
        self.edtAddrFrom.Text = "Chrys 1345"  # Example: partial street name + number

        # Find Address button — resolves the From address without routing.
        self.btnResolve = pdk.TGIS_PvlButton(self.groupBox1.Context)
        self.btnResolve.Place(75, 23, None, 94, None, 155)
        self.btnResolve.Caption = "Find Address"
        self.btnResolve.OnClick = self.btnResolve_click

        # To address input — the end point for routing.
        self.lblAddrTo = pdk.TGIS_PvlLabel(self.groupBox1.Context)
        self.lblAddrTo.Place(145, 20, None, 24, None, 172)
        self.lblAddrTo.Caption = "To"

        self.edtAddrTo = pdk.TGIS_PvlEdit(self.groupBox1.Context)
        self.edtAddrTo.Place(145, 20, None, 24, None, 188)
        self.edtAddrTo.Text = "wash"  # Example: partial street name

        # Find Route button — geocodes both addresses and computes the route.
        self.btnRoute = pdk.TGIS_PvlButton(self.groupBox1.Context)
        self.btnRoute.Place(75, 22, None, 94, None, 210)
        self.btnRoute.Caption = "Find Route"
        self.btnRoute.OnClick = self.btnRoute_click

        # Read-only text area for turn-by-turn directions output.
        self.memRoute = pdk.TGIS_PvlMemo(self.groupBox1.Context)
        self.memRoute.Place(188, 227, None, 3, None, 240)
        self.memRoute.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # ------------------------------------------------------------------
        # TGIS_ViewerWnd — the main map viewer component.
        # Anchored to all four sides so it fills the available space.
        # ------------------------------------------------------------------
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 414
        self.GIS.Height = 480
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom  # Default to rubber-band zoom interaction

        # Scale-bar overlay linked to the viewer — displays real-world distances.
        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Place(145, 25, None, 8, None, 8)

    def form_show(self, _sender):
        """
        Called when the form becomes visible for the first time.

        Opens the California TatukGIS project and initialises the geocoding and
        routing engines.  The viewer is locked during setup to suppress
        intermediate redraws — the standard DK pattern for batch updates.

        TGIS_Utils.GisSamplesDataDirDownload() returns the path to the TatukGIS
        sample data directory (downloaded separately from the SDK installer).
        """
        self.GIS.Lock()

        # Open the TatukGIS project which contains the California street data.
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Projects/California.TTKPROJECT")

        # Retrieve the streets vector layer by name so the geocoding and
        # routing engines can operate on its shape and attribute data.
        self.layerSrc = self.GIS.Get("streets")

        if self.layerSrc is None:
            return

        # Zoom to the full extent of the street network on startup.
        self.GIS.VisibleExtent = self.layerSrc.Extent

        # ------------------------------------------------------------------
        # Create an in-memory overlay layer for route visualisation.
        # UseConfig = False prevents the DK from persisting a style config file.
        # Red line (Width = -2, negative = device pixels) and 1-px marker outline.
        # The layer's CS must match the viewer's CS.
        # ------------------------------------------------------------------
        self.layerRoute = pdk.TGIS_LayerVector()
        self.layerRoute.UseConfig = False

        self.layerRoute.Params.Line.Color = pdk.TGIS_Color().Red
        self.layerRoute.Params.Line.Width = -2
        self.layerRoute.Params.Marker.OutlineWidth = 1
        self.layerRoute.Name = 'RouteDisplay'
        self.layerRoute.CS = self.GIS.CS
        self.GIS.Add(self.layerRoute)

        # ------------------------------------------------------------------
        # Configure the geocoding engine with TIGER/Line field mappings.
        #   Offset    — distance along the segment to place the geocoded point
        #               (avoids placing it exactly on a road node).
        #   RoadName  — attribute field containing the full street name.
        #   LFrom/LTo — address number range, left side of the street.
        #   RFrom/RTo — address number range, right side of the street.
        #               TIGER/Line uses these four fields to interpolate the
        #               house number position along the segment.
        # ------------------------------------------------------------------
        self.geoObj = pdk.TGIS_Geocoding(self.layerSrc)
        self.geoObj.Offset = 0.0001
        self.geoObj.RoadName = "FULLNAME"
        self.geoObj.LFrom = "LFROMADD"
        self.geoObj.LTo = "LTOADD"
        self.geoObj.RFrom = "RFROMADD"
        self.geoObj.RTo = "RTOADD"

        # ------------------------------------------------------------------
        # Configure the routing engine.
        #   LinkTypeEvent — callback classifying each segment (see doLinkType).
        #   LoadTheData   — builds the Dijkstra graph from all arcs in layerSrc.
        #   RoadName      — field used to label each step in the directions.
        # ------------------------------------------------------------------
        self.rtrObj = pdk.TGIS_ShortestPath(self.GIS)
        self.rtrObj.LinkTypeEvent = doLinkType
        self.rtrObj.LoadTheData(self.layerSrc)
        self.rtrObj.RoadName = "FULLNAME"

        self.GIS.Unlock()
        # Uncomment to display scale bar in miles (EPSG 9035):
        # self.GIS_ControlScale.Units = pdk.TGIS_Utils().CSUnitsList.ByEPSG(9035)

    def btnRoute_click(self, _sender):
        """
        Handles the Find Route button click.
        Geocodes both addresses, computes the shortest path between them,
        and displays the route as a red line with turn-by-turn directions.

        Cost modifiers derived from the highway/local-road sliders are applied
        before routing so the user can tune road-type preference at runtime.
        The formula maps slider values 1–10 to cost multipliers 1.0–~0.09
        (lower = cheaper = preferred by the router).

        The Compass property of each route item encodes turn direction:
          0 = straight, 1..3 = right (slight/right/sharp), 4 = U-turn,
          -1..-3 = left (slight/left/sharp), -4 = left U-turn.
        Consecutive steps on the same named street are suppressed.
        """
        # Apply slider-derived cost modifiers.
        # CostModifiers(0, x) sets the highway multiplier; (1, x) sets local road.
        self.rtrObj.CostModifiers(0, 1 - 1/11.0 * self.trkHighways.Position)
        self.rtrObj.CostModifiers(1, 1 - 1/11.0 * self.trkSmallRoads.Position)

        # Geocode the start address.
        # Parse() returns the number of matching candidates found.
        res = self.geoObj.Parse(self.edtAddrFrom.Text, True, True)
        if res <= 0:
            self.edtAddrFrom.Caption = " ???"

        # Abort if the start address could not be resolved.
        if res <= 0:
            return
        pt_a = self.geoObj.Point(0)   # Geocoded start coordinate

        # Geocode the end address.
        res = self.geoObj.Parse(self.edtAddrTo.Text, True, True)
        if res > 0:
            self.edtAddrTo.Text = self.geoObj.Query(0)  # Refine to canonical name
        else:
            self.edtAddrTo.Text = "???"

        # Abort if the end address could not be resolved.
        if res <= 0:
            return
        pt_b = self.geoObj.Point(0)   # Geocoded end coordinate

        # UpdateTheData refreshes the graph (e.g. after data edits).
        # Find() computes the shortest path; Unproject converts viewer display
        # coordinates to the layer's native coordinate system.
        self.rtrObj.UpdateTheData()
        self.rtrObj.Find(self.layerRoute.Unproject(pt_a), self.layerRoute.Unproject(pt_b))

        self.memRoute.Clear()
        old_name = ""   # Track last street name to suppress duplicate direction lines

        # Build turn-by-turn directions text.
        ang = ""
        for i in range(self.rtrObj.ItemsCount-1):
            item = self.rtrObj.Items(i)

            # Map the numeric Compass value to a readable direction abbreviation.
            if item.Compass == 0:  ang = "FWD  "
            if item.Compass == 1:  ang = "RIGHT"   # Slight right
            if item.Compass == 2:  ang = "RIGHT"   # Right
            if item.Compass == 3:  ang = "RIGHT"   # Sharp right
            if item.Compass == 4:  ang = "BACK "   # U-turn
            if item.Compass == -1: ang = "LEFT "   # Slight left
            if item.Compass == -2: ang = "LEFT "   # Left
            if item.Compass == -3: ang = "LEFT "   # Sharp left
            if item.Compass == -4: ang = "BACK "   # Left U-turn

            # Suppress consecutive items on the same named street.
            if old_name == item.Name:
                continue

            old_name = item.Name
            ang = ang + " " + item.Name
            self.memRoute.AppendLine(ang)

        # Clear the route display layer and repopulate with the new path.
        self.layerRoute.RevertShapes()

        # Copy each route segment from the source layer into the display layer.
        for i in range(self.rtrObj.ItemsCount - 1):
            item = self.rtrObj.Items(i)

            shp = item.Layer.GetShape(item.Uid)
            if shp is None:
                continue
            self.layerRoute.AddShape(shp)
            if i == 0:
                self.layerRoute.Extent = shp.Extent  # Seed the bounding extent

        # Place a green point marker at the start position (pt_a).
        # Lock/Unlock brackets shape modification to maintain internal extent.
        shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pt_a)
        shp.Params.Marker.Color = pdk.TGIS_Color().Green
        shp.Unlock()

        # Place a red (default colour) point marker at the end position (pt_b).
        shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pt_b)
        shp.Unlock()

        # Zoom to the route bounding box, pulling back slightly (0.7×) for context.
        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerRoute.Extent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()

    def btnResolve_click(self, _sender):
        """
        Handles the Find Address button click.
        Geocodes the address typed in edtAddrFrom and highlights all matching
        street segments on the map with a green point marker at each geocoded
        coordinate.

        Parse() returns the number of matching candidates found in the street data.
        Each candidate provides Query(i) (canonical name), Uid(i) (primary segment
        ID), UidEx(i) (complementary opposite-side segment ID), and Point(i)
        (interpolated coordinate for the house number along the matched segment).
        """
        if self.geoObj is None:
            return

        # Clear any previously displayed route or address highlights.
        self.layerRoute.RevertShapes()

        # Parse returns the number of matches; r is the last valid index.
        # Append "???" caption if no match was found.
        r = self.geoObj.Parse(self.edtAddrFrom.Text, True, True) - 1
        if r < 0:
            self.edtAddrFrom.Caption = "???"

        for i in (0, r):
            # Refine the text field to the canonical name of each matched street.
            self.edtAddrFrom.Text = self.geoObj.Query(i)
            self.GIS.ProcessMessages()  # Allow the UI to refresh between results

            # Add the primary matching segment to the route display layer.
            shp = self.layerSrc.GetShape(self.geoObj.Uid(i))
            self.layerRoute.AddShape(shp)

            # Seed the bounding extent from the first matched segment.
            if i == 0:
                self.layerRoute.Extent = shp.ProjectedExtent

            # Add the complementary (opposite-side) segment if available.
            # UidEx returns the ID of the adjacent segment for the same address range.
            shp = self.layerSrc.GetShape(self.geoObj.UidEx(i))
            if shp is not None:
                self.layerRoute.AddShape(shp)

            # Place a green marker at the interpolated geocoded coordinate.
            # CS.FromCS converts from the source layer's CS to the route layer's CS.
            shp = self.layerRoute.CreateShape(pdk.TGIS_ShapeType().Point)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            shp.AddPoint(self.layerRoute.CS.FromCS(self.layerSrc.CS, self.geoObj.Point(i)))
            shp.Params.Marker.Color = pdk.TGIS_Color().Green
            shp.Unlock()

        # Zoom to the matched results with a slight zoom-out factor for context.
        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerRoute.ProjectedExtent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()


def main():
    """
    Application entry point.
    Creates the form window, shows it, and starts the PDK event loop.
    RunPvl blocks until the window is closed.
    """
    frm = GeocodingForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
