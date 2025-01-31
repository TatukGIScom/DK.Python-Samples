import tatukgis_pdk as pdk

def GIS_PaintExtraEvent(_sender, renderer, _mode):
    rct = pdk.TRect()
    rct.Left = 50
    rct.Top = 50
    rct.Width = 100
    rct.Height = 100
    renderer.CanvasFont.Size = 10
    renderer.CanvasDrawText(rct, "Hello Renderer")


class CustomPaintForm(pdk.TGIS_PvlForm):
    bmp = pdk.TGIS_Bitmap()
    ll = pdk.TGIS_LayerVector()
    px = pdk.TGIS_Pixels()

    def __init__(self, _owner):
        self.Caption = "CustomPaint - TatukGIS DK Sample"
        self.ClientWidth = 784
        self.ClientHeight = 561
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 41
        self.GIS.Height = 520
        self.GIS.Width = 784
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.PaintExtraEvent = GIS_PaintExtraEvent

    def form_show(self, _sender):
        self.px.SetLength(25)
        self.px[0] = 0xFFFF0000
        self.px[1] = 0xFFFF0000
        self.px[2] = 0xFFFF0000
        self.px[3] = 0xFFFF0000
        self.px[4] = 0xFFFF0000
        self.px[5] = 0x00000000
        self.px[6] = 0x00000000
        self.px[7] = 0xFF0000FF
        self.px[8] = 0x00000000
        self.px[9] = 0x00000000
        self.px[10] = 0x00000000
        self.px[11] = 0x00000000
        self.px[12] = 0xFF0000FF
        self.px[13] = 0x00000000
        self.px[14] = 0x00000000
        self.px[15] = 0x00000000
        self.px[16] = 0x00000000
        self.px[17] = 0xFF0000FF
        self.px[18] = 0x00000000
        self.px[19] = 0x00000000
        self.px[20] = 0x00000000
        self.px[21] = 0x00000000
        self.px[22] = 0xFF0000FF
        self.px[23] = 0x00000000
        self.px[24] = 0x00000000

        self.ll.Name = "CustomPaint"

        self.GIS.Add(self.ll)

        self.ll.PaintShapeEvent = self.GIS_PaintShapeEvent

        self.ll.AddField("type", pdk.TGIS_FieldType().String, 100, 0)
        self.ll.Extent = self.GIS.Extent

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(-25, 25))
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Rectangle")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(25, 25))
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Ellipse")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(-25, -25))
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Image1")
        shp.Unlock()

        shp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(25, -25))
        shp.Params.Marker.Size = 0
        shp.SetField("type", "Image2")
        shp.Unlock()

        self.ll.Extent = pdk.TGIS_Utils.GisExtent(-100, -100, 100, 100)

        self.bmp = pdk.TGIS_Bitmap()
        self.bmp.LoadFromFile(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/police.bmp")

        self.GIS.FullExtent()

    def GIS_PaintShapeEvent(self, _sender, shape: pdk.TGIS_Shape):
        pt = self.GIS.MapToScreen(shape.PointOnShape())
        shape.Draw()
        rdr = shape.Layer.Renderer

        # Drawing with our renderer
        if shape.GetField("type") == "Rectangle":
            rdr.CanvasPen.Color = pdk.TGIS_Color().Red
            rdr.CanvasBrush.Color = pdk.TGIS_Color().Yellow
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 20
            rct.Height = 20
            rdr.CanvasDrawRectangle(rct)
            pt.Y = pt.Y - 20
            rct = pdk.TRect()
            rct.Left = pt.X
            rct.Top = pt.Y
            rct.Width = 50
            rct.Height = 20
            rdr.CanvasDrawText(rct, "Rectangle")

        elif shape.GetField("type") == "Ellipse":
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
    frm = CustomPaintForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
