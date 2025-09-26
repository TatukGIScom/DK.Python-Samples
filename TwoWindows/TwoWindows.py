import tatukgis_pdk as pdk


class TwoWindowsForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "TwoWindows - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 30, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(40, 25, None, 0, None, 3)
        self.btnFullExtent.Caption = "Open"
        self.btnFullExtent.OnClick = self.btnOpen_click

        self.chkKeepZoom = pdk.TGIS_PvlCheckBox(self.toolbar_buttons.Context)
        self.chkKeepZoom.Place(100, 25, None, 51, None, 3)
        self.chkKeepZoom.Caption = "Keep zoom"
        self.chkKeepZoom.OnClick = self.chkKeepZoom_click

        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(592, 23, None, 0, None, 447)
        self.status_bar.Align = "Bottom"

        self.GIS1 = pdk.TGIS_ViewerWnd(self.Context)
        self.status_bar.Place(592, 23, None, 0, None, 447)
        self.GIS1.Place(240, 450, None, 0, None, 30)
        self.GIS1.VisibleExtentChangeEvent = self.AfterPaint_1
        self.GIS1.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS1.Mode = pdk.TGIS_ViewerMode().Zoom

        self.GIS2 = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS2.Place(450, 450, None, 250, None, 30)
        self.GIS2.VisibleExtentChangeEvent = self.AfterPaint_2
        self.GIS2.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                             pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS2.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnOpen_click(self, _sender):
        self.GIS1.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                       '/World/Countries/Poland/DCW/poland.ttkproject')
        self.GIS1.Zoom = self.GIS1.Zoom * 3.0

        self.GIS2.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                       '/World/Countries/Poland/DCW/poland.ttkproject')
        self.GIS2.Zoom = self.GIS2.Zoom * 4.0

    def chkKeepZoom_click(self, _sender):
        if self.GIS1.IsEmpty:
            return
        self.GIS1.Mode = pdk.TGIS_ViewerMode().Zoom

    def AfterPaint_1(self, _sender):
        # synchronize two viewers
        if pdk.TGIS_Utils.GisIsSamePoint(self.GIS2.Center, self.GIS1.Center):
            return

        self.GIS2.Center = self.GIS1.Center
        if self.chkKeepZoom.Checked:
            self.GIS2.Zoom = self.GIS1.Zoom

    def AfterPaint_2(self, _sender):
        # synchronize two viewers
        if pdk.TGIS_Utils.GisIsSamePoint(self.GIS2.Center, self.GIS1.Center):
            return
        self.GIS1.Center = self.GIS2.Center

        if self.chkKeepZoom.Checked:
            self.GIS1.Zoom = self.GIS2.Zoom



def main():
    frm = TwoWindowsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
