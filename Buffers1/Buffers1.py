# =============================================================================
# Buffers1 - TatukGIS DK11 Python (PDK) sample
# =============================================================================
#
# Demonstrates how to compute a spatial buffer around a selected vector shape
# using the TatukGIS Developer Kernel (PDK) for Python.
#
# What the sample shows:
#   - Building a simple windowed GIS application using TGIS_PvlForm and the
#     PDK panel / widget helpers
#   - Opening a vector shapefile in TGIS_ViewerWnd
#   - Creating a transparent in-memory overlay layer (TGIS_LayerVector) to
#     hold the buffer result polygon
#   - Selecting a source shape by clicking on the map via GIS.OnMouseDown
#     (GIS.ScreenToMap + GIS.Locate)
#   - Using TGIS_Topology.MakeBuffer to compute a planar buffer polygon
#   - Controlling the buffer distance (-50..+50 km) with a TGIS_PvlTrackBar.
#     Negative values produce an inward (erosion) buffer.
#   - Updating the buffer polygon each time the slider position changes
#     (RevertShapes + AddShape)
#
# Key TatukGIS PDK types used:
#   TGIS_ViewerWnd    - map display widget
#   TGIS_LayerVector  - in-memory or file-backed vector layer
#   TGIS_Topology     - spatial operations engine (MakeBuffer, etc.)
#   TGIS_Shape        - a single geographic feature
#   TGIS_Utils        - utility helpers (GisSamplesDataDirDownload, etc.)
#   TGIS_PvlForm      - base class for PDK application windows
#   TGIS_PvlPanel     - container panel widget
#   TGIS_PvlTrackBar  - slider control
#   TGIS_PvlButton    - push-button widget
#   TGIS_PvlLabel     - static text label
# =============================================================================

import tatukgis_pdk as pdk


class Buffers1Form(pdk.TGIS_PvlForm):
    """
    Main form for the Buffers1 sample.

    Loads a topology shapefile, lets the user click a shape to select it,
    then draws a buffer polygon around it at a distance chosen via a slider
    (-50..+50 km).  The selected shape's Uid is kept in ``shp_id`` so the
    correct shape can be retrieved when the slider is moved.
    """

    # shp_id stores the Uid of the currently selected source shape.
    # Initialised to None; set to 2 (the second shape) in form_show so that
    # a default buffer is visible before the user clicks anything.
    shp_id = None

    def __init__(self, _owner):
        # ── Form geometry and caption ─────────────────────────────────────────
        self.Caption = "Buffers1 - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 422
        # form_show is called once when the window is first displayed
        self.OnShow = self.form_show

        # ── Toolbar panel (top strip) ─────────────────────────────────────────
        # A panel that hosts the minus button, slider, and plus button in a row
        # at the top of the window.
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        # Minus button: decrements the slider by 1 step (shrinks the buffer)
        self.btnMinus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnMinus.Place(22, 22, None, 10, None, 3)
        self.btnMinus.Caption = " - "
        self.btnMinus.OnClick = self.btnMinus_click

        # Slider: controls the buffer distance in kilometres (-50..+50)
        self.trackBar1 = pdk.TGIS_PvlTrackBar(self.toolbar_buttons.Context)
        self.trackBar1.Place(169, 33, None, 33, None, 6)
        self.trackBar1.OnChange = self.trackBar1_Scroll
        self.trackBar1.Maximum = 50
        self.trackBar1.Minimum = -50

        # Plus button: increments the slider by 1 step (grows the buffer)
        self.btnPlus = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPlus.Place(22, 22, None, 203, None, 3)
        self.btnPlus.Caption = " + "
        self.btnPlus.OnClick = self.btnPlus_click

        # ── Map viewer ────────────────────────────────────────────────────────
        # TGIS_ViewerWnd is the main map display; it occupies the centre of the
        # form below the toolbar.
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 366
        self.GIS.OnMouseDown = self.GISMouseDown
        # OnClick is also wired to btnPlus_click here; this appears to be a
        # placeholder / legacy wire-up that is effectively a no-op for normal
        # map interaction.
        self.GIS.OnClick = self.btnPlus_click

        # ── Status bar (bottom panel) ─────────────────────────────────────────
        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        # Instruction label shown at the bottom of the window
        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Click on shapes to choose one for buffer creation"

    def form_show(self, _sender):
        """
        Initialises the map when the form is first displayed.

        Steps:
          1. Pre-select shape Uid 2 as the default buffer source.
          2. Create an empty in-memory "buffer" overlay layer (50 % transparent,
             red fill) so that the buffer result is visually distinct from the
             source shapes.
          3. Lock the viewer, open the topology sample shapefile, add the buffer
             layer, then unlock and zoom to the full data extent.
        """
        # Default shape selection so a buffer is available before the user clicks
        self.shp_id = 2

        # Buffer overlay: 50 % transparent so the underlying county layer shows through
        lb = pdk.TGIS_LayerVector()
        lb.Name = "buffer"
        lb.Transparency = 50
        lb.Params.Area.Color = pdk.TGIS_Color().Red

        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Topology/topology.shp")
        self.GIS.Add(lb)
        self.GIS.Unlock()
        self.GIS.FullExtent()

    def GISMouseDown(self, _sender, _button, _shift, x, y):
        """
        Handles mouse-press events on the map to select the buffer source shape.

        Converts the pixel position (x, y) to map coordinates via
        GIS.ScreenToMap, then calls GIS.Locate with a 5-pixel tolerance
        (in map units = 5.0 / GIS.Zoom) to find the topmost shape under the
        cursor.  The shape's Uid is stored in ``shp_id`` and the shape briefly
        flashes to give the user visual confirmation of the selection.
        """
        if self.GIS.IsEmpty:
            return

        # Convert screen pixel coordinates to map (geographic) coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        # Locate the nearest shape within 5 pixels of the click point
        shp = self.GIS.Locate(ptg, 5.0 / self.GIS.Zoom)

        if shp is not None:
            self.shp_id = shp.Uid   # remember for use in trackBar1_Scroll
            shp.Flash()             # brief visual highlight to confirm selection

    def btnPlus_click(self, _sender):
        """
        Increments the slider position by 1 step (increases buffer distance).
        The OnChange event fires automatically, which triggers trackBar1_Scroll.
        """
        self.trackBar1.Position = self.trackBar1.Position + 1

    def btnMinus_click(self, _sender):
        """
        Decrements the slider position by 1 step (decreases buffer distance).
        The OnChange event fires automatically, which triggers trackBar1_Scroll.
        """
        self.trackBar1.Position = self.trackBar1.Position - 1

    def trackBar1_Scroll(self, _sender):
        """
        Recomputes the buffer polygon each time the slider value changes.

        Algorithm:
          1. Retrieve the source layer (index 0) and the "buffer" overlay layer.
          2. Fetch the previously selected shape by its stored Uid.
          3. Clear the buffer layer (RevertShapes) then call
             TGIS_Topology.MakeBuffer with the distance in metres.
             ``trackBar1.Position * 1000`` converts the kilometre value to metres;
             negative values produce an inward (erosion) buffer.
          4. Add the new result to the buffer layer and refresh the view.
        """
        # Retrieve layers; bail out if either is unavailable
        ll = self.GIS.Items[0]
        if ll is None:
            return

        lb = self.GIS.Get("buffer")
        if lb is None:
            return

        # Retrieve the currently selected shape by its stored Uid
        shp = ll.GetShape(self.shp_id)
        if shp is None:
            return

        # Compute the buffer polygon using the topology engine
        tpl = pdk.TGIS_Topology()
        lb.RevertShapes()  # discard the previous buffer polygon
        # MakeBuffer distance is in metres; slider position is in kilometres
        tmp = tpl.MakeBuffer(shp, self.trackBar1.Position * 1000)
        if tmp is not None:
            lb.AddShape(tmp)  # store the new buffer polygon in the overlay layer

        # Recalculate the layer extents and redraw
        lb.RecalcExtent()
        self.GIS.FullExtent()


def main():
    """
    Application entry point.
    Creates the main form, shows it, and hands control to the PDK event loop.
    """
    frm = Buffers1Form(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
