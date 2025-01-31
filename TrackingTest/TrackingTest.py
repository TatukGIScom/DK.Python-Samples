import tatukgis_pdk as pdk
from random import randint
import math

class TrackingTestForm(pdk.TGIS_PvlForm):
    FIELD_NAME = "Name"

    def __init__(self, _owner):
        self.Caption = "Tracking Test - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.chkUseLock = pdk.TGIS_PvlCheckBox(self.toolbar_buttons.Context)
        self.chkUseLock.Place(75, 22, None, 3, None, 3)
        self.chkUseLock.Caption = "Use Lock"

        self.btnAnimate = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAnimate.Place(75, 22, None, 79, None, 3)
        self.btnAnimate.Caption = "Animate"
        self.btnAnimate.OnClick = self.btnAnimate_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(300, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 600
        self.GIS.Height = 450
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

    def form_show(self, _sender):
        self.GIS.Lock()
        try:
            self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                          "/World/VisibleEarth/world_8km.jpg")
            self.GIS.Zoom = self.GIS.Zoom * 2
            self.GIS.InvalidateWholeMap()

            # create a layer and add a field
            ll = pdk.TGIS_LayerVector()
            ll.Params.Marker.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Symbols/2267.cgm")
            ll.Params.Marker.SymbolRotate = math.pi / 2
            ll.Params.Marker.Size = -20
            ll.Params.Line.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Symbols/1301.cgm")
            ll.Params.Line.Width = -5
            ll.CachedPaint = False
            ll.CS = self.GIS.CS
            self.GIS.Add(ll)
            ll.AddField(self.FIELD_NAME, pdk.TGIS_FieldType().String, 255, 0)
            ll.Params.Labels.Field = self.FIELD_NAME

            # add random plains
            lv = self.GIS.Items.Item(1)
            for i in range(100):
                shp = lv.CreateShape(pdk.TGIS_ShapeType().Point)
                shp.SetField(self.FIELD_NAME, str(i + 1))
                shp.Params.Marker.SymbolRotate = randint(0, 360) * math.pi/180
                shp.Params.Marker.Color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                                                 randint(0, 255),
                                                                 randint(0, 255))
                shp.Params.Marker.OutlineColor = shp.Params.Marker.Color
                shp.Lock(pdk.TGIS_Lock().Extent)
                shp.AddPart()
                shp.AddPoint(pdk.TGIS_Utils.GisPoint(-180 + randint(0, 360),
                                                     90 - randint(0, 180)))
                shp.Unlock()
        finally:
            self.GIS.Unlock()
    
    def doLabelPaint(self, _sender, _shape):
        ll = self.GIS.Items[0]
        shp = ll.GetShape(_shape.Uid)
        pt_a = _shape.Viewer.Ref.MapToScreen(shp.GetPoint(0, 0))
        pt_b = _shape.Viewer.Ref.MapToScreen(_shape.GetPoint(0, 0))

        rdr = self.GIS.Renderer
        # while rdr:
        rdr.CanvasPen.Color = pdk.TGIS_Color().Blue
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rdr.CanvasPen.Width = 1
        rdr.CanvasDrawLine(pt_a.X, pt_a.Y, pt_b.X, pt_b.Y)

        # draw label itself
        _shape.Params.Labels.Value = shp.GetField(self.FIELD_NAME)
        _shape.DrawLabel()

    def btnAnimate_click(self, _sender):
        self.btnAnimate.Enabled = False
        for _ in range(90):
            if self.chkUseLock.Checked:
                self.GIS.Lock()

            # move plains
            for j in range(1, 90):

                shp = self.GIS.Items.Item(1).GetShape(j)
                pt = shp.Centroid()

                delta = j % 3 - 1
                shp.SetPosition(pdk.TGIS_Utils.GisPoint(pt.X + delta, pt.Y), None, 0)
                self.GIS.ProcessMessages()

            if self.chkUseLock.Checked:
                self.GIS.Unlock()
                self.GIS.InvalidateTopmost()
                self.GIS.ProcessMessages()

        self.btnAnimate.Enabled = True


def main():
    frm = TrackingTestForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
