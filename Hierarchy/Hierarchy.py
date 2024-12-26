import tatukgis_pdk as pdk

class HierarchyForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "Hierarchy - TatukGIS DK Sample"
        self.ClientWidth = 504
        self.ClientHeight = 404

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(504, 23, None, 0, None, 0)

        self.btnHierarchy = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnHierarchy.Place(86, 23, None, 0, None, 0)
        self.btnHierarchy.Caption = "Build Hierarchy"
        self.btnHierarchy.OnClick = self.btnHierarchy_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 180
        self.GIS.Top = 23
        self.GIS.Width = 324
        self.GIS.Height = 381
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_Legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_Legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_Legend.GIS_Viewer = self.GIS
        self.GIS_Legend.Place(180, 381, None, 0, None, 23)
        self.GIS_Legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

    def btnHierarchy_click(self, _sender):
        self.GIS.Close()
        self.GIS_Legend.Mode = pdk.TGIS_ControlLegendMode().Groups

        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/World/Countries/Poland/DCW/poland.ttkproject", False)

        self.GIS.Hierarchy.ClearGroups()

        group = self.GIS.Hierarchy.CreateGroup("My group")

        for i in range(int(self.GIS.Items.Count/2)):
            group.AddLayer(self.GIS.Items[i])

        for i in range(int(self.GIS.Items.Count/2)):
            group.DeleteLayer(self.GIS.Items[i])

        group = self.GIS.Hierarchy.CreateGroup("Root")
        group.CreateGroup("Leaf")

        self.GIS.Hierarchy.Groups("Leaf").CreateGroup("node").AddLayer(self.GIS.Get("city1"))

        self.GIS.Hierarchy.MoveGroup("Root", "My group")

        group = self.GIS.Hierarchy.CreateGroup("Poland")
        group = group.CreateGroup("Waters")
        group.AddLayer(self.GIS.Get("Lakes"))
        group.AddLayer(self.GIS.Get("Rivers"))

        group = self.GIS.Hierarchy.Groups("Poland").CreateGroup("Areas")
        group.AddLayer(self.GIS.Get("city"))
        group.AddLayer(self.GIS.Get("Country area"))

        self.GIS.Hierarchy.AddOtherLayers()

        self.GIS.FullExtent()


def main():
    frm = HierarchyForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
