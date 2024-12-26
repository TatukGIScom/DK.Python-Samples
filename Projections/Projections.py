import tatukgis_pdk as pdk

class ProjectionsForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Projections - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500
        self.OnShow = self.form_show

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        self.cbxSrcProjection = pdk.TGIS_PvlComboBox(self.toolbar.Context)
        self.cbxSrcProjection.Place(175, 22, None, 3, None, 3)
        self.cbxSrcProjection.OnChange = self.cbxSrcProjection_Change

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoom.Place(75, 22, None, 179, None, 3)
        self.btnZoom.Caption = "Zooming"
        self.btnZoom.OnClick = self.btnZoom_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Align = "Client"

    def form_show(self, _sender):
        for i in range(0, pdk.TGIS_Utils().CSProjList.Count()):
            if pdk.TGIS_Utils().CSProjList.Projection(i).IsStandard:
                proj_object = pdk.TGIS_Utils().CSProjList.Projection(i)
                self.cbxSrcProjection.ItemsAdd(proj_object.WKT)

        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      "/Samples/Projects/world.ttkproject")
        self.GIS.FullExtent()

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def cbxSrcProjection_Change(self, _sender):
        s_proj = self.cbxSrcProjection.Text

        o_gcs = pdk.TGIS_Utils().CSGeographicCoordinateSystemList.ByEPSG(4030)
        o_unit = pdk.TGIS_Utils().CSUnitsList.ByWKT('METER')
        o_proj = pdk.TGIS_Utils().CSProjList.ByWKT(s_proj)
        
        ocs = pdk.TGIS_CSProjectedCoordinateSystem(
            -1, 'Test', o_gcs.EPSG, o_unit.EPSG, o_proj.EPSG,
            pdk.TGIS_Utils().CSProjectedCoordinateSystemList.DefaultParams(o_proj.EPSG)
        )

        self.GIS.Lock()
        try:
            try:
                self.GIS.CS = ocs
                self.GIS.FullExtent()
            except pdk.EGIS_Exception:
                pass
                # we are aware of problems upon switching
                # between two incompatible systems    
        finally:
            self.GIS.Unlock()


def main():
    frm = ProjectionsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
