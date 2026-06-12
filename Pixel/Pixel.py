# Pixel sample — demonstrates rendering raster layers with various visual effects (Python PDK).
#
# What the sample shows:
#   - Loading a pre-built .ttkproject file containing a raster layer
#   - Switching between rendering profiles via combo box selector
#   - Normal rendering: standard colour display for multi-band imagery
#   - Normal with histogram: histogram-stretch for enhanced contrast
#   - Grayscale rendering: single-channel conversion for monochrome display
#   - Transparent rendering: alpha-channel and transparency support
#   - Colorize rendering: maps pixel values through custom colour gradients
#   - Inversion rendering: inverts all colour channels (negative effect)
#   - Inversion by RGB: inverts individual R, G, B channels separately
#   - Building UI using PDK widget toolkit instead of native Python frameworks
#   - Navigating with zoom and pan controls
#
# Key TatukGIS API concepts shown here:
#   TGIS_ViewerWnd                  - main visual map control widget
#   TGIS_LayerPixel                 - raster/pixel layer (imagery, DEMs, etc.)
#   GIS.Open()                      - opens .ttkproject with all layers
#   GIS.FullExtent()                - zoom to combined extent of all layers
#   TGIS_ViewerMode                 - interaction modes (Zoom, Drag)
#   TGIS_Utils.GisSamplesDataDirDownload() - resolves bundled sample data path
#   TGIS_PvlForm                    - base class for PDK forms
#   TGIS_PvlPanel                   - container widget for layout
#   TGIS_PvlComboBox                - dropdown selector widget for rendering modes

import tatukgis_pdk as pdk


class PixelForm(pdk.TGIS_PvlForm):
    """
    Main form for the Pixel sample.
    Provides a toolbar with navigation buttons and a combo box for selecting
    which rendering project to load into the GIS viewer.
    """

    def __init__(self, _owner):
        self.Caption = "Pixel - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        # Wire up the OnShow event so the viewer is populated once the window
        # is actually visible (avoids layout issues during construction).
        self.OnShow = self.form_show

        # --- Toolbar panel (docked to the top of the form) ---
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        # Full Extent button - resets the view to show all loaded layers
        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.btnFullExtent_click

        # Zoom button - enables rubber-band zoom interaction
        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "Zoom"
        self.button2.OnClick = self.btnZoom_click

        # Drag button - enables pan/scroll interaction
        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 156, None, 3)
        self.button3.Caption = "Drag"
        self.button3.OnClick = self.btnDrag_click

        # Project combo box - each entry is a .ttkproject file that encodes
        # the raster source together with a specific rendering configuration
        self.ComboProject = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.ComboProject.Place(175, 22, None, 300, None, 3)
        names = ("Normal.ttkproject",
                 "Normal with histogram.ttkproject",
                 "Grayscale.ttkproject",
                 "Colorize.ttkproject",
                 "Inversion.ttkproject",
                 "Inversion by RGB.ttkproject")
        for name in names:
            self.ComboProject.ItemsAdd(name)
        self.ComboProject.OnChange = self.Project_Change

        # Thin status panel docked to the bottom of the form
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        # TatukGIS map viewer - fills the remaining client area between the
        # toolbar and the status bar
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom  # Start in zoom mode

    def form_show(self, _sender):
        """
        Called when the form becomes visible for the first time.
        Selects the first item in the combo box, which triggers
        Project_Change() and loads the default rendering project.
        """
        self.ComboProject.ItemIndex = 0

    def btnFullExtent_click(self, _sender):
        """
        Resets the map view so that all loaded layers are visible
        simultaneously.  Guards against an empty viewer.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        """
        Switches the viewer to Zoom mode.
        The user draws a rectangle to zoom in, or right-clicks to zoom out.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        Switches the viewer to Drag (pan) mode.
        The user can scroll the map by clicking and dragging.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def Project_Change(self, _sender):
        """
        Opens the .ttkproject file selected in the combo box.
        GIS.Open() closes any previously loaded content and replaces it with
        the layers defined in the project file.  Each project in this sample
        points at the same raster image but with different rendering settings
        (colour mode, histogram stretch, etc.).
        GisSamplesDataDirDownload() returns the platform-specific base path
        for the bundled sample data.
        """
        project = self.ComboProject.Text
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "Samples/Projects/" + project)


def main():
    """Creates the form, shows it, and starts the PDK event loop."""
    frm = PixelForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
