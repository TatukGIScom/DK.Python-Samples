import tatukgis_pdk as pdk

class EnumeratorsForm(pdk.TGIS_PvlForm):
    FIELD_COUNT = "COUNT"

    def __init__(self, _owner):
        self.Caption = "Enumerators - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.btnFullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "ZoomIn"
        self.button2.OnClick = self.btnZoomIn_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 155, None, 3)
        self.button3.Caption = "ZoomOut"
        self.button3.OnClick = self.btnZoomOut_click

        self.button4 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button4.Place(75, 22, None, 230, None, 3)
        self.button4.Caption = "Dragging"
        self.button4.OnClick = self.btnDrag_click

        self.button5 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button5.Place(75, 22, None, 305, None, 3)
        self.button5.Caption = "Enumerate"
        self.button5.OnClick = self.btnEnumerate_click

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 592
        self.GIS.Height = 425
        self.GIS.Open(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "/World/Countries/USA/States/California/tl_2008_06_county.shp"
        )
        self.GIS.FullExtent()

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def btnDrag_click(self, _sender):
        # change viewer mode
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnEnumerate_click(self, _sender):
        # get a layer with world shape
        lv = self.GIS.Items[0]

        if lv.FindField(self.FIELD_COUNT) < 0:
            lv.AddField(self.FIELD_COUNT, pdk.TGIS_FieldType().Number, 10, 0)

        self.GIS.HourglassPrepare()

        # mark all shapes that can be affected as editable
        # to keep the layer consistent after modifying shapes
        # also compute numer of shape that can be affected
        max_cnt = 0
        try:
            for shp in lv.Loop():
                cnt = -1
                for _ in lv.Loop(shp.ProjectedExtent, '', shp, '****T', True):
                    cnt += 1
                    self.GIS.HourglassShake()

                tmp_shp = shp.MakeEditable()
                tmp_shp.SetField(self.FIELD_COUNT, cnt)
                if cnt > max_cnt:
                    max_cnt = cnt
        finally:
            self.GIS.HourglassRelease()

        lv.Params.Labels.Field = self.FIELD_COUNT
        lv.Params.Render.Expression = self.FIELD_COUNT
        lv.Params.Render.MinVal = 1.
        lv.Params.Render.MaxVal = float(max_cnt)
        lv.Params.Render.StartColor = pdk.TGIS_Color.White
        lv.Params.Render.EndColor = pdk.TGIS_Color.Red
        lv.Params.Render.Zones = 5
        lv.Params.Area.Color = pdk.TGIS_Color.RenderColor

        # and now refresh map
        self.GIS.InvalidateWholeMap()


def main():
    frm = EnumeratorsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
