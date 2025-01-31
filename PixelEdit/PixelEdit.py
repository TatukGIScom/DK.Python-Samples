import tatukgis_pdk as pdk
import os
from random import random

class PixelEditForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "PixelEdit - TatukGIS Sample"
        self.Left = 200
        self.Top = 120
        self.Width = 651
        self.Height = 504
        
        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(635, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"
        
        self.btnProfile = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnProfile.Place(120, 22, None, 3, None, 3)
        self.btnProfile.Caption = "Terrain profile"
        self.btnProfile.OnClick = self.btnProfileClick

        self.btnMinMax = pdk.TGIS_PvlButton(self.Context)
        self.btnMinMax.Place(120, 22, None, 123, None, 3)
        self.btnMinMax.Caption = "Grid Min/Max"
        self.btnMinMax.OnClick = self.btnMinMaxClick

        self.btnAverageColor = pdk.TGIS_PvlButton(self.Context)
        self.btnAverageColor.Place(120, 22, None, 243, None, 3)
        self.btnAverageColor.Caption = "Bitmap average color"
        self.btnAverageColor.OnClick = self.btnAverageColorClick

        self.btnCreateBitmap = pdk.TGIS_PvlButton(self.Context)
        self.btnCreateBitmap.Place(120, 22, None, 363, None, 3)
        self.btnCreateBitmap.Caption = "Create a new JPG"
        self.btnCreateBitmap.OnClick = self.btnCreateBitmapClick

        self.btnCreateGrid = pdk.TGIS_PvlButton(self.Context)
        self.btnCreateGrid.Place(120, 22, None, 483, None, 3)
        self.btnCreateGrid.Caption = "Create a new GRD"
        self.btnCreateGrid.OnClick = self.btnCreateGridClick
        
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

        self.Memo1 = pdk.TGIS_PvlMemo(self.Context)
        # self.Memo1.ReadOnly = True
        self.Memo1.AppendLine("Memo")
        self.Memo1.Place(635, 89, None, 0, None, 376)
        self.Memo1.Align = "Bottom"
        
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(169, 347, None, 0, None, 29)
        self.GIS_legend.Align = "Left"

    def btnProfileClick(self, _sender):
        self.Memo1.Clear()
        
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/grid.ttkproject')

        lp = self.GIS.Get("elevation")
        lv = self.GIS.Get("line")
        shp = lv.GetShape(1).MakeEditable()
        shp.IsSelected = True

        # self.Memo1.BeginUpdate()
        try:
            for px in lp.Loop(0, shp, True):
                self.Memo1.AppendLine(
                    f"Distance: {px.Distance}, Height:{px.Value:.2f})"
                )
                px.Value = 0.
        finally:
            pass

            
        self.GIS.InvalidateWholeMap()

    def btnMinMaxClick(self, _sender):
        self.Memo1.Clear()
        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/grid.ttkproject')

        lp = self.GIS.Get('elevation')
        lv = self.GIS.Get('polygon')
        shp = lv.GetShape(1).MakeEditable()
        shp.IsSelected = True

        px_max = -1e38
        px_min = 1e38
        pt_min = None
        pt_max = None

        for px in lp.Loop(shp.Extent, 0, shp, 'T', False):    
            if px.Value < px_min:
                px_min = px.Value
                pt_min = px.Center
            
            if px.Value > px_max:
                px_max = px.Value
                pt_max = px.Center
        
        l_tmp = pdk.TGIS_LayerVector()
        l_tmp.CS = lp.CS
        self.GIS.Add(l_tmp)

        l_tmp.Params.Marker.Style = pdk.TGIS_MarkerStyle().Cross
        l_tmp.Params.Marker.Size = -10
        l_tmp.Params.Marker.Color = pdk.TGIS_Color.Black

        shp_tmp = l_tmp.CreateShape(pdk.TGIS_ShapeType().Point)
        shp_tmp.AddPart()
        shp_tmp.AddPoint(pt_min)

        shp_tmp = l_tmp.CreateShape(pdk.TGIS_ShapeType().Point)
        shp_tmp.AddPart()
        shp_tmp.AddPoint(pt_max)

        self.GIS.InvalidateWholeMap()

        self.Memo1.AppendLine(
            f"Min: {px_min:.2f}, Location: {pt_min.X:.2f}, {pt_min.Y:.2f}"
        )
        self.Memo1.AppendLine(
            f"Max: {px_max:.2f}, Location: {pt_max.X:.2f}, {pt_max.Y:.2f}"
        )
        
    def btnAverageColorClick(self, _sender):
        self.Memo1.Clear()

        self.GIS.Open(pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                      '/Samples/PixelEdit/bitmap.ttkproject')

        lp = self.GIS.Get('bluemarble')
        lv = self.GIS.Get('countries')

        shp = lv.GetShape(679).MakeEditable()  # Spain
        self.GIS.Lock()
        self.GIS.VisibleExtent = shp.ProjectedExtent
        self.GIS.Zoom = self.GIS.Zoom / 2.0
        self.GIS.Unlock()
        
        cnt = 0
        r = 0
        g = 0
        b = 0

        for px in lp.Loop(shp.Extent, 0, shp, 'T', False):
            r += px.Color.R
            g += px.Color.G
            b += px.Color.B
            cnt += 1

        if cnt > 0:
            cl = pdk.TGIS_Color.FromRGB(int(r/cnt), int(g/cnt), int(b/cnt))
            
            for px in lp.Loop(shp.Extent, 0, shp, 'T', True):
                px.Color = cl
            
        self.GIS.InvalidateWholeMap()

    def btnCreateBitmapClick(self, _sender):
        self.GIS.Close()
        self.Memo1.Clear()

        test_jpg = "test.jpg"
        if os.path.exists(test_jpg):
            os.remove(test_jpg)
            
        lp = pdk.TGIS_LayerJPG()
        lp.Build(
            test_jpg,
            pdk.TGIS_CSFactory.ByEPSG(4326),
            pdk.TGIS_Utils().GisExtent(-180, -90, 180, 90),
            360,
            180
        )
        
        # direct access to pixels
        lck = lp.LockPixels(pdk.TGIS_Utils.GisExtent(-45, -45, 45, 45), lp.CS, True)
        try:
            for x in range(lck.Bounds.Left, lck.Bounds.Right+1):
                for y in range(lck.Bounds.Top, lck.Bounds.Bottom+1):
                    lck.Bitmap.Value(lck.BitmapPos(x, y), pdk.TGIS_Color().Red.ARGB)
            
        finally:
            lp.UnlockPixels(lck)
            
        lp.SaveData()
        self.GIS.Open(test_jpg)

    def btnCreateGridClick(self, _sender):
        self.GIS.Close()
        self.Memo1.Clear()

        test_grd = "test.grd"
        if os.path.exists(test_grd):
            os.remove(test_grd)

        lp = pdk.TGIS_LayerGRD()
        lp.Build(
            test_grd,
            pdk.TGIS_CSFactory.ByEPSG(4326),
            pdk.TGIS_Utils().GisExtent(-180, -90, 180, 90),
            360,
            180
        )

        # direct access to pixels
        lck = lp.LockPixels(pdk.TGIS_Utils.GisExtent(-45, -45, 45, 45), lp.CS, True)
        try:
            for x in range(lck.Bounds.Left, lck.Bounds.Right+1):
                for y in range(lck.Bounds.Top, lck.Bounds.Bottom+1):
                    lck.Grid[y][x] = 100*random()
                    # or in an alternative way
                    # lck.Grid.Value(y, x, 100*random())
        finally:
            lp.UnlockPixels(lck)

        lp.SaveData()
        self.GIS.Open(test_grd)
            
            
def main():
    frm = PixelEditForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
