import tatukgis_pdk as pdk

class WktForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "WKT - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Align = "Top"
        self.toolbar.Height = 29
        
        self.cbType = pdk.TGIS_PvlComboBox(self.toolbar.Context)
        self.cbType.Place(175, 22, None, 3, None, 3)
        names = (
            "POINT", 
            "MULTIPOINT", 
            "LINESTRING", 
            "MULTILINESTRING", 
            "POLYGON",
            "POINT 3D",
            "MULTIPOINT 3D", 
            "LINESTRING 3D", 
            "MULTILINESTRING 3D", 
            "POLYGON 3D",
            "GEOMETRYCOLLECTION"
        )
        for name in names:
            self.cbType.ItemsAdd(name)
        self.cbType.ItemIndex = 4
        self.cbType.OnChange = self.cbType_Change

        self.statusbar = pdk.TGIS_PvlPanel(self.Context)
        self.statusbar.Place(592, 19, None, 0, None, 480)
        self.statusbar.Align = "Bottom"

        self.lblStatus = pdk.TGIS_PvlLabel(self.Context)
        self.lblStatus.Caption = "Use list to change WKT type"
        self.lblStatus.Align = "Bottom"

        self.memoWkt = pdk.TGIS_PvlMemo(self.Context)
        self.memoWkt.Text = "POLYGON( ( 5 5, 25 5, 25 25, 5 25, 5 5 ), ( 10 10, 10 20, 20 20, 20 10, 10 10 ) )"
        self.memoWkt.Place(592, 50, None, 0, None, 447)
        self.memoWkt.Top = self.memoWkt.Top - self.memoWkt.Height
        self.memoWkt.Align = "Bottom"
        self.memoWkt.OnChange = self.memo_Change
        self.memoWkt.OnClick = self.memo_Change

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 592
        self.GIS.Height = 351
        self.GIS.Align = "Client"

        self.layerObj = pdk.TGIS_LayerVector()
        self.layerObj.Name = 'output'
        self.layerObj.Transparency = 50
        self.layerObj.Params.Area.Color = pdk.TGIS_Color.Red
        self.GIS.Add(self.layerObj)

        shp = pdk.TGIS_Utils.GisCreateShapeFromWKT(self.memoWkt.Text)
        self.layerObj.RevertShapes()
        self.layerObj.AddShape(shp)
        self.layerObj.RecalcExtent()
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def cbType_Change(self, _sender):
        if self.cbType.ItemIndex == 0:
            wkt = 'POINT (30 30)'
        elif self.cbType.ItemIndex == 1:
            wkt = 'MULTIPOINT (4 4, 5 5, 6 6 ,7 7)'
        elif self.cbType.ItemIndex == 2: 
            wkt = 'LINESTRING (3 3, 10 10)'
        elif self.cbType.ItemIndex == 3: 
            wkt = 'MULTILINESTRING ((5 5, 25 5, 25 25, 5 25, 5 5), \
                (10 10, 10 20, 20 20, 20 10, 10 10))'
        elif self.cbType.ItemIndex == 4: 
            wkt = 'POLYGON ((5 5, 25 5, 25 25, 5 25, 5 5), \
                (10 10, 10 20, 20 20, 20 10, 10 10))'
        elif self.cbType.ItemIndex == 5: 
            wkt = 'POINTZ (30 30 100)'
        elif self.cbType.ItemIndex == 6: 
            wkt = 'MULTIPOINTZ (4 4 100, 5 5 100, 6 6 100, 7 7 100)'
        elif self.cbType.ItemIndex == 7: 
            wkt = 'LINESTRINGZ (3 3 100, 10 10 100)'
        elif self.cbType.ItemIndex == 8: 
            wkt = 'MULTILINESTRINGZ ((5 5 100, 25 5 100, 25 25 100, 5 25 100, \
                5 5 100), (10 10 100, 10 20 100, 20 20 100, 20 10 100, 10 10 100))'
        elif self.cbType.ItemIndex == 9: 
            wkt = 'POLYGONZ ((5 5 100, 25 5 100, 25 25 100, 5 25 100, 5 5 100), \
                (10 10 100, 10 20 100, 20 20 100, 20 10 100, 10 10 100))'
        elif self.cbType.ItemIndex == 10:
            wkt = 'GEOMETRYCOLLECTION (POINT (30 30), LINESTRING (3 3, 10 10) )'
        else:
            wkt = ''

        self.memoWkt.Text = wkt
        shp = pdk.TGIS_Utils.GisCreateShapeFromWKT(wkt)
        self.layerObj.RevertShapes()
        self.layerObj.AddShape(shp)
        self.layerObj.RecalcExtent()
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def memo_Change(self, _sender):
        self.layerObj.RevertShapes()
        shp = pdk.TGIS_Utils.GisCreateShapeFromWKT(self.memoWkt.Text)
        if shp is None:
            self.memoWkt.SetFontAlarm()
            return
        self.layerObj.AddShape(shp)
        self.layerObj.RecalcExtent()
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()


def main():
    frm = WktForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
