import tatukgis_pdk as pdk
from math import pi, radians
from random import randint
from time import sleep

class InMemoryForm(pdk.TGIS_PvlForm):
    currPoss = 0
    SHIP: pdk.TGIS_ShapeType

    def __init__(self, _owner):
        self.Caption = "InMemory - TatukGIS Sample"
        self.Left = 200
        self.Top = 120
        self.Width = 608
        self.Height = 512
        self.myshp = None

        self.toolbar = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar.Place(592, 29, None, 0, None, 0)
        self.toolbar.Align = "Top"

        self.btnCreateLayer = pdk.TGIS_PvlButton(self.toolbar.Context)
        self.btnCreateLayer.Place(75, 22, None, 3, None, 3)
        self.btnCreateLayer.Caption = "Create Layer"
        self.btnCreateLayer.OnClick = self.btnCreateLayer_click

        self.btnAddPoints = pdk.TGIS_PvlButton(self.Context)
        self.btnAddPoints.Place(75, 22, None, 78, None, 3)
        self.btnAddPoints.Caption = "Add Points"
        self.btnAddPoints.OnClick = self.btnAddPoints_click

        self.btnAddLine = pdk.TGIS_PvlButton(self.Context)
        self.btnAddLine.Place(75, 22, None, 153, None, 3)
        self.btnAddLine.Caption = "Add Lines"
        self.btnAddLine.OnClick = self.btnAddLine_click

        self.btnAnimate = pdk.TGIS_PvlButton(self.Context)
        self.btnAnimate.Place(75, 22, None, 228, None, 3)
        self.btnAnimate.Caption = "Animate"
        self.btnAnimate.OnClick = self.btnAnimate_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Align = "Client"
        
        self.statusbar = pdk.TGIS_PvlPanel(self.Context)
        self.statusbar.Align = "Bottom"
        
        self.lblStatus = pdk.TGIS_PvlLabel(self.statusbar.Context)
        self.lblStatus.Place(100, 19, None, 3, None, 0)
        self.lblStatus.Caption = ''
        
    def is_gis_empty(self) -> bool:
        if self.GIS.IsEmpty:
            pdk.TGIS_PvlMessages.ShowInfo("Create a layer first !", self.Context)
            return True
        return False

    def btnCreateLayer_click(self, _sender):
        """Create layer"""
        
        # create a layer loading symbols for marker and line
        ll = pdk.TGIS_LayerVector()
        
        sample_dir = pdk.TGIS_Utils.GisSamplesDataDirDownload()
        symbol_list = pdk.TGIS_Utils().SymbolList
        ll.Params.Marker.Symbol = symbol_list.Prepare(
            sample_dir + "Symbols/2267.cgm"
        )
        ll.Params.Marker.SymbolRotate = pi/2
        ll.Params.Marker.Size = -20
        ll.Params.Line.Symbol = symbol_list.Prepare(
            sample_dir + "Symbols/1301.cgm"
        )
        ll.Params.Line.Width = -5

        self.GIS.Add(ll)
        ll.CachedPaint = False
        ll.Extent = pdk.TGIS_Utils.GisExtent(-180, -90, 180, 90)

        self.GIS.FullExtent()

        self.lblStatus.Caption = "Layer created."
        self.btnCreateLayer.Enabled = False

    def btnAddPoints_click(self, _sender):
        """Add points"""

        if self.is_gis_empty():
            return

        lv = self.GIS.Items[0]

        # fill the viewer with points
        for _ in range(100):
            shp = lv.CreateShape(pdk.TGIS_ShapeType().Point)
            
            shp.Params.Marker.SymbolRotate = radians(randint(0, 359))
            color = pdk.TGIS_Color.FromRGB(randint(0, 255),
                                           randint(0, 255),
                                           randint(0, 255))

            shp.Params.Marker.Color = color
            shp.Params.Marker.OutlineColor = color
            shp.Lock(pdk.TGIS_Lock().Extent)
            try:
                shp.AddPart()
                shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 360) - 180,
                                                     randint(0, 180) - 90))
            finally:
                shp.UnLock()
            
        self.GIS.InvalidateWholeMap()
        self.lblStatus.Caption = "Points added."

    def btnAddLine_click(self, _sender):
        """Add line"""

        if self.is_gis_empty():
            return

        lv = self.GIS.Items[0]
        shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        for i in range(20):
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 360) - 180,
                                                 randint(0, 180) - 90))
        shp.Unlock()

        self.GIS.InvalidateWholeMap()
        self.lblStatus.Caption = "Line added."

    def btnAnimate_click(self, _sender):
        """Create a ship and fly"""

        if self.is_gis_empty():
            return

        # create a ship and fly
        lv = self.GIS.Items[0]
        shp = lv.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(0, 0))

        shp.Params.Marker.Color = pdk.TGIS_Color.Blue
        shp.Params.Marker.OutlineColor = pdk.TGIS_Color.Blue
        shp.Params.Marker.Size = -20

        shp.Unlock()
        shp.Invalidate()

        for i in range(90):
            shp.SetPosition(pdk.TGIS_Utils.GisPoint(i*2, i), None, 0)
            sleep(0.01)
            self.GIS.ProcessMessages()


def main():
    frm = InMemoryForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
