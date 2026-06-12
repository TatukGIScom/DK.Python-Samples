# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Projections Sample
# ==================
# Demonstrates how TatukGIS PDK supports on-the-fly coordinate reprojection
# for map display in a Python application using the tatukgis_pdk bindings.
#
# Key concepts covered:
#
#   pdk.TGIS_Utils().CSProjList
#       The projection catalogue accessed through a TGIS_Utils instance.
#       Contains every known map-projection method (Mercator, Lambert, UTM,
#       etc.).  Each entry exposes IsStandard and WKT attributes.
#
#   pdk.TGIS_CSProjectedCoordinateSystem(epsg, name, gcs_epsg, unit_epsg,
#                                         proj_epsg, default_params)
#       A full CRS assembled at runtime from a geographic datum, a linear
#       unit, and a projection method.  EPSG = -1 marks it as user-defined.
#
#   TGIS_CSGeographicCoordinateSystem (EPSG 4030)
#       WGS 84 unscaled — the geographic datum base used for every CRS
#       constructed in this sample, independent of the projection method.
#
#   GIS.CS property
#       Assigning a new CRS triggers on-the-fly reprojection of every loaded
#       layer without reloading or modifying source data.
#
#   GIS.FullExtent()
#       Zooms the viewport to the combined bounding box of all layers in the
#       currently assigned coordinate system.
#
# Workflow:
#   1. form_show populates the combo box with "standard" projection WKT names
#      from the catalogue, then opens the bundled world map project.
#   2. cbxSrcProjection_Change builds a projected CRS (WGS 84 + metres + the
#      chosen projection) and assigns it to the viewer for on-the-fly reprojection.
#   3. btnZoom_click restores Zoom interaction mode if the user has accidentally
#      changed it (e.g. by panning).
# =============================================================================

import tatukgis_pdk as pdk


class ProjectionsForm(pdk.TGIS_PvlForm):
    """
    Main application form for the Projections sample.

    Shows a world map that is immediately reprojected whenever the user picks
    a different projection method from the combo box.  A Zoom button restores
    the interactive zoom mode.
    """

    def __init__(self, _owner):
        # Set window geometry and title.
        self.Caption = "Projections - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500

        # Wire up the OnShow event so that data loading happens after the
        # window is fully initialised and visible.
        self.OnShow = self.form_show

        # --- Toolbar panel (docked to the top of the form) ---
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        # Combo box: lists all standard projection WKT names.
        # OnChange fires cbxSrcProjection_Change on every selection change.
        self.cbxSrcProjection = pdk.TGIS_PvlComboBox(self.toolbar.Context)
        self.cbxSrcProjection.Place(175, 22, None, 3, None, 3)
        self.cbxSrcProjection.OnChange = self.cbxSrcProjection_Change

        # Button to restore Zoom interaction mode after panning.
        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 179, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        # --- Map viewer (fills the remaining client area) ---
        # TGIS_ViewerWnd is the TatukGIS viewer control; Align="Client" makes
        # it fill the area below the toolbar.
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def form_show(self, _sender):
        """
        Called once when the form becomes visible.

        Populates the projection combo box with every "standard" projection
        from the TatukGIS catalogue, then opens the bundled world map project
        and zooms to its full extent.

        Only "standard" projections are shown (IsStandard == True) to avoid
        cluttering the list with partial or experimental entries.
        """
        for i in range(0, pdk.TGIS_Utils().CSProjList.Count()):
            # IsStandard filters out non-standard / experimental entries.
            if pdk.TGIS_Utils().CSProjList.Projection(i).IsStandard:
                proj_object = pdk.TGIS_Utils().CSProjList.Projection(i)
                # WKT is the Well-Known Text identifier used as both the
                # display label and the lookup key for the catalogue.
                self.cbxSrcProjection.ItemsAdd(proj_object.WKT)

        # Open the bundled world map project; GisSamplesDataDirDownload()
        # resolves the path to the TatukGIS sample data directory.
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      "/Samples/Projects/world.ttkproject")

        # Zoom to the full world extent in the project's default CRS.
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        """
        Restores the viewer's Zoom interaction mode.

        After panning or other interactions the mode can change; this button
        returns the viewer to the standard zoom-in/zoom-out behaviour.
        IsEmpty guards against calling Mode when no layers are loaded.
        """
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def cbxSrcProjection_Change(self, _sender):
        """
        Called whenever the user selects a different projection in the combo.

        Core on-the-fly reprojection pattern:
          1. Read the WKT name of the selected projection.
          2. Look up the geographic datum (EPSG 4030 = WGS 84 unscaled),
             linear unit (Metre), and projection method from the catalogues.
          3. Construct a TGIS_CSProjectedCoordinateSystem by combining those
             three components.  EPSG = -1 marks it as user-defined.
             DefaultParams() supplies sensible default parameter values
             (central meridian, standard parallels, etc.) so no manual
             parameter entry is required.
          4. Assign the new CRS to GIS.CS.  The viewer reprojects all loaded
             layers in memory; no source data is modified or reloaded.
          5. Call GIS.FullExtent() to re-zoom to the world extent in the CRS.

        Lock()/Unlock() prevent intermediate repaints between the CRS
        assignment and the extent reset, eliminating flicker.  The inner
        try/except catches pdk.EGIS_Exception: some projection methods cannot
        represent the full global extent and will raise; the viewer stays in
        its last valid state when this occurs.
        """
        # Read the WKT name of the projection selected by the user.
        s_proj = self.cbxSrcProjection.Text

        # WGS 84 unscaled — the standard geographic datum base for on-the-fly
        # CRS construction without committing to a specific ellipsoid scaling.
        o_gcs = pdk.TGIS_Utils().CSGeographicCoordinateSystemList.ByEPSG(4030)

        # Metre — the most common linear unit for projected coordinate systems.
        o_unit = pdk.TGIS_Utils().CSUnitsList.ByWKT('METER')

        # Look up the projection method object from the global catalogue.
        o_proj = pdk.TGIS_Utils().CSProjList.ByWKT(s_proj)

        # Build a complete projected CRS dynamically.
        # EPSG = -1  : user-defined, not registered in the EPSG database.
        # 'Test'     : temporary display name for this CRS.
        # DefaultParams provides canonical parameter values (central meridian,
        # standard parallels, etc.) for the projection so no manual input
        # is required.
        ocs = pdk.TGIS_CSProjectedCoordinateSystem(
            -1, 'Test', o_gcs.EPSG, o_unit.EPSG, o_proj.EPSG,
            pdk.TGIS_Utils().CSProjectedCoordinateSystemList.DefaultParams(o_proj.EPSG)
        )

        # Lock prevents repaints during the combined CS + extent update.
        self.GIS.Lock()
        try:
            try:
                # Assigning CS triggers on-the-fly reprojection of all layers.
                self.GIS.CS = ocs

                # Re-zoom to the full world extent expressed in the new CRS.
                self.GIS.FullExtent()
            except pdk.EGIS_Exception:
                pass
                # Some projection methods cannot represent the global extent
                # (e.g. polar projections applied to equatorial data).
                # Silently ignore to leave the viewer in its last valid state.
        finally:
            self.GIS.Unlock()


def main():
    """Application entry point: creates and shows the Projections form."""
    frm = ProjectionsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
