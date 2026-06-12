# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Topology Sample – Demonstrates polygon set-algebra operations using TGIS_Topology.
#
# This sample loads two overlapping polygon shapes (A and B) from a shapefile
# and lets the user compute the following topological combinations:
#
#   A + B   : Union            – area covered by either A or B (or both)
#   A * B   : Intersection     – area covered by both A and B
#   A - B   : Difference       – area in A but not in B
#   B - A   : Difference       – area in B but not in A
#   A xor B : SymDifference    – area in A or B but not in both (exclusive OR)
#
# Results are displayed in a separate in-memory TGIS_LayerVector rendered in red
# with 50% transparency so the original shapes remain visible underneath.
#
# Key TatukGIS PDK (Python DK) classes used:
#   TGIS_Topology            – engine that performs polygon boolean operations
#   TGIS_TopologyCombineType – enumeration of the five combine modes
#   TGIS_LayerVector         – in-memory vector layer used to display results
#   TGIS_ViewerWnd           – map viewer widget
#   TGIS_PvlForm             – base class for PDK application forms
# =============================================================================

import tatukgis_pdk as pdk


class TopologyForm(pdk.TGIS_PvlForm):
    """
    Main form for the Topology sample application.

    Demonstrates the five polygon boolean (set-algebra) operations provided
    by TGIS_Topology: Union, Intersection, Difference (A-B),
    Difference (B-A), and Symmetrical Difference (XOR).

    Attributes
    ----------
    shpA      : TGIS_Shape        – editable copy of source polygon A (shape index 1)
    shpB      : TGIS_Shape        – editable copy of source polygon B (shape index 2)
    layerObj  : TGIS_LayerVector  – output layer that receives the computed result shape
    topologyObj : TGIS_Topology   – engine that executes the boolean operations
    """

    shpA: pdk.TGIS_Shape = None
    shpB: pdk.TGIS_Shape = None
    layerObj: pdk.TGIS_LayerVector = None
    topologyObj: pdk.TGIS_Topology = None

    def __init__(self, _owner):
        """
        Build the form layout.

        Creates a toolbar panel with five operation buttons (one per boolean
        mode), a map viewer that fills the remaining space, and a status bar
        at the bottom.  Actual data loading is deferred to form_show() so
        the viewer is fully initialised before Open() is called.
        """
        self.Caption = "Topology - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 462
        self.OnShow = self.form_show   # Defer data load until the form is visible

        # --- Toolbar panel ---
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Union: A + B
        self.btnAplusB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAplusB.Place(75, 22, None, 0, None, 3)
        self.btnAplusB.Caption = "A + B"
        self.btnAplusB.OnClick = self.btnAplusB_click

        # Intersection: A * B
        self.btnAmultiB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAmultiB.Place(75, 22, None, 75, None, 3)
        self.btnAmultiB.Caption = "A * B"
        self.btnAmultiB.OnClick = self.btnAmultiB_click

        # Difference: A - B
        self.btnAminusB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAminusB.Place(75, 22, None, 150, None, 3)
        self.btnAminusB.Caption = "A - B"
        self.btnAminusB.OnClick = self.btnAminusB_click

        # Reverse difference: B - A
        self.btnBminusA = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnBminusA.Place(75, 22, None, 225, None, 3)
        self.btnBminusA.Caption = "B - A"
        self.btnBminusA.OnClick = self.btnBminusA_click

        # Symmetrical difference (XOR): A xor B
        self.btnAxorB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAxorB.Place(75, 22, None, 300, None, 3)
        self.btnAxorB.Caption = "A xor B"
        self.btnAxorB.OnClick = self.btnAxorB_click

        # --- Map viewer ---
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 400
        # Anchor all four edges so the viewer resizes with the form
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # --- Status bar ---
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

    def form_show(self, _sender):
        """
        Load the topology sample data when the form first becomes visible.

        Opens the bundled shapefile, extracts editable copies of the two
        source polygons, and creates the transparent output layer.

        MakeEditable() returns a detached, writable copy of each shape so the
        topology engine can operate on the geometry without modifying the
        underlying file-backed layer.
        """
        self.layerObj = pdk.TGIS_LayerVector()
        # Create the topology engine (stateless; safe to reuse across calls)
        self.topologyObj = pdk.TGIS_Topology()

        self.GIS.Lock()  # Suspend repaints during batch modifications

        # Open the bundled topology sample shapefile (two overlapping polygons)
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Topology/topology.shp")

        ll = self.GIS.Items[0]   # First (and only) vector layer loaded
        if ll is None:
            return

        # MakeEditable() returns a detached, editable copy; required by the topology engine
        self.shpA = ll.GetShape(1).MakeEditable()
        if self.shpA is None:
            return

        self.shpB = ll.GetShape(2).MakeEditable()
        if self.shpB is None:
            return

        # Create a blank in-memory layer to hold the topology result.
        # The layer sits on top of the source layer in the viewer stack.
        self.layerObj = pdk.TGIS_LayerVector()
        self.layerObj.Name = "output"
        self.layerObj.Transparency = 50           # 50% transparent so source shows through
        self.layerObj.Params.Area.Color = pdk.TGIS_Color().Red  # Result fill colour

        self.GIS.Add(self.layerObj)
        self.GIS.Unlock()      # Resume painting
        self.GIS.FullExtent()  # Zoom to fit all layers

    # ------------------------------------------------------------------
    # Topology operation handlers
    # Each handler:
    #   1. Clears the output layer (RevertShapes)
    #   2. Calls Combine() with the appropriate TGIS_TopologyCombineType value
    #   3. Adds the result shape to the output layer if one was produced
    #   4. Forces a full repaint of the viewer
    # ------------------------------------------------------------------

    def btnAplusB_click(self, _sender):
        """
        Union (A + B): covers all area in either polygon A or B,
        merging any overlapping regions into a single contiguous polygon.
        """
        self.layerObj.RevertShapes()   # Clear previous result
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Union)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAmultiB_click(self, _sender):
        """
        Intersection (A * B): covers only the area simultaneously inside
        both polygon A and polygon B.
        """
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Intersection)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAminusB_click(self, _sender):
        """
        Difference A minus B (A - B): area of polygon A with the overlap
        of B removed.  The first Combine() argument is the base shape;
        the second is subtracted from it.
        """
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Difference)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnBminusA_click(self, _sender):
        """
        Reverse Difference B minus A (B - A): identical logic to A-B but
        with operands swapped so that the area of A is subtracted from B.
        """
        self.layerObj.RevertShapes()
        # Note: shpB is the first (base) argument; shpA is what gets subtracted
        tmp = self.topologyObj.Combine(self.shpB, self.shpA, pdk.TGIS_TopologyCombineType().Difference)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAxorB_click(self, _sender):
        """
        Symmetrical Difference (A xor B): covers area belonging to exactly
        one of the two polygons.  Equivalent to Union minus Intersection,
        or a logical XOR applied to the two polygon areas.
        """
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().SymmetricalDifference)
        if tmp is not None:
            self.layerObj.AddShape(tmp)

        self.GIS.InvalidateWholeMap()


def main():
    """Entry point: create and show the form, then hand control to the PDK event loop."""
    frm = TopologyForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
