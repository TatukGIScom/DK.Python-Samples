# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Renderer sample (Python / PDK edition) — demonstrates how to load and
# display a TatukGIS project file that contains pre-configured custom
# rendering rules using the TatukGIS Python Developer Kernel (tatukgis_pdk).
#
# Key concepts shown:
#   - Building a simple UI using TGIS_PvlForm and TGIS_PvlButton
#   - Opening a .ttkproject file with TGIS_ViewerWnd.Open
#   - Switching the viewer interaction mode (TGIS_ViewerMode) between
#     Select, Zoom, and Drag
#   - Guarding mode changes with GIS.IsEmpty to avoid operating on an
#     uninitialised viewer
#
# The rendering definitions (symbol styles, color ramps, scale-dependent
# rules, etc.) are stored inside renderer.ttkproject.  The Open button loads
# that project; Zooming and Dragging buttons change navigation behaviour.
# =============================================================================

import tatukgis_pdk as pdk  # TatukGIS Python Developer Kernel


class RendererForm(pdk.TGIS_PvlForm):
    """Main application form for the Renderer sample.

    Creates a toolbar with Open, Zooming, and Dragging buttons above a
    full-client TGIS_ViewerWnd map control.
    """

    def __init__(self, _owner):
        # --- Form geometry ---
        self.Caption = "Renderer - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        # --- Toolbar panel docked to the top of the form ---
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        # --- Open button: loads the renderer project file ---
        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        # --- Zooming button: switches viewer to Zoom interaction mode ---
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        # --- Dragging button: switches viewer to Drag/pan interaction mode ---
        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnDrag.Place(75, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Dragging"
        self.btnDrag.OnClick = self.btnDrag_click

        # --- Map viewer: fills the remaining client area below the toolbar ---
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def btnOpen_click(self, _sender):
        """Opens the pre-configured renderer project file.

        TGIS_Utils().GisSamplesDataDirDownload() returns the root path of the
        downloaded TatukGIS sample dataset.  After opening, the viewer is
        switched to Select mode so the user can interact with features.
        """
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      "Samples/Projects/renderer.ttkproject")
        # Switch to Select mode so the user can click features after opening.
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoom_click(self, _sender):
        """Switches the viewer to Zoom interaction mode.

        In Zoom mode the user can draw a rubber-band rectangle to zoom into a
        specific area, or use the scroll wheel to zoom in/out.
        IsEmpty guards against mode changes before any layers are loaded.
        """
        if self.GIS.IsEmpty:
            return  # No layers loaded yet — ignore the request
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """Switches the viewer to Drag (pan) interaction mode.

        In Drag mode the user can click and drag the map to pan across the
        dataset.  IsEmpty guards against mode changes before layers are loaded.
        """
        if self.GIS.IsEmpty:
            return  # No layers loaded yet — ignore the request
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag


def main():
    """Entry point: creates the form, shows it, and starts the PDK event loop."""
    frm = RendererForm(None)
    frm.Show()
    pdk.RunPvl(frm)  # Starts the TatukGIS PDK message/event loop

if __name__ == '__main__':
    main()
