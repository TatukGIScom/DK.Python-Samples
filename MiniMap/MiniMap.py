import tatukgis_pdk as pdk

class MiniMapForm(pdk.TGIS_PvlForm):
    MINIMAP_NAME = 'minimap_rect'
    MINIMAP_OUTLINE_NAME = 'minimap_rect_outline'
    mini_shp = None
    mini_shp_outline = None
    mini_move = None

    def __init__(self, _owner):
        self.Caption = "MiniMap - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        self.toolbar_buttons.Border = True
        self.toolbar_buttons.Align = "Top"

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "FullExtent"
        self.button1.OnClick = self.btnFullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "ZoomIn"
        self.button2.OnClick = self.btnZoomIn_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 155, None, 3)
        self.button3.Caption = "ZoomOut"
        self.button3.OnClick = self.btnZoomOut_click

        self.button4 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button4.Place(75, 22, None, 230, None, 3)
        self.button4.Caption = "Zoom"
        self.button4.OnClick = self.btnZoom_click

        self.button5 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button5.Place(75, 22, None, 306, None, 3)
        self.button5.Caption = "Dragging"
        self.button5.OnClick = self.btnDrag_click

        self.status_bar_bottom = pdk.TGIS_PvlGroupBox(self.Context)
        self.status_bar_bottom.Place(592, 49, None, 0, self.toolbar_buttons, 350)
        self.status_bar_bottom.Align = "Bottom"

        self.label5 = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.label5.Place(200, 29, None, 10, None, 10)
        self.label5.Caption = ''

        self.status_bar_left = pdk.TGIS_PvlGroupBox(self.Context)
        self.status_bar_left.Place(200, 100, None, 10, self.status_bar_bottom, 0)
        self.status_bar_left.Align = "Bottom"

        self.labelP1 = pdk.TGIS_PvlLabel(self.status_bar_left.Context)
        self.labelP1.Place(200, 19, None, 5, None, 10)
        self.labelP1.Align = "Top"
        self.labelP1.Caption = 'label1'

        self.labelP2 = pdk.TGIS_PvlLabel(self.status_bar_left.Context)
        self.labelP2.Place(200, 19, None, 5, None, 30)
        self.labelP2.Align = "Top"
        self.labelP2.Caption = 'label2'

        self.labelP3 = pdk.TGIS_PvlLabel(self.status_bar_left.Context)
        self.labelP3.Place(200, 19, None, 5, None, 50)
        self.labelP3.Align = "Top"
        self.labelP3.Caption = 'label3'

        self.labelP4 = pdk.TGIS_PvlLabel(self.status_bar_left.Context)
        self.labelP4.Place(200, 19, None, 5, None, 70)
        self.labelP4.Align = "Top"
        self.labelP4.Caption = 'label4'

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.VisibleExtentChangeEvent = self.VisibleExtentChange
        self.GIS.OnMouseMove = self.GISMouseMove
        self.GIS.OnMouseUp = self.GISMouseUp

        self.GISm = pdk.TGIS_ViewerWnd(self.Context)
        self.GISm.Place(200, 100, None, 5, None, 250)
        self.GISm.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)
        self.GISm.OnMouseDown = self.GISmMouseDown
        self.GISm.OnMouseMove = self.GISmMouseMove
        self.GISm.OnMouseUp = self.GISmMouseUp

    def form_show(self, _sender):
        if not self.GIS.IsEmpty:
            return
        self.GIS.Lock()
        self.GISm.Lock()

        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      'World/Countries/Poland/DCW/poland.ttkproject')
        self.GIS.SetCSByEPSG(2180)
        llm = pdk.TGIS_Utils.GisCreateLayer(
            "country",
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/Countries/Poland/DCW/country.shp'
        )
        llm.Params.Area.Color = pdk.TGIS_Color.White
        llm.Params.Area.OutlineColor = pdk.TGIS_Color.Silver
        self.GISm.Add(llm)  # add to minimap
        llm.CachedPaint = False

        lv = pdk.TGIS_LayerVector()  # minimap transparent rectangle
        lv.Transparency = 30
        lv.Params.Area.Color = pdk.TGIS_Color.Red
        lv.Params.Area.OutlineWidth = -2
        lv.Name = self.MINIMAP_NAME
        lv.CS = llm.CS
        self.GISm.Add(lv)
        lv.CachedPaint = False

        self.mini_shp = self.GISm.Get(self.MINIMAP_NAME).CreateShape(
            pdk.TGIS_ShapeType().Polygon
        )

        lw = pdk.TGIS_LayerVector()
        lw.Params.Line.Color = pdk.TGIS_Color.Maroon
        lw.Params.Line.Width = -2
        lw.Name = self.MINIMAP_OUTLINE_NAME
        lw.CS = llm.CS
        self.GISm.Add(lw)
        lw.CachedPaint = False

        self.mini_shp_outline = self.GISm.Get(self.MINIMAP_OUTLINE_NAME).CreateShape(
            pdk.TGIS_ShapeType().Arc
        )

        self.GIS.Unlock()
        self.GISm.Unlock()

        self.GISm.FullExtent()
        self.GIS.FullExtent()

        self.GISm.RestrictedExtent = self.GISm.Extent
        self.mini_shp.Layer.Extent = self.GISm.Extent
        # self.GISm.Cursor = pdk.Cursors.Hand
        self.mini_move = False

    def btnFullExtent_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def miniMapRefresh(self, _sender):
        if self.GIS.IsEmpty:
            return

        ex = self.GISm.CS.ExtentFromCS(self.GIS.CS, self.GIS.VisibleExtent)
        ex = self.GIS.UnrotatedExtent(ex)

        if (ex.XMin < -360) and (ex.XMax > 360) and (ex.YMin < -180) and (ex.YMax > 180):
            return

        ptg1 = pdk.TGIS_Utils.GisPoint(ex.XMin, ex.YMin)
        ptg2 = pdk.TGIS_Utils.GisPoint(ex.XMax, ex.YMin)
        ptg3 = pdk.TGIS_Utils.GisPoint(ex.XMax, ex.YMax)
        ptg4 = pdk.TGIS_Utils.GisPoint(ex.XMin, ex.YMax)

        if self.mini_shp:
            self.mini_shp.Reset()
            self.mini_shp.Lock(pdk.TGIS_Lock().Extent)
            self.mini_shp.AddPart()
            self.mini_shp.AddPoint(ptg1)
            self.mini_shp.AddPoint(ptg2)
            self.mini_shp.AddPoint(ptg3)
            self.mini_shp.AddPoint(ptg4)
            self.mini_shp.Unlock()

        if self.mini_shp_outline:
            self.mini_shp_outline.Reset()
            self.mini_shp_outline.Lock(pdk.TGIS_Lock().Extent)
            self.mini_shp_outline.AddPart()
            self.mini_shp_outline.AddPoint(ptg1)
            self.mini_shp_outline.AddPoint(ptg2)
            self.mini_shp_outline.AddPoint(ptg3)
            self.mini_shp_outline.AddPoint(ptg4)
            self.mini_shp_outline.AddPoint(ptg1)
            self.mini_shp_outline.Unlock()

        self.GISm.InvalidateWholeMap()

    def VisibleExtentChange(self, _sender):
        ex = self.GIS.VisibleExtent
        p1 = pdk.TGIS_Utils.GisPoint(ex.XMin, ex.YMin)
        p2 = pdk.TGIS_Utils.GisPoint(ex.XMax, ex.YMin)
        p3 = pdk.TGIS_Utils.GisPoint(ex.XMax, ex.YMax)
        p4 = pdk.TGIS_Utils.GisPoint(ex.XMin, ex.YMax)
        self.labelP1.Caption = f"P1  x: {p1.X:.4f}  y: {p1.Y:.4f}"
        self.labelP2.Caption = f"P2  x: {p2.X:.4f}  y: {p2.Y:.4f}"
        self.labelP3.Caption = f"P3  x: {p3.X:.4f}  y: {p3.Y:.4f}"
        self.labelP4.Caption = f"P4  x: {p4.X:.4f}  y: {p4.Y:.4f}"

        self.miniMapRefresh(self)

    def GISMouseUp(self, _sender, _button, _shift, _x, _y):
        if self.GIS.IsEmpty:
            return
        self.miniMapRefresh(self)

    def GISMouseMove(self, _sender, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.label5.Caption = f"x: {ptg.X:.4f}  y: {ptg.Y:.4f}"

    def GISmMouseUp(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return
        if not self.mini_move:
            return

        # convert screen coordinates to map coordinates
        ptg = self.GISm.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.mini_shp.SetPosition(ptg, None, 1)

        self.GISm.InvalidateWholeMap()
        self.mini_move = False

        p1 = self.mini_shp.GetPoint(0, 0)
        p2 = self.mini_shp.GetPoint(0, 1)
        p3 = self.mini_shp.GetPoint(0, 2)
        p4 = pdk.TGIS_Point()
        p4.X = p1.X + (p2.X - p1.X) / 2
        p4.Y = p1.Y + (p3.Y - p2.Y) / 2
        self.GIS.Center = self.GISm.CS.ToCS(self.GIS.CS, p4)

    def GISmMouseMove(self, _sender, shift, x, y):
        if self.GIS.IsEmpty:
            return
        if not self.mini_move and "ssCtrl" not in shift:
            return

        ptg = self.GISm.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.mini_shp.SetPosition(ptg, None, 1)

        if "ssShift" in shift:
            self.mini_move = True
            self.GISmMouseUp(_sender, [], shift, x, y)

    def GISmMouseDown(self, _sender, button, _shift, _x, _y):
        if self.GIS.IsEmpty:
            return

        if button == "mRight":
            return

        self.mini_move = True


def main():
    frm = MiniMapForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
