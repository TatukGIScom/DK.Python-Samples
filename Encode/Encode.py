import tatukgis_pdk as pdk

def doWrite(_sender, pos, buffer, count):
    for i in range(count):
        buffer[i] = buffer[i] ^ ((pos + i) % 256)

def doRead(_sender, pos, buffer, count):
    for i in range(count):
        buffer[i] = buffer[i] ^ ((pos + i) % 256)

class EncodeForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Encode - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(90, 22, None, 3, None, 3)
        self.button1.Caption = "Close All"
        self.button1.OnClick = self.btnClose_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(90, 22, None, 96, None, 3)
        self.button2.Caption = "Open Base"
        self.button2.OnClick = self.btnOpenBase_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(90, 22, None, 189, None, 3)
        self.button3.Caption = "Encode Layer"
        self.button3.OnClick = self.btnEncode_click

        self.button4 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button4.Place(90, 22, None, 282, None, 3)
        self.button4.Caption = "Open Encoded"
        self.button4.OnClick = self.btnOpenEncoded_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 425
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnOpenBase_click(self, _sender):
        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/WorldDCW/world.shp'
        ll.Name = "base"
        ll.Params.Labels.Field = "NAME"
        self.GIS.Add(ll)
        self.GIS.FullExtent()

    def btnClose_click(self, _ender):
        self.GIS.Close()

    def btnEncode_click(self, _sender):
        if self.GIS.IsEmpty:
            pdk.TGIS_PvlMessages.ShowInfo("Open Base layer first", self.Context)
            return

        ls = self.GIS.Items[0]
        if ls is not None and ls.Name == 'encoded':
            pdk.TGIS_PvlMessages.ShowInfo("This layer is already encoded, open base layer", self.Context)
            return

        ld = pdk.TGIS_LayerSHP()
        ld.ReadEvent = doRead
        ld.WriteEvent = doWrite
        ld.Path = 'encoded.shp'
        ld.ImportLayer(ls, self.GIS.Extent, pdk.TGIS_ShapeType().Polygon, '', False)

    def btnOpenEncoded_click(self, _sender):
        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = "encoded.shp"
        ll.Name = "encoded"
        ll.ReadEvent = doRead
        ll.WriteEvent = doWrite
        ll.Params.Labels.Field = "NAME"
        ll.Params.Area.Color = pdk.TGIS_Color().Green
        self.GIS.Add(ll)
        self.GIS.FullExtent()


def main():
    frm = EncodeForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
