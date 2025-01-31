import tatukgis_pdk as pdk

class StatisticsForm(pdk.TGIS_PvlForm):
    LAYER_COUNTIES = "counties"
    FIELD_POPULATION = "population"
    FIELD_AREA = "area"
    FIELD_CNTYIDFP = "CNTYIDFP"
    FIELD_NAME = "NAME"

    def __init__(self, _owner):
        self.Caption = "Statistics - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Align = "Client"

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

        self.comboStatistic = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.comboStatistic.Place(110, 22, None, 300, None, 3)
        self.comboStatistic.OnChange = self.comboStatistic_change
        self.comboStatistic.ItemsAdd('By population')
        self.comboStatistic.ItemsAdd('By area')

        self.comboLabels = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.comboLabels.Place(110, 22, None, 420, None, 3)
        self.comboLabels.OnChange = self.comboLabels_change
        self.comboLabels.ItemsAdd('No Labels')
        self.comboLabels.ItemsAdd('By FIPS')
        self.comboLabels.ItemsAdd('By NAME')

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

    def form_show(self, _sender):
        # add country layer
        ll = pdk.TGIS_LayerSHP()
        ll.Path = (pdk.TGIS_Utils().GisSamplesDataDirDownload() +
                   'World/Countries/USA/States/California/Counties.SHP')
        ll.Name = self.LAYER_COUNTIES
        ll.UseConfig = False

        # set custom painting routine
        ll.PaintShapeEvent = self.paint_shape
        self.GIS.Add(ll)

        self.GIS.FullExtent()

        self.comboStatistic.ItemIndex = 0
        self.comboLabels.ItemIndex = 0

    def paint_shape(self, _sender, shape):
        # calculate parameters
        population = shape.GetField(self.FIELD_POPULATION)
        area = shape.GetField(self.FIELD_AREA)

        if self.comboStatistic.ItemIndex == 1:
            factor = area

            # assign different bitmaps for factor value
            if factor < 40:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x00F00C)
            elif factor < 130:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0xAEFFB3)
            elif factor < 400:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0xCCCCFF)
            elif factor < 2000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x3535FF)
            elif factor < 10000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x0000B3)
            else:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x3000B3)

        else:
            factor = population
            if factor < 5000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x00F00C)
            elif factor < 22000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0xAEFFB3)
            elif factor < 104000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0xCCCCFF)
            elif factor < 478000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x3535FF)
            elif factor < 2186000:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x0000B3)
            else:
                shape.Params.Area.Color = pdk.TGIS_Color().FromBGR(0x3000B3)

        # draw bitmaps
        shape.Draw()

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

    def comboStatistic_change(self, _sender):
        self.GIS.InvalidateWholeMap()

    def comboLabels_change(self, _sender):
        ll = self.GIS.Get(self.LAYER_COUNTIES)
        if ll is not None:
            if self.comboLabels.ItemIndex == 1:
                ll.Params.Labels.Field = self.FIELD_CNTYIDFP
            elif self.comboLabels.ItemIndex == 2:
                ll.Params.Labels.Field = self.FIELD_NAME
            else:
                ll.Params.Labels.Field = ''

        self.GIS.InvalidateWholeMap()


def main():
    frm = StatisticsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
