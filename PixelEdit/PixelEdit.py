"""
PixelEdit - demonstrates how to read and modify raster (pixel) layer data
programmatically using TatukGIS (Python PDK edition).

Five operations are shown, each triggered by a dedicated button:

1. Terrain profile (btnProfile)
   Iterates over every pixel that lies under a polyline shape, reading the
   grid elevation value (px.Value) and the cumulative distance along the
   line (px.Distance).  Results are shown in the Memo text area.
   API: TGIS_LayerPixel.Loop(distanceStep, shape, editable)

2. Grid min/max (btnMinMax)
   Finds the pixels with the lowest and highest elevation values inside a
   polygon area.  A temporary vector layer with cross markers is added at
   the two extreme locations so they are visible in the viewer.
   API: TGIS_LayerPixel.Loop(extent, step, shape, mode, editable)

3. Bitmap average colour (btnAverageColor)
   Reads every pixel of a satellite image that falls inside a country
   polygon (Spain, shape #679) to compute the average R, G, B colour.
   It then writes that flat colour back into every pixel of the same
   region, demonstrating read-then-write iteration.
   API: TGIS_PixelItem.Color

4. Create new JPG (btnCreateBitmap)
   Creates a brand-new JPEG raster layer spanning the entire world in
   WGS-84 (EPSG:4326), then uses LockPixels/UnlockPixels to paint a
   square region red by writing directly into the raw bitmap buffer.
   API: TGIS_LayerJPG.Build(), TGIS_LayerPixel.LockPixels(),
        TGIS_LayerPixelLock.Bitmap, TGIS_LayerPixelLock.BitmapPos()

5. Create new GRD (btnCreateGrid)
   Creates a brand-new ESRI Grid raster layer, then fills a region with
   random elevation values using the low-level Grid[][] accessor.
   API: TGIS_LayerGRD.Build(), TGIS_LayerPixelLock.Grid[][]

Key TatukGIS API concepts shown here:
  - TGIS_LayerPixel      : base class for all raster layers
  - TGIS_LayerJPG        : JPEG raster layer subclass; supports Build() and SaveData()
  - TGIS_LayerGRD        : ESRI Grid raster layer subclass; stores float elevations
  - TGIS_PixelItem       : a single raster cell during Loop() iteration; exposes
                           Value (float), Color (TGIS_Color), Center (point),
                           Distance (cumulative distance along profile line)
  - Loop()               : enumerator-based iteration over raster cells;
                           last boolean parameter controls write access
  - LockPixels()         : locks a rectangular region for direct raw-buffer access;
                           must be paired with UnlockPixels()
  - TGIS_LayerPixelLock  : holds the locked pixel buffer and its pixel-space bounds
  - TGIS_CSFactory.ByEPSG: creates a coordinate system from an EPSG code
  - GIS.Lock()/Unlock()  : suspends/resumes map repainting during batch operations
  - TGIS_PvlMemo         : multi-line text widget used here to display results
  - TGIS_PvlControlLegend: layer legend widget docked to the left of the map
"""

import tatukgis_pdk as pdk
import os
from random import random


class PixelEditForm(pdk.TGIS_PvlForm):
    """
    Main form for the PixelEdit sample.
    Provides a toolbar with five action buttons that each demonstrate a
    different aspect of reading or writing raster pixel data via the TatukGIS API.
    """

    def __init__(self, _owner):
        self.Caption = "PixelEdit - TatukGIS Sample"
        self.Left = 200
        self.Top = 120
        self.Width = 651
        self.Height = 504

        # --- Toolbar panel docked to the top of the form ---
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(635, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        # Terrain profile button: reads px.Distance and px.Value along a polyline
        self.btnProfile = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnProfile.Place(120, 22, None, 3, None, 3)
        self.btnProfile.Caption = "Terrain profile"
        self.btnProfile.OnClick = self.btnProfileClick

        # Grid Min/Max button: locates the extreme elevation pixels in a polygon
        self.btnMinMax = pdk.TGIS_PvlButton(self.Context)
        self.btnMinMax.Place(120, 22, None, 123, None, 3)
        self.btnMinMax.Caption = "Grid Min/Max"
        self.btnMinMax.OnClick = self.btnMinMaxClick

        # Bitmap average colour button: read-then-write pixel colour example
        self.btnAverageColor = pdk.TGIS_PvlButton(self.Context)
        self.btnAverageColor.Place(120, 22, None, 243, None, 3)
        self.btnAverageColor.Caption = "Bitmap average color"
        self.btnAverageColor.OnClick = self.btnAverageColorClick

        # Create new JPG button: demonstrates Build() + LockPixels/UnlockPixels
        self.btnCreateBitmap = pdk.TGIS_PvlButton(self.Context)
        self.btnCreateBitmap.Place(120, 22, None, 363, None, 3)
        self.btnCreateBitmap.Caption = "Create a new JPG"
        self.btnCreateBitmap.OnClick = self.btnCreateBitmapClick

        # Create new GRD button: demonstrates Grid[][] accessor for float elevations
        self.btnCreateGrid = pdk.TGIS_PvlButton(self.Context)
        self.btnCreateGrid.Place(120, 22, None, 483, None, 3)
        self.btnCreateGrid.Caption = "Create a new GRD"
        self.btnCreateGrid.OnClick = self.btnCreateGridClick

        # TatukGIS map viewer - fills the centre of the form
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

        # Memo output area docked to the bottom - shows numeric results
        self.Memo1 = pdk.TGIS_PvlMemo(self.Context)
        # self.Memo1.ReadOnly = True
        self.Memo1.AppendLine("Memo")
        self.Memo1.Place(635, 89, None, 0, None, 376)
        self.Memo1.Align = "Bottom"

        # Layer legend panel docked to the left of the map viewer
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(169, 347, None, 0, None, 29)
        self.GIS_legend.Align = "Left"

    def btnProfileClick(self, _sender):
        """
        Reads a terrain elevation profile along a polyline shape.

        Opens the grid project, retrieves the elevation layer and the "line"
        vector layer (shape 1), then iterates over all raster cells that the
        line crosses using Loop(step=0, shape, editable=True).

        px.Distance - cumulative distance along the line to this cell's centre.
        px.Value    - elevation value at this cell.

        As a side effect, each visited pixel's value is zeroed out (px.Value = 0)
        to illustrate that write access is granted when editable=True.
        GIS.InvalidateWholeMap() forces a repaint after the loop.
        """
        self.Memo1.Clear()

        # Load the grid project (contains the DEM and the profile-line vector layer)
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/grid.ttkproject')

        # Retrieve layers by name from the loaded project
        lp = self.GIS.Get("elevation")
        lv = self.GIS.Get("line")
        shp = lv.GetShape(1).MakeEditable()
        shp.IsSelected = True  # Highlight the profile line in the viewer

        try:
            # Loop(step=0, shape, editable=True): step=0 visits every cell
            # the line crosses; editable=True grants write access.
            for px in lp.Loop(0, shp, True):
                self.Memo1.AppendLine(
                    f"Distance: {px.Distance}, Height:{px.Value:.2f})"
                )
                px.Value = 0.  # Zero out each visited cell to demonstrate editing

        finally:
            pass  # EndUpdate equivalent if needed

        self.GIS.InvalidateWholeMap()  # Repaint to reflect zeroed pixel values

    def btnMinMaxClick(self, _sender):
        """
        Finds the minimum and maximum elevation pixels inside a polygon area
        and marks those locations on the map with cross symbols.

        The Loop call uses the "T" (mask) flag to clip iteration to the exact
        polygon boundary rather than its bounding box.  After the scan, a
        temporary TGIS_LayerVector is created in the same CRS as the raster and
        point shapes are added at the min/max locations.  Cross markers with a
        negative size are rendered in screen pixels rather than map units.
        """
        self.Memo1.Clear()
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/grid.ttkproject')

        lp = self.GIS.Get('elevation')
        lv = self.GIS.Get('polygon')
        shp = lv.GetShape(1).MakeEditable()
        shp.IsSelected = True  # Highlight the polygon to show the search area

        # Sentinels: initialise to extreme values so the first real pixel wins
        px_max = -1e38
        px_min = 1e38
        pt_min = None
        pt_max = None

        # Iterate pixels clipped to the polygon boundary ("T" = use shape as mask)
        for px in lp.Loop(shp.Extent, 0, shp, 'T', False):
            if px.Value < px_min:
                px_min = px.Value
                pt_min = px.Center  # Geographic centre of this raster cell

            if px.Value > px_max:
                px_max = px.Value
                pt_max = px.Center

        # Create a temporary in-memory vector layer in the raster's CRS for markers
        l_tmp = pdk.TGIS_LayerVector()
        l_tmp.CS = lp.CS
        self.GIS.Add(l_tmp)

        # Style with cross markers; negative size = screen pixels, not map units
        l_tmp.Params.Marker.Style = pdk.TGIS_MarkerStyle().Cross
        l_tmp.Params.Marker.Size = -10
        l_tmp.Params.Marker.Color = pdk.TGIS_Color.Black

        # Add point shapes at the extreme locations
        shp_tmp = l_tmp.CreateShape(pdk.TGIS_ShapeType().Point)
        shp_tmp.AddPart()
        shp_tmp.AddPoint(pt_min)

        shp_tmp = l_tmp.CreateShape(pdk.TGIS_ShapeType().Point)
        shp_tmp.AddPart()
        shp_tmp.AddPoint(pt_max)

        self.GIS.InvalidateWholeMap()  # Force repaint to show the new markers

        self.Memo1.AppendLine(
            f"Min: {px_min:.2f}, Location: {pt_min.X:.2f}, {pt_min.Y:.2f}"
        )
        self.Memo1.AppendLine(
            f"Max: {px_max:.2f}, Location: {pt_max.X:.2f}, {pt_max.Y:.2f}"
        )

    def btnAverageColorClick(self, _sender):
        """
        Computes the average pixel colour inside Spain and paints the whole region
        with that colour, demonstrating read-then-write pixel iteration.

        Two passes are made over the Blue Marble satellite image pixels:
          1. Read pass (editable=False): accumulate R, G, B channel sums.
          2. Write pass (editable=True): replace every pixel with the average.

        GIS.Lock()/Unlock() suppress intermediate screen updates while the view
        is panned and zoomed to Spain.  px.Color = cl flushes the write immediately.
        """
        self.Memo1.Clear()

        # Open the Blue Marble satellite imagery project
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/bitmap.ttkproject')

        # Retrieve the raster layer and the country polygon layer
        lp = self.GIS.Get('bluemarble')
        lv = self.GIS.Get('countries')

        # Shape 679 is Spain; MakeEditable() returns a writable copy
        shp = lv.GetShape(679).MakeEditable()  # Spain

        # Suppress repaints while repositioning the viewport
        self.GIS.Lock()
        self.GIS.VisibleExtent = shp.ProjectedExtent
        self.GIS.Zoom = self.GIS.Zoom / 2.0  # Zoom out slightly for context
        self.GIS.Unlock()

        cnt = 0
        r = 0
        g = 0
        b = 0

        # First pass: accumulate R, G, B values for all pixels inside Spain
        # "T" = clip iteration to the polygon boundary (not just its bounding box)
        for px in lp.Loop(shp.Extent, 0, shp, 'T', False):
            r += px.Color.R  # Red channel (0-255)
            g += px.Color.G  # Green channel (0-255)
            b += px.Color.B  # Blue channel (0-255)
            cnt += 1

        if cnt > 0:
            # Build the average colour from the accumulated sums
            cl = pdk.TGIS_Color.FromRGB(int(r/cnt), int(g/cnt), int(b/cnt))

            # Second pass: write the average colour back to every pixel inside Spain.
            # editable=True grants write access; px.Color = cl flushes immediately.
            for px in lp.Loop(shp.Extent, 0, shp, 'T', True):
                px.Color = cl

        self.GIS.InvalidateWholeMap()  # Repaint to show the modified imagery

    def btnCreateBitmapClick(self, _sender):
        """
        Creates a new JPEG raster layer from scratch and paints a rectangular
        region red using the low-level LockPixels interface.

        Build() defines the file path, coordinate system (EPSG:4326 = WGS-84),
        geographic extent (the whole world), and pixel dimensions (360x180).

        LockPixels() returns a TGIS_LayerPixelLock whose Bitmap provides array-
        style access to the raw pixel buffer.  Bitmap.Value(index, argb) sets a
        pixel; BitmapPos(x, y) computes the flat array index from 2-D coordinates.

        UnlockPixels() must always be called (in a finally block) to flush the
        writes and release the lock before SaveData() persists the file.
        """
        self.GIS.Close()
        self.Memo1.Clear()

        test_jpg = "test.jpg"
        if os.path.exists(test_jpg):
            os.remove(test_jpg)  # Remove any stale file from a previous run

        lp = pdk.TGIS_LayerJPG()

        # Build() creates the JPEG file with the given georeferencing and dimensions
        lp.Build(
            test_jpg,
            pdk.TGIS_CSFactory.ByEPSG(4326),                 # WGS-84 geographic CRS
            pdk.TGIS_Utils().GisExtent(-180, -90, 180, 90),   # Whole world
            360,                                               # Pixel width
            180                                                # Pixel height
        )

        # Lock a 90x90-degree sub-region centred on the equator for write access
        lck = lp.LockPixels(pdk.TGIS_Utils.GisExtent(-45, -45, 45, 45), lp.CS, True)
        try:
            # Iterate every pixel in the locked bounds and write solid red.
            # range() uses +1 on the Right/Bottom bounds to be inclusive.
            # TGIS_Color().Red.ARGB is the 32-bit ARGB integer for opaque red.
            for x in range(lck.Bounds.Left, lck.Bounds.Right+1):
                for y in range(lck.Bounds.Top, lck.Bounds.Bottom+1):
                    lck.Bitmap.Value(lck.BitmapPos(x, y), pdk.TGIS_Color().Red.ARGB)

        finally:
            # UnlockPixels() flushes buffered writes and releases the lock.
            lp.UnlockPixels(lck)

        lp.SaveData()        # Write the modified JPEG data to disk
        self.GIS.Open(test_jpg)  # Display the newly created image

    def btnCreateGridClick(self, _sender):
        """
        Creates a new ESRI Grid raster layer from scratch and fills a region with
        random elevation values using the low-level Grid[][] accessor.

        The ESRI Grid format stores continuous floating-point values (e.g. elevations)
        rather than RGB colours.  The locked region is accessed via Grid[y][x]
        (row-major storage: first index = row = y, second = column = x).
        An alternative PDK syntax is lck.Grid.Value(y, x, value).

        The workflow mirrors btnCreateBitmapClick: Build -> LockPixels -> write
        -> UnlockPixels -> SaveData -> Open.
        """
        self.GIS.Close()
        self.Memo1.Clear()

        test_grd = "test.grd"
        if os.path.exists(test_grd):
            os.remove(test_grd)  # Remove stale file from a previous run

        lp = pdk.TGIS_LayerGRD()

        # Build the GRD file with the same world-extent georeferencing as the JPG above
        lp.Build(
            test_grd,
            pdk.TGIS_CSFactory.ByEPSG(4326),                 # WGS-84 geographic CRS
            pdk.TGIS_Utils().GisExtent(-180, -90, 180, 90),   # Whole world
            360,                                               # Pixel width
            180                                                # Pixel height
        )

        # Lock the central sub-region for write access
        lck = lp.LockPixels(pdk.TGIS_Utils.GisExtent(-45, -45, 45, 45), lp.CS, True)
        try:
            for x in range(lck.Bounds.Left, lck.Bounds.Right+1):
                for y in range(lck.Bounds.Top, lck.Bounds.Bottom+1):
                    # Grid[y][x] = row-major storage; random() in [0,1) scaled to [0,100)
                    lck.Grid[y][x] = 100*random()
                    # Alternative PDK syntax: lck.Grid.Value(y, x, 100*random())
        finally:
            lp.UnlockPixels(lck)  # Flush writes and release the lock

        lp.SaveData()            # Persist the grid data to disk
        self.GIS.Open(test_grd)  # Display the newly created grid


def main():
    """Creates the PixelEdit form, shows it, and starts the PDK event loop."""
    frm = PixelEditForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
