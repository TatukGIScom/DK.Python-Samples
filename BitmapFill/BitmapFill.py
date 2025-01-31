import tatukgis_pdk as pdk
import os

class BitmapFillForm(pdk.TGIS_PvlForm):
    NAME_COUNTIES = "counties"
    FIELD_POPULATION = "population"
    FIELD_AREA = "area"
    FIELD_CNTYIDFP = "CNTYIDFP"
    FIELD_NAME = "NAME"

    def __init__(self, _owner):
        self.Caption = "Bitmap Fill - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        self.GIS.Align = "Client"

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.FullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, self.button1, 3, None, 3)
        self.button2.Caption = "ZoomIn"
        self.button2.OnClick = self.btnZoomIn_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, self.button2, 3, None, 3)
        self.button3.Caption = "ZoomOut"
        self.button3.OnClick = self.btnZoomOut_click

        self.comboStatistic = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.comboStatistic.Place(75, 22, self.button3, 3, None, 3)
        self.comboStatistic.OnChange = self.comboStatistic_Change
        self.comboStatistic.ItemsAdd('By population')
        self.comboStatistic.ItemsAdd('By density')

        self.comboLabels = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.comboLabels.Place(75, 22, self.comboStatistic, 3, None, 3)
        self.comboLabels.OnChange = self.comboLabels_Change
        self.comboLabels.ItemsAdd('No Labels')
        self.comboLabels.ItemsAdd('By FIPS')
        self.comboLabels.ItemsAdd('By NAME')

        script_path = os.path.dirname(__file__)

        self.Image1 = pdk.TGIS_Bitmap()
        self.Image1.LoadFromFile(script_path + "/pictureBox1.bmp")

        self.Image2 = pdk.TGIS_Bitmap()
        self.Image2.LoadFromFile(script_path + "/pictureBox2.bmp")

        self.Image3 = pdk.TGIS_Bitmap()
        self.Image3.LoadFromFile(script_path + "/pictureBox3.bmp")

        self.Image4 = pdk.TGIS_Bitmap()
        self.Image4.LoadFromFile(script_path + "/pictureBox4.bmp")

        self.Image5 = pdk.TGIS_Bitmap()
        self.Image5.LoadFromFile(script_path + "/pictureBox5.bmp")

        self.panel = pdk.TGIS_PvlPanel(self.Context)
        self.panel.Height = 300
        self.panel.Width = 90
        self.panel.Align = "Right"

        self.smblist = pdk.TGIS_PvlIconsList(self.Context)
        self.smblist.Add(script_path + "/pictureBox1.bmp")
        self.smblist.Add(script_path + "/pictureBox2.bmp")
        self.smblist.Add(script_path + "/pictureBox3.bmp")
        self.smblist.Add(script_path + "/pictureBox4.bmp")
        self.smblist.Add(script_path + "/pictureBox5.bmp")

        self.box1 = pdk.TGIS_PvlIconButton(self.panel.Context)
        self.box1.IconsList = self.smblist
        self.box1.IconSize = 60
        self.box1.IconIndex = 2
        self.box1.Place(60, 60, None, 10, None, 10)

        self.box2 = pdk.TGIS_PvlIconButton(self.panel.Context)
        self.box2.IconsList = self.smblist
        self.box2.IconSize = 60
        self.box2.IconIndex = 1
        self.box2.Place(60, 60, None, 10, self.box1, 10)

        self.box3 = pdk.TGIS_PvlIconButton(self.panel.Context)
        self.box3.IconsList = self.smblist
        self.box3.IconIndex = 2
        self.box3.IconSize = 60
        self.box3.Place(60, 60, None, 10, self.box2, 10)

        self.box4 = pdk.TGIS_PvlIconButton(self.panel.Context)
        self.box4.IconsList = self.smblist
        self.box4.IconIndex = 3
        self.box4.IconSize = 60
        self.box4.Place(60, 60, None, 10, self.box3, 10)

        self.box5 = pdk.TGIS_PvlIconButton(self.panel.Context)
        self.box5.IconsList = self.smblist
        self.box5.IconIndex = 4
        self.box5.IconSize = 60
        self.box5.Place(60, 60, None, 10, self.box4, 10)
        # self.box5.Enabled = True

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

    def form_show(self, _sender):
        # add country layer
        ll = pdk.TGIS_LayerSHP()
        ll.Path = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                   + '/World/Countries/USA/States/California/Counties.SHP')
        ll.Name = self.NAME_COUNTIES
        ll.UseConfig = False

        # set custom painting routine
        ll.PaintShapeEvent = self.PaintShape
        self.GIS.Add(ll)

        self.GIS.FullExtent()

        self.comboStatistic.ItemIndex = 0
        self.comboLabels.ItemIndex = 0

    def PaintShape(self, _sender, _shape):
        # calculate parameters
        population = _shape.GetField(self.FIELD_POPULATION)
        area = _shape.GetField(self.FIELD_AREA)
        if area == 0:
            return

        old_bitmap = None

        if _shape.Params.Area.Bitmap:
            if not _shape.Params.Area.Bitmap.IsEmpty:
                old_bitmap = _shape.Params.Area.Bitmap

        _shape.Params.Area.Bitmap = pdk.TGIS_Bitmap()
        _shape.Params.Area.Pattern = pdk.TGIS_BrushStyle().Solid
        _shape.Params.Area.Color = pdk.TGIS_Color.Red
        _shape.Params.Area.OutlineColor = pdk.TGIS_Color.DimGray
        _shape.Params.Area.OutlineWidth = 20

        if self.comboStatistic.itemIndex == 1:
            factor = population/area
            # assign different bitmaps for factor value
            if factor < 1:
                _shape.Params.Area.Bitmap = self.Image1
            elif factor < 7:
                _shape.Params.Area.Bitmap = self.Image2
            elif factor < 52:
                _shape.Params.Area.Bitmap = self.Image3
            elif factor < 380:
                _shape.Params.Area.Bitmap = self.Image4
            elif factor < 3000:
                _shape.Params.Area.Bitmap = self.Image5
        else:
            factor = population
            if factor < 5000:
                _shape.Params.Area.Bitmap = self.Image1
            elif factor < 22000:
                _shape.Params.Area.Bitmap = self.Image2
            elif factor < 104000:
                _shape.Params.Area.Bitmap = self.Image3
            elif factor < 478000:
                _shape.Params.Area.Bitmap = self.Image4
            elif factor < 2186000:
                _shape.Params.Area.Bitmap = self.Image5

        # draw bitmaps
        _shape.Draw()
        if old_bitmap is not None:
            _shape.Params.Area.Bitmap = old_bitmap

    def FullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def comboStatistic_Change(self, _sender):
        self.GIS.InvalidateWholeMap()

    def comboLabels_Change(self, _sender):
        ll = self.GIS.Get(self.NAME_COUNTIES)
        if ll:
            if self.comboLabels.ItemIndex == 1:
                ll.Params.Labels.Field = self.FIELD_CNTYIDFP
            elif self.comboLabels.ItemIndex == 2:
                ll.Params.Labels.Field = self.FIELD_NAME
            else:
                ll.Params.Labels.Field = ""

        self.GIS.InvalidateWholeMap()


def main():
    frm = BitmapFillForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
