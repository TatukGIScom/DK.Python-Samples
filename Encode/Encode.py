# =============================================================================
# Encode sample — demonstrates transparent layer encoding using ReadEvent and
# WriteEvent callbacks on TGIS_LayerSHP (Python PDK).
#
# What the sample shows:
#   - Loading a world shapefile into the GIS viewer with labels
#   - Creating a separate vector layer and exporting it to a new file with encryption applied
#   - Using TGIS_LayerSHP ReadEvent and WriteEvent callbacks to apply/reverse XOR cipher
#     byte-by-byte (keyed on file position)
#   - The encoded shapefile can be re-opened with the same callback wired to transparently
#     decode it on the fly, while rendering with a distinct color
#   - Four toolbar buttons control the workflow: Close All, Open Base, Encode Layer, Open Encoded
#
# Key TatukGIS PDK types used:
#   TGIS_ViewerWnd        - main visual map control
#   TGIS_LayerSHP         - ESRI Shapefile layer (source and destination)
#   TGIS_LayerVector      - base class for vector layers
#   TGIS_Layer.ImportLayer - export/convert layer to different format with transformation
#   ReadEvent/WriteEvent  - callbacks for transparent cipher operations during I/O
#   TGIS_Color            - color constants (Green for encoded layer visualization)
#   TGIS_PvlForm          - base class for PDK application windows
#   TGIS_PvlButton        - push-button widget for toolbar actions
# =============================================================================
import tatukgis_pdk as pdk

def doWrite(_sender, pos, buffer, count):
    """Encodes each byte by XOR-ing it with (pos + i) mod 256."""
    for i in range(count):
        buffer[i] = buffer[i] ^ ((pos + i) % 256)

def doRead(_sender, pos, buffer, count):
    """Decodes each byte by XOR-ing it with (pos + i) mod 256, reversing the encoding."""
    for i in range(count):
        buffer[i] = buffer[i] ^ ((pos + i) % 256)

class EncodeForm(pdk.TGIS_PvlForm):
    """
    Main form for the Encode sample.

    Hosts a TGIS_ViewerWnd and a toolbar with four buttons:
      Close All, Open Base, Encode Layer, Open Encoded.
    """
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

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 425
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnOpenBase_click(self, _sender):
        """Opens the base world shapefile (WorldDCW) with country name labels."""
        self.GIS.Close()

        ll = pdk.TGIS_LayerSHP()
        ll.Path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + 'World/WorldDCW/world.shp'
        ll.Name = "base"
        ll.Params.Labels.Field = "NAME"
        self.GIS.Add(ll)
        self.GIS.FullExtent()

    def btnClose_click(self, _ender):
        """Closes all loaded layers."""
        self.GIS.Close()

    def btnEncode_click(self, _sender):
        """Exports the base layer to encoded.shp via ImportLayer with the XOR write callback wired."""
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
        """Opens the encoded shapefile with the read callback wired so the XOR cipher is reversed on every read.  Layer is tinted green."""
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
