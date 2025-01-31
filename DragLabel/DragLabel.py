import tatukgis_pdk as pdk
from random import randint
from time import sleep

class DragLabelForm(pdk.TGIS_PvlForm):
    NAME_REALPOINTS = "realpoints"
    NAME_SIDEKICKS = "sidekicks"
    FIELD_NAME = "name"
    LABEL_TEXT = "Ship"
    currShape = None

    def __init__(self, _owner):
        self.Caption = "Drag Label - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show
        
        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        self.button1 = pdk.TGIS_PvlButton(self.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Animate"
        self.button1.OnClick = self.animate_click

        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(592, 19, None, 0, None, 454)
        
        self.status_label = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.status_label.Place(100, 19, None, 3, None, 0)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.OnMouseDown = self.GIS_MouseDown
        self.GIS.OnMouseMove = self.GIS_MouseMove
        self.GIS.OnMouseUp = self.GIS_MouseUp

    def is_gis_empty(self) -> bool:
        if self.GIS.IsEmpty:
            pdk.TGIS_PvlMessages.ShowInfo("Create a layer first !", self.Context)
            return True
        return False

    def doLabelPaint(self, _sender, _shape):
        ll = self.GIS.Items[0]
        shp = ll.GetShape(_shape.Uid)
        pt_a = _shape.Viewer.Ref.MapToScreen(shp.GetPoint(0, 0))
        pt_b = _shape.Viewer.Ref.MapToScreen(_shape.GetPoint(0, 0))

        rdr = _shape.Layer.Renderer

        rdr.CanvasPen.Color = pdk.TGIS_Color.Blue
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rdr.CanvasPen.Width = 1
        rdr.CanvasDrawLine(pt_a.X, pt_a.Y, pt_b.X, pt_b.Y)

        # draw label itself
        _shape.Params.Labels.Value = shp.GetField(self.FIELD_NAME)
        _shape.DrawLabel()

    def form_show(self, _sender):
        # create real point layer
        ll = pdk.TGIS_LayerVector()
        symbol_list = pdk.TGIS_Utils().SymbolList
        ll.Params.Marker.Symbol = symbol_list.Prepare(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Symbols/2267.cgm"
        )
        ll.Name = self.NAME_REALPOINTS
        ll.CachedPaint = False
        
        self.GIS.Add(ll)
        ll.AddField(self.FIELD_NAME, pdk.TGIS_FieldType().String, 100, 0)
        ll.Extent = pdk.TGIS_Utils.GisExtent(-180, -180, 180, 180)

        # create display sidekick
        ll = pdk.TGIS_LayerVector()
        ll.Name = self.NAME_SIDEKICKS
        ll.Params.Marker.Size = 0
        ll.Params.Labels.Position = [pdk.TGIS_LabelPosition().MiddleCenter]
        ll.CachedPaint = False

        self.GIS.Add(ll)
        ll.PaintShapeLabelEvent = self.doLabelPaint
        ll.Params.Labels.Allocator = False

        # add points
        shp_type = pdk.TGIS_ShapeType().Point
        lv = self.GIS.Items[0]
        lv_sidekicks = self.GIS.Get(self.NAME_SIDEKICKS)
        
        # fill the viewer with points
        for _ in range(20):
            ptg = pdk.TGIS_Utils.GisPoint(randint(0, 360) - 180,
                                          randint(0, 180) - 90)

            color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                           randint(0, 255),
                                           randint(0, 255))

            shp = lv.CreateShape(shp_type)
            shp.Lock(pdk.TGIS_Lock().Extent)
            try:
                shp.AddPart()
                shp.AddPoint(ptg)
                shp.Params.Marker.SymbolRotate = float(shp.Uid)
                shp.Params.Marker.Color = color
                shp.Params.Marker.Size = 250
                shp.Params.Marker.OutlineColor = color
                shp.SetField(self.FIELD_NAME, self.LABEL_TEXT + f"{shp.Uid}")
            finally:
                shp.UnLock()

            # add sidekicks
            shp = lv_sidekicks.CreateShape(shp_type)

            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()

            # with a small offset
            ptg.X = ptg.X + 15/self.GIS.Zoom
            ptg.Y = ptg.Y + 15/self.GIS.Zoom
            shp.AddPoint(ptg)
            shp.Unlock()

        self.GIS.FullExtent()

    def synchroMove(self, _shp, _x, _y):
        # move main shape
        ptg_a = _shp.GetPoint(0, 0)
        ptg_a.X = ptg_a.X + _x
        ptg_a.Y = ptg_a.Y + _y
        _shp.SetPosition(ptg_a, None, 0)

        # move "sidekick"
        ll = self.GIS.Get(self.NAME_SIDEKICKS)
        shp = ll.GetShape(_shp.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ptg_b.X = ptg_b.X + _x
        ptg_b.Y = ptg_b.Y + _y
        shp.SetPosition(ptg_b, None, 0)

        # additional invalidation
        ex = pdk.TGIS_Extent()
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

    def animate_click(self, _sender):
        lv = self.GIS.Items[0]
        shp = lv.GetShape(5)
        for _ in range(90):
            self.synchroMove(shp, 2, 1)
            sleep(0.1)
            self.GIS.ProcessMessages()

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # start editing of some shape from sidekicks
        ll = self.GIS.Get(self.NAME_SIDEKICKS)
        pt = pdk.TPoint(int(x), int(y))
        ptg = self.GIS.ScreenToMap(pt)
        shp = ll.Locate(ptg, 100/self.GIS.Zoom)
        self.currShape = shp

        if not self.currShape:
            return

        # we are not changing the GIS.Mode to TGIS_ViewerMode.Edit because we
        # want to control editing on our own, so instead we will call
        # MouseBegin, MouseMove and MouseEnd "manually"
        self.GIS.Editor.MouseBegin(pt, True)

    def GIS_MouseMove(self, _sender, _shift, x, y):
        if self.GIS.IsEmpty:
            return
        if not self.currShape:
            return
        
        # additional invalidation
        ptg_a = self.currShape.GetPoint(0, 0)
        ll = self.GIS.Get(self.NAME_REALPOINTS)
        shp = ll.GetShape(self.currShape.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ex = pdk.TGIS_Extent()
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

        ptg_a = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        if pdk.TGIS_Utils.GisIsPointInsideExtent(ptg_a, self.GIS.Extent):
            self.currShape.SetPosition(ptg_a, None, 0)

        # additional invalidation
        ptg_a = self.currShape.GetPoint(0, 0)
        shp = ll.GetShape(self.currShape.Uid)
        ptg_b = shp.GetPoint(0, 0)
        ex.XMin = min(ptg_a.X, ptg_b.X)
        ex.YMin = min(ptg_a.Y, ptg_b.Y)
        ex.XMax = max(ptg_a.X, ptg_b.X)
        ex.YMax = max(ptg_a.Y, ptg_b.Y)

    def GIS_MouseUp(self, _sender, _button, _shift, _x, _y):
        if self.GIS.IsEmpty:
            return
        self.currShape = None


def main():
    frm = DragLabelForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
