# Zooming - TatukGIS Developer Kernel sample (Python / PDK).
#
# Demonstrates multiple ways to zoom and navigate a loaded map:
#   1. Loading a TatukGIS project file (.ttkproject) which bundles all
#      layer definitions, styles, and coordinate system settings.
#   2. Zoom mode - rubber-band rectangle zoom (left click + drag to zoom in,
#      right click to zoom out by one step).
#   3. Drag mode - panning by clicking and dragging the map.
#
# Note: this PDK sample uses the minimal set of navigation controls.
# See the HelloDK sample for an example of mouse-wheel zoom via ZoomBy().

import tatukgis_pdk as pdk


class ZoomingForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        # Set up the main form dimensions and caption
        self.Caption = "Zooming - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        # Toolbar panel anchored to the top of the form
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        # "Open" button - loads the sample project file
        self.btnOpen = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnOpen.Place(75, 22, None, 3, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        # "Zooming" button - enables rubber-band zoom interaction
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        # "Dragging" button - enables pan/drag interaction
        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnDrag.Place(75, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Dragging"
        self.btnDrag.OnClick = self.btnDrag_click

        # The central GIS map viewer control, filling the remaining form area
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def btnOpen_click(self, _sender):
        """
        "Open" button click handler.
        Opens the sample Poland project file. A .ttkproject file is a TatukGIS
        project format that bundles multiple layer definitions, their rendering
        styles, and coordinate system settings into a single file, so no manual
        layer configuration is required.
        After opening, the mode is set to Select so the user can interact
        with features immediately.
        """
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "World/Countries/Poland/DCW/poland.ttkproject")
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoom_click(self, _sender):
        """
        "Zooming" button click handler.
        Switches the viewer to Zoom mode. The user can left-click and drag to
        draw a rubber-band rectangle defining the new view area; a right-click
        zooms out by one step.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        "Dragging" button click handler.
        Switches the viewer to Drag mode, allowing the user to pan the map
        by clicking and dragging with the mouse.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag


def main():
    frm = ZoomingForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
