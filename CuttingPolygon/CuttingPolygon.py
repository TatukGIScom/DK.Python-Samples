# =============================================================================
# CuttingPolygon sample — demonstrates how to clip a raster (pixel) layer's rendering to
# within an arbitrary polygon boundary using TGIS_LayerPixel.CuttingPolygon.
#
# What the sample shows:
#   - Loading a raster image (world map) into the GIS viewer
#   - Creating an in-memory vector layer with a custom polygon
#   - Implementing raster clipping/masking via CuttingPolygon property
#   - Assigning a triangular polygon as the cutting mask
#   - Toggling clipping on/off via button click (Do Cutting)
#   - Raster rendering constrained to polygon boundary
#   - Remaining regions outside polygon are not rendered
#   - Interactive zoom and pan with clipped raster display
#
# Key TatukGIS API concepts shown here:
#   TGIS_ViewerWnd              - main visual map control
#   TGIS_LayerPixel             - raster/image layer
#   TGIS_LayerVector            - in-memory vector layer
#   TGIS_LayerPixel.CuttingPolygon - masking/clipping property
#   TGIS_Shape                  - polygon geometry for clipping
#   TGIS_ControlLegend          - layer list/legend panel
#   OnShow event                - initialization workflow
# =============================================================================
import tatukgis_pdk as pdk

class CuttingPolygonForm(pdk.TGIS_PvlForm):
    """CuttingPolygon sample — clips a raster layer's rendering to within an arbitrary polygon
    boundary using TGIS_LayerPixel.CuttingPolygon."""
    NAME_SHAPE = "shape"

    def __init__(self, _owner):
        self.Caption = "Cutting Polygon - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)
        
        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Do cutting"
        self.button1.OnClick = self.btnCutting_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "Zoom"
        self.button2.OnClick = self.btnZoom_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 30
        self.GIS.Width = 418
        self.GIS.Height = 486
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(175, 486, None, 420, None, 30)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

    def form_show(self, _sender):
        """Opens the world raster image, creates an in-memory vector layer named "shape", and adds
        a triangular polygon shape to it."""
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/VisibleEarth/world_8km.jpg")
        ll = pdk.TGIS_LayerVector()
        ll.Name = self.NAME_SHAPE
        self.GIS.Add(ll)
        shp = ll.CreateShape(pdk.TGIS_ShapeType().Polygon)
        shp.Lock(pdk.TGIS_Lock().Extent)
        try:
            shp.AddPart()
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(-5, 8))
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(40, 2))
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(20, -20))
        finally:    
            shp.Unlock()

        self.GIS.InvalidateWholeMap()

    def btnZoom_click(self, _sender):
        """Switches the viewer to Zoom mode."""
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnCutting_click(self, _sender):
        """Assigns the "shape" layer's first polygon as the raster layer's CuttingPolygon
        (converting to the raster's coordinate system), then hides the vector layer."""
        ll = self.GIS.Get(self.NAME_SHAPE)

        lp = self.GIS.Items[0]
        lp.CuttingPolygon = ll.GetShape(1).CreateCopyCS(lp.CS)

        ll.Active = False
        self.GIS.InvalidateWholeMap()


def main():
    frm = CuttingPolygonForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
