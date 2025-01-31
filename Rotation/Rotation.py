import tatukgis_pdk as pdk
from math import radians

class RotationForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "Rotation - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Height = 28
        self.toolbar.Align = "Top"

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnFullExtent.Place(67, 22, None, 3, None, 3)
        self.btnFullExtent.Caption = "Full Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click
        
        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomIn.Place(67, 22, None, 73, None, 3)
        self.btnZoomIn.Caption = "Zoom In"
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnZoomOut.Place(67, 22, None, 143, None, 3)
        self.btnZoomOut.Caption = "Zoom Out"
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        self.btnReset = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnReset.Place(47, 22, None, 213, None, 3)
        self.btnReset.Caption = "Reset"
        self.btnReset.OnClick = self.btnReset_click
        
        self.chkCenter = pdk.TGIS_PvlCheckBox(self.toolbar.Context)
        self.chkCenter.Caption = "Center on click"
        self.chkCenter.Place(107, 22, None, 263, None, 3)

        self.btnMinus = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnMinus.Place(17, 22, None, 373, None, 3)
        self.btnMinus.Caption = "-"
        self.btnMinus.OnClick = self.btnMinus_click

        self.tbRotate = pdk.TGIS_PvlTrackBar(self.toolbar.Context)
        self.tbRotate.Place(97, 33, None, 393, None, 3)
        self.tbRotate.OnChange = self.trackbar_change
        self.tbRotate.Minimum = 0
        self.tbRotate.Maximum = 360
        self.tbRotate.Position = 0

        self.btnPlus = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnPlus.Place(17, 22, None, 493, None, 3)
        self.btnPlus.Caption = "+"
        self.btnPlus.OnClick = self.btnPlus_click

        self.lblDegree = pdk.TGIS_PvlLabel(self.toolbar.Context)
        self.lblDegree.Place(67, 22, None, 513, None, 3)
        self.lblDegree.Caption = f"Degree: {int(self.tbRotate.Position)}"
        # self.lblDegree.Align = "Center"
        
        self.statusbar = pdk.TGIS_PvlPanel(self.Context)
        self.statusbar.Height = 20
        self.statusbar.Align = "Bottom"
        
        self.lblStatus = pdk.TGIS_PvlLabel(self.statusbar.Context)
        self.lblStatus.Width = 400
        self.lblStatus.Caption = "Click on the map to set a new rotation point"
        
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        # self.GIS.Left = 0
        # self.GIS.Top = 29
        # self.GIS.Width = 592
        # self.GIS.Height = 425
        self.GIS.Align = "Client"
        self.GIS.OnMouseDown = self.GISMouseDown

        self.northArrow = pdk.TGIS_PvlControlNorthArrow(self.Context)
        self.northArrow.Width = 60
        self.northArrow.Height = 60
        self.northArrow.Top = 20
        self.northArrow.Left = 452
        self.northArrow.GIS_Viewer = self.GIS

    def form_show(self, _sender):
        # self.GIS.RotationAngle = 0
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "/World/Countries/Poland/DCW/poland.ttkproject")

        # show layers in the viewer and set a rotation point in the central point of extent
        self.GIS.FullExtent()
        self.GIS.Zoom = self.GIS.Zoom * 2
        self.GIS.RotationPoint = pdk.TGIS_Utils.GisCenterPoint(self.GIS.Extent)

    def btnFullExtent_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def btnPlus_click(self, _sender):
        self.tbRotate.Position += 1

    def btnMinus_click(self, _sender):
        self.tbRotate.Position -= 1

    def trackbar_change(self, _sender):
        rotate = self.tbRotate.Position
        self.GIS.RotationAngle = radians(rotate)
        self.GIS.InvalidateWholeMap()
        self.lblDegree.Caption = f"Degree: {int(rotate)}"

    def btnReset_click(self, _sender):
        self.tbRotate.Position = 0

    def GISMouseDown(self, _sender, _button, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # convert screen coordinates to map coordinates
        pt = pdk.TPoint(int(x), int(y))
        # if clicked change a rotation point and move viewport
        self.GIS.RotationPoint = self.GIS.ScreenToMap(pt)

        if self.chkCenter.Checked:
            self.GIS.Center = self.GIS.ScreenToMap(pt)


def main():
    frm = RotationForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
