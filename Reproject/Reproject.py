import tatukgis_pdk as pdk

class ReprojectForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "Reproject - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 25
        self.GIS.Width = 592
        self.GIS.Height = 441
        self.GIS.Align = "Client"

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 25, None, 0, None, 0)

        self.cbxSrcProjection = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cbxSrcProjection.Place(201, 21, None, 8, None, 2)
        self.cbxSrcProjection.OnChange = self.cbxSrcProjection_change

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 21, None, 217, None, 2)
        self.button1.Caption = "Reproject"
        self.button1.OnClick = self.button1_click

    def form_show(self, _sender):
        projections = []
        try:
            for projection in range(pdk.TGIS_Utils().CSProjList.Count()):
                wkt = pdk.TGIS_Utils().CSProjList.Projection(projection).WKT
                projections.append(wkt)

            projections.sort()
        except Exception as e:
            print('Something went wrong: ' + str(e))

        self.cbxSrcProjection.ItemsAdd("Select projection...")
        for projection in projections:
            self.cbxSrcProjection.ItemsAdd(projection)

        self.cbxSrcProjection.ItemIndex = 0
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/Poland/DCW/country.shp")

    def button1_click(self, _sender):
        if self.GIS.IsEmpty:
            return

        dlg_save = pdk.TGIS_PvlOpenDialog(self.Context)
        # dlg_save.DefaultExt = "shp"
        dlg_save.Filter = "SHP File|*.shp"
        if not dlg_save.Execute():
            return

        lv = self.GIS.Items[0]

        lo = pdk.TGIS_LayerSHP()
        lo.Path = dlg_save.FileName
        lo.CS = self.GIS.CS
        try:
            lo.ImportLayer(lv, pdk.TGIS_Utils.GisWholeWorld(), pdk.TGIS_ShapeType().Unknown, "", False)
        except pdk.EGIS_Exception as e:
            pdk.TGIS_PvlMessages.ShowInfo(str(e), self.Context)

    def cbxSrcProjection_change(self, _sender):
        if self.cbxSrcProjection.ItemIndex == 0:
            return

        proj_str = self.cbxSrcProjection.Text
        proj = pdk.TGIS_Utils().CSProjList.ByWKT(proj_str)
        gcs = pdk.TGIS_Utils().CSGeographicCoordinateSystemList.ByEPSG(4030)
        unit = pdk.TGIS_Utils().CSUnitsList.ByWKT("METER")
        cs = pdk.TGIS_CSProjectedCoordinateSystem(
            -1, "Test",
            gcs.EPSG, unit.EPSG, proj.EPSG,
            pdk.TGIS_Utils().CSProjectedCoordinateSystemList.DefaultParams(proj.EPSG))

        self.GIS.Lock()
        try:
            try:
                self.GIS.CS = pdk.TGIS_CSFactory().ByWKT(cs.FullWKT)
            except pdk.EGIS_Exception as e:
                pdk.TGIS_PvlMessages.ShowInfo(str(e), self.Context)
                self.cbxSrcProjection.ItemIndex = 0
                self.GIS.CS = None
        finally:
            self.GIS.Unlock()
            self.GIS.FullExtent()



def main():
    frm = ReprojectForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
