import tatukgis_pdk as pdk
import sqlite3

class JoinAndRenderForm(pdk.TGIS_PvlForm):
    sqlConnection = None

    def __init__(self, _owner):
        self.Caption = "JoinAndChart - TatukGIS DK Sample"
        self.ClientWidth = 552
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

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
        self.cmbSize.Place(100, 22, None, 250, None, 3)
        names = ("pop2000",
                 "under18",
                 "asia",
                 "black",
                 "white",
                 "hisp_lat",
                 "male2000",
                 "female2000")
        for name in names:
            self.cmbSize.ItemsAdd(name)
        self.cmbSize.ItemIndex = 0
        self.cmbSize.OnChange = self.cmb_change

        self.pColorStart = pdk.TGIS_PvlPreviewPanel(self.toolbar_buttons.Context)
        self.pColorStart.Place(20, 22, None, 360, None, 2)
        self.pColorStart.Color = pdk.TGIS_Color().Aqua
        self.pColorStart.Caption = ''
        self.pColorStart.OnClick = self.pColorStart_click

        self.pColorEnd = pdk.TGIS_PvlPreviewPanel(self.toolbar_buttons.Context)
        self.pColorEnd.Place(20, 22, None, 381, None, 2)
        self.pColorEnd.Color = pdk.TGIS_Color().Navy
        self.pColorEnd.Caption = ''
        self.pColorEnd.OnClick = self.pColorEnd_click

        self.scrTransparency = pdk.TGIS_PvlTrackBar(self.toolbar_buttons.Context)
        self.scrTransparency.Place(137, 45, None, 406, None, 0)
        self.scrTransparency.Minimum = 1
        self.scrTransparency.Maximum = 100
        self.scrTransparency.Position = 100
        self.scrTransparency.OnChange = self.scrTransparency_scroll

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(552, 19, None, 0, None, 480)
        self.status_bar_bottom.Align = "Bottom"

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 143
        self.GIS.Top = 28
        self.GIS.Width = 400
        self.GIS.Height = 452
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(143, 452, None, 0, None, 28)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

    def cmb_change(self, _sender):
        if self.GIS.Items.Count == 0:
            return
        ll = self.GIS.Items[0]
        if ll is None:
            return

        # get params
        v_size = self.cmbSize.Text

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
        ll.Params.Render.Zones = 10
        ll.Params.Render.MinVal = v_min
        ll.Params.Render.MaxVal = v_max
        ll.Params.Render.StartColor = self.pColorStart.Color
        ll.Params.Render.EndColor = self.pColorEnd.Color
        ll.Params.Area.Color = pdk.TGIS_Color().RenderColor
        ll.Params.Area.ShowLegend = True

        self.GIS.InvalidateWholeMap()

    def form_show(self, sender):
        # create connection object
        self.sqlConnection = sqlite3.connect(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                                             "World/Countries/USA/Statistical/Stats.db")
        # use layer to display charts
        ll = pdk.TGIS_LayerSHP()
        ll.Path = (pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                   "/World/Countries/USA/States/California/tl_2008_06_county.shp")
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

        self.cmb_change(sender)

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

    def scrTransparency_scroll(self, _sender):
        ll = self.GIS.Items[0]
        if ll is None:
            return

        # change transparency
        ll.Transparency = int(self.scrTransparency.Position)

        self.GIS.InvalidateWholeMap()

    def pColorStart_click(self, sender):
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pColorStart.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return

        self.pColorStart.Color = dlg_color.Color
        self.cmb_change(sender)

    def pColorEnd_click(self, sender):
        dlg_color = pdk.TGIS_ControlColor(self)
        dlg_color.Color = self.pColorEnd.Color
        if dlg_color.Execute() != pdk.TGIS_PvlModalResult().OK:
            return

        self.pColorEnd.Color = dlg_color.Color
        self.cmb_change(sender)


def main():
    frm = JoinAndRenderForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
