import tatukgis_pdk as pdk
from WMTSConnection import WMTSConnection

class WMTSManagerForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "WMTSManager - TatukGIS DK Sample"
        self.ClientWidth = 749
        self.ClientHeight = 566

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 21, None, 12, None, 0)

        self.btnNew = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnNew.Place(55, 21, None, 0, None, 0)
        self.btnNew.Caption = "Open"
        self.btnNew.OnClick = self.btnNew_click

        self.btnClose = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnClose.Place(55, 21, None, 56, None, 0)
        self.btnClose.Caption = "Close"
        self.btnClose.OnClick = self.btnClose_click

        self.btnFulLExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFulLExtent.Place(55, 21, None, 112, None, 0)
        self.btnFulLExtent.Caption = "Full"
        self.btnFulLExtent.OnClick = self.btnFulLExtent_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(55, 21, None, 168, None, 0)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(55, 21, None, 224, None, 0)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnSelect = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnSelect.Place(55, 21, None, 280, None, 0)
        self.btnSelect.Caption = "Select"
        self.btnSelect.OnClick = self.btnSelect_click

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 170
        self.GIS.Top = 29
        self.GIS.Width = 584
        self.GIS.Height = 514
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(164, 514, None, 0, None, 29)
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)


    def btnNew_click(self, _sender):
        wmts_form = WMTSConnection(None)
        wmts_form.SetGIS(self.GIS)
        wmts_form.Show()

    def btnClose_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Close()

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFulLExtent_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def btnSelect_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select


def main():
    frm = WMTSManagerForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
