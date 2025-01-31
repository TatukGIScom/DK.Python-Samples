import tatukgis_pdk as pdk
import math

class ShapeOperationsForm(pdk.TGIS_PvlForm):
    handleMouseMove = None
    prevPtg = pdk.TGIS_Point()
    prevX = None
    prevY = None
    edtLayer = None
    currShape = None
    edtShape = None

    def __init__(self, _owner):
        self.Caption = "ShapeOperations - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 40, None, 0, None, 0)

        self.rbRotate = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbRotate.Place(57, 25, None, 12, None, 7)
        self.rbRotate.Caption = "Rotate"
        self.rbRotate.Checked = True
        self.rbRotate.OnChange = self.rbRotate_change

        self.rbScale = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbScale.Place(56, 25, None, 75, None, 7)
        self.rbScale.Caption = "Scale"
        self.rbScale.OnChange = self.rbScale_change

        self.rbMove = pdk.TGIS_PvlRadioButton(self.toolbar_buttons.Context)
        self.rbMove.Place(56, 25, None, 133, None, 7)
        self.rbMove.Caption = "Move"
        self.rbMove.OnChange = self.rbMove_change

        self.lbHint = pdk.TGIS_PvlLabel(self.toolbar_buttons.Context)
        self.lbHint.Place(400, 25, None, 197, None, 7)
        self.lbHint.Caption = "Select shape on the map to start transform"

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblAltitude = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblAltitude.Place(300, 19, None, 3, None, 0)
        self.lblAltitude.Caption = ""

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 35
        self.GIS.Width = 600
        self.GIS.Height = 440
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseMove = self.GIS_MouseMove
        self.GIS.OnMouseUp = self.GIS_MouseUp

    def form_show(self, _sender):
        self.GIS.Lock()
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples/3D/buildings.shp")
        self.GIS.Zoom = self.GIS.Zoom * 4

        self.edtLayer = pdk.TGIS_LayerVector()
        self.edtLayer.CS = self.GIS.CS
        self.edtLayer.CachedPaint = False
        self.edtLayer.Params.Area.Pattern = pdk.TGIS_BrushStyle().Clear
        self.edtLayer.Params.Area.OutlineColor = pdk.TGIS_Color().Red

        self.GIS.Add(self.edtLayer)
        self.GIS.Unlock()

    def TransformSelectedShape(self, shp, xx, yx, xy, yy, dx, dy):
        if shp is None:
            return

        centroid = shp.Centroid()
        # transform
        # x' = x*xx + y*xy + dx
        # y' = x*yx + y*yy + dx
        # z' = z
        shp.Transform(pdk.TGIS_Utils.GisPoint3DFrom2D(centroid),
                      xx, yx, 0,
                      xy, yy, 0,
                      0,  0, 1,
                      dx, dy, 0,
                      False)
        self.GIS.InvalidateTopmost()

    def RotateSelectedShape(self, shp, angle):
        self.TransformSelectedShape(
            shp,
            math.cos(angle), math.sin(angle),
            -math.sin(angle), math.cos(angle),
            0, 0
        )

    def ScaleSelectedShape(self, shp, x, y):
        self.TransformSelectedShape(
            shp,
            x, 0,
            0, y,
            0, 0
        )

    def TranslateSelectedShape(self, shp, x, y):
        self.TransformSelectedShape(
            shp,
            1, 0,
            0, 1,
            x, y
        )

    def GIS_MouseMove(self, _sender, _shift, x, y):
        if self.edtShape is None:
            return

        if self.handleMouseMove:
            ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

            if self.rbRotate.Checked:
                self.RotateSelectedShape(self.edtShape, math.pi / 180 * (int(x) - self.prevX))

            elif self.rbScale.Checked:
                if (self.prevX != 0) and (self.prevY != 0):
                    self.ScaleSelectedShape(self.edtShape, float(x / self.prevX), float(y / self.prevY))

            elif self.rbMove.Checked:
                self.TranslateSelectedShape(self.edtShape, (ptg.X-self.prevPtg.X), (ptg.Y-self.prevPtg.Y))

            self.prevPtg.X = ptg.X
            self.prevPtg.Y = ptg.Y
            self.prevX = x
            self.prevY = y

    def GIS_MouseUp(self, _sender, _button, _shift, x, y):
        self.lbHint.Caption = "No selected shape. Select shape"

        if self.currShape:
            self.currShape.CopyGeometry(self.edtShape)
            self.edtLayer.RevertAll()
            self.currShape = None
            self.edtShape = None
            self.GIS.InvalidateWholeMap()
            self.handleMouseMove = False
            return

        # if there is no layer, or we are not in select mode, exit
        if self.GIS.IsEmpty:
            return
        if self.GIS.Mode != pdk.TGIS_ViewerMode().Select:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        # let's try to locate a selected shape on the map
        shp = self.GIS.Locate(ptg, 5/self.GIS.Zoom)
        if shp is None:
            return

        self.currShape = shp.MakeEditable()

        self.edtShape = self.edtLayer.AddShape(self.currShape.CreateCopy())

        self.lbHint.Caption = f"Selected shape: {self.currShape.Uid}. Click to commit changes"

        self.prevPtg.X = ptg.X
        self.prevPtg.Y = ptg.Y
        self.prevX = x
        self.prevY = y

        self.handleMouseMove = not self.handleMouseMove

    def rbRotate_change(self, _sender):
        if not self.rbRotate.Checked:
            return
        
        self.lbHint.Caption = 'Select shape to start rotating'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False

    def rbScale_change(self, _sender):
        if not self.rbScale.Checked:
            return

        self.lbHint.Caption = 'Select shape to start scaling'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False

    def rbMove_change(self, _sender):
        if not self.rbMove.Checked:
            return        

        self.lbHint.Caption = 'Select shape to start moving'
        if self.currShape:
            self.GIS.InvalidateTopmost()
            self.currShape = None
            self.handleMouseMove = False


def main():
    frm = ShapeOperationsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
