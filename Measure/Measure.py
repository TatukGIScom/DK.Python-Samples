import tatukgis_pdk as pdk

class MeasureForm(pdk.TGIS_PvlForm):
    isLine = False
    isPolygon = False

    def __init__(self, _owner):
        self.Caption = "Measure - TatukGIS DK Sample"
        self.ClientWidth = 686
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(662, 33, None, 12, None, 5)

        self.btnLine = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnLine.Place(75, 23, None, 16, None, 5)
        self.btnLine.Caption = "By line"
        self.btnLine.OnClick = self.btnLine_click

        self.btnPolygon = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnPolygon.Place(75, 23, None, 100, None, 5)
        self.btnPolygon.Caption = "By Polygon"
        self.btnPolygon.OnClick = self.btnPolygon_click

        self.btnClear = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnClear.Place(75, 23, None, 184, None, 5)
        self.btnClear.Caption = "Clear"
        self.btnClear.OnClick = self.btnClear_click

        self.panel_controls = pdk.TGIS_PvlPanel(self.Context)
        self.panel_controls.Place(200, 400, None, 474, None, 45)
        self.panel_controls.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.lblLength = pdk.TGIS_PvlLabel(self.panel_controls.Context)
        self.lblLength.Place(43, 13, None, 3, None, 16)
        self.lblLength.Caption = "Length:"

        self.edtLength = pdk.TGIS_PvlEdit(self.panel_controls.Context)
        self.edtLength.Place(191, 20, None, 6, None, 32)

        self.lblArea = pdk.TGIS_PvlLabel(self.panel_controls.Context)
        self.lblArea.Place(43, 13, None, 3, None, 83)
        self.lblArea.Caption = "Area:"

        self.edtArea = pdk.TGIS_PvlEdit(self.panel_controls.Context)
        self.edtArea.Place(191, 20, None, 6, None, 99)

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 15
        self.GIS.Top = 45
        self.GIS.Width = 453
        self.GIS.Height = 396
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.EditorChangeEvent = self.GIS_EditorChangeEvent
        self.GIS.OnMouseDown = self.GIS_MouseDown

        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(600, 23, None, 0, None, 443)
        self.status_bar.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.lblMsg.Place(300, 19, None, 12, None, 0)
        self.lblMsg.Caption = "Use left mouse button to measure"

    def form_show(self, _sender):
        self.GIS.Lock()
        try:
            self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                          + "/World/WorldDCW/world.shp")

            ll = pdk.TGIS_LayerVector()
            ll.Name = "Measure"
            ll.Params.Line.Color = pdk.TGIS_Color.Red
            ll.Params.Line.Width = 25
            ll.SetCSByEPSG(4326)

            self.GIS.Add(ll)
            self.GIS.RestrictedExtent = self.GIS.Extent
        finally:
            self.GIS.Unlock()
    
        self.GIS.Editor.EditingLinesStyle.PenWidth = 10
        self.GIS.Editor.Mode = pdk.TGIS_EditorMode().AfterActivePoint

    def btnLine_click(self, _sender):
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        self.isPolygon = False
        self.isLine = True

        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnPolygon_click(self, _sender):
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        self.isPolygon = True
        self.isLine = False

        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnClear_click(self, _sender):
        self.GIS.Editor.DeleteShape()
        self.GIS.Editor.EndEdit()

        self.edtArea.Text = ""
        self.edtLength.Text = ""

        self.isLine = False
        self.isPolygon = False

        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def GIS_EditorChangeEvent(self, _sender):
        unit = pdk.TGIS_Utils().CSUnitsList.ByEPSG(904201)

        if self.GIS.Editor.CurrentShape is not None:
            if self.isLine:
                self.edtLength.Text = unit.AsLinear(self.GIS.Editor.CurrentShape.LengthCS(), True)
            elif self.isPolygon:
                self.edtLength.Text = unit.AsLinear(self.GIS.Editor.CurrentShape.LengthCS(), True)
                self.edtArea.Text = unit.AsAreal(self.GIS.Editor.CurrentShape.AreaCS(), True, "%s²")

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.Mode == pdk.TGIS_ViewerMode().Edit:
            return
        ll = self.GIS.Get("Measure")
        if ll is None:
            return
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        if self.isLine:
            self.GIS.Editor.CreateShape(ll, ptg, pdk.TGIS_ShapeType().Arc)
        elif self.isPolygon:
            self.GIS.Editor.CreateShape(ll, ptg, pdk.TGIS_ShapeType().Polygon)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Edit
        
    
def main():
    frm = MeasureForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
