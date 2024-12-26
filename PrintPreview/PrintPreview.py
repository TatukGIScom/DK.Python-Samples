import tatukgis_pdk as pdk

class PrintPreviewForm(pdk.TGIS_PvlForm):
    printManager = None

    def __init__(self, _owner):
        self.Caption = "PrintPreview - TatukGIS DK Sample"
        self.ClientWidth = 925
        self.ClientHeight = 728
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(925, 45, None, 0, None, 0)
        self.toolbar_buttons.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                                        pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(301, 39, None, 301, None, 2)
        self.button1.Caption = "TGIS_ControlPrintPreview"
        self.button1.OnClick = self.button1_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(301, 39, None, 0, None, 2)
        self.button2.Caption = "TGIS_ControlPrintPreviewSimple"
        self.button2.OnClick = self.button2_click

        self.lbPrintTitle = pdk.TGIS_PvlLabel(self.Context)
        self.lbPrintTitle.Place(80, 20, None, 649, None, 62)
        self.lbPrintTitle.Caption = "Print title:"

        self.btTitleFont = pdk.TGIS_PvlButton(self.Context)
        self.btTitleFont.Place(105, 32, None, 650, None, 125)
        self.btTitleFont.Caption = "Font"
        self.btTitleFont.OnClick = self.btFont_click
        self.btTitleFont.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.edPrintTitle = pdk.TGIS_PvlEdit(self.Context)
        self.edPrintTitle.Place(262, 22, None, 650, None, 88)
        self.edPrintTitle.Text = "Title"
        self.edPrintTitle.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.lbPrintSubtitle = pdk.TGIS_PvlLabel(self.Context)
        self.lbPrintSubtitle.Place(110, 20, None, 650, None, 175)
        self.lbPrintSubtitle.Caption = "Print subtitle:"
        
        self.btSubTitleFont = pdk.TGIS_PvlButton(self.Context)
        self.btSubTitleFont.Place(105, 32, None, 650, None, 250)
        self.btSubTitleFont.Caption = "Font"
        self.btSubTitleFont.OnClick = self.btSubFont_click
        self.btSubTitleFont.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.edPrintSubTitle = pdk.TGIS_PvlEdit(self.Context)
        self.edPrintSubTitle.Place(262, 22, None, 650, None, 200)
        self.edPrintSubTitle.Text = "Subtitle"
        self.edPrintSubTitle.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.chkStandardPrint = pdk.TGIS_PvlCheckBox(self.Context)
        self.chkStandardPrint.Place(164, 26, None, 650, None, 300)
        self.chkStandardPrint.Caption = "Standard print:"
        self.chkStandardPrint.OnClick = self.chkStandardPrint_change
        self.chkStandardPrint.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 300
        self.GIS.Top = 62
        self.GIS.Width = 339
        self.GIS.Height = 264
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top)

        self.GIS_ControlLegend1 = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_ControlLegend1.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_ControlLegend1.GIS_Viewer = self.GIS
        self.GIS_ControlLegend1.Place(274, 262, None, 12, None, 62)

        self.GIS_ControlPrintPreview1 = pdk.TGIS_PvlControlPrintPreview(self.Context)
        self.GIS_ControlPrintPreview1.Place(889, 364, None, 12, None, 338)
        self.GIS_ControlPrintPreview1.GIS_Viewer = self.GIS
        self.GIS_ControlPrintPreview1.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                                                 pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)




    @staticmethod
    def inch(value, ppi):
        return round(value * ppi)

    def GIS_PrintPage(self, _sender, pm, last_page):
        pr = pm.Printer
        if pr is None:
            return

        rnd = pr.Renderer
        r = pdk.TGIS_PvlPanel()

        # left panel
        r.Left = self.inch(0.2, rnd.ppi)
        r.Top = self.inch(0.5, rnd.ppi)
        r.Right = pr.PrintArea.Width
        r.Bottom = pr.PrintArea.Height

        # left panel: gray rectangle
        r.Right = r.Right - pr.TwipsToX(2 * 1440) - self.inch(0.2, rnd.ppi)
        rnd.CanvasBrush.Color = pdk.TGIS_Color().Gray
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Solid
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Clear
        rnd.CanvasDrawRectangle(r)

        # left panel: white rectangle
        r.Left = r.Left - self.inch(0.1, rnd.ppi)
        r.Top = r.Top - self.inch(0.1, rnd.ppi)
        r.Right = r.Right - self.inch(0.1, rnd.ppi)
        r.Bottom = r.Bottom - self.inch(0.1, rnd.ppi)
        rnd.CanvasBrush.Color = pdk.TGIS_Color().White
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Solid
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Clear
        rnd.CanvasDrawRectangle(r)
        fr = pdk.TRect(r.Left, r.Top, r.Right, r.Bottom)

        # left panel: map
        r.Left = r.Left + self.inch(0.1, rnd.ppi)
        r.Top = r.Top + self.inch(0.1, rnd.ppi)
        r.Right = r.Right - self.inch(0.1, rnd.ppi)
        r.Bottom = r.Bottom - self.inch(0.1, rnd.ppi)

        # 'scale' returned by the function is the real map scale used during printing.
        # It should be passed to the following DrawControl methods.
        # If legend or scale controls have to be printed before map (for some reason)
        # use the following frame:
        #    scale = 0
        #    pm.GetDrawingParams( GIS, GIS.Extent, r, scale )  ...
        #    pm.DrawControl( GIS_ControlLegend1, r1, scale )   ...
        #    pm.DrawMap( GIS, GIS.Extent, r, scale )
        scale = pdk.VarParameter()
        scale.Value = 0.0
        pm.DrawMap(self.GIS, self.GIS.Extent, r, scale)
        mr = pdk.TRect(r.Left, r.Top, r.Right, r.Bottom)

        # left panel: black frame
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Clear
        rnd.CanvasPen.Color = pdk.TGIS_Color().Black
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rnd.CanvasDrawRectangle(fr)

        # right panel
        r.Left = 0
        r.Top = self.inch(0.5, rnd.ppi)
        r.Right = pr.PrintArea.Width
        r.Bottom = pr.PrintArea.Height

        # right panel: gray rectangle
        r.Left = r.Right - pr.TwipsToX(2 * 1440)
        rnd.CanvasBrush.Color = pdk.TGIS_Color().Gray
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Solid
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Clear
        rnd.CanvasDrawRectangle(r)

        # right panel: white rectangle
        r.Left = r.Left - self.inch(0.1, rnd.ppi)
        r.Top = r.Top - self.inch(0.1, rnd.ppi)
        r.Right = r.Right - self.inch(0.1, rnd.ppi)
        r.Bottom = r.Bottom - self.inch(0.1, rnd.ppi)
        rnd.CanvasBrush.Color = pdk.TGIS_Color().White
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Solid
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Clear
        rnd.CanvasDrawRectangle(r)
        fr = pdk.TRect(r.Left, r.Top, r.Right, r.Bottom)

        # right panel: legend
        r.Left = r.Left + self.inch(0.1, rnd.ppi)
        r.Top = r.Top + self.inch(0.1, rnd.ppi)
        r.Right = r.Right - self.inch(0.1, rnd.ppi)
        r.Bottom = r.Bottom - self.inch(0.1, rnd.ppi)
        pm.DrawControl(self.GIS_ControlLegend1, r, scale.Value)

        # right panel: black frame
        rnd.CanvasBrush.Style = pdk.TGIS_BrushStyle().Clear
        rnd.CanvasPen.Color = pdk.TGIS_Color().Black
        rnd.CanvasPen.Style = pdk.TGIS_PenStyle().Solid
        rnd.CanvasDrawRectangle(fr)

        r = mr
        # page number
        rnd.CanvasBrush.Color = pdk.TGIS_Color().White
        rnd.CanvasFont.Name = 'Arial'
        rnd.CanvasFont.Size = 12
        rnd.CanvasFont.Color = pdk.TGIS_Color().Black
        txt = f"'Page {pr.PageNumber}"
        h = rnd.CanvasTextExtent(txt).Y
        w = rnd.CanvasTextExtent(txt).X
        x = r.Left
        rnd.CanvasDrawText(pdk.TRect(x, r.Bottom - h, x + w, r.Bottom), f"Page {pr.PageNumber}")

        # title
        rnd.CanvasFont.Name = pm.TitleFont.Name
        rnd.CanvasFont.Size = pm.TitleFont.Size
        rnd.CanvasFont.Style = pm.TitleFont.Style
        rnd.CanvasFont.Color = pm.TitleFont.Color
        h = rnd.CanvasTextExtent(pm.Title).Y
        w = rnd.CanvasTextExtent(pm.Title).X
        x = int((r.Left + r.Right - w)/2)
        rnd.CanvasDrawText(pdk.TRect(x, pr.TwipsToY(720), x + w, pr.TwipsToY(720) + h), pm.Title)
        h_margin = h

        # subtitle
        rnd.CanvasFont.Name = pm.SubtitleFont.Name
        rnd.CanvasFont.Size = pm.SubtitleFont.Size
        rnd.CanvasFont.Style = pm.SubtitleFont.Style
        rnd.CanvasFont.Color = pm.SubtitleFont.Color
        h = rnd.CanvasTextExtent(pm.SubTitle).Y
        w = rnd.CanvasTextExtent(pm.SubTitle).X
        x = int((r.Left + r.Right - w)/2)
        rnd.CanvasDrawText(
            pdk.TRect(x, pr.TwipsToY(720) + h_margin, x + w, pr.TwipsToY(720) + h_margin + h),
            pm.SubTitle
        )
        last_page.Value = True

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDir() + "/World/Countries/Poland/DCW/poland.ttkproject")

        self.printManager = pdk.TGIS_PrintManager()
        self.printManager.Title = self.edPrintTitle.Text
        self.printManager.Subtitle = self.edPrintSubTitle.Text
        self.printManager.Footer = "Footer"

        self.printManager.TitleFont.Name = "Arial"
        self.printManager.TitleFont.Size = 18
        self.printManager.TitleFont.Style = [pdk.TGIS_FontStyle.Bold]
        self.printManager.TitleFont.Color = pdk.TGIS_Color().Black

        self.printManager.SubtitleFont.Name = "Arial"
        self.printManager.SubtitleFont.Size = 14
        self.printManager.SubtitleFont.Style = [pdk.TGIS_FontStyle().Italic]
        self.printManager.SubtitleFont.Color = pdk.TGIS_Color().Black

        self.printManager.FooterFont.Name = "Arial"
        self.printManager.FooterFont.Size = 10
        self.printManager.FooterFont.Style = []
        self.printManager.FooterFont.Color = pdk.TGIS_Color().Black

        self.chkStandardPrint.Checked = True
        self.printManager.PrintPageEvent = None
        self.GIS_ControlPrintPreview1.Preview(1, None, self.printManager)

    def chkStandardPrint_change(self, _sender):
        if self.chkStandardPrint.Checked:
            self.printManager.PrintPageEvent = None
        else:
            self.printManager.Title = self.edPrintTitle.Text
            self.printManager.Subtitle = self.edPrintSubTitle.Text
            self.printManager.PrintPageEvent = self.GIS_PrintPage
        self.GIS_ControlPrintPreview1.Preview(1, None, self.printManager)

    def btFont_click(self, _sender):
        dlg_font_title = pdk.TGIS_ControlFont(self)
        dlg_font_title.Symbol.Font.Name = self.printManager.TitleFont.Name
        dlg_font_title.Symbol.Font.Style = self.printManager.TitleFont.Style
        if dlg_font_title.Execute() != pdk.TGIS_PvlModalResult().OK:
            return
        self.printManager.TitleFont.Name = dlg_font_title.Symbol.Font.Name
        self.printManager.TitleFont.Style = dlg_font_title.Symbol.Font.Style

    def btSubFont_click(self, _sender):
        dlg_font_title = pdk.TGIS_ControlFont(self)
        dlg_font_title.Symbol.Font.Name = self.printManager.TitleFont.Name
        dlg_font_title.Symbol.Font.Style = self.printManager.TitleFont.Style
        if dlg_font_title.Execute() != pdk.TGIS_PvlModalResult().OK:
            return
        self.printManager.SubTitleFont.Name = dlg_font_title.Symbol.Font.Name
        self.printManager.SubTitleFont.Style = dlg_font_title.Symbol.Font.Style

    def button1_click(self, _sender):
        self.printManager.Title = self.edPrintTitle.Text
        self.printManager.Subtitle = self.edPrintSubTitle.Text
        self.GIS_ControlPrintPreview1.Preview(1, None, self.printManager)

    def button2_click(self, _sender):
        self.printManager.Title = self.edPrintTitle.Text
        self.printManager.Subtitle = self.edPrintSubTitle.Text

        self.GIS_ControlPrintPreviewSimple1 = pdk.TGIS_PvlControlPrintPreviewSimple(self.Context)
        self.GIS_ControlPrintPreviewSimple1.GIS_Viewer = self.GIS
        self.GIS_ControlPrintPreviewSimple1.Preview(self.printManager)


def main():
    frm = PrintPreviewForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
