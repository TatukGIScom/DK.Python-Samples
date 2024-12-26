import tatukgis_pdk as pdk

class TriangulationForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Triangulation - TatukGIS DK Sample"
        self.ClientWidth = 604
        self.ClientHeight = 404
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnFullExtent = pdk.TGIS_PvlButton(self.Context)
        self.btnFullExtent.Place(73, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomIn.Place(75, 22, None, 79, None, 3)
        self.btnZoomIn.Caption = "ZoomIn"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomOut.Place(75, 22, None, 155, None, 3)
        self.btnZoomOut.Caption = "ZoomOut"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        self.GIS_Attributes = pdk.TGIS_PvlControlAttributes(self.Context)
        self.GIS_Attributes.Place(180, 141, None, 424, None, 28)
        self.GIS_Attributes.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Right,
                                       pdk.TGIS_PvlAnchor().Bottom)

        self.grpbxResult = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxResult.Caption = "Result"
        self.grpbxResult.Place(180, 92, None, 424, None, 175)
        self.grpbxResult.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.rbtnVoronoi = pdk.TGIS_PvlRadioButton(self.grpbxResult.Context)
        self.rbtnVoronoi.Place(120, 17, None, 6, None, 19)
        self.rbtnVoronoi.Caption = "Voronoi Diagram"
        self.rbtnVoronoi.Checked = True
        self.rbtnVoronoi.OnClick = self.rbtnVoronoi_click

        self.rbtnDelaunay = pdk.TGIS_PvlRadioButton(self.grpbxResult.Context)
        self.rbtnDelaunay.Place(120, 17, None, 6, None, 42)
        self.rbtnDelaunay.Caption = "Delaunay Diagram"
        self.rbtnDelaunay.Checked = False
        self.rbtnDelaunay.OnClick = self.rbtnDelaunay_click

        self.lblLayer = pdk.TGIS_PvlLabel(self.grpbxResult.Context)
        self.lblLayer.Place(68, 13, None, 6, None, 68)
        self.lblLayer.Caption = "Layer name :"

        self.edtLayer = pdk.TGIS_PvlEdit(self.grpbxResult.Context)
        self.edtLayer.Place(94, 20, None, 80, None, 65)
        self.edtLayer.Text = "Voronoi"

        self.btnGenerate = pdk.TGIS_PvlButton(self.grpbxResult.Context)
        self.btnGenerate.Place(168, 23, None, 6, None, 95)
        self.btnGenerate.Caption = "Generate"
        self.btnGenerate.OnClick = self.btnGenerate_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 28
        self.GIS.Width = 424
        self.GIS.Height = 354
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.FullExtent()

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(180, 80, None, 424, None, 302)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS.OnMouseDown = self.GIS_MouseDown

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/city.shp")

        # and add a new parameter
        lv = self.GIS.Items[0]
        lv.Params.Marker.Color = pdk.TGIS_Color().FromRGB(0x4080FF)
        lv.Params.Marker.OutlineWidth = 2
        lv.Params.Marker.Style = pdk.TGIS_MarkerStyle().Circle

        lv.ParamsList.Add()
        lv.Params.Style = "selected"
        lv.Params.Area.OutlineWidth = 1
        lv.Params.Area.Color = pdk.TGIS_Color().Blue

        self.GIS.InvalidateWholeMap()

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def rbtnVoronoi_click(self, _sender):
        self.edtLayer.Text = "Voronoi"

    def rbtnDelaunay_click(self, _sender):
        self.edtLayer.Text = "Delaunay"

    def GIS_MouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # let's locate a shape after click
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        shp = self.GIS.Locate(ptg, 5 / self.GIS.Zoom)  # 5 pixels precision
        if shp is not None:
            self.GIS_Attributes.ShowShape(shp)

    def btnGenerate_click(self, _sender):
        if self.GIS.Get(self.edtLayer.Text) is not None:
            pdk.TGIS_PvlMessages.ShowInfo("Result layer already exists. Use different name.", self.Context)
            return

        if self.rbtnVoronoi.Checked:
            lv = pdk.TGIS_LayerVoronoi()
        else:
            lv = pdk.TGIS_LayerDelaunay()

        lv.Name = self.edtLayer.Text
        lv.ImportLayer(self.GIS.Items[0], self.GIS.Extent, pdk.TGIS_ShapeType().Unknown, "", False)
        lv.Transparency = 60

        lv.Params.Render.Expression = "GIS_AREA"
        lv.Params.Render.MinVal = 10000000.0
        lv.Params.Render.MaxVal = 1300000000.0
        lv.Params.Render.StartColor = pdk.TGIS_Color().White
        if self.rbtnVoronoi.Checked:
            lv.Params.Render.EndColor = pdk.TGIS_Color().Red
        else:
            lv.Params.Render.EndColor = pdk.TGIS_Color().Blue

        lv.Params.Render.Zones = 10
        lv.Params.Area.Color = pdk.TGIS_Color.RenderColor
        lv.CS = self.GIS.CS

        self.GIS.Add(lv)
        self.GIS.InvalidateWholeMap()
        # self.GIS_Legend.Invalidate()


def main():
    frm = TriangulationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
