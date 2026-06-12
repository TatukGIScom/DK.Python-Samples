# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Legend Sample - Python (PDK / PvlForm)
#
# Demonstrates how to use the TGIS_PvlControlLegend panel alongside a map
# viewer using the TatukGIS Python Developer Kernel (PDK).
#
# The legend control provides an interactive layer list that lets the user
# toggle layer visibility, reorder layers, expand/collapse layer symbology,
# and open layer property dialogs - all without writing any extra code.
#
# Key concepts shown:
#   - Placing TGIS_PvlControlLegend next to TGIS_ViewerWnd inside a
#     TGIS_PvlForm and linking them via GIS_Viewer so the legend reflects
#     the loaded map automatically.
#   - Switching between two display modes at runtime:
#       * TGIS_ControlLegendMode.Layers - flat list of every individual layer
#       * TGIS_ControlLegendMode.Groups - tree grouped by layer group membership
#   - Opening a .ttkproject file that bundles multiple SHP layers together.
#   - Controlling the viewer interaction mode (Zoom / Drag).
#   - Persisting any layer-style changes back to the project file with SaveAll.
#   - Reflecting the current map scale in a status label via VisibleExtentChangeEvent.
#
# Layout (left-to-right):
#   [Legend panel (160 px wide)] | [Map viewer (fills remaining width)]
#   Below legend: [Layers btn] [Groups btn]
#   Top: [Full Extent] [Zoom Mode] [Drag Mode] [Save config]
#   Bottom: scale label
# =============================================================================

import tatukgis_pdk as pdk


class LegendForm(pdk.TGIS_PvlForm):
    """
    Main application window for the Legend sample.

    Inherits from TGIS_PvlForm which provides the cross-platform windowing
    surface used by the TatukGIS Python PDK.
    """

    def __init__(self, _owner):
        """
        Constructs the form and all of its child controls.

        All controls are positioned using Place() which takes
        (width, height, right_anchor, left, bottom_anchor, top) arguments.
        Controls with Anchors set will resize proportionally with the form.
        """
        self.Caption = "Legend - TatukGIS DK Sample"
        self.ClientHeight = 500
        self.ClientWidth = 600

        # -----------------------------------------------------------------
        # Top toolbar panel - holds the navigation and save buttons
        # -----------------------------------------------------------------
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Full Extent button: zooms the viewer to fit all loaded layers
        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.btnFullExtent_click

        # Zoom Mode button: switches the viewer to rubber-band zoom interaction
        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "Zoom Mode"
        self.button2.OnClick = self.btnZoom_click

        # Drag Mode button: switches the viewer to click-drag panning interaction
        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 156, None, 3)
        self.button3.Caption = "Drag Mode"
        self.button3.OnClick = self.btnDrag_click

        # Save Config button: persists all layer changes back to the project file
        self.button4 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button4.Place(75, 22, None, 233, None, 3)
        self.button4.Caption = "Save config"
        self.button4.OnClick = self.btnSaveConfig_click

        # -----------------------------------------------------------------
        # Bottom status bar panel - displays the current map scale
        # -----------------------------------------------------------------
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        # Label that shows the current map scale (e.g. "Scale: 1 : 250 000")
        self.label = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.label.Place(200, 19, None, 3, None, 0)

        # -----------------------------------------------------------------
        # Map viewer (TGIS_ViewerWnd)
        # The map canvas that renders all loaded layers and handles
        # mouse-driven zoom and pan interactions.
        # Anchored to all four edges so it fills the remaining space as the
        # form is resized.
        # -----------------------------------------------------------------
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        # VisibleExtentChangeEvent fires after every viewport change (pan/zoom),
        # which is the appropriate moment to refresh the scale display.
        self.GIS.VisibleExtentChangeEvent = self.VisibleExtentChange
        self.GIS.Left = 140
        self.GIS.Top = 29
        self.GIS.Width = 452
        self.GIS.Height = 452
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        # Open the bundled Poland DCW project immediately after viewer creation.
        # GisSamplesDataDirDownload() resolves the shared sample-data directory.
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/Poland/DCW/poland.ttkproject"
        )

        # -----------------------------------------------------------------
        # Legend panel (TGIS_PvlControlLegend)
        # Shows the list of all layers currently loaded in the map viewer.
        # Setting GIS_Viewer links the legend to the viewer so it populates
        # automatically and stays in sync as layers are added or removed.
        # Anchored to left, top and bottom so it stretches vertically with
        # the form but keeps its fixed width.
        # -----------------------------------------------------------------
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        # Start in Layers mode (flat list); the user can switch to Groups mode
        # with the buttons below the legend panel.
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        # Link the legend to the viewer - this causes the legend to observe the
        # viewer's layer list and refresh whenever layers are loaded or changed.
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(160, 447, None, 0, None, 29)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        # -----------------------------------------------------------------
        # Mode-selection toolbar (docked to the bottom of the legend panel)
        # Lets the user switch the legend between Layers and Groups display modes.
        # -----------------------------------------------------------------
        self.toolbar_select = pdk.TGIS_PvlPanel(self.GIS_legend.Context)
        self.toolbar_select.Place(592, 29, None, 0, None, 0)
        self.toolbar_select.Align = "Bottom"

        # "Layers" button: switches legend to flat Layers mode
        self.button5 = pdk.TGIS_PvlButton(self.toolbar_select.Context)
        self.button5.Place(75, 22, None, 3, None, 3)
        self.button5.Caption = "Layers"
        self.button5.OnClick = self.btnLayers_click

        # "Groups" button: switches legend to hierarchical Groups mode
        self.button6 = pdk.TGIS_PvlButton(self.toolbar_select.Context)
        self.button6.Place(75, 22, None, 82, None, 3)
        self.button6.Caption = "Groups"
        self.button6.OnClick = self.btnGroups_click

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def btnFullExtent_click(self, _sender):
        """
        Resets the map viewport to show all loaded layers at their combined
        extent. Useful after zooming in and wanting to return to the overview.
        """
        # Zoom out to fit the complete bounding box of all visible layers
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        """
        Switches the viewer to Zoom mode.
        In Zoom mode a left-click-drag defines a rubber-band rectangle that
        the viewer zooms into; a right-click zooms back out.
        Guards against acting on an unloaded viewer.
        """
        if self.GIS.IsEmpty:
            return
        # TGIS_ViewerMode.Zoom: left-drag to zoom in, right-click to zoom out
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        Switches the viewer to Drag (pan) mode.
        In Drag mode the user pans the map by click-dragging, which is the
        most natural way to explore a map after zooming in.
        Guards against acting on an unloaded viewer.
        """
        if self.GIS.IsEmpty:
            return
        # TGIS_ViewerMode.Drag: click-drag to pan the visible map extent
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnSaveConfig_click(self, _sender):
        """
        Saves all layer configuration changes (symbology, visibility, order)
        back to the originating project or layer files.
        Guards against calling SaveAll on an empty viewer.
        """
        if self.GIS.IsEmpty:
            return  # Nothing loaded - nothing to save

        # Persist any legend changes (visibility flags, symbology edits, layer
        # order) back to the .ttkproject file and its referenced layer files.
        self.GIS.SaveAll()

    def btnLayers_click(self, _sender):
        """
        Switches the legend to flat Layers mode.
        In Layers mode every individual layer appears as a separate top-level
        item in the legend list, regardless of any group hierarchy.
        """
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers

    def btnGroups_click(self, _sender):
        """
        Switches the legend to Groups mode.
        In Groups mode layers are nested inside their parent group nodes,
        matching the logical structure defined in the project file.
        """
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Groups

    def VisibleExtentChange(self, _sender):
        """
        Fired by TGIS_ViewerWnd after every viewport change (zoom or pan).
        Updates the scale label with the human-readable map scale string
        (e.g. "Scale: 1 : 250 000") so the user always knows the zoom level.
        Guards against accessing properties on an empty (unloaded) viewer.
        """
        if self.GIS.IsEmpty:
            return

        # ScaleAsText returns a formatted "1 : N" string for the current viewport
        self.label.Caption = "Scale: " + self.GIS.ScaleAsText


def main():
    """
    Application entry point.
    Creates the form, makes it visible, then enters the PDK event loop.
    RunPvl() blocks until the form is closed.
    """
    frm = LegendForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
