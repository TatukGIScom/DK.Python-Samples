import tatukgis_pdk as pdk
import os

class TemplatePrintForm(pdk.TGIS_PvlForm):
    manager: pdk.TGIS_PrintManager
    template: pdk.TGIS_TemplatePrint

    def __init__(self, _owner):
        self.Caption = "Pipeline - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(935, 30, None, 0, None, 0)
        self.toolbar_buttons.Align = "Top"

        self.btnFullExtent = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnFullExtent.Place(40, 25, None, 0, None, 3)
        self.btnFullExtent.Caption = "Full"
        self.btnFullExtent.OnClick = self.btnFullExtent_click

        self.btnZoom = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnZoom.Place(40, 25, None, 41, None, 3)
        self.btnZoom.Caption = "Zoom"
        self.btnZoom.OnClick = self.btnZoom_click

        self.btnDrag = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.btnDrag.Place(40, 25, None, 82, None, 3)
        self.btnDrag.Caption = "Drag"
        self.btnDrag.OnClick = self.btnDrag_click

        self.button1 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button1.Place(75, 25, None, 145, None, 2)
        self.button1.Caption = "Print"
        self.button1.OnClick = self.button1_click

        self.button2 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button2.Place(75, 25, None, 222, None, 2)
        self.button2.Caption = "Design"
        self.button2.OnClick = self.button2_click
        self.button2.Enabled = False

        self.button3 = pdk.TGIS_PvlButton(self.toolbar_buttons.Context)
        self.button3.Place(75, 25, None, 300, None, 2)
        self.button3.Caption = "Change"
        self.button3.OnClick = self.button3_click

        self.status_bar = pdk.TGIS_PvlPanel(self.Context)
        self.status_bar.Place(592, 23, None, 0, None, 447)
        self.status_bar.Align = "Bottom"

        self.scale_label = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.scale_label.Place(100, 19, None, 10, None, 0)

        self.file_label = pdk.TGIS_PvlLabel(self.status_bar.Context)
        self.file_label.Place(200, 19, None, 230, None, 0)

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        # self.GIS.Left = 229
        # self.GIS.Top = 115
        # self.GIS.Width = 718
        # self.GIS.Height = 486
        self.GIS.VisibleExtentChangeEvent = self.GIS_AfterPaint
        self.GIS.Align = "Client"

        self.GIS_ControlLegend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_ControlLegend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_ControlLegend.GIS_Viewer = self.GIS
        self.GIS_ControlLegend.Place(111, 486, None, 12, None, 115)
        self.GIS_ControlLegend.Align = "Left"

        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Place(129, 25, None, 412, None, 389)
        self.GIS_ControlScale.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_ControlNorthArrow = pdk.TGIS_PvlControlNorthArrow(self.Context)
        self.GIS_ControlNorthArrow.GIS_Viewer = self.GIS
        self.GIS_ControlNorthArrow.Place(60, 60, None, 481, None, 34)
        self.GIS_ControlNorthArrow.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right)

        # self.splitter1 = pdk.TGIS_PvlSplitter(self.Context)
        # self.splitter1.Place(3, 419, None, 145, None, 28)

        self.GIS_ControlPrintPreviewSimple = pdk.TGIS_ControlPrintPreviewSimple(None)
        self.GIS_ControlPrintPreviewSimple.GIS_Viewer = self.GIS

        self.dlg = pdk.TGIS_PvlOpenDialog(self.Context)
        self.dlg.Filter = "Print template|*.tpl;*.ttktemplate"

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "World/Countries/Poland/DCW/poland.ttkproject")

        # copy self.template file to the current directory as .ttktemplate
        src_path = (pdk.TGIS_Utils.GisSamplesDataDirDownload()
                    + "Samples/PrintTemplate/printtemplate.tpl")
        tpl_path = os.getcwd() + "//printtemplate.ttktemplate"
        pdk.TGIS_TemplatePrintBuilder.CopyTemplateFile(src_path, tpl_path, False)

        # prepare self.template for printing
        self.template = pdk. TGIS_TemplatePrint()
        self.template.TemplatePath = tpl_path
        self.template.GIS_Viewer(1, self.GIS)
        self.template.GIS_Legend(1, self.GIS_ControlLegend)
        self.template.GIS_Scale(1, self.GIS_ControlScale)
        # self.template.GIS_NorthArrow(1, self.GIS_ControlNorthArrow)
        self.template.GIS_ViewerExtent(1, self.GIS.Extent)
        self.template.Text(1, "Title")
        self.template.Text(2, "Copyright")

        # prepare print manager
        self.manager = pdk.TGIS_PrintManager()
        self.manager.Template = self.template

        self.file_label.Caption = "printtemplate.ttktemplate"

    def btnZoom_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

    def btnDrag_click(self, _sender):
        if self.GIS.IsEmpty:
            return
        self.GIS.Mode = pdk.TGIS_ViewerMode().Drag

    def btnFullExtent_click(self, _sender):
        self.GIS.FullExtent()

    def button1_click(self, _sender):
        # cr = self.GIS.Cursor
        # self.GIS.Cursor = -11   # Cursors.WaitCursor
        try:
            self.GIS_ControlPrintPreviewSimple.Preview(self.manager)
        finally: pass
            # self.GIS.Cursor = cr

    def button2_click(self, sender):
        # not implemented yet
        pass

    def button3_click(self, _sender):
        self.dlg.FileName = ""
        self.dlg.InitialDir = os.getcwd()

        if self.dlg.Execute():
            old = self.template.TemplatePath
            try:
                self.template.TemplatePath = self.dlg.FileName
                self.file_label.Caption = os.path.basename(self.template.TemplatePath)
            except BaseException as e:
                pdk.TGIS_PvlMessages.ShowInfo(f"Exception: {type(e).__name__} {e}", self.Context)
                self.template.TemplatePath = old

    def GIS_AfterPaint(self, _sender):
        self.scale_label.Caption = f"Scale: {self.GIS.ScaleAsText}"


def main():
    frm = TemplatePrintForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
