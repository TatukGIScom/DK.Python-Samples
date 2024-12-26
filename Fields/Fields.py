import tatukgis_pdk as pdk
import math
from random import randint

class FieldsForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Fields - TatukGIS DK Sample"
        self.ClientWidth = 624
        self.ClientHeight = 514

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(624, 514, None, 0, None, 0)

        self.btnCreateLayer = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnCreateLayer.Place(75, 23, None, 0, None, 0)
        self.btnCreateLayer.Caption = "Create Layer"
        self.btnCreateLayer.OnClick = self.btnCreateLayer_click

        self.btnUpdate = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnUpdate.Place(75, 23, None, 170, None, 0)
        self.btnUpdate.Caption = "Update"
        self.btnUpdate.OnClick = self.btnUpdate_click

        self.chckbxUseSymbols = pdk.TGIS_PvlCheckBox(self.toolbar_buttons.Context)
        self.chckbxUseSymbols.Place(87, 17, None, 81, None, 4)
        self.chckbxUseSymbols.Caption = "Use Symbol"
        self.chckbxUseSymbols.Checked = False

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 141
        self.GIS.Top = 27
        self.GIS.Width = 483
        self.GIS.Height = 320
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(141, 320, None, 0, None, 27)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        self.dataGrid1 = pdk.TGIS_PvlGrid(self.Context)
        self.dataGrid1.Place(624, 145, None, 0, None, 347)
        self.dataGrid1.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS_DataSet1 = pdk.TGIS_DataSet(None)

        self.stsbr1 = pdk.TGIS_PvlPanel(self.Context)
        self.stsbr1.Place(624, 22, None, 0, None, 492)
        self.stsbr1.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.stsbr1.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Open a layer properties form to change parameters"

    def btnUpdate_click(self, _sender):
        self.GIS.InvalidateWholeMap()

    def btnCreateLayer_click(self, _sender):
        self.GIS.Close()

        lv = pdk.TGIS_LayerVector()
        lv.Name = "Fields"
        lv.Open()

        lv.AddField("rotateLabel", pdk.TGIS_FieldType().Float, 10, 4)
        lv.AddField("rotateSymbol", pdk.TGIS_FieldType().Float, 10, 4)
        lv.AddField("color", pdk.TGIS_FieldType().Number, 10, 0)
        lv.AddField("outlinecolor", pdk.TGIS_FieldType().Number, 10, 0)
        lv.AddField("size", pdk.TGIS_FieldType().Number, 10, 0)
        lv.AddField("label", pdk.TGIS_FieldType().String, 1, 0)
        lv.AddField("position", pdk.TGIS_FieldType().String, 1, 0)
        lv.AddField("scale", pdk.TGIS_FieldType().Float, 10, 4)

        for i in range(11):
            shp = lv.CreateShape(pdk.TGIS_ShapeType().Point)
            shp.Lock(pdk.TGIS_Lock().Projection)
            shp.AddPart()
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20), randint(0, 20)))
            an = randint(0, 360)
            shp.SetField("rotateLabel", an)
            shp.SetField("rotateSymbol", an)
            shp.SetField("color", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("label", "Point" + str(i))
            shp.SetField("size", randint(0, 400))
            ar = [pdk.TGIS_LabelPosition().UpLeft, pdk.TGIS_LabelPosition().UpCenter, pdk.TGIS_LabelPosition().UpRight,
                  pdk.TGIS_LabelPosition().MiddleLeft, pdk.TGIS_LabelPosition().MiddleCenter,
                  pdk.TGIS_LabelPosition().MiddleRight,
                  pdk.TGIS_LabelPosition().DownLeft, pdk.TGIS_LabelPosition().DownCenter,
                  pdk.TGIS_LabelPosition().DownRight]
            shp.SetField("position", pdk.TGIS_Utils.ConstructParamPosition([ar[randint(0, 8)]]))
            shp.SetField("scale", math.pi / 180)
            shp.Unlock()
        
        shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        for i in range(11):
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20) - 10, randint(0, 20) - 10))
        an = randint(0, 360)
        shp.SetField("rotateLabel", an)
        shp.SetField("rotateSymbol", an)
        shp.SetField("color", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("label", "Point" + str(1))
        shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("scale", math.pi / 180)
        shp.Unlock()

        for i in range(12):
            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(20 + 2 * i, 0))
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(30 + 2 * i, 10))
            an = randint(0, 360)
            shp.SetField("rotateLabel", an)
            shp.SetField("rotateSymbol", an)
            shp.SetField("size", 20 * i)
            shp.SetField("color", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("scale", math.pi / 180)
            shp.Unlock()

        shp = lv.CreateShape(pdk.TGIS_ShapeType().Polygon)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        for i in range(4):
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20) - 10, randint(0, 20) - 10))
        an = randint(0, 360)
        shp.SetField("rotateLabel", an)
        shp.SetField("rotateSymbol", an)
        shp.SetField("color", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("label", "Point" + str(2))
        shp.Unlock()

        lv.Params.Marker.ColorAsText = "FIELD:color"
        lv.Params.Marker.OutlineColorAsText = "FIELD:outlinecolor"
        lv.Params.Marker.OutlineWidth = 1
        lv.Params.Marker.Size = -20

        if self.chckbxUseSymbols.Checked:
            lv.Params.Marker.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/2267.cgm"
            )
            lv.Params.Marker.SizeAsText = "FIELD:size:1 px"
            lv.Params.Marker.SymbolRotateAsText = "FIELD:rotateSymbol"

        lv.Params.Labels.Field = "label"
        lv.Params.Labels.Allocator = False
        lv.Params.Labels.ColorAsText = "FIELD:color"
        lv.Params.Labels.OutlineColorAsText = "FIELD:outlinecolor"
        lv.Params.Labels.PositionAsText = "FIELD:position"
        lv.Params.Labels.FontColorAsText = "FIELD:color"
        lv.Params.Labels.RotateAsText = "FIELD:rotateLabel:1 deg"

        if self.chckbxUseSymbols.Checked:
            lv.Params.Line.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/1301.cgm"
            )
            lv.Params.Line.SymbolRotateAsText = "FIELD:rotateSymbol:1 deg"
        
        lv.Params.Line.Width = -10
        lv.Params.Line.ColorAsText = "FIELD:color"
        lv.Params.Line.OutlineColorAsText = "FIELD:outlinecolor"
        lv.Params.Line.WidthAsText = "FIELD:size:1 px"

        lv.Params.Area.SymbolRotateAsText = "FIELD:rotateSymbol:1 deg"
        if self.chckbxUseSymbols.Checked:
            lv.Params.Area.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/1301.cgm"
            )
        lv.Params.Area.ColorAsText = "FIELD:color"
        lv.Params.Area.OutlineColorAsText = "FIELD:outlinecolor"

        self.GIS.Add(lv)
        self.GIS.FullExtent()
        self.GIS_legend.GIS_Layer = lv
        # self.GIS_legend.Update()
        self.GIS_DataSet1.Open(lv, lv.Extent)
        # pdk.TGIS_PvlBindingHelper.Bind(self, self.GIS_DataSet1, self.dataGrid1)
        self.dataGrid1.DataSet = self.GIS_DataSet1

def main():
    frm = FieldsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
