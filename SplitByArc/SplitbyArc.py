import tatukgis_pdk as pdk
from random import randint

class SplitByArcForm(pdk.TGIS_PvlForm):
    layerArc: pdk.TGIS_LayerVector()
    layerPolygon: pdk.TGIS_LayerVector()
    layerObj: pdk.TGIS_LayerVector()
    shpArc: pdk.TGIS_ShapeArc()
    shpPolygon: pdk.TGIS_ShapePolygon()

    def __init__(self, _owner):
        self.Caption = "SplitByArc - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.btnLine = pdk.TGIS_PvlButton(self.Context)
        self.btnLine.Place(129, 25, None, 28, None, 24)
        self.btnLine.Caption = "New line / Create line"
        self.btnLine.OnClick = self.btnLine_click

        self.btnSplit = pdk.TGIS_PvlButton(self.Context)
        self.btnSplit.Place(129, 25, None, 28, None, 64)
        self.btnSplit.Caption = "Split shape"
        self.btnSplit.Enabled = False
        self.btnSplit.OnClick = self.btnSplit_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lbInfo = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lbInfo.Place(400, 19, None, 3, None, 0)
        self.lbInfo.Caption = ""

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 185
        self.GIS.Top = 0
        self.GIS.Width = 407
        self.GIS.Height = 447
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseDown = self.GISMouseDown

    def form_show(self, _sender):
        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'Samples/Topology/topology3.shp')

        self.layerPolygon = self.GIS.Items[0]
        self.shpPolygon = self.layerPolygon.GetShape(1).MakeEditable()
        if self.shpPolygon is None:
            return

        # create layer for line
        self.layerArc = pdk.TGIS_LayerVector()
        self.layerArc.Params.Line.Color = pdk.TGIS_Color().Red
        self.layerArc.Params.Line.Width = 25
        self.GIS.Add(self.layerArc)

        self.shpArc = self.layerArc.CreateShape(pdk.TGIS_ShapeType().Arc)
        if self.shpArc is None:
            return

        # create layer for new shapes - after split
        self.layerObj = pdk.TGIS_LayerVector()
        self.layerObj.Name = 'Splits'
        self.GIS.Add(self.layerObj)
        self.GIS.Unlock()

        self.GIS.FullExtent()
        self.GIS.RestrictedExtent = self.GIS.Extent

    def btnLine_click(self, _sender):
        self.layerObj.RevertShapes()  # clear layer with new polygons
        self.shpArc.Reset()           # clear line
        self.shpArc.AddPart()         # initiate for new points
        self.lbInfo.Caption = '...'
        self.GIS.InvalidateWholeMap()
        self.btnSplit.Enabled = False

    def btnSplit_click(self, _sender):
        self.layerObj.RevertShapes()
        topology_obj = pdk.TGIS_Topology()
        shape_list = topology_obj.SplitByArc(self.shpPolygon, self.shpArc, True)
        if shape_list is not None:
            self.lbInfo.Caption = str(shape_list.Count)
            for shp in shape_list:
                shp.Params.Area.Color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                                               randint(0, 255),
                                                               randint(0, 255))
                self.layerObj.AddShape(shp)

        self.GIS.InvalidateWholeMap()

    def GISMouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return
        if self.shpArc.GetNumParts() == 0:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.shpArc.Lock(pdk.TGIS_Lock().Extent)
        self.shpArc.AddPoint(ptg)
        self.shpArc.Unlock()
        self.GIS.InvalidateWholeMap()
        if self.shpArc.Intersect(self.shpPolygon):
            self.btnSplit.Enabled = True

    def GISMouseUp(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.shpArc.Lock(pdk.TGIS_Lock().Extent)
        self.shpArc.AddPoint(ptg)
        self.shpArc.Unlock()
        self.GIS.InvalidateWholeMap()
        if self.shpArc.Intersect(self.shpPolygon):
            self.btnSplit.Enabled = True


def main():
    frm = SplitByArcForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
