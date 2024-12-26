import tatukgis_pdk as pdk

class MultiselectForm(pdk.TGIS_PvlForm):
    ctrlPressed = None
    FIELD_NAME = "NAME"

    def __init__(self, _owner):
        self.Caption = "Multiselect - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(592, 29, None, 0, None, 0)

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 26
        self.GIS.Width = 417
        self.GIS.Height = 480
        self.GIS.Mode = pdk.TGIS_ViewerMode().Select
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseDown = self.GISMouseDown
        
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

        self.GIS_Attributes = pdk.TGIS_PvlControlAttributes(self.Context)
        self.GIS_Attributes.Place(175, 280, None, 417, None, 26)
        self.GIS_Attributes.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.lbSelected = pdk.TGIS_PvlListBox(self.Context)
        self.lbSelected.Place(175, 220, None, 417, None, 256)
        self.lbSelected.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.status_bar_bottom = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar_bottom.Place(600, 23, None, 0, None, 380)
        self.status_bar_bottom.Align = "Bottom"

        self.lblMsg = pdk.TGIS_PvlLabel(self.status_bar_bottom.Context)
        self.lblMsg.Place(300, 19, None, 3, None, 0)
        self.lblMsg.Caption = "Ctrl + Mouse click to select/deselect multiple shapes"

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "World/Countries/USA/States/California/Counties.SHP")

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def btnFullExtent_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.FullExtent()

    def GISMouseMove(self, _sender,  _shift, x, y):
        if self.GIS.IsEmpty:
            return

        # convert screen coordinates to map coordinates
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # calculate precision of location as 5 pixels
        precision = 5.0 / self.GIS.Zoom
        # let's try to locate a selected shape on the map
        shp = self.GIS.Locate(ptg, precision)

        if shp is not None:
            self.button1.Caption = shp.GetField(self.FIELD_NAME)

    def GISMouseDown(self, _sender, _button, shift, x, y):
        if self.GIS.IsEmpty:
            return

        lv = self.GIS.Items[0]

        # locate a shape after click
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))
        shp = self.GIS.Locate(ptg, 5.0 / self.GIS.Zoom)

        if shp is not None:
            shp = shp.MakeEditable()

            # if any found
            if "Ctrl" in shift:  # multiple select
                # set it as selected
                shp.IsSelected = not shp.IsSelected
                shp.Invalidate()

                self.lbSelected.BeginUpdate()
                self.lbSelected.ItemsClear()

                # find a selected shape
                tmp_shp = lv.FindFirst(pdk.TGIS_Utils.GisWholeWorld(), "GIS_SELECTED=True")

                # if not found clear attribute control
                if not tmp_shp:
                    self.GIS_Attributes.Clear()

                # let's locate another one, if also found - show statistic attributes
                tmp2_shp = lv.FindNext()
                if tmp2_shp:
                    self.GIS_Attributes.ShowSelected(lv)
                else:
                    self.GIS_Attributes.ShowShape(tmp_shp)

                for i in range(lv.Items.Count):
                    # we can do this because selected items are MakeEditable,
                    # so they exist on Items list
                    tmp_shp = lv.Items.Item(i)

                    # add selected shapes to list
                    if tmp_shp.IsSelected:
                        self.lbSelected.ItemsAdd(tmp_shp.GetField(self.FIELD_NAME))
                self.lbSelected.EndUpdate()
            else:
                # deselect existing
                lv.DeselectAll()
                self.lbSelected.ItemsClear()
                self.lbSelected.ItemsAdd(shp.GetField(self.FIELD_NAME))
                # set as selected this clicked
                shp.IsSelected = True
                shp.Invalidate()
                # update attribute control
                self.GIS_Attributes.ShowShape(shp)

        else:
            # deselect existing
            lv.DeselectAll()
            self.lbSelected.ItemsClear()
            self.GIS_Attributes.Clear()


def main():
    frm = MultiselectForm(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
