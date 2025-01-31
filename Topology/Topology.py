import tatukgis_pdk as pdk

class TopologyForm(pdk.TGIS_PvlForm):
    shpA: pdk.TGIS_Shape = None
    shpB: pdk.TGIS_Shape = None
    layerObj: pdk.TGIS_LayerVector = None
    topologyObj: pdk.TGIS_Topology = None

    def __init__(self, _owner):
        self.Caption = "Topology - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 462
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.btnAplusB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAplusB.Place(75, 22, None, 0, None, 3)
        self.btnAplusB.Caption = "A + B"
        self.btnAplusB.OnClick = self.btnAplusB_click

        self.btnAmultiB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAmultiB.Place(75, 22, None, 75, None, 3)
        self.btnAmultiB.Caption = "A * B"
        self.btnAmultiB.OnClick = self.btnAmultiB_click

        self.btnAminusB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAminusB.Place(75, 22, None, 150, None, 3)
        self.btnAminusB.Caption = "A - B"
        self.btnAminusB.OnClick = self.btnAminusB_click

        self.btnBminusA = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnBminusA.Place(75, 22, None, 225, None, 3)
        self.btnBminusA.Caption = "B - A"
        self.btnBminusA.OnClick = self.btnBminusA_click

        self.btnAxorB = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnAxorB.Place(75, 22, None, 300, None, 3)
        self.btnAxorB.Caption = "A xor B"
        self.btnAxorB.OnClick = self.btnAxorB_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 400
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(400, 19, None, 3, None, 0)
        self.lblMsg.Caption = ""

    def form_show(self, _sender):
        self.layerObj = pdk.TGIS_LayerVector()
        self.topologyObj = pdk.TGIS_Topology()

        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/Topology/topology.shp")
        ll = self.GIS.Items[0]
        if ll is None:
            return

        self.shpA = ll.GetShape(1).MakeEditable()
        if self.shpA is None:
            return

        self.shpB = ll.GetShape(2).MakeEditable()
        if self.shpB is None:
            return

        self.layerObj = pdk.TGIS_LayerVector()
        self.layerObj.Name = "output"
        self.layerObj.Transparency = 50
        self.layerObj.Params.Area.Color = pdk.TGIS_Color().Red

        self.GIS.Add(self.layerObj)
        self.GIS.Unlock()
        self.GIS.FullExtent()

    def btnAplusB_click(self, _sender):
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Union)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAmultiB_click(self, _sender):
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Intersection)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAminusB_click(self, _sender):
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().Difference)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnBminusA_click(self, _sender):
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpB, self.shpA, pdk.TGIS_TopologyCombineType().Difference)
        if tmp:
            self.layerObj.AddShape(tmp)
            tmp.Free()
        self.GIS.InvalidateWholeMap()

    def btnAxorB_click(self, _sender):
        self.layerObj.RevertShapes()
        tmp = self.topologyObj.Combine(self.shpA, self.shpB, pdk.TGIS_TopologyCombineType().SymmetricalDifference)
        if tmp is not None:
            self.layerObj.AddShape(tmp)

        self.GIS.InvalidateWholeMap()


def main():
    frm = TopologyForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
