# =============================================================================
# Buffers2 - TatukGIS DK11 Python (PDK) sample
# =============================================================================
#
# Demonstrates an advanced buffer workflow that combines TGIS_Topology.MakeBuffer
# with a spatial intersection query to highlight all features that overlap the
# computed buffer polygon.
#
# This sample extends Buffers1 by:
#   - Loading a real-world shapefile (California counties) via
#     TGIS_Utils.GisCreateLayer, a factory that automatically selects the
#     correct layer class for the file format
#   - Finding a specific county by attribute name ("Merced") using
#     TGIS_LayerVector.FindFirst with a SQL-style filter expression
#   - Computing a planar buffer around that county at a distance controlled
#     by a slider (0..200, divided by 100 = 0..2 geographic degrees)
#   - Performing a two-stage spatial intersection query:
#       Stage 1 - FindFirst(buf.Extent): bounding-box pre-filter (fast)
#       Stage 2 - buf.IsCommonPoint(tmp): precise geometric overlap test
#   - Marking intersecting counties blue (MakeEditable + Params.Area.Color)
#     and listing their names in a side list box
#   - Assigning the viewer's coordinate system (CS) to the buffer layer so
#     that spatial distances are interpreted in the same projection as the
#     source data (geographic degrees in this example)
#
# Key TatukGIS PDK types used:
#   TGIS_ViewerWnd    - map display widget
#   TGIS_LayerVector  - in-memory or file-backed vector layer
#   TGIS_LayerAbstract- base type returned by GisCreateLayer
#   TGIS_Topology     - spatial operations engine (MakeBuffer, etc.)
#   TGIS_Shape        - a single geographic feature
#   TGIS_Utils        - utility helpers (GisCreateLayer, GisWholeWorld, etc.)
#   TGIS_PvlForm      - base class for PDK application windows
#   TGIS_PvlPanel     - container panel widget
#   TGIS_PvlTrackBar  - slider control
#   TGIS_PvlButton    - push-button widget
#   TGIS_PvlListBox   - list box widget (shows intersecting county names)
#   TGIS_PvlLabel     - static text label
# =============================================================================

import tatukgis_pdk as pdk


class Buffers2Form(pdk.TGIS_PvlForm):
    """
    Main form for the Buffers2 sample.

    Loads California county data, computes a buffer around Merced County at a
    distance set by the slider, then highlights every county that intersects
    the buffer polygon and lists their names in ``lbSelected``.

    The core buffer-and-intersect logic lives in ``tmp()`` (named for the
    temporary shape variable used throughout the algorithm).  It is called from
    form_show on startup and from each button / slider event handler.
    """

    def __init__(self, _owner):
        # ── Form geometry and caption ─────────────────────────────────────────
        self.Caption = "Buffers2 - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        # form_show is called once when the window is first displayed
        self.OnShow = self.form_show

        # ── Toolbar panel (top strip) ─────────────────────────────────────────
        # Hosts the minus button, the distance slider, and the plus button.
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Minus button: decrements the slider by 25 steps (coarser step than
        # Buffers1 because the range is 0..200 rather than -50..+50)
        self.btnMinus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnMinus.Place(22, 22, None, 10, None, 3)
        self.btnMinus.Caption = " - "
        self.btnMinus.OnClick = self.btnMinus_click

        # Slider: controls buffer distance in tenths of a degree (0..200).
        # Divide by 100 to obtain degrees: 0 = no buffer, 200 = 2° buffer.
        self.trackBar1 = pdk.TGIS_PvlTrackBar(self.toolbar_buttons.Context)
        self.trackBar1.Place(169, 33, None, 33, None, 6)
        self.trackBar1.OnChange = self.trackBar1_Scroll
        self.trackBar1.Maximum = 200
        self.trackBar1.Minimum = 0

        # Plus button: increments the slider by 25 steps
        self.btnPlus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPlus.Place(22, 22, None, 203, None, 3)
        self.btnPlus.Caption = " + "
        self.btnPlus.OnClick = self.btnPlus_click

        # ── Map viewer ────────────────────────────────────────────────────────
        # TGIS_ViewerWnd occupies the left portion of the form.
        # Anchors pin all four edges so the viewer resizes with the window.
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 477
        self.GIS.Height = 448
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # ── Intersecting-county list ──────────────────────────────────────────
        # Docked to the right; shows the names of counties whose geometry
        # intersects the computed buffer polygon.
        self.lbSelected = pdk.TGIS_PvlListBox(self.Context)
        self.lbSelected.Place(120, 448, None, 480, None, 29)
        self.lbSelected.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right,
                                   pdk.TGIS_PvlAnchor().Bottom)

        # ── Status bar (bottom panel) ─────────────────────────────────────────
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        # Shows the current buffer distance value while the slider is moved
        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

    def tmp(self):
        """
        Core buffer and spatial intersection logic.

        This method is called after every slider or button change to recompute
        which counties intersect the current buffer.

        Algorithm:
          1. Retrieve the "counties" source layer and the "buffer" overlay layer
             by their logical names via GIS.Get.
          2. Use FindFirst with a whole-world extent and the attribute filter
             "name='Merced'" to locate the Merced County shape.
          3. Clear the buffer overlay (RevertShapes) and call
             TGIS_Topology.MakeBuffer.  The distance is
             ``trackBar1.Position / 100.0``, which converts the 0..200 integer
             range to 0..2 geographic degrees.
          4. Store the resulting buffer polygon in the overlay layer via AddShape,
             which returns the stored shape reference (``buf``) used next.
          5. Two-stage spatial query over the county layer:
               - FindFirst(buf.Extent): fast bounding-box pre-filter - only
                 counties whose envelope overlaps the buffer's bounding box are
                 visited.
               - buf.IsCommonPoint(tmp): precise geometric intersection test -
                 filters out candidates that are adjacent in extent but do not
                 actually share any geometry with the buffer.
          6. Matching counties are made editable (MakeEditable) so that their
             per-shape colour can be changed, then coloured blue and their names
             added to the list box.
          7. GIS.InvalidateWholeMap redraws the display to reflect all changes.
        """
        # Retrieve layers by their logical names
        ll = self.GIS.Get("counties")
        if not ll:
            return

        lb = self.GIS.Get("buffer")
        if not lb:
            return

        # FindFirst with GisWholeWorld() as the extent ensures no shape is
        # excluded by bounding-box pre-filtering; the attribute filter does the
        # actual selection.
        shp = ll.FindFirst(pdk.TGIS_Utils.GisWholeWorld(), "name='Merced'")
        if not shp:
            return

        # Compute the buffer polygon around Merced County
        tpl = pdk.TGIS_Topology()
        lb.RevertShapes()  # discard any previously computed buffer polygon
        # Divide by 100.0 to convert the integer slider value to degrees
        tmp = tpl.MakeBuffer(shp, self.trackBar1.Position / 100.0)
        if tmp is not None:
            # AddShape copies the geometry into the overlay layer and returns
            # the stored shape reference used in the intersection query below
            buf = lb.AddShape(tmp)
        else:
            return  # MakeBuffer returned nothing (e.g. distance = 0)

        # ── Spatial intersection query ────────────────────────────────────────
        # Re-fetch the county layer (AddShape may have invalidated the reference)
        ll = self.GIS.Get("counties")
        # IgnoreShapeParams = False allows per-shape colour overrides to take
        # effect.  When True (the default after RevertShapes), the layer's
        # default colour is used for all shapes regardless of per-shape Params.
        ll.IgnoreShapeParams = False
        if ll is None:
            return

        ll.RevertShapes()       # reset per-shape colour overrides from the previous run
        self.lbSelected.ItemsClear()  # clear the previous list of county names

        # Stage 1: bounding-box pre-filter
        tmp = ll.FindFirst(buf.Extent)
        while tmp is not None:
            # Stage 2: precise geometric intersection test
            if buf.IsCommonPoint(tmp):
                # MakeEditable returns a writable copy so Params.Area.Color can
                # be changed; shapes from a file-backed layer are read-only.
                tmp = tmp.MakeEditable()
                self.lbSelected.ItemsAdd(str(tmp.GetField("name")))  # add county name
                tmp.Params.Area.Color = pdk.TGIS_Color().Blue        # colour it blue
            tmp = ll.FindNext()  # advance to the next bounding-box candidate

        # Redraw the map to show the updated buffer and highlighted counties
        self.GIS.InvalidateWholeMap()

    def form_show(self, _sender):
        """
        Initialises the map when the form is first displayed.

        Steps:
          1. Lock the viewer to suppress intermediate repaints during setup.
          2. Open the California counties shapefile via GisCreateLayer (factory
             that selects the right layer class for the SHP format) and add it
             to the viewer with the logical name "counties".
          3. Create an empty in-memory "buffer" overlay layer (70 % transparent,
             yellow fill).  Assign the viewer's CS so that spatial distances are
             interpreted in the same projection as the county data.
          4. Unlock, zoom to the full data extent, and run the initial buffer
             query by calling ``tmp()`` directly.
        """
        self.GIS.Lock()

        # GisCreateLayer selects the correct TGIS_Layer subclass for the file
        # format and assigns the logical name "counties" used later by GIS.Get
        la = pdk.TGIS_Utils.GisCreateLayer(
            "counties",
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/USA/States/California/Counties.shp"
        )
        self.GIS.Add(la)

        # Buffer overlay: 70 % transparent yellow so the counties show through
        lb = pdk.TGIS_LayerVector()
        lb.Name = "buffer"
        lb.Transparency = 70
        lb.Params.Area.Color = pdk.TGIS_Color().Yellow
        # Sharing the viewer's CS ensures buffer distances are in the same
        # projection (geographic degrees) as the county source data
        lb.CS = self.GIS.CS

        self.GIS.Add(lb)
        self.GIS.Unlock()
        self.GIS.FullExtent()
        # Run the initial buffer query at slider position 0
        self.tmp()

    def btnPlus_click(self, _sender):
        """
        Increments the slider by 25 steps (grows the buffer by 0.25 degrees)
        then immediately triggers a buffer recompute via ``tmp()``.

        A step of 25 is used (rather than 1 as in Buffers1) because the slider
        range is 0..200 and a coarser step provides more responsive interaction.
        """
        self.trackBar1.Position = self.trackBar1.Position + 25
        self.tmp()

    def btnMinus_click(self, _sender):
        """
        Decrements the slider by 25 steps (shrinks the buffer by 0.25 degrees)
        then immediately triggers a buffer recompute via ``tmp()``.
        """
        self.trackBar1.Position = self.trackBar1.Position - 25
        self.tmp()

    def trackBar1_Scroll(self, _sender):
        """
        Called whenever the slider value changes (user drags the thumb).

        Updates the status label with the current distance value so the user
        has immediate feedback while dragging, then calls ``tmp()`` to recompute
        the buffer and intersection results.

        Note: unlike the non-Python editions which use a debounce timer,
        the PDK edition recomputes synchronously on every scroll event.
        """
        # Show the current distance in the status bar while dragging
        self.lblMsg.Caption = str(self.trackBar1.Position) + ' km'
        self.tmp()


def main():
    """
    Application entry point.
    Creates the main form, shows it, and hands control to the PDK event loop.
    """
    frm = Buffers2Form(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
