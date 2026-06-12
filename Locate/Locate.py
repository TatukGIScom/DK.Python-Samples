# =============================================================================
# Locate sample — demonstrates feature identification and location by finding
# shapes at the cursor position using spatial queries and coordinate conversion
# (Python PDK).
#
# What the sample shows:
#   - Loading a polygon shapefile (California Counties) into the GIS viewer
#   - Feature location: finding which shape is at a given position
#   - Screen-to-map coordinate conversion via ScreenToMap
#   - Spatial tolerance: 5-pixel screen tolerance for easier feature selection
#   - GIS.Locate: queries features at a geographic position
#   - Shape attributes: retrieving field values from selected features
#   - Shape flashing: visual feedback highlighting the selected shape
#   - Dynamic status bar: real-time display of feature attributes (hover tooltip)
#   - Toolbar with Full Extent, Zoom In/Out navigation buttons
#
# Key TatukGIS PDK types used:
#   TGIS_ViewerWnd       - main visual map control
#   TGIS_ViewerWnd.ScreenToMap - convert screen pixel to geographic coordinate
#   TGIS_ViewerWnd.Locate      - find topmost shape at location with tolerance
#   TGIS_Shape           - geographic feature with field access
#   TGIS_Shape.Flash()   - briefly highlight shape for visual feedback
#   OnMouseMove / OnMouseDown - user interaction event handling
#   TGIS_PvlForm         - base class for PDK application windows
#   TGIS_PvlButton       - push-button widget
#   TGIS_PvlLabel        - static text label
# =============================================================================

import tatukgis_pdk as pdk

class LocateForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Locate - TatukGIS DK Sample"
        self.Left = 200
        self.Top = 100
        self.Width = 600
        self.Height = 500
        self.OnShow = self.form_show

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"
        
        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnFullExtent.Place(75, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomIn.Place(75, 22, None, 79, None, 3)
        self.btnZoomIn.Caption = "Zoom In"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomOut.Place(75, 22, None, 155, None, 3)
        self.btnZoomOut.Caption = "Zoom Out"
        self.btnZoomOut.OnClick = self.btnZoomOut_click
        
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"
        self.GIS.OnMouseMove = self.GISMouseMove
        self.GIS.OnMouseDown = self.GISMouseDown

        self.statusbar = pdk.TGIS_PvlPanel(self.Context)
        self.statusbar.Align = "Bottom"
        
        self.lblStatus = pdk.TGIS_PvlLabel(self.statusbar.Context)
        self.lblStatus.Place(100, 19, None, 3, None, 0)

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "/World/Countries/USA/States/California/Counties.shp")
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        self.GIS.Zoom = self.GIS.Zoom / 2

    def GISMouseMove(self, _sender,  _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # convert screen coordinates to map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # calculate precision of location as 5 pixels
        precision = 5.0 / self.GIS.Zoom

        # let's try to locate a selected shape on the map
        shp = self.GIS.Locate(ptg, precision)

        if shp:
            self.lblStatus.Caption = shp.GetField('NAME')

    def GISMouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # convert screen coordinates to map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # calculate precision of location as 5 pixels
        precision = 5.0 / self.GIS.Zoom

        # let's try to locate a selected shape on the map
        shp = self.GIS.Locate(ptg, precision)

        if shp is not None:
            shp.Flash()


def main():
    frm = LocateForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
