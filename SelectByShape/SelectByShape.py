import tatukgis_pdk as pdk
from random import randint
import math

class SelectByShapeForm(pdk.TGIS_PvlForm):
    oldPos = pdk.TPoint()
    oldPos2 = pdk.TPoint()
    oldRadius = 0
    ll = pdk.TGIS_LayerVector()

    def __init__(self, _owner):
        self.Caption = "SelectByShape - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 417
        self.GIS.Height = 480
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.btnCircle = pdk.TGIS_PvlRadioButton(self.Context)
        self.btnCircle.Place(75, 23, None, 3, None, 1)
        self.btnCircle.Caption = "By circle"

        self.btnRect = pdk.TGIS_PvlRadioButton(self.Context)
        self.btnRect.Place(76, 23, None, 85, None, 1)
        self.btnRect.Caption = "By rectangle"

        self.lbSelected = pdk.TGIS_PvlListBox(self.Context)
        self.lbSelected.Place(184, 447, None, 408, None, 0)
        self.lbSelected.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 447)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(300, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Use the left mouse button to select by chosen shape"

        self.GIS.PaintExtraEvent = self.GISPaintExtraEvent
        self.GIS.OnMouseDown = self.GISMouseDown
        self.GIS.OnMouseMove = self.GISMouseMove
        self.GIS.OnMouseUp = self.GISMouseUp

    def form_show(self, _sender):
        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/USA/States/California/Counties.SHP")
        self.ll = pdk.TGIS_LayerVector()
        self.ll.Params.Area.Color = pdk.TGIS_Color().Blue
        self.ll.Transparency = 50
        self.ll.Name = "Points"
        self.ll.CS = self.GIS.CS
        self.GIS.Add(self.ll)

        self.ll = pdk.TGIS_LayerVector()
        self.ll.Params.Area.Color = pdk.TGIS_Color().Blue
        self.ll.Params.Area.OutlineColor = pdk.TGIS_Color().Blue
        self.ll.Transparency = 60
        self.ll.Name = "Buffers"
        self.ll.CS = self.GIS.CS
        self.GIS.Add(self.ll)
        self.GIS.Unlock()
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

        self.btnRect.Checked = True

    def GISPaintExtraEvent(self, _sender, renderer, _mode):
        rdr = renderer
        rdr.CanvasPen.Width = 1
        rdr.CanvasPen.Color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                                     randint(0, 255),
                                                     randint(0, 255))
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rdr.CanvasBrush.Style = pdk.TGIS_BrushStyle().Clear

        if self.btnRect.Checked:
            if (self.oldPos.X == self.oldPos2.X) and (self.oldPos.Y == self.oldPos2.Y):
                return

            rct = pdk.TRect()
            rct.Left = self.oldPos.X
            rct.Top = self.oldPos.Y
            rct.Width = self.oldPos2.X - self.oldPos.X
            rct.Height = self.oldPos2.Y - self.oldPos.Y
            rdr.CanvasDrawRectangle(rct)

        if self.btnCircle.Checked:
            rdr.CanvasDrawEllipse(
                self.oldPos.X - round(self.oldRadius),
                self.oldPos.Y - round(self.oldRadius),
                self.oldRadius * 2,
                self.oldRadius * 2
            )

    def GISMouseMove(self, _sender, shift, x, y):
        if self.GIS.IsEmpty:
            return

        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return
        if not ("Left" in shift):
            return

        if self.btnRect.Checked:
            self.oldPos2 = pdk.TPoint(int(x), int(y))

        if self.btnCircle.Checked:
            self.oldRadius = round(math.sqrt(math.pow(self.oldPos.X - int(x), 2) + math.pow(self.oldPos.Y - int(y), 2)))

        self.GIS.InvalidateSelection()

    def GISMouseUp(self, _sender, button, _shift, _x, y):
        if self.GIS.IsEmpty:
            return

        if button == pdk.TMouseButton().mbRight:
            self.GIS.Mode = pdk.TGIS_ViewerMode.Select
            return

        if self.btnRect.Checked:
            if (self.oldPos.X == self.oldPos2.X) and (self.oldPos.Y == self.oldPos2.Y):
                return

        if self.btnCircle.Checked:
            if self.oldRadius == 0:
                return

        self.ll = self.GIS.Get("Points")
        self.ll.Lock()

        tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)

        ptg, ptg1 = None, None
        if self.btnCircle.Checked:
            ptg = self.GIS.ScreenToMap(self.oldPos)
            tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
            tmp.Params.Marker.Size = 0
            tmp.Lock(pdk.TGIS_Lock().Extent)
            tmp.AddPart()
            tmp.AddPoint(ptg)
            tmp.Unlock()
            self.ll.Unlock()
            ptg1 = self.GIS.ScreenToMap(pdk.TPoint(self.oldPos.X + int(self.oldRadius), int(y)))

        if self.btnRect.Checked:
            ptg = self.GIS.ScreenToMap(self.oldPos)
            tmp = self.ll.CreateShape(pdk.TGIS_ShapeType().Point)
            tmp.Params.Marker.Size = 0
            tmp.Lock(pdk.TGIS_Lock().Extent)
            tmp.AddPart()
            tmp.AddPoint(ptg)
            tmp.Unlock()
            ptg = self.GIS.ScreenToMap(self.oldPos2)
            tmp.AddPoint(ptg)
            self.ll.Unlock()
            ptg1 = self.GIS.ScreenToMap(self.oldPos)

        buf = self.ll.CreateShape(pdk.TGIS_ShapeType().Unknown)

        self.ll = self.GIS.Get("Buffers")
        self.ll.RevertShapes()

        if self.btnCircle.Checked:
            if ptg is None or ptg1 is None:
                return
            distance = ptg1.X - ptg.X

            tpl = pdk.TGIS_Topology()
            buf = tpl.MakeBuffer(tmp, distance, 32, True)
            buf = self.ll.AddShape(buf)

        if self.btnRect.Checked:
            ptg2 = self.GIS.ScreenToMap(self.oldPos2)
            buf = self.ll.CreateShape(pdk.TGIS_ShapeType().Polygon)
            buf.AddPart()
            buf.AddPoint(ptg1)
            buf.AddPoint(pdk.TGIS_Utils.GisPoint(ptg1.X, ptg2.Y))
            buf.AddPoint(ptg2)
            buf.AddPoint(pdk.TGIS_Utils.GisPoint(ptg2.X, ptg1.Y))

        self.ll = self.GIS.Items[0]
        if self.ll is None:
            self.GIS.InvalidateWholeMap()
            return

        self.ll.DeselectAll()

        self.lbSelected.ItemsClear()

        self.GIS.InvalidateWholeMap()
        self.GIS.Lock()
        for tmp in self.ll.Loop(buf.Extent, "", buf, pdk.TGIS_Utils.GIS_RELATE_INTERSECT()):
            self.lbSelected.ItemsAdd(str(tmp.GetField("name")))
            tmp.IsSelected = True

        self.GIS.Unlock()

    def GISMouseDown(self, _sender, button, _shift, x, y):
        if self.GIS.IsEmpty:
            return
        if button == pdk.TMouseButton().mbRight:
            self.GIS.Mode = pdk.TGIS_ViewerMode.Zoom
            return

        self.oldPos = pdk.TPoint(int(x), int(y))
        self.oldPos2 = pdk.TPoint(int(x), int(y))
        self.oldRadius = 0

    # def btnCircle_click(self, _sender):
    #     self.btnRect.Checked = not self.btnCircle.Checked
    #
    # def btnRect_click(self, _sender):
    #     self.btnCircle.Checked = not self.btnRect.Checked


def main():
    frm = SelectByShapeForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
