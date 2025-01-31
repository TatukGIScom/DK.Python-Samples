import tatukgis_pdk as pdk
import os

SCRIPT_PATH = os.path.dirname(__file__)

def get_directory_path(number):
    return f"{SCRIPT_PATH}/Shapes{number}/"

class DirectWriteForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "DirectWrite - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnBuild = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnBuild.Place(90, 22, None, 3, None, 3)
        self.btnBuild.Caption = "Build Layer"
        self.btnBuild.OnClick = self.btnBuild_click

        self.btnImport = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnImport.Place(90, 22, None, 96, None, 3)
        self.btnImport.Caption = "Import Layer"
        self.btnImport.Enabled = False
        self.btnImport.OnClick = self.btnImport_click

        self.btnMergeLayer = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnMergeLayer.Place(90, 22, None, 189, None, 3)
        self.btnMergeLayer.Caption = "Marge Layer"
        self.btnMergeLayer.Enabled = False
        self.btnMergeLayer.OnClick = self.btnMargeLayer_click

        self.btnWrite = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnWrite.Place(90, 22, None, 282, None, 3)
        self.btnWrite.Caption = "Direct Write"
        self.btnWrite.Enabled = False
        self.btnWrite.OnClick = self.btnWrite_click

        self.btnMergeHelper = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnMergeHelper.Place(90, 22, None, 375, None, 3)
        self.btnMergeHelper.Caption = "Marge Helper"
        self.btnMergeHelper.Enabled = False
        self.btnMergeHelper.OnClick = self.btnMargeHelper_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(200, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 425
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        
        self.number = 0

    def form_show(self, _sender):
        exist = True
        while exist:
            if os.path.exists(get_directory_path(self.number)):
                self.number += 1
            else:
                exist = False
                
        os.mkdir(get_directory_path(self.number))

    def btnBuild_click(self, _sender):
        self.GIS.Close()

        self.btnImport.Enabled = True

        lv = pdk.TGIS_LayerSHP()
        lv.Build(get_directory_path(self.number) + "build.shp",
                 pdk.TGIS_Utils.GisExtent(-180, -90, 180, 90),
                 pdk.TGIS_ShapeType().Point, pdk.TGIS_DimensionType().XY)
        lv.Open()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/WorldDCW/cities.shp"
        ll.Open()

        lv.ImportStructure(ll)
        lv.CS = ll.CS

        for shp in ll.Loop():
            lv.AddShape(shp, True)
        
        lv.SaveData()

        self.GIS.Add(lv)
        self.GIS.FullExtent()
        self.GIS.InvalidateWholeMap()

    def btnImport_click(self, _sender):
        self.btnMergeLayer.Enabled = True
        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/WorldDCW/cities.shp"
        self.GIS.Add(ll)

        shp = pdk.TGIS_GeometryFactory().GisCreateShapeFromWKT(
            'POLYGON((7.86 56.39,31.37 56.39,31.37 39.48,7.86 39.48,7.868 56.39))'
        )

        lv = pdk.TGIS_LayerSHP()
        lv.Path = get_directory_path(self.number) + 'imported.shp'
        lv.CS = ll.CS

        lv.ImportLayerEx(ll, ll.Extent, pdk.TGIS_ShapeType().Unknown, '',
                         shp, pdk.TGIS_Utils.GIS_RELATE_CONTAINS(), False)

        self.GIS.Add(lv)
        lv.Params.Marker.Color = pdk.TGIS_Color.Green
        self.GIS.VisibleExtent = lv.Extent
        self.GIS.InvalidateWholeMap()

    def btnMargeLayer_click(self, _sender):
        self.btnWrite.Enabled = True

        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/WorldDCW/cities.shp'
        self.GIS.Add(ll)

        shp = pdk.TGIS_GeometryFactory.GisCreateShapeFromWKT(
            'POLYGON((7.86 56.39,31.37 56.39,31.37 39.48,7.86 39.48,7.868 56.39))'
        )

        lv = pdk.TGIS_LayerSHP()
        lv.Path = get_directory_path(self.number) + 'imported.shp'
        lv.CS = ll.CS
        lv.MergeLayerEx(ll, ll.Extent, pdk.TGIS_ShapeType().Unknown, '',
                        shp, pdk.TGIS_Utils.GIS_RELATE_DISJOINT(), False, False)

        self.GIS.Add(lv)
        lv.Params.Marker.Color = pdk.TGIS_Color.Green
        self.GIS.FullExtent()
        self.GIS.InvalidateWholeMap()

    def btnWrite_click(self, _sender):
        self.btnMergeHelper.Enabled = True

        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/WorldDCW/cities.shp'
        ll.Open()

        lv = pdk.TGIS_LayerSHP()
        lv.ImportStructure(ll)
        lv.CS = ll.CS

        dwh = pdk.TGIS_LayerVectorDirectWriteHelper(lv)
        dwh.Build(get_directory_path(self.number) + "direct_write.shp", ll.Extent,
                  pdk.TGIS_ShapeType().Point, pdk.TGIS_DimensionType().XY)

        for shp in ll.Loop():
            dwh.AddShape(shp)

        dwh.Close()

        self.GIS.Add(lv)
        self.GIS.FullExtent()

    def btnMargeHelper_click(self, _sender):
        self.btnMergeHelper.Enabled = False
        self.btnImport.Enabled = False
        self.btnMergeLayer.Enabled = False
        self.btnWrite.Enabled = False

        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/WorldDCW/cities.shp'
        ll.Open()

        lv = pdk.TGIS_LayerSHP()
        lv.ImportStructure(ll)
        lv.CS = ll.CS
        lv.Build(get_directory_path(self.number) + "merge_helper.shp", ll.Extent,
                 pdk.TGIS_ShapeType().Point, pdk.TGIS_DimensionType().XY)

        mh = pdk.TGIS_LayerVectorMergeHelper(lv, 500)

        for shp in ll.Loop():
            mh.AddShape(shp)
            mh.Commit()

        self.GIS.Add(lv)
        self.GIS.FullExtent()


def main():
    frm = DirectWriteForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
