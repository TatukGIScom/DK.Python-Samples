"""
=============================================================================
This source code is a part of TatukGIS Developer Kernel.
=============================================================================

Grid Sample (Python / PDK edition)

Demonstrates how to manipulate a raster grid (DEM) layer presentation.

This sample demonstrates:
  - Loading a raster DEM (NED - National Elevation Dataset) in ArcInfo
    Binary Grid (.adf) format using TGIS_ViewerWnd.Open, which auto-detects
    the file format and creates a TGIS_LayerPixel internally.
  - Clearing altitude colour zones (AltitudeMapZones) to revert the layer
    to its default greyscale gradient.
  - Defining custom altitude colour zones that map elevation ranges to named
    colours, creating a hypsometric tint effect (cool/warm colour coding
    of terrain by height).
  - Loading display parameters from an external INI configuration file via
    ConfigName / RereadConfig, allowing the colour scheme to be stored and
    shared without modifying source code.
  - Toggling hill-shading (GridShadow) which simulates a directional light
    source to give the terrain a 3-D appearance.
  - Reading the raw (native) elevation value at the geographic point under
    the mouse cursor using TGIS_LayerPixel.Locate and displaying it in a
    status label at the bottom of the form.

Key TatukGIS API classes used:
  TGIS_ViewerWnd          - map viewer component (PDK visual form host)
  TGIS_LayerPixel         - raster/grid layer (DEM, imagery, etc.)
  TGIS_PvlControlLegend   - layer list / legend panel
  TGIS_Utils              - utility helpers (sample data directory)

Python-specific notes:
  - The PDK uses TGIS_PvlControlLegend (not TGIS_ControlLegend) for the legend.
  - VarParameter wrappers are required for out/ref parameters in Locate()
    because Python cannot pass variables by reference natively.
  - TGIS_DoubleArray is the PDK array wrapper; access individual elements
    via .Value(index).
  - IsEmpty is checked before Locate to avoid errors when no layer is loaded.
"""

import tatukgis_pdk as pdk


class GridForm(pdk.TGIS_PvlForm):
    """
    Main form for the Grid sample application.

    Lays out the toolbar buttons, the map viewer, a legend panel, and a
    status bar label.  All button event handlers are wired in __init__.
    """

    def __init__(self, _owner):
        # Set the window caption and initial client dimensions
        self.Caption = "Grid - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        # --- Toolbar panel (full-width strip at the top) ----------------------
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Full Extent button - zooms the viewer to show all loaded layers
        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(45, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        # Zoom button - activates rubber-band zoom mode on the viewer
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(45, 22, None, 49, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        # Drag button - activates pan/drag mode on the viewer
        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(45, 22, None, 96, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        # Clear button - removes all custom altitude colour zones
        self.btnClear = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnClear.Place(79, 22, None, 180, None, 3)
        self.btnClear.Caption = "Clear"
        self.btnClear.OnClick = self.btnClear_click

        # Shadow button - toggles hill-shading (GridShadow) on/off
        self.btnShadow = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnShadow.Place(89, 22, None, 260, None, 3)
        self.btnShadow.Caption = "Shadow on/off"
        self.btnShadow.OnClick = self.btnShadow_click

        # User Defined button - applies a hard-coded hypsometric colour scheme
        self.btnUserDef = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnUserDef.Place(79, 22, None, 350, None, 3)
        self.btnUserDef.Caption = "User Defined"
        self.btnUserDef.OnClick = self.btnUserDef_click

        # User INI button - loads the bundled sample INI colour configuration
        self.btnUserINI = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnUserINI.Place(79, 22, None, 430, None, 3)
        self.btnUserINI.Caption = "User INI"
        self.btnUserINI.OnClick = self.btnUserINI_click

        # Reload INI button - reloads config from the layer's own INI file
        self.btnReloadINI = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnReloadINI.Place(79, 22, None, 510, None, 3)
        self.btnReloadINI.Caption = "Reload INI"
        self.btnReloadINI.OnClick = self.btnReloadINI_click

        # --- Status bar (anchored to bottom) ----------------------------------
        # Shows the raw elevation value under the mouse cursor
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblAltitude = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblAltitude.Place(300, 19, None, 3, None, 0)
        self.lblAltitude.Caption = ''

        # --- Map viewer -------------------------------------------------------
        # TGIS_ViewerWnd is the core map display widget
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 130
        self.GIS.Top = 30
        self.GIS.Width = 480
        self.GIS.Height = 450
        # Open the NED DEM directly on creation - the viewer auto-detects ADF format
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
        # Wire the mouse-move handler to report elevation under the cursor
        self.GIS.OnMouseMove = self.GIS_MouseMove

        # --- Legend panel (layer list, left side) ----------------------------
        # TGIS_PvlControlLegend reflects all layers currently loaded in the viewer
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(130, 450, None, 0, None, 30)
        # self.GIS_legend.Align = "Left"

    def GIS_MouseMove(self, _sender, _shift, x, y):
        """
        Fires on every mouse move over the map viewer.

        Reads the raw (native) elevation value from the DEM at the geographic
        point corresponding to the mouse cursor position and displays it in
        the status label at the bottom of the form.

        How it works:
          1. GIS.ScreenToMap converts the screen pixel (x, y) to map coordinates.
          2. TGIS_LayerPixel.Locate queries the raster at that point and fills
             the VarParameter wrappers:
               ref_rgb_mapped  - rendered colour at the queried pixel
               ref_natives_vals - raw band values; .Value(0) = elevation in metres
               ref_transparency - True if the pixel is outside the data extent
          3. The raw elevation is shown in lblAltitude.

        VarParameter wrappers are required because Python cannot pass variables
        by reference; they act as mutable containers for the output values.
        """
        # Do nothing if no layer has been loaded yet
        if self.GIS.IsEmpty:
            return

        # Convert screen pixel coordinates to geographic map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        # Retrieve the first (and only) layer in the viewer
        ll = self.GIS.Items[0]

        # Initialise VarParameter output wrappers for the Locate call
        ref_rgb_mapped = pdk.VarParameter()
        ref_rgb_mapped.Value = pdk.TGIS_Color()      # will receive rendered colour
        ref_natives_vals = pdk.VarParameter()
        ref_natives_vals.Value = pdk.TGIS_DoubleArray()  # will receive raw band values
        ref_transparency = pdk.VarParameter()
        ref_transparency.Value = False                # will receive transparency flag

        txt = ""
        # Locate returns True when the queried point falls within the raster extent
        if ll.Locate(ptg, ref_rgb_mapped, ref_natives_vals, ref_transparency):
            natives_vals = ref_natives_vals.Value
            # natives_vals.Value(0) is the raw DEM elevation in the native unit (metres)
            txt = txt + f"Altitude = {natives_vals.Value(0):.2f}"
        else:
            txt = txt + "Unknown"

        self.lblAltitude.Caption = txt

    def btnZoom_click(self, _sender):
        """
        Switches the viewer to rubber-band zoom mode.
        The user can then drag a rectangle to zoom into a specific area.
        Guards against calling on an empty viewer.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        Switches the viewer to pan/drag mode.
        The user can then scroll the map by clicking and dragging.
        Guards against calling on an empty viewer.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFullExtent_click(self, _sender):
        """
        Zooms the viewer to the combined extent of all loaded layers so the
        entire dataset is visible at once.
        """
        self.GIS.FullExtent()

    def btnClear_click(self, _sender):
        """
        Removes all custom altitude colour zones from the pixel layer,
        reverting it to the default greyscale gradient.

        AltitudeMapZones is the collection of "minElevation, maxElevation,
        colourName, zoneLabel" strings that define a hypsometric tint.
        Clearing it removes all custom assignments and falls back to the
        built-in gradient.
        """
        ll = self.GIS.Items[0]
        ll.Params.Pixel.AltitudeMapZones.Clear()
        # Force a full redraw so the change is immediately visible
        self.GIS.InvalidateWholeMap()

    def btnUserDef_click(self, _sender):
        """
        Applies a hard-coded hypsometric colour scheme by adding altitude
        zones programmatically.

        Each zone string follows the format:
          "minElevation, maxElevation, colourName, zoneLabel"
        where elevations are in the DEM's native unit (metres for NED data).
        The six bands span the terrain range of the San Bernardino NED tile.

        Always clear first to avoid accumulating duplicate zones.
        """
        ll = self.GIS.Items[0]
        # Clear any existing zones before adding the new scheme
        ll.Params.Pixel.AltitudeMapZones.Clear()
        # Define six elevation bands from valley floor to high peaks
        ll.Params.Pixel.AltitudeMapZones.Add("200, 400, OLIVE, VERY LOW")
        ll.Params.Pixel.AltitudeMapZones.Add("400, 700, OLIVE, LOW")
        ll.Params.Pixel.AltitudeMapZones.Add("700, 900, GREEN, MID")
        ll.Params.Pixel.AltitudeMapZones.Add("900, 1200, BLUE, HIGH")
        ll.Params.Pixel.AltitudeMapZones.Add("1200, 1700, RED, SKY")
        ll.Params.Pixel.AltitudeMapZones.Add("1700, 2200, YELLOW, HEAVEN")
        self.GIS.InvalidateWholeMap()

    def btnReloadINI_click(self, _sender):
        """
        Reloads the layer display configuration from the INI file that is
        co-located with the grid data file.

        Setting ConfigName to the data file path causes TatukGIS to look for
        a matching ".ini" companion file in the same directory.  RereadConfig
        re-parses that file and applies all stored display parameters (colour
        zones, shadow, transparency, etc.).
        """
        ll = self.GIS.Items[0]
        # Point ConfigName to the data file; TatukGIS resolves the matching INI
        ll.ConfigName = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                         + "World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
        ll.RereadConfig()
        self.GIS.InvalidateWholeMap()

    def btnShadow_click(self, _sender):
        """
        Toggles the hill-shading (GridShadow) effect on the DEM layer.

        Hill-shading simulates a directional light source over the terrain,
        darkening north-facing slopes and brightening south-facing ones.
        This dramatically improves the perceived depth and readability of the
        terrain without changing any underlying data values.
        """
        ll = self.GIS.Items[0]
        # Flip the current shadow state (on -> off, or off -> on)
        ll.Params.Pixel.GridShadow = not ll.Params.Pixel.GridShadow
        self.GIS.InvalidateWholeMap()

    def btnUserINI_click(self, _sender):
        """
        Loads a pre-built sample INI file (dem_ned.ini) that ships with the
        TatukGIS sample data.

        This demonstrates that the entire colour zone and rendering
        configuration can be stored in an external file and applied at runtime
        without modifying source code.  ConfigName points to the INI file and
        RereadConfig parses and applies all settings stored in it.
        """
        ll = self.GIS.Items[0]
        # Point ConfigName to the bundled sample INI configuration file
        ll.ConfigName = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                         + "Samples/Projects/dem_ned.ini")
        ll.RereadConfig()
        self.GIS.InvalidateWholeMap()


def main():
    """
    Application entry point.
    Creates the GridForm, displays it, and starts the PDK event loop.
    """
    frm = GridForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
