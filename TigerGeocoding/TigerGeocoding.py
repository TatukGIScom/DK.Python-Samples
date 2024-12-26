import tatukgis_pdk as pdk
from HelpForm import HelpForm
from MatchesForm import MatchesForm

class TigerGeocodingForm(pdk.TGIS_PvlForm):
    layerSrc = None
    layerResult = None

    infoFields = None
    fieldNames = None
    selectedRow = None
    state = None
    doAbort = None
    fShown = None
    geoObj = None

    matches_form = None

    def __init__(self, _owner):
        self.help_form = None

        self.Caption = "TigerGeocoding - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.btnOpenDefault = pdk.TGIS_PvlButton(self.Context)
        self.btnOpenDefault.Place(84, 22, None, 3, None, 3)
        self.btnOpenDefault.Caption = "Open Default"
        self.btnOpenDefault.OnClick = self.btnOpenDefault_click

        self.btnOpen = pdk.TGIS_PvlButton(self.Context)
        self.btnOpen.Place(80, 22, None, 87, None, 3)
        self.btnOpen.Caption = "Open"
        self.btnOpen.OnClick = self.btnOpen_click

        self.gbxFind = pdk.TGIS_PvlGroupBox(self.Context)
        self.gbxFind.Place(241, 129, None, 351, None, 29)
        self.gbxFind.Caption = "Find Address(es):"
        self.gbxFind.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.edtAddress = pdk.TGIS_PvlEdit(self.gbxFind.Context)
        self.edtAddress.Place(205, 20, None, 20, None, 30)

        self.chkExtended = pdk.TGIS_PvlCheckBox(self.gbxFind.Context)
        self.chkExtended.Place(154, 17, None, 22, None, 58)
        self.chkExtended.Caption = "Exact street- a. city names"

        self.btnHelp = pdk.TGIS_PvlButton(self.gbxFind.Context)
        self.btnHelp.Place(41, 23, None, 184, None, 58)
        self.btnHelp.Caption = "Help"
        self.btnHelp.OnClick = self.btnHelp_click

        self.btnFindFirst = pdk.TGIS_PvlButton(self.gbxFind.Context)
        self.btnFindFirst.Place(63, 23, None, 19, None, 89)
        self.btnFindFirst.Caption = "Find First"
        self.btnFindFirst.OnClick = self.btnFindFirst_click

        self.btnFindAll = pdk.TGIS_PvlButton(self.gbxFind.Context)
        self.btnFindAll.Place(63, 23, None, 88, None, 89)
        self.btnFindAll.Caption = "Find All"
        self.btnFindAll.OnClick = self.btnFindAll_click

        self.btnMatches = pdk.TGIS_PvlButton(self.gbxFind.Context)
        self.btnMatches.Place(57, 23, None, 169, None, 89)
        self.btnMatches.Caption = "Matches"
        self.btnMatches.OnClick = self.btnMatches_click

        self.lstMemo = pdk.TGIS_PvlMemo(self.gbxFind.Context)
        self.lstMemo.Place(241, 308, None, 0, None, 129)
        self.lstMemo.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.lstMemo.OnClick = self.lstMemo_click

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 29
        self.GIS.Width = 351
        self.GIS.Height = 437
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom

        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Place(145, 25, None, 10, None, 37)

        self.progressBar1 = pdk.TGIS_PvlLabel(self.Context)
        self.progressBar1.Place(97, 23, None, 177, None, 2)

        self.open_dialog = pdk.TGIS_PvlOpenDialog(self.Context)
        self.open_dialog.Filter = "SHP files (*.SHP)|*.SHP"

    def form_show(self, _sender):
        self.infoFields = []
        self.infoFields.append("HOUSENUMBER")
        self.infoFields.append("DIRPREFIX")
        self.infoFields.append("STREETNAME")
        self.infoFields.append("DIRSUFFIX")
        self.infoFields.append("STREETTYPE")
        self.fieldNames = []
        self.fieldNames.append("FULLNAME")
        self.fieldNames.append("LFROMADD")
        self.fieldNames.append("LTOADD")
        self.fieldNames.append("RFROMADD")
        self.fieldNames.append("RTOADD")
        self.fieldNames.append("ZIPL")
        self.fieldNames.append("ZIPR")

        self.selectedRow = -1
        self.state = -1

    def busy(self, _sender, pos, end, _abort):
        # show progress
        if pos == 0:
            self.progressBar1.Max = 100
            self.progressBar1.Value = 0
            self.doAbort = False
        elif pos == -1:
            self.progressBar1.Max = 100
            self.progressBar1.Value = 100
        else:
            self.progressBar1.Max = float(end)
            self.progressBar1.Value = float(pos)

        self.GIS.ProcessMessages()

    def open_coverage(self, path):
        # free what it wants to
        if self.layerResult is not None:
            self.GIS.Delete(self.layerResult.Name)
            self.self.layerResult = None

        if self.geoObj is not None:
            self.geoObj.Dispose()
            self.geoObj = None

        if self.layerSrc is not None:
            self.GIS.Close()

        self.btnFindFirst.Enabled = False
        self.btnFindAll.Enabled = False
        self.btnHelp.Enabled = False
        self.btnMatches.Enabled = False

        self.progressBar1.Visible = True
        self.GIS.BusyEvent = self.busy
        self.GIS.Lock()
        self.GIS.Open(path)
        self.GIS.BusyEvent = None
        self.progressBar1.Visible = False

        self.layerSrc = self.GIS.Items[0]
        if self.layerSrc is None:
            return
        
        self.layerSrc.Params.Line.SmartSize = -1
        self.layerSrc.Params.Labels.Field = "FULLNAME"
        self.layerSrc.Params.Labels.Alignment = pdk.TGIS_LabelAlignment().Follow
        self.layerSrc.Params.Labels.Color = pdk.TGIS_Color().Black

        self.layerSrc.ParamsList.Add()
        self.layerSrc.Params.Query = "MTFCC < 'S1400'"
        self.layerSrc.Params.Line.Width = -2
        self.layerSrc.Params.Line.Style = pdk.TGIS_PenStyle().Solid
        self.layerSrc.UseConfig = False
        self.layerSrc.CS = self.GIS.CS

        # create route layer
        self.layerResult = pdk.TGIS_LayerVector()
        self.layerResult.UseConfig = False
        self.layerResult.Params.Line.Color = pdk.TGIS_Color().Red
        self.layerResult.Params.Line.Width = -2
        self.layerResult.Params.Marker.OutlineWidth = 1
        self.layerResult.Name = "RouteDisplay"
        self.layerResult.CS = self.GIS.CS
        self.GIS.Add(self.layerResult)

        # create geocoding object, set fields for routing
        self.geoObj = pdk.TGIS_Geocoding(self.layerSrc)
        self.geoObj.Offset = 0.0001
        self.geoObj.LoadFormulas(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Samples/Geocoding/us_addresses.geo",
                                 pdk.TGIS_Utils.GisSamplesDataDirDownload() + "/Samples/Geocoding/tiger2008.geo")

        self.GIS.Unlock()
        self.GIS.FullExtent()

        self.GIS_ControlScale.Visible = True

        self.btnFindFirst.Enabled = True
        self.btnFindAll.Enabled = True
        self.btnHelp.Enabled = True

        # focus on edit window
        self.edtAddress.Text = ""
        self.edtAddress.SetFocus()

        self.lstMemo.Clear()
        self.state = -1
        self.selectedRow = -1

    def btnOpen_click(self, _sender):
        self.open_dialog.Execute()
        self.GIS.Open(self.open_dialog.FileName)

    def btnOpenDefault_click(self, _sender):
        self.open_coverage(
            pdk.TGIS_Utils.GisSamplesDataDirDownload() +
            "World/Countries/USA/States/California/San Bernardino/TIGER/tl_2008_06071_edges_trunc.SHP")

    def btnHelp_click(self, _sender):
        self.help_form = HelpForm(None)
        self.help_form.Show()

    def btnMatches_click(self, _sender):
        self.matches_form.Show()

    def btnFindFirst_click(self, _sender):
        self.find_address(True, not self.chkExtended.Checked)

    def btnFindAll_click(self, _sender):
        self.find_address(False, not self.chkExtended.Checked)

    def find_address(self, find_first, extended_scope):
        if self.geoObj is None:
            pdk.TGIS_PvlMessages.ShowInfo("Open a TIGER/Line file.", self.Context)
            return

        self.layerResult.RevertAll()
        self.lstMemo.Clear()
        self.state = -1
        self.selectedRow = -1
        self.btnMatches.Enabled = False

        # locate shapes meeting query
        try:
            r = self.parse(find_first, extended_scope) - 1

        except pdk.EGIS_Exception as e:
            pdk.TGIS_PvlMessages.ShowInfo(f"EGIS_Exception: {e}", self.Context)
            r = -1

        except BaseException as e:
            pdk.TGIS_PvlMessages.ShowInfo(f"Exception: {type(e).__name__} {e}", self.Context)
            r = -1

        if r < 0:
            self.edtAddress.Text = self.edtAddress.Text + " ???"
        else:
            self.edtAddress.Text = self.geoObj.Query(0)
            if find_first:
                self.state = 0
            else:
                self.state = 1

        for i in range(r+1):
            # add found shape to route layer (red color)
            shp = self.layerSrc.GetShape(self.geoObj.Uid(i))
            self.layerResult.AddShape(shp)

            if i == 0:
                self.layerResult.Extent = shp.Extent

            if find_first:
                if i == 0:
                    for j in range(len(self.fieldNames)):
                        s = str(shp.GetField(str(self.fieldNames[j])))
                        self.lstMemo.AppendLine(self.fieldNames[j] + "=" + s)
            else:
                self.lstMemo.AppendLine(self.geoObj.Query(i))

            shp = self.layerSrc.GetShape(self.geoObj.UidEx(i))
            if shp is not None:
                self.layerResult.AddShape(shp)
                if find_first:
                    if i == 0:
                        self.lstMemo.AppendLine("---------------------------")
                        for j in range(len(self.fieldNames)):
                            s = str(shp.GetField(str(self.fieldNames[j])))
                            self.lstMemo.AppendLine(self.fieldNames[j] + "=" + s)

            # mark address as green square
            shp = self.layerResult.CreateShape(pdk.TGIS_ShapeType().Point)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            shp.AddPoint(self.geoObj.Point(i))
            shp.Params.Marker.Color = pdk.TGIS_Color().Yellow
            shp.Unlock()

        # self.lstMemo.EndUpdate()

        self.GIS.Lock()
        self.GIS.VisibleExtent = self.layerResult.Extent
        self.GIS.Zoom = 0.7 * self.GIS.Zoom
        self.GIS.Unlock()

    def parse(self, find_first, extended_scope):
        ref_resolved_addresses = pdk.VarParameter()
        ref_resolved_addresses.Value = None
        ref_resolved_addresses2 = pdk.VarParameter()
        ref_resolved_addresses2.Value = None
        res = 0
        try:
            if self.geoObj.Match(self.edtAddress.Text, ref_resolved_addresses, ref_resolved_addresses2):

                self.matches_form = MatchesForm(None)
                self.matches_form.ShowMatches(ref_resolved_addresses.Value, ref_resolved_addresses2.Value)

                res = self.geoObj.ParseEx(ref_resolved_addresses.Value,
                                          ref_resolved_addresses2.Value,
                                          find_first,
                                          extended_scope,
                                          True)

                self.btnMatches.Enabled = True
        finally:
            pass

        return res

    def show_info(self):
        if self.layerSrc is None:
            return
        if self.selectedRow == -1:
            return

        # get current shape
        shp = self.layerSrc.GetShape(self.geoObj.Uid(self.selectedRow))
        self.GIS.VisibleExtent = shp.Extent

        self.GIS.Zoom = 0.7 * self.GIS.Zoom

    def lstMemo_click(self, _sender):
        # check if the cell can be selected
        can_select = (self.lstMemo.CursorPos.Y < self.lstMemo.Lines.Count) and not \
            ((self.lstMemo.Lines.Count == 1) and (self.lstMemo.Lines[self.lstMemo.CaretPosition.Line] == ""))
        if can_select and self.state == 1:
            self.selectedRow = self.lstMemo.CursorPos.Y   #self.lstMemo.CaretPosition.Line
            self.show_info()


def main():
    frm = TigerGeocodingForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
