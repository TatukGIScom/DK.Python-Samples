"""
CustomPaint sample - demonstrates how to perform custom drawing on top of a
TatukGIS map viewer using two complementary paint-hook mechanisms in Python
with the TatukGIS Python Developer Kernel (PDK).

Key concepts demonstrated:
  PaintShapeEvent
    Registered on a TGIS_LayerVector via ``ll.PaintShapeEvent = handler``.
    The callback fires once for every shape in that layer during each repaint
    cycle and completely replaces the layer's default rendering for those shapes.
    The handler converts the shape's geographic position to screen pixels with
    ``GIS.MapToScreen(shape.PointOnShape())`` and then draws primitives using
    TGIS_RendererAbstract Canvas* methods (CanvasDrawRectangle, CanvasDrawEllipse,
    CanvasDrawBitmap, CanvasDrawText).

  PaintExtraEvent (GIS_PaintExtraEvent module-level function)
    Wired to ``self.GIS.PaintExtraEvent`` in the form constructor.  It fires
    once after all layers have been rendered.  This is the correct place for
    full-frame overlays (watermarks, HUD elements) that must always appear on
    top.  The handler uses CanvasFont and CanvasDrawText via the abstract
    renderer, demonstrating the preferred portable drawing approach.

Layer layout:
  One TGIS_LayerVector ("CustomPaint") with four invisible point shapes
  (Marker.Size = 0) placed at the four geographic quadrants.  A "type"
  string field selects the drawing primitive in GIS_PaintShapeEvent:
    "Rectangle" at (-25,  25) -> CanvasDrawRectangle (red border, yellow fill)
    "Ellipse"   at ( 25,  25) -> CanvasDrawEllipse   (black border, red fill)
    "Image1"    at (-25, -25) -> CanvasDrawBitmap(TGIS_Bitmap from police.bmp)
    "Image2"    at ( 25, -25) -> CanvasDrawBitmap(TGIS_Pixels raw ARGB buffer)

Raw pixel buffer (px):
  A 5x5 ARGB pixel image stored in a TGIS_Pixels object:
    Index 0-4:  opaque red   (0xFFFF0000)
    Diagonal column 2 [7],[12],[17],[22]: opaque blue (0xFF0000FF)
    All other indices: fully transparent (0x00000000)
  Format: TGIS_BitmapFormat().ARGB (0xAARRGGBB per element, alpha in high byte).
  Line order: TGIS_BitmapLinesOrder().Down (scanlines run top-to-bottom).
"""

import tatukgis_pdk as pdk


def GIS_PaintExtraEvent(_sender, renderer, _mode):
    """
    PaintExtraEvent callback - fires once per frame after all layers have
    finished rendering.

    This function is registered on the GIS viewer in CustomPaintForm.__init__
    via ``self.GIS.PaintExtraEvent = GIS_PaintExtraEvent``.

    Unlike PaintShapeEvent (which is per-shape), this callback fires exactly
    once per frame and is the right place for overlays that must appear on
    top of all layer content.

    Here we use TGIS_RendererAbstract Canvas methods (CanvasFont, CanvasDrawText)
    which are backend-agnostic and work regardless of the active renderer.
    This is the recommended approach - direct access to native canvas handles
    (Graphics2D, Direct2D, etc.) is possible but not portable.

    Args:
        _sender:  The viewer object that fired the event (unused here).
        renderer: The active TGIS_RendererAbstract instance.  Use its
                  Canvas* methods or CanvasNative for native access.
        _mode:    TGIS_DrawMode hint (full vs incremental repaint).
    """
    # Build a screen-pixel rectangle for the overlay text position
    rct = pdk.TRect()
    rct.Left = 50
    rct.Top = 50
    rct.Width = 100
    rct.Height = 100
    # Set font size via the abstract renderer's CanvasFont property
    renderer.CanvasFont.Size = 10
    # CanvasDrawText draws text within the given rectangle using the current
    # font and pen settings.  This call is backend-agnostic.
    renderer.CanvasDrawText(rct, "Hello Renderer")


class CustomPaintForm(pdk.TGIS_PvlForm):
    """
    Main application form for the CustomPaint sample.

    Hosts a TGIS_ViewerWnd and demonstrates custom drawing via PaintShapeEvent
    (per-shape) and PaintExtraEvent (per-frame) callbacks using the TatukGIS
    abstract renderer API.

    Class-level attributes:
        bmp: TGIS_Bitmap loaded from police.bmp for the Image1 drawing case.
        ll:  The "CustomPaint" TGIS_LayerVector containing the four demo shapes.
        px:  TGIS_Pixels raw ARGB buffer (5x5) for the Image2 drawing case.
    """

    bmp = pdk.TGIS_Bitmap()    # bitmap wrapper for the Image1 case (file-backed)
    ll = pdk.TGIS_LayerVector()  # the single demo layer
    px = pdk.TGIS_Pixels()     # raw pixel buffer for the Image2 case

    def __init__(self, _owner):
        """
        Constructs the form layout.

        The GIS viewer anchors to all four edges so it fills the client area
        below the toolbar.  PaintExtraEvent is wired to the module-level
        function GIS_PaintExtraEvent so it fires once per frame.
        form_show is deferred until the form is actually displayed (OnShow)
        so that the viewer's extent is valid before shapes are added.
        """
        self.Caption = "CustomPaint - TatukGIS DK Sample"
        self.ClientWidth = 784
        self.ClientHeight = 561
        # Defer layer initialisation to form_show so the viewer is fully sized
        self.OnShow = self.form_show

        # Main GIS viewer: anchor to all four edges to fill the client area
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 41
        self.GIS.Height = 520
        self.GIS.Width = 784
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        # Register the per-frame paint callback.
        # GIS_PaintExtraEvent fires once after all layers have been drawn.
        self.GIS.PaintExtraEvent = GIS_PaintExtraEvent

    def form_show(self, _sender):
        """
        OnShow handler - builds the data model and populates the layer.

        Called when the form becomes visible.  At this point the viewer has a
        valid size so GIS.Extent is meaningful and FullExtent() will fit all
        four shapes on screen.

        Pixel buffer initialisation:
          px is a TGIS_Pixels COM buffer (25 elements = 5x5 grid).
          Values are ARGB-encoded 32-bit integers:
            0xFFFF0000 = opaque red
            0xFF0000FF = opaque blue
            0x00000000 = fully transparent

        Layer construction:
          Four invisible point shapes (Marker.Size=0) are added at the four
          map quadrants.  Lock(Extent)/Unlock prevents the layer from
          automatically expanding its stored extent during construction.
          The "type" string field value selects the drawing primitive in
          GIS_PaintShapeEvent.
        """
        # --- Initialise the raw ARGB pixel buffer for Image2 ---
        # 25 elements = 5 columns x 5 rows, row-major order.
        self.px.SetLength(25)
        # Row 0: five opaque red pixels
        self.px[0] = 0xFFFF0000
        self.px[1] = 0xFFFF0000
        self.px[2] = 0xFFFF0000
        self.px[3] = 0xFFFF0000
        self.px[4] = 0xFFFF0000
        # Row 1: transparent except column 2 (opaque blue)
        self.px[5] = 0x00000000
        self.px[6] = 0x00000000
        self.px[7] = 0xFF0000FF   # opaque blue diagonal pixel
        self.px[8] = 0x00000000
        self.px[9] = 0x00000000
        # Row 2
        self.px[10] = 0x00000000
        self.px[11] = 0x00000000
        self.px[12] = 0xFF0000FF
        self.px[13] = 0x00000000
        self.px[14] = 0x00000000
        # Row 3
        self.px[15] = 0x00000000
        self.px[16] = 0x00000000
        self.px[17] = 0xFF0000FF
        self.px[18] = 0x00000000
        self.px[19] = 0x00000000
        # Row 4
        self.px[20] = 0x00000000
        self.px[21] = 0x00000000
        self.px[22] = 0xFF0000FF
        self.px[23] = 0x00000000
        self.px[24] = 0x00000000

        # --- Build the "CustomPaint" layer ---
        self.ll.Name = "CustomPaint"
        self.GIS.Add(self.ll)

        # Register the per-shape paint callback.
        # GIS_PaintShapeEvent fires once per shape per repaint,
        # replacing the layer's default rendering.
        self.ll.PaintShapeEvent = self.GIS_PaintShapeEvent

        # Add the "type" attribute field read by the paint callback
        self.ll.AddField("type", pdk.TGIS_FieldType().String, 100, 0)
        self.ll.Extent = self.GIS.Extent

        # --- Create the four invisible demo point shapes ---
        # Lock(Extent) freezes extent expansion during shape construction;
        # Unlock() releases it after AddPoint.

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(-25, 25))  # NW quadrant
        shp.Params.Marker.Size = 0   # invisible; all visuals from custom paint
        shp.SetField("type", "Rectangle")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(25, 25))   # NE quadrant
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Ellipse")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(-25, -25)) # SW quadrant
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Image1")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(25, -25))  # SE quadrant
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Image2")
        shp.Unlock()

        # Set the layer extent to enclose all four shapes
        self.ll.Extent = pdk.TGIS_Utils.GisExtent(-100, -100, 100, 100)

        # Load the file-based bitmap used by the Image1 drawing case.
        # TGIS_Bitmap is TatukGIS's cross-renderer bitmap wrapper.
        self.bmp = pdk.TGIS_Bitmap()
        self.bmp.LoadFromFile(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/police.bmp")

        # Fit the viewer to the full extent of all layers
        self.GIS.FullExtent()

    def GIS_PaintShapeEvent(self, _sender, shape: pdk.TGIS_Shape):
        """
        PaintShapeEvent callback - called once per shape per repaint pass.

        Replaces default rendering for every shape in the "CustomPaint" layer.
        ``self.GIS.MapToScreen(shape.PointOnShape())`` converts the shape's
        geographic coordinates to screen pixel coordinates inside the viewer.

        The handler then calls ``shape.Draw()`` to run any remaining default
        rendering hooks (a no-op for Marker.Size=0 shapes, but good practice),
        obtains the abstract renderer from the shape's layer, and selects a
        drawing primitive based on the "type" attribute field.

        All pixel coordinates and sizes are in screen pixels; the 20x20 size
        is fixed and does not scale with the map zoom level.

        Drawing cases:
            "Rectangle" - yellow-filled, red-bordered 20x20 box with a label
                          20 pixels above it.
            "Ellipse"   - red-filled, black-bordered ellipse with a label above.
            "Image1"    - TGIS_Bitmap (police.bmp) stretched to 20x20 with label.
            "Image2"    - TGIS_Pixels raw ARGB buffer stretched to 20x20 with label.
                          TPoint(5,5) as the source offset skips the first 5
                          pixels (the solid-red row) to start at the diagonal.

        Args:
            _sender: The layer that fired the event (unused here).
            shape:   The TGIS_Shape currently being painted.
        """
        # Convert the shape's geographic position to screen-pixel coordinates.
        pt = self.GIS.MapToScreen(shape.PointOnShape())
        # Run any remaining default rendering hooks (no-op for Size=0 markers).
        shape.Draw()
        # Obtain the abstract renderer from the shape's owning layer.
        rdr = shape.Layer.Renderer

        # --- Select drawing primitive by "type" attribute field ---

        if shape.GetField("type") == "Rectangle":
            # Yellow-filled, red-bordered rectangle at the shape's screen position
            rdr.CanvasPen.Color = pdk.TGIS_Color().Red
            rdr.CanvasBrush.Color = pdk.TGIS_Color().Yellow
            # Build and draw a 20x20 pixel TRect at the shape's screen position.
            # TRect uses (Left, Top, Width, Height) in the PDK.
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 20
            rct.Height = 20
            rdr.CanvasDrawRectangle(rct)
            # Draw label 20 pixels above the rectangle
            pt.Y = pt.Y - 20
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 50
            rct.Height = 20
            rdr.CanvasDrawText(rct, "Rectangle")

        elif shape.GetField("type") == "Ellipse":
            # Red-filled, black-bordered ellipse; width=20, height=20
            rdr.CanvasPen.Color = pdk.TGIS_Color().Black
            rdr.CanvasBrush.Color = pdk.TGIS_Color().Red
            rdr.CanvasDrawEllipse(pt.X, pt.Y, 20, 20)
            pt.Y = pt.Y - 20
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 50
            rct.Height = 20
            rdr.CanvasDrawText(rct, "Ellipse")

        elif shape.GetField("type") == "Image1":
            # Stretch TGIS_Bitmap (police.bmp) into a 20x20 destination rectangle.
            # TGIS_Bitmap is the TatukGIS cross-renderer bitmap wrapper; it is
            # automatically converted to the appropriate format by the renderer.
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 20
            rct.Height = 20
            rdr.CanvasDrawBitmap(self.bmp, rct)
            pt.Y = pt.Y - 20
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 50
            rct.Height = 20
            rdr.CanvasDrawText(rct, "Image1")

        elif shape.GetField("type") == "Image2":
            # Draw using a raw TGIS_Pixels ARGB buffer.
            # TPoint(5, 5) = source offset: skip the first 5 pixels (red row),
            #   start reading from pixel (5, 5) in the source buffer.
            # TGIS_BitmapFormat().ARGB = pixel layout 0xAARRGGBB per element.
            # TGIS_BitmapLinesOrder().Down = scanlines run top-to-bottom.
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 20
            rct.Height = 20
            rdr.CanvasDrawBitmap(
                self.px,
                pdk.TPoint(5, 5),
                rct,
                pdk.TGIS_BitmapFormat().ARGB,
                pdk.TGIS_BitmapLinesOrder().Down
            )
            pt.Y = pt.Y - 20
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 50
            rct.Height = 20
            rdr.CanvasDrawText(rct, "Image2")


def main():
    """
    Application entry point.  Creates the CustomPaintForm, displays it,
    and starts the PDK event loop.
    """
    frm = CustomPaintForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
