import tatukgis_pdk as pdk

class PaintEventsForm(pdk.TGIS_PvlForm):
    center_ptg: pdk.TGIS_Point

    def __init__(self, _owner):
        self.Caption = "PaintEvents - TatukGIS DK Sample"
        self.ClientWidth = 776
        self.ClientHeight = 606
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 30, None, 0, None, 0)

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(40, 25, None, 0, None, 3)
        self.btnFullExtent.Caption = "Extent"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoomIn = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomIn.Place(40, 25, None, 41, None, 3)
        self.btnZoomIn.Caption = " + "
        self.btnZoomIn.OnClick = self.btnZoomIn_click

        self.btnZoomOut = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoomOut.Place(40, 25, None, 82, None, 3)
        self.btnZoomOut.Caption = " - "
        self.btnZoomOut.OnClick = self.btnZoomOut_click

        self.chkDrag = pdk.TGIS_PvlCheckBox(self.toolbar_buttons.Context)
        self.chkDrag.Place(121, 28, None, 132, None, 2)
        self.chkDrag.Caption = "Dragging"
        self.chkDrag.OnChange = self.chkDrag_change

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 30
        self.GIS.Width = 552
        self.GIS.Height = 552
        self.GIS.BeforePaintRendererEvent = self.GIS_BeforePaintRendererEvent
        self.GIS.AfterPaintRendererEvent = self.GIS_AfterPaintRendererEvent
        self.GIS.PaintExtraEvent = self.GIS_PaintExtraEvent
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.toolbar_checkboxes = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_checkboxes.Place(224, 552, None, 552, None, 30)
        self.toolbar_checkboxes.Anchors = (pdk.TGIS_PvlAnchor().Top,
                                           pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.chkBeforePaintRendererEvent = pdk.TGIS_PvlCheckBox(self.toolbar_checkboxes.Context)
        self.chkBeforePaintRendererEvent.Place(200, 21, None, 16, None, 21)
        self.chkBeforePaintRendererEvent.Caption = "BeforePaintRendererEvent"
        self.chkBeforePaintRendererEvent.Checked = True
        self.chkBeforePaintRendererEvent.OnChange = self.chkBeforePaintRendererEvent_change

        self.chkPaintExtraEvent = pdk.TGIS_PvlCheckBox(self.toolbar_checkboxes.Context)
        self.chkPaintExtraEvent.Place(200, 21, None, 16, None, 49)
        self.chkPaintExtraEvent.Caption = "PaintExtraEvent"
        self.chkPaintExtraEvent.Checked = True
        self.chkPaintExtraEvent.OnChange = self.chkPaintExtraEvent_change

        self.chkAfterPaintRendererEvent = pdk.TGIS_PvlCheckBox(self.toolbar_checkboxes.Context)
        self.chkAfterPaintRendererEvent.Place(200, 21, None, 16, None, 77)
        self.chkAfterPaintRendererEvent.Caption = "AfterPaintRendererEvent"
        self.chkAfterPaintRendererEvent.Checked = True
        self.chkAfterPaintRendererEvent.OnChange = self.chkAfterPaintRendererEvent_change

        self.btnTestPrintBmp = pdk.TGIS_PvlButton(self.toolbar_checkboxes.Context)
        self.btnTestPrintBmp.Place(188, 28, None, 16, None, 188)
        self.btnTestPrintBmp.Caption = "Test PrintBmp"
        self.btnTestPrintBmp.OnClick = self.btnTestPrintBmp_click

        self.chkPrintBmpWithEvents = pdk.TGIS_PvlCheckBox(self.toolbar_checkboxes.Context)
        self.chkPrintBmpWithEvents.Place(200, 21, None, 16, None, 223)
        self.chkPrintBmpWithEvents.Caption = "PrintBmp with events"
        self.chkPrintBmpWithEvents.Checked = True

    def form_show(self, _sender):
        # add  layer
        ll = pdk.TGIS_LayerSHP()
        ll.Path = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                   + "World/Countries/USA/States/California/Counties.shp")
        ll.Params.Area.Color = pdk.TGIS_Color().LightGray
        self.GIS.Add(ll)
        self.GIS.FullExtent()
        self.center_ptg = self.GIS.CenterPtg

    def chkDrag_change(self, _sender):
        if self.chkDrag.Checked:
            self.GIS.Mode = pdk.TGIS_ViewerMode().Drag
        else:
            self.GIS.Mode = pdk.TGIS_ViewerMode().Select

    def btnZoomIn_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom * 2

    def btnZoomOut_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Zoom = self.GIS.Zoom / 2

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def chkBeforePaintRendererEvent_change(self, _sender):
        if self.chkBeforePaintRendererEvent.Checked:
            self.GIS.BeforePaintRendererEvent = self.GIS_BeforePaintRendererEvent            
        else:
            self.GIS.BeforePaintRendererEvent = None
        self.GIS.InvalidateWholeMap()

    def chkPaintExtraEvent_change(self, _sender):
        if self.chkPaintExtraEvent.Checked:
            self.GIS.PaintExtraEvent = self.GIS_PaintExtraEvent
        else:
            self.GIS.PaintExtraEvent = None
        self.GIS.InvalidateWholeMap()

    def chkAfterPaintRendererEvent_change(self, _sender):
        if self.chkAfterPaintRendererEvent.Checked:
            self.GIS.AfterPaintRendererEvent = self.GIS_AfterPaintRendererEvent
        else:
            self.GIS.AfterPaintRendererEvent = None
        self.GIS.InvalidateWholeMap()

    def GIS_BeforePaintRendererEvent(self, _sender, rdr: pdk.TGIS_RendererAbstract, _mode):
        rdr.CanvasBrush.Color = pdk.TGIS_Color.FromRGB(0xEE, 0xE8, 0xAA)
        rdr.CanvasPen.Style = pdk.TGIS_PenStyle().Clear
        rdr.CanvasDrawRectangle(pdk.TRect(10, 10, self.GIS.Width - 2 * 10, self.GIS.Height - 2 * 10))

    def GIS_PaintExtraEvent(self, _sender, rdr, _mode):
        txt = "PaintExtra"
        rdr.CanvasFont.Name = "Courier New"
        rdr.CanvasFont.Size = 24
        rdr.CanvasFont.Color = pdk.TGIS_Color().Blue
        pt = rdr.CanvasTextExtent(txt)
        ptc = self.GIS.MapToScreen(self.center_ptg)
        rdr.CanvasDrawText(pdk.TRect(int(ptc.X - pt.X / 2),
                                     int(ptc.Y - pt.Y / 2),
                                     int(ptc.X + pt.X),
                                     int(ptc.Y + pt.Y / 2)), txt)

    def GIS_AfterPaintRendererEvent(self, _sender, rdr: pdk.TGIS_RendererAbstract, _mode):
        rdr.CanvasPen.Width = 1
        rdr.CanvasBrush.Style = pdk.TGIS_BrushStyle().Clear
        rdr.CanvasDrawRectangle(pdk.TRect(100, 100, self.GIS.Width - 2 * 80, self.GIS.Height - 2 * 80))

    def btnTestPrintBmp_click(self, _sender):
        pdk.TGIS_PvlMessages.ShowInfo("This method is not implemented yet", self.Context)
        '''
        dlg_open = pdk.TGIS_PvlOpenDialog(self.Context)
        dlg_open.Filter = "Window Bitmap (*.bmp)|*.BMP"
        # dlg_open.DefaultExt = "BMP"

        if not dlg_open.Execute():
            return
        bitmap = pdk.VarParameter()
        self.GIS.PrintBmp(bitmap, self.chkPrintBmpWithEvents.Checked)
        bitmap.Value.SaveToFile(dlg_open.FileName)
        '''

def main():
    frm = PaintEventsForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
