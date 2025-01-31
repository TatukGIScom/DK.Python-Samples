import tatukgis_pdk as pdk

class TransformForm(pdk.TGIS_PvlForm):
    GIS_TRN_EXT = ".trn"

    def __init__(self, _owner):
        self.Caption = "Transform - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.btnTransform = pdk.TGIS_PvlButton(self.Context)
        self.btnTransform.Place(90, 25, None, 15, None, 10)
        self.btnTransform.Caption = "Transform"
        self.btnTransform.OnClick = self.btnTransform_click

        self.btnCutting = pdk.TGIS_PvlButton(self.Context)
        self.btnCutting.Place(90, 25, None, 15, None, 45)
        self.btnCutting.Caption = "Cutting Polygon"
        self.btnCutting.OnClick = self.btnCutting_click

        self.btnSave = pdk.TGIS_PvlButton(self.Context)
        self.btnSave.Place(90, 25, None, 15, None, 80)
        self.btnSave.Caption = "Save to File"
        self.btnSave.OnClick = self.btnSave_click

        self.btnRead = pdk.TGIS_PvlButton(self.Context)
        self.btnRead.Place(90, 25, None, 15, None, 115)
        self.btnRead.Caption = "Read From File"
        self.btnRead.OnClick = self.btnRead_click

        self.lblCoordinates = pdk.TGIS_PvlLabel(self.Context)
        self.lblCoordinates.Place(200, 20, None, 140, None, 480)
        self.lblCoordinates.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 130
        self.GIS.Top = 0
        self.GIS.Width = 480
        self.GIS.Height = 480
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseMove = self.GIS_MouseMove

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "Samples/Rectify/satellite.jpg")

    def GIS_MouseMove(self, _sender, _shift, x, y):
        if self.GIS.IsEmpty:
            return

        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        self.lblCoordinates.Caption = f"X : {ptg.X:.4f} | Y : {ptg.Y:.4f}"

    def btnTransform_click(self, _sender):
        lp = self.GIS.Items[0]

        trn = pdk.TGIS_TransformPolynomial()
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 239703.615056818),
                     0, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 244759.524147727),
                     1, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1279722.65909091, 245859.524147727),
                     2, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1279744.93181818, 239725.887784091),
                     3, True)
        trn.Prepare(pdk.TGIS_PolynomialOrder().First)
        
        lp.Transform = trn
        lp.Transform.Active = True
        lp.SetCSByEPSG(102748)
        
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def btnCutting_click(self, _sender):
        lp = self.GIS.Items[0]

        trn = pdk.TGIS_TransformPolynomial()
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 239703.615056818),
                     0, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 244759.524147727),
                     1, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1279722.65909091, 244759.524147727),
                     2, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1279744.93181818, 239725.887784091),
                     3, True)
        
        trn.CuttingPolygon =\
            "POLYGON((421.508902077151 -320.017804154303,"\
            "518.161721068249 -223.364985163205,"\
            "688.725519287834 -210.572700296736,"\
            "864.974777448071 -254.635014836795,"\
            "896.244807121662 -335.652818991098,"\
            "894.823442136499 -453.626112759644,"\
            "823.755192878338 -615.661721068249,"\
            "516.740356083086 -607.13353115727,"\
            "371.761127596439 -533.222551928783,"\
            "340.491097922849 -456.46884272997,"\
            "421.508902077151 -320.017804154303))"

        trn.Prepare(pdk.TGIS_PolynomialOrder().First)
        lp.Transform = trn
        lp.Transform.Active = True
        
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def btnSave_click(self, _sender):
        lp = self.GIS.Items[0]

        if lp.Transform is not None:
            lp.Transform.SaveToFile(lp.Path + self.GIS_TRN_EXT)

    def btnRead_click(self, _sender):
        lp = self.GIS.Items[0]

        trn = pdk.TGIS_TransformPolynomial()
        trn.LoadFromFile(lp.Path + self.GIS_TRN_EXT)
        lp.Transform = trn
        lp.Transform.Active = True
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()


def main():
    frm = TransformForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
