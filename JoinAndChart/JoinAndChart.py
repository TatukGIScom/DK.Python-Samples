import tatukgis_pdk as pdk
import sqlite3

class JoinAndChartForm(pdk.TGIS_PvlForm):
    sqlConnection = None

    def __init__(self, _owner):
        self.Caption = "JoinAndChart - TatukGIS DK Sample"
        self.ClientWidth = 650
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(640, 29, None, 0, None, 0)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 22, None, 3, None, 3)
        self.button1.Caption = "Full Extent"
        self.button1.OnClick = self.FullExtent_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 22, None, 79, None, 3)
        self.button2.Caption = "ZoomIn"
        self.button2.OnClick = self.btnZoomIn_click

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 22, None, 155, None, 3)
        self.button3.Caption = "ZoomOut"
        self.button3.OnClick = self.btnZoomOut_click

        self.cmbSize = pdk.TGIS_PvlComboBox(self.Context)
        self.cmbSize.Place(100, 22, None, 300, None, 3)
        names = ("pop2000",
                 "male2000",
                 "female2000",
                 "under18",
                 "asia",
                 "black",
                 "white",
                 "hisp_lat")
        for name in names:
            self.cmbSize.ItemsAdd(name)
        self.cmbSize.OnChange = self.cmb_change

        self.cmbValues = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cmbValues.Place(130, 22, None, 405, None, 3)
        self.cmbValues.ItemsAdd("black:white")
        self.cmbValues.ItemsAdd("pop2000:square_mil")
        self.cmbValues.ItemsAdd("male2000:female2000")
        self.cmbValues.OnChange = self.cmb_change

        self.cmbStyle = pdk.TGIS_PvlComboBox(self.toolbar_buttons.Context)
        self.cmbStyle.Place(100, 22, None, 540, None, 3)
        self.cmbStyle.ItemsAdd("Pie")
        self.cmbStyle.ItemsAdd("Bar")
        self.cmbStyle.OnChange = self.cmb_change

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(592, 19, None, 0, None, 482)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = -2
        self.GIS.Top = 30
        self.GIS.Width = 700
        self.GIS.Height = 480
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

    def form_show(self, _sender):
        self.cmbSize.ItemIndex = 0
        self.cmbValues.ItemIndex = 0
        self.cmbStyle.ItemIndex = 0

        # create connection object
        self.sqlConnection = sqlite3.connect(
            pdk.TGIS_Utils().GisSamplesDataDirDownload() +
            "World/Countries/USA/Statistical/Stats.db"
        )

        # use layer to display charts
        ll = pdk.TGIS_LayerSHP()
        ll.Path = (pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                   "World/Countries/USA/States/California/tl_2008_06_county.shp")
        ll.Name = "tl_2008_06_county"

        ll.UseConfig = False
        ll.Params.Labels.Field = "name"
        ll.Params.Labels.Pattern = pdk.TGIS_BrushStyle().Clear
        ll.Params.Labels.OutlineWidth = 0
        ll.Params.Labels.FontColor = pdk.TGIS_Color().White
        ll.Params.Labels.Color = pdk.TGIS_Color().Black
        ll.Params.Labels.Position = [pdk.TGIS_LabelPosition().MiddleCenter or pdk.TGIS_LabelPosition().Flow]
        ll.Params.Chart.Size = pdk.TGIS_Utils.GIS_RENDER_SIZE()
        ll.Params.Render.StartSize = 350
        ll.Params.Render.EndSize = 1000

        self.GIS.Add(ll)
        self.GIS.FullExtent()

        self.cmb_change(0)

    def cmb_change(self, _sender):
        if self.GIS.Items.Count == 0:
            return

        ll = self.GIS.Items[0]
        if ll is None:
            return

        # get params
        v_size = self.cmbSize.Text
        v_values = self.cmbValues.Text
        v_style = self.cmbStyle.Text

        # find min, max values for shapes
        cursor = self.sqlConnection.cursor()
        cursor.execute("SELECT min({0}) AS mini, max({1}) AS maxi FROM ce2000t".format(v_size, v_size))
        r = cursor.fetchone()
        v_min = r[0]
        v_max = r[1]

        # let's load data to recordset
        cursor.execute("SELECT * FROM ce2000t ORDER BY fips")

        # connect layer with query results
        ll.JoinDBAPI2 = cursor

        # set primary and foreign keys
        ll.JoinPrimary = "cntyidfp"
        ll.JoinForeign = "fips"

        # render results
        ll.Params.Render.Expression = v_size
        ll.Params.Render.Chart = "0:0:" + v_values
        ll.Params.Chart.Style = pdk.TGIS_Utils.ParamChart(v_style, pdk.TGIS_ChartStyle().Pie)
        ll.Params.Render.Zones = 10
        ll.Params.Render.MinVal = v_min
        ll.Params.Render.MaxVal = v_max

        self.GIS.InvalidateWholeMap()

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
        ll = self.GIS.Get("counties")
        if ll is None:
            return

        if self.comboLabels.ItemIndex == 1:
            ll.Params.Labels.Field = self.CNTYIDFP
        elif self.comboLabels.ItemIndex == 2:
            ll.Params.Labels.Field = self.NAME
        else:
            ll.Params.Labels.Field = ''

        self.GIS.InvalidateWholeMap()


def main():
    frm = JoinAndChartForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
