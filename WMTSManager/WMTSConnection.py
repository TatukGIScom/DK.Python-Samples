import tatukgis_pdk as pdk

class WMTSConnection(pdk.TGIS_PvlForm):
    _gis: pdk.TGIS_ViewerWnd

    def __init__(self, _owner):
        self.Caption = "WMTS Connection"
        self.ClientWidth = 857
        self.ClientHeight = 110

        self.lServers = pdk.TGIS_PvlLabel(self.Context)
        self.lServers.Place(43, 13, None, 12, None, 9)
        self.lServers.Caption = "Servers"

        self.cbxServers = pdk.TGIS_PvlComboBox(self.Context)
        self.cbxServers.Place(737, 21, None, 15, None, 25)
        self.cbxServers.Anchors = ["akTop", "akLeft"]
        servers = (
            "http://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/wmts",
            "http://garden.gis.vt.edu/arcgis/rest/services/VBMP2011/VBMP2011_Infrared_WGS"
            "/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
            "http://geodata.nationaalgeoregister.nl/tiles/service/wmts/bgtstandaard" 
            "?VERSION=1.0.0&request=GetCapabilities",
            "http://geodata.nationaalgeoregister.nl/tiles/service/wmts/brtachtergrondkaart" 
            "?REQUEST=getcapabilities&amp;VERSION=1.0.0",
            "http://gis.oregonmetro.gov/services/wmts/1.0.0/WMTSGetCapabilities.xml",
            "http://hazards.fema.gov/gis/nfhl/rest/services/MapSearch/MapSearch_DFIRM_Tiles/MapServer/WMTS",
            "http://kortforsyningen.kms.dk/orto_foraar?SERVICE=WMTS&request=GetCapabilities",
            "http://kortforsyningen.kms.dk/orto_foraar?VERSION=1.0.0&LAYER=orto_foraar" 
            "&request=GetCapabilities&SERVICE=WMTS&login=qgistest&password=qgistestpw",
            "http://maps.columbus.gov/arcgis/rest/services/Imagery/Imagery2013" 
            "/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
            "http://maps.edc.uri.edu/arcgis/rest/services/Atlas_elevation/Hillshade" 
            "/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
            "http://maps.warwickshire.gov.uk/gs/gwc/service/wmts?REQUEST=GetCapabilities",
            "http://maps.wien.gv.at/wmts/1.0.0/WMTSCapabilities.xml?request=GetCapabilities",
            "http://opencache.statkart.no/gatekeeper/gk/gk.open_wmts" 
            "?Version=1.0.0&service=wmts&request=getcapabilities",
            "http://s1-mdc.cloud.eaglegis.co.nz/arcgis/rest/services/Cache/TopographicMaps/MapServer/WMTS",
            "http://sdi.provinz.bz.it/geoserver/gwc/service/wmts?REQUEST=getcapabilities",
            "http://suite.opengeo.org/geoserver/gwc/service/wmts/?request=GetCapabilities",
            "http://tileserver.maptiler.com/wmts",
            "http://tryitlive.arcgis.com/arcgis/rest/services/ImageryHybrid/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
            "http://webgis.arpa.piemonte.it/ags101free/rest/services" 
            "/topografia_dati_di_base/Sfumo_Europa_WM/MapServer/WMTS",
            "http://www.basemap.at/wmts/1.0.0/WMTSCapabilities.xml",
            "http://www.wien.gv.at/wmts/1.0.0/WMTSCapabilities.xml"
        )
        for server in servers:
            self.cbxServers.ItemsAdd(server)

        self.btnConnect = pdk.TGIS_PvlButton(self.Context)
        self.btnConnect.Place(75, 23, None, 758, None, 23)
        self.btnConnect.Anchors = ["akTop", "akRight"]
        self.btnConnect.Caption = "Connect"
        self.btnConnect.OnClick = self.btnConnect_click

        self.lLayers = pdk.TGIS_PvlLabel(self.Context)
        self.lLayers.Place(38, 13, None, 12, None, 49)
        self.lLayers.Caption = "Layers"

        self.cbxLayers = pdk.TGIS_PvlComboBox(self.Context)
        self.cbxLayers.Place(651, 21, None, 15, None, 65)
        self.cbxLayers.Anchors = ["akTop", "akLeft"]

        self.cbInvertAxis = pdk.TGIS_PvlCheckBox(self.Context)
        self.cbInvertAxis.Place(74, 17, None, 672, None, 67)
        self.cbInvertAxis.Anchors = ["akTop", "akRight"]
        self.cbInvertAxis.Caption = "Invert axis"

        self.btnAdd = pdk.TGIS_PvlButton(self.Context)
        self.btnAdd.Place(75, 23, None, 758, None, 63)
        self.btnAdd.Anchors = ["akTop", "akRight"]
        self.btnAdd.Caption = "Add"
        self.btnAdd.OnClick = self.btnAdd_click

        # self.GIS = pdk.TGIS_ViewerWnd(self)
        # self.GIS.Left = 0
        # self.GIS.Top = 0
        # self.GIS.Width = 0
        # self.GIS.Height = 0

    def SetGIS(self, gis):
        self._gis = gis

    def btnConnect_click(self, _sender):
        wmts = pdk.TGIS_LayerWMTS()
        wmts.Path = self.cbxServers.Text
        try:
            available_layers = wmts.GetAvailableLayers()
            for layer_info in available_layers:
                self.cbxLayers.ItemsAdd(layer_info.Name)
            if self.cbxLayers.ItemsCount > 0:
                self.cbxLayers.ItemIndex = 0
        except pdk.EGIS_Exception as e:
            pdk.TGIS_PvlMessages.ShowInfo(f"EGIS_Exception: {e}", self.Context)

    def btnAdd_click(self, _sender):
        layer_info_name = self.cbxLayers.Text

        tkn = pdk.TGIS_Tokenizer()
        tkn.Execute(layer_info_name, [";"])
        layer = tkn.Result
        layer_name = layer[0]
        image_format = layer[1]
        tile_matrix_set = layer[2]

        str_invert = str(self.cbInvertAxis.Checked)
        wmts = pdk.TGIS_LayerWMTS()
        wmts.Path = "TatukGIS Layer\n" \
                    "Storage=WMTS\n" \
                    "Layer=" + layer_name + "\n" \
                    "Url=" + self.cbxServers.Text + "\n" \
                    "TileMatrixSet=" + tile_matrix_set + "\n" \
                    "ImageFormat=" + image_format + "\n" \
                    "InvertAxis=" + str_invert + "\n"

        self._gis.Add(wmts)
        if self._gis.Items.Count == 1:
            self._gis.FullExtent()
        else:
            self._gis.InvalidateWholeMap()
