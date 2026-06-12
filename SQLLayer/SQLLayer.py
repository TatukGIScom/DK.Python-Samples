# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# SQLLayer Sample - Python (TatukGIS PDK)
# ========================================
# Demonstrates how to open and display an SQL layer using TatukGIS DK11.
#
# An SQL layer (*.ttkls file) is a virtual layer definition that describes how
# to retrieve spatial data from a relational database (e.g. PostgreSQL/PostGIS,
# SQL Server, SQLite, Oracle Spatial) using a SQL query.  The .ttkls file
# contains the connection string, the SQL statement, and field mappings; it
# can be opened just like any other layer format supported by the DK.
#
# Key concepts shown:
#   - Creating a TGIS_PvlForm-based application window with the PDK UI toolkit
#   - Opening a .ttkls project with TGIS_ViewerWnd.Open
#   - Fitting the view to the full data extent with FullExtent
#   - Switching the viewer between Zoom and Drag interaction modes
#
# To adapt this sample to your own database:
#   Edit the gistest.ttkls file (in the Samples/SQLLayers data directory) to
#   supply your connection string and SQL query before running.
# =============================================================================

import tatukgis_pdk as pdk  # TatukGIS Python Developer Kernel


class SQLLayerForm(pdk.TGIS_PvlForm):
    """
    Main application window for the SQLLayer sample.

    Inherits from TGIS_PvlForm which provides a cross-platform windowing
    abstraction used by TatukGIS Python samples.  The window hosts a
    TGIS_ViewerWnd map viewer and a small toolbar panel.
    """

    def __init__(self, _owner):
        # Configure the form window
        self.Caption = "SQLLayer - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466

        # Register the form_show callback; called when the window first becomes
        # visible, allowing deferred data loading after the UI is ready.
        self.OnShow = self.form_show

        # ------------------------------------------------------------------
        # TGIS_ViewerWnd — the main map viewer component.
        # Align="Client" makes it fill the entire form area below the toolbar.
        # ------------------------------------------------------------------
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

        # ------------------------------------------------------------------
        # Toolbar panel — placed at the top of the form (y=0).
        # Place(width, height, right_anchor, left, bottom_anchor, top)
        # ------------------------------------------------------------------
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 26, None, 0, None, 0)

        # Full Extent button — zooms the map to show all loaded features
        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(73, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        # Zoom button — activates rubber-band zoom interaction mode
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(73, 22, None, 79, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        # Drag button — activates pan/drag interaction mode
        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(73, 22, None, 155, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

    def form_show(self, _sender):
        """
        Called when the form becomes visible for the first time.

        Opens the SQL layer definition file (.ttkls).  TGIS_ViewerWnd.Open
        accepts any supported layer or project format; for .ttkls files it
        connects to the configured database, executes the SQL query, and
        creates a virtual vector layer from the result set.

        TGIS_Utils.GisSamplesDataDirDownload() returns the path to the
        TatukGIS sample data directory (downloaded separately).
        """
        # Open the .ttkls SQL layer definition file.
        # Edit Samples/SQLLayers/gistest.ttkls to point at your own database.
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/SQLLayers/gistest.ttkls")

    def btnZoom_click(self, _sender):
        """
        Activates rubber-band zoom interaction mode.
        In this mode, click-drag draws a rectangle to zoom into.
        Guards against calling on an empty (unloaded) viewer.
        """
        if self.GIS.IsEmpty:
            return
        # TGIS_ViewerMode().Zoom — rubber-band zoom interaction
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        """
        Activates pan/drag interaction mode.
        In this mode, click-drag scrolls the map at the current zoom level.
        Guards against calling on an empty (unloaded) viewer.
        """
        if self.GIS.IsEmpty:
            return
        # TGIS_ViewerMode().Drag — pan/scroll interaction
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFullExtent_click(self, _sender):
        """
        Zooms the map to the full extent of all loaded layers, making every
        feature visible.
        """
        self.GIS.FullExtent()


def main():
    """
    Application entry point.
    Creates the form window, shows it, and starts the PDK event loop.
    RunPvl blocks until the window is closed.
    """
    frm = SQLLayerForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
