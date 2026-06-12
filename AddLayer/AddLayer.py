# AddLayer sample — demonstrates dynamic layer addition and visual parameter configuration (Python PDK).
#
# What the sample shows:
#   - Building a UI using the TatukGIS PDK widget toolkit (not native Python)
#   - Creating custom form classes using TGIS_PvlForm as base class
#   - Embedding TGIS_ViewerWnd map viewer inside a PDK form
#   - Creating TGIS_LayerSHP instances to load ESRI Shapefiles
#   - Adding layers to the viewer via GIS.Add() method
#   - Using TGIS_Utils.GisCreateLayer() factory for automatic layer type detection
#   - Setting visual rendering parameters: fill colour, line colour, line width
#   - Customising layer appearance through Params property tree
#   - Fitting viewport to all loaded layers with GIS.FullExtent()
#   - Toggling viewer interaction modes: Drag (pan) vs. Select (click features)
#   - Zooming programmatically with guards for empty viewers
#
# Key TatukGIS API concepts shown here:
#   TGIS_ViewerWnd              - main visual map control widget
#   TGIS_LayerSHP              - vector layer for ESRI Shapefiles
#   GisCreateLayer()            - factory function for automatic layer detection
#   TGIS_Params                 - layer styling and rendering parameters
#   TGIS_Utils                  - utility functions (sample data path, etc.)
#   GIS.Add()                   - adds a layer to the viewer
#   GIS.FullExtent()            - zoom to combined extent of all loaded layers
#   GIS.Mode                    - interaction mode property (Drag, Select, Zoom)
#   TGIS_PvlForm                - base class for PDK forms
#   TGIS_PvlPanel               - container widget for layout
# =============================================================================

import tatukgis_pdk as pdk   # TatukGIS Python Developer Kernel bindings


class AddLayerForm(pdk.TGIS_PvlForm):
    """
    AddLayer sample — demonstrates how to programmatically add vector layers to a GIS viewer.
    Creates shapefile layers (TGIS_LayerSHP) for country polygons and rivers polylines, sets visual
    styling parameters (fill color, line width, line color), and adds them to the viewer using GIS.Add().
    Provides zoom navigation and interaction mode switching (pan/select).
    """

    # Named constants for layer identifiers make the code self-documenting and
    # prevent accidental typos when the name strings are referenced in multiple
    # places.
    COUNTRY = "country"
    RIVERS  = "rivers"

    def __init__(self, _owner):
        """
        Builds the form layout: a toolbar panel at the top containing
        navigation buttons and a drag-mode checkbox, and the GIS viewer
        filling the remaining space.

        Parameters
        ----------
        _owner : object
            Parent owner passed to the PDK form (typically None for a
            top-level window).
        """
        self.Caption = "AddLayer - TatukGIS DK Sample"
        # self.SetBounds(200, 100, 600, 500)  # Uncomment to set explicit size/position

        # --- Toolbar panel ---
        # TGIS_PvlPanel groups the navigation controls in a fixed-height strip
        # docked to the top of the form.
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"   # Dock to the top edge; the GIS viewer fills the rest

        # "Open" button: loads the map layers on first click.
        # Layers are loaded lazily here (on button click) rather than at startup
        # so that the form appears immediately and the user triggers the data load.
        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)  # Width, Height, After, Left offset, Above, Top offset
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        # "ZoomIn" button: doubles the current zoom level.
        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomIn.Place(75, 22, self.btnOpen, 3, None, 3)  # Placed to the right of btnOpen
        self.btnZoomIn.Caption = "ZoomIn"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        # "ZoomOut" button: halves the current zoom level.
        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomOut.Place(75, 22, self.btnZoomIn, 3, None, 3)
        self.btnZoomOut.Caption = "ZoomOut"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        # Drag-mode checkbox: toggles between pan and feature-selection modes.
        self.chkDrag = pdk.TGIS_PvlCheckBox(self.toolbar.Context)
        self.chkDrag.Caption = "Dragging"
        self.chkDrag.Place(75, 22, self.btnZoomOut, 3, None, 3)
        self.chkDrag.OnChange = self.chkDrag_change

        # --- GIS viewer ---
        # TGIS_ViewerWnd is the map rendering control.  Setting Align = "Client"
        # causes it to fill all remaining space in the form below the toolbar.
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def btnOpen_click(self, _sender):
        """
        Handles the Open button click.  Loads the country outline and rivers
        Shapefile layers, configures their rendering params, and fits the
        viewport to their combined extent.

        This handler adds layers every time it is invoked.  In a production
        sample you would typically guard against duplicate additions, but here
        the intent is to keep the code simple and illustrative.
        """
        # --- Layer 1: Country outline (polygon / area layer) ---
        # Construct the layer directly.  TGIS_LayerSHP wraps an ESRI Shapefile;
        # the geometry type (polygon) is inferred from the .shp file header.
        ll = pdk.TGIS_LayerSHP()

        # GisSamplesDataDirDownload() returns the root path where TatukGIS sample
        # datasets were installed or downloaded.
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/country.shp"

        # A human-readable label shown in layer lists and legends.
        ll.Name = self.COUNTRY

        # Params.Area.Color sets the solid polygon fill.  LightGray provides a
        # neutral background so the rivers overlay is clearly readable on top.
        ll.Params.Area.Color = pdk.TGIS_Color.LightGray

        # GIS.Add appends the layer to the internal layer stack.  Layers added
        # earlier are rendered first (drawn at the bottom of the visual stack).
        self.GIS.Add(ll)

        # --- Layer 2: Rivers (polyline layer) ---
        # TGIS_Utils.GisCreateLayer is a factory that inspects the file extension
        # and instantiates the matching TGIS_Layer subclass automatically.
        # The first argument becomes the layer's Name property.
        ll = pdk.TGIS_Utils.GisCreateLayer(
            self.RIVERS,
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/lwaters.shp"
        )

        # Line.Width is in screen pixels at the reference zoom level.
        ll.Params.Line.Width = 3
        ll.Params.Line.Color = pdk.TGIS_Color.Blue

        self.GIS.Add(ll)

        # Zoom the viewport to the combined bounding box of all layers so the
        # full map is visible immediately after load.
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        """
        Doubles the current zoom level, shrinking the visible area by half.
        Guards against operating on an empty viewer.
        """
        if self.GIS.IsEmpty:
            return
        # Multiplying Zoom by 2 increases the scale, zooming in one step.
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        """
        Halves the current zoom level, doubling the visible area.
        Guards against operating on an empty viewer.
        """
        if self.GIS.IsEmpty:
            return
        # Dividing Zoom by 2 decreases the scale, zooming out one step.
        self.GIS.Zoom = self.GIS.Zoom / 2

    def chkDrag_change(self, _sender):
        """
        Toggles the viewer's active interaction mode in response to the
        checkbox state.

        TGIS_ViewerMode.Drag   – left-click and drag pans the map canvas.
        TGIS_ViewerMode.Select – left-click picks the topmost feature under
                                 the cursor.
        """
        if self.chkDrag.Checked:
            # Enable pan-drag mode so the user can scroll the map by dragging.
            self.GIS.Mode = pdk.TGIS_ViewerMode().Drag
        else:
            # Revert to feature-selection mode.
            self.GIS.Mode = pdk.TGIS_ViewerMode().Select


def main():
    """
    Application entry point.  Creates the form and starts the PDK event loop.

    RunPvl() blocks until the user closes the form, similar to
    Application.Run() in WinForms or app.exec_() in Qt.
    """
    frm = AddLayerForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
