# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Triangulation Sample – Demonstrates Delaunay triangulation and Voronoi diagrams.
#
# This sample opens a point shapefile (Polish cities) and uses two specialised
# TGIS_LayerVector subclasses from the TatukGIS PDK (Python DK) to compute
# geometric structures derived from the point distribution:
#
#   Delaunay Triangulation
#     Connects input points into triangles such that no point lies inside the
#     circumscribed circle of any triangle.  Produces a TIN (Triangulated
#     Irregular Network) suitable for surface modelling and proximity analysis.
#
#   Voronoi Diagram
#     Partitions the plane into one region per input point, where each region
#     contains all locations closer to that point than to any other input point.
#     The Voronoi diagram is the geometric dual of the Delaunay triangulation.
#
# After generation the result layer is colour-graduated by polygon area
# (GIS_AREA attribute) over a white-to-red (Voronoi) or white-to-blue (Delaunay)
# gradient rendered across 10 equal-interval zones.  This highlights relative
# cell / triangle area variation across the study region.
#
# User interaction:
#   - Click a point on the map to display its attributes in the Attributes panel
#   - Radio buttons select Delaunay vs Voronoi mode before generation
#   - "Generate" adds the result layer; duplicate layer names are rejected
#   - Toolbar buttons provide Full Extent, Zoom In, and Zoom Out navigation
#
# Key TatukGIS PDK classes used:
#   TGIS_LayerDelaunay       – generates and stores a Delaunay triangulation
#   TGIS_LayerVoronoi        – generates and stores a Voronoi diagram
#   TGIS_LayerVector         – base class; ImportLayer() copies source point data
#   TGIS_PvlControlAttributes – attribute display panel (shape property viewer)
#   TGIS_PvlControlLegend    – layer legend / style control panel
#   TGIS_ViewerWnd           – map viewer widget
#   TGIS_PvlForm             – base class for PDK application forms
# =============================================================================

import tatukgis_pdk as pdk


class TriangulationForm(pdk.TGIS_PvlForm):
    """
    Main form for the Triangulation sample application.

    Demonstrates Delaunay triangulation and Voronoi diagram generation using
    TGIS_LayerDelaunay and TGIS_LayerVoronoi.  The result layer is
    colour-graduated by polygon area (GIS_AREA attribute) to give an immediate
    visual impression of size variation across the plane.

    Layout
    ------
    - Top toolbar : Full Extent / Zoom In / Zoom Out buttons
    - Left area   : Map viewer (TGIS_ViewerWnd), fills available space
    - Right column: Attribute panel, mode radio buttons, layer name field,
                    Generate button, legend panel
    """

    def __init__(self, _owner):
        """
        Build the form layout programmatically.

        All widgets are created and positioned here.  Actual data loading is
        deferred to form_show() so the viewer is fully initialised before
        Open() is called.
        """
        self.Caption = "Triangulation - TatukGIS DK Sample"
        self.ClientWidth = 604
        self.ClientHeight = 404
        self.OnShow = self.form_show  # Defer data load until form is visible

        # --- Toolbar panel (top strip) ---
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Full Extent button – zooms to fit all layers
        self.btnFullExtent = pdk.TGIS_PvlButton(self.Context)
        self.btnFullExtent.Place(73, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        # Zoom In button – doubles the current zoom factor
        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomIn.Place(75, 22, None, 79, None, 3)
        self.btnZoomIn.Caption = "ZoomIn"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        # Zoom Out button – halves the current zoom factor
        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomOut.Place(75, 22, None, 155, None, 3)
        self.btnZoomOut.Caption = "ZoomOut"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        # --- Attribute panel (right column, top) ---
        # Displays the attribute table row for the shape most recently clicked on the map
        self.GIS_Attributes = pdk.TGIS_PvlControlAttributes(self.Context)
        self.GIS_Attributes.Place(180, 141, None, 424, None, 28)
        self.GIS_Attributes.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Right,
                                       pdk.TGIS_PvlAnchor().Bottom)

        # --- Result group box (right column, middle) ---
        # Contains the mode radio buttons, layer name field, and Generate button
        self.grpbxResult = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxResult.Caption = "Result"
        self.grpbxResult.Place(180, 92, None, 424, None, 175)
        self.grpbxResult.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Voronoi radio button – selects diagram generation mode
        self.rbtnVoronoi = pdk.TGIS_PvlRadioButton(self.grpbxResult.Context)
        self.rbtnVoronoi.Place(120, 17, None, 6, None, 19)
        self.rbtnVoronoi.Caption = "Voronoi Diagram"
        self.rbtnVoronoi.Checked = True   # Voronoi is the default mode
        self.rbtnVoronoi.OnChange = self.rbtnVoronoi_change

        # Delaunay radio button – selects triangulation generation mode
        self.rbtnDelaunay = pdk.TGIS_PvlRadioButton(self.grpbxResult.Context)
        self.rbtnDelaunay.Place(120, 17, None, 6, None, 42)
        self.rbtnDelaunay.Caption = "Delaunay Diagram"
        self.rbtnDelaunay.Checked = False
        self.rbtnDelaunay.OnChange = self.rbtnDelaunay_change

        # Label and text field for the output layer name
        self.lblLayer = pdk.TGIS_PvlLabel(self.grpbxResult.Context)
        self.lblLayer.Place(68, 13, None, 6, None, 68)
        self.lblLayer.Caption = "Layer name :"

        self.edtLayer = pdk.TGIS_PvlEdit(self.grpbxResult.Context)
        self.edtLayer.Place(94, 20, None, 80, None, 65)
        self.edtLayer.Text = "Voronoi"  # Default matches the selected mode

        # Generate button – triggers triangulation / diagram computation
        self.btnGenerate = pdk.TGIS_PvlButton(self.grpbxResult.Context)
        self.btnGenerate.Place(168, 23, None, 6, None, 95)
        self.btnGenerate.Caption = "Generate"
        self.btnGenerate.OnClick = self.btnGenerate_click

        # --- Map viewer (left area, fills available space) ---
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 28
        self.GIS.Width = 424
        self.GIS.Height = 354
        # Anchor all four edges so the viewer resizes with the form
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.FullExtent()
        self.GIS.OnMouseDown = self.GIS_MouseDown  # Wire mouse click for attribute lookup

        # --- Legend panel (right column, bottom) ---
        # Shows all loaded layers and allows basic style editing
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(180, 80, None, 424, None, 302)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

    def form_show(self, _sender):
        """
        Load the triangulation sample data when the form first becomes visible.

        Opens the Polish city point shapefile and configures the city marker style.
        A second "selected" param set is registered so that shapes shown in the
        Attributes panel receive a distinct blue area fill.
        """
        # Open the Polish city point data – this layer provides the seed
        # point set for both the Delaunay and Voronoi algorithms.
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/city.shp")

        # Retrieve the first (and only) vector layer just loaded
        lv = self.GIS.Items[0]

        # Customise the default marker style for city points
        lv.Params.Marker.Color = pdk.TGIS_Color().FromRGB(0x4080FF)
        lv.Params.Marker.OutlineWidth = 2
        lv.Params.Marker.Style = pdk.TGIS_MarkerStyle().Circle

        # Add a second named param set; shapes displayed in the attribute panel
        # use the "selected" style so they stand out on the map.
        lv.ParamsList.Add()
        lv.Params.Style = "selected"
        lv.Params.Area.OutlineWidth = 1
        lv.Params.Area.Color = pdk.TGIS_Color().Blue

        self.GIS.InvalidateWholeMap()  # Repaint to apply the new style

    # ------------------------------------------------------------------
    # Navigation handlers
    # ------------------------------------------------------------------

    def btnFullExtent_click(self, _sender):
        """Zoom the viewer to fit all loaded layers within the visible area."""
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        """Double the current zoom factor, zooming into the centre of the map."""
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        """Halve the current zoom factor, zooming out from the centre of the map."""
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    # ------------------------------------------------------------------
    # Mode selection handlers
    # ------------------------------------------------------------------

    def rbtnVoronoi_change(self, _sender):
        """
        Pre-fills the output layer name when the Voronoi radio button becomes selected.
        The handler fires on any state change; the guard ensures it only acts when
        the button transitions to the checked state.
        """
        if not self.rbtnVoronoi.Checked:
            return
        self.edtLayer.Text = "Voronoi"

    def rbtnDelaunay_change(self, _sender):
        """
        Pre-fills the output layer name when the Delaunay radio button becomes selected.
        """
        if not self.rbtnDelaunay.Checked:
            return
        self.edtLayer.Text = "Delaunay"

    # ------------------------------------------------------------------
    # Map interaction
    # ------------------------------------------------------------------

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        """
        Hit-test the map on mouse press to find the nearest shape and display
        its attribute data in the GIS_Attributes panel.

        ScreenToMap converts pixel coordinates to geographic (map) coordinates.
        Locate searches all layers for the nearest shape within a tolerance of
        5 screen pixels (converted to map units by dividing by the zoom factor).
        """
        if self.GIS.IsEmpty:
            return

        # Convert screen pixel position to geographic map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        # Locate the nearest shape within a 5-pixel screen tolerance
        shp = self.GIS.Locate(ptg, 5 / self.GIS.Zoom)  # 5 pixels precision
        if shp is not None:
            self.GIS_Attributes.ShowShape(shp)  # Populate the attribute panel

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def btnGenerate_click(self, _sender):
        """
        Create either a TGIS_LayerVoronoi or TGIS_LayerDelaunay layer, import
        the city point data as input, configure a graduated colour render style,
        and add the result to the viewer.

        ImportLayer copies all features from the source layer into the new
        triangulation layer and runs the algorithm immediately; after the call
        the layer contains fully formed polygon shapes ready for display.

        The GIS_AREA attribute (computed automatically by the triangulation engine)
        drives a white-to-colour gradient over 10 equal-interval zones.
        Voronoi uses red as the end colour; Delaunay uses blue.
        """
        # Prevent overwriting an existing layer with the same name
        if self.GIS.Get(self.edtLayer.Text) is not None:
            pdk.TGIS_PvlMessages.ShowInfo("Result layer already exists. Use different name.", self.Context)
            return

        # Instantiate the correct layer type based on the radio button selection
        if self.rbtnVoronoi.Checked:
            lv = pdk.TGIS_LayerVoronoi()   # Voronoi diagram
        else:
            lv = pdk.TGIS_LayerDelaunay()   # Delaunay triangulation

        lv.Name = self.edtLayer.Text

        # ImportLayer reads all point features from the source layer (index 0) and
        # uses them as the input seed set for the triangulation / diagram computation.
        # TGIS_ShapeType().Unknown lets the engine infer the output shape type automatically.
        lv.ImportLayer(self.GIS.Items[0], self.GIS.Extent, pdk.TGIS_ShapeType().Unknown, "", False)
        lv.Transparency = 60  # Semi-transparent so the source city layer shows through

        # Configure graduated colour rendering keyed on the built-in GIS_AREA attribute.
        # GIS_AREA holds the area of each output polygon in map coordinate units squared.
        lv.Params.Render.Expression = "GIS_AREA"
        lv.Params.Render.MinVal = 10000000.0    # ~10 km² lower bound
        lv.Params.Render.MaxVal = 1300000000.0  # ~1300 km² upper bound
        lv.Params.Render.StartColor = pdk.TGIS_Color().White
        # Differentiate Voronoi (red) from Delaunay (blue) visually
        if self.rbtnVoronoi.Checked:
            lv.Params.Render.EndColor = pdk.TGIS_Color().Red
        else:
            lv.Params.Render.EndColor = pdk.TGIS_Color().Blue

        lv.Params.Render.Zones = 10  # Divide the colour range into 10 equal steps
        # RenderColor instructs the renderer to substitute the computed gradient
        # colour for the polygon fill during painting.
        lv.Params.Area.Color = pdk.TGIS_Color.RenderColor

        # Inherit the coordinate system from the source layer so all layers align
        lv.CS = self.GIS.CS

        self.GIS.Add(lv)
        self.GIS.InvalidateWholeMap()  # Repaint the viewer
        # self.GIS_Legend.Invalidate()  # Uncomment to force legend refresh


def main():
    """Entry point: create and show the form, then hand control to the PDK event loop."""
    frm = TriangulationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
