import tatukgis_pdk as pdk
import os

class ExportToImageForm(pdk.TGIS_PvlForm):
    DEFAULT_PPI = 300
    DEFAULT_PPI_DOC = 300
    DEFAULT_PPI_WEB = 96
    DEFAULT_WIDTH_PX = 4200
    DEFAULT_WIDTH_PX_WEB = 640
    DEFAULT_WIDTH_DOC_MM = 160
    DEFAULT_WIDTH_DOC_CM = 16
    DEFAULT_WIDTH_DOC_INCH = 6.3

    UNITS_MM = 0
    UNITS_CM = 1
    UNITS_INCH = 2

    capabilities_list = []
    lp_out: pdk.TGIS_LayerPixel
    extent: pdk.TGIS_Extent
    ppi: int
    expWidth: float
    expHeight: float
    pixWidth: float
    pixHeight: float

    def __init__(self, _owner):
        self.Caption = "ExportToImage - TatukGIS DK Sample"
        self.ClientWidth = 560
        self.ClientHeight = 508
        self.OnShow = self.form_show

        self.groupBox1 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox1.Place(517, 231, None, 25, None, 22)
        self.groupBox1.Caption = "Viewer"

        self.rbImage = pdk.TGIS_PvlRadioButton(self.groupBox1.Context)
        self.rbImage.Place(54, 17, None, 438, None, 35)
        self.rbImage.Caption = "Image"
        self.rbImage.Checked = True
        self.rbImage.OnClick = self.rbImage_CheckedChanged

        self.rbGrid = pdk.TGIS_PvlRadioButton(self.groupBox1.Context)
        self.rbGrid.Place(44, 17, None, 438, None, 59)
        self.rbGrid.Caption = "Grid"
        self.rbGrid.OnClick = self.rbGrid_CheckedChanged

        self.GIS = pdk.TGIS_PvlViewerWnd(self.Context)
        self.GIS.Left = 31
        self.GIS.Top = 41
        self.GIS.Width = 426
        self.GIS.Height = 198

        self.groupBox2 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox2.Place(517, 55, None, 25, None, 277)
        self.groupBox2.Caption = "File"

        self.edtPath = pdk.TGIS_PvlEdit(self.groupBox2.Context)
        self.edtPath.Place(426, 20, None, 6, None, 20)
        self.edtPath.Enabled = False

        self.btnSelectFile = pdk.TGIS_PvlButton(self.groupBox2.Context)
        self.btnSelectFile.Place(35, 23, None, 438, None, 18)
        self.btnSelectFile.Caption = "..."
        self.btnSelectFile.OnClick = self.btnSelectFile_click

        self.rdbgrp1 = 'radiobuttongroupoptions'

        self.groupBox3 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox3.Place(517, 123, None, 25, None, 349)
        self.groupBox3.Caption = "Options"
        self.groupBox3.Enabled = False

        self.lbFormat = pdk.TGIS_PvlLabel(self.groupBox3.Context)
        self.lbFormat.Place(39, 13, None, 21, None, 22)
        self.lbFormat.Caption = "Format"

        self.cbFormat = pdk.TGIS_PvlComboBox(self.groupBox3.Context)
        self.cbFormat.Place(121, 21, None, 61, None, 18)

        self.lbExtent = pdk.TGIS_PvlLabel(self.groupBox3.Context)
        self.lbExtent.Place(37, 13, None, 20, None, 51)
        self.lbExtent.Caption = "Extent"

        self.rbExtentFull = pdk.TGIS_PvlRadioButton(self.groupBox3.Context)
        self.rbExtentFull.Place(41, 17, None, 61, None, 51)
        self.rbExtentFull.Caption = "Full"
        self.rbExtentFull.Group = self.rdbgrp1

        self.rbExtentVisible = pdk.TGIS_PvlRadioButton(self.groupBox3.Context)
        self.rbExtentVisible.Place(55, 17, None, 61, None, 74)
        self.rbExtentVisible.Caption = "Visible"
        self.rbExtentVisible.Group = self.rdbgrp1

        self.rdbgrp2 = 'radiobuttongroupresolution'

        self.groupBox4 = pdk.TGIS_PvlGroupBox(self.groupBox3.Context)
        self.groupBox4.Place(260, 109, None, 251, None, 8)
        self.groupBox4.Caption = "Resolution"

        self.rbBestQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbBestQ.Place(79, 17, None, 7, None, 37)
        self.rbBestQ.Caption = "Best quality"
        self.rbBestQ.Group = self.rdbgrp2

        self.rbDocQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbDocQ.Place(90, 17, None, 7, None, 60)
        self.rbDocQ.Caption = "For document"
        self.rbDocQ.Group = self.rdbgrp2

        self.rbWebQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbWebQ.Place(66, 17, None, 7, None, 83)
        self.rbWebQ.Caption = "For Web"
        self.rbWebQ.Group = self.rdbgrp2

        self.btnExport = pdk.TGIS_PvlButton(self.Context)
        self.btnExport.Place(75, 23, None, 237, None, 478)
        self.btnExport.Caption = "Export"
        self.btnExport.Enabled = False
        self.btnExport.OnClick = self.btnExport_click

    def form_show(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/VisibleEarth/world_8km.jpg")
        self.rbBestQ.Checked = True
        self.rbExtentFull.Checked = True

    def rbImage_CheckedChanged(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/VisibleEarth/world_8km.jpg")
        self.edtPath.Text = ""
        self.cbFormat.ItemsClear()
        self.groupBox3.Enabled = False
        self.btnExport.Enabled = False

    def rbGrid_CheckedChanged(self, _sender):
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/Countries/USA/States/California/San Bernardino/NED/hdr.adf")
        self.edtPath.Text = ""
        self.cbFormat.ItemsClear()
        self.groupBox3.Enabled = False
        self.btnExport.Enabled = False

    def btnSelectFile_click(self, _sender):
        save_dlg = pdk.TGIS_PvlSaveDialog(self)

        if self.rbImage.Checked:
            ext = ".jpg"
            save_dlg.Filter = ("JPEG File Interchange Format (*.jpg)|*.jpg|Portable Network Graphic (*.png)|*.png|"
                               + "Tag Image File Format (*.tif)|*.tif|Window Bitmap (*.bmp)|*.bmp|"
                               + "TatukGIS PixelStore (*.ttkps)|*.ttkps")
        elif self.rbGrid.Checked:
            ext = ".flt"
            save_dlg.Filter = ("Arc/Info Binary Grid (*.flt)|*.flt|Arc/Info ASCII Grid (*.grd)|"
                               + "*.grd|TatukGIS PixelStore (*.ttkps)|*.ttkps")

        if save_dlg.Execute() == "Cancel":
            return

        self.edtPath.Text = save_dlg.FileName + ext

        self.cbFormat.ItemsClear()
        self.capabilities_list.clear()

        try:
            if self.rbImage.Checked:
                self.lp_out = pdk.TGIS_Utils.GisCreateLayer(os.getcwd() + self.edtPath.Text, save_dlg.FileName + ext)
            else:
                self.lp_out = pdk.TGIS_Utils.GisCreateLayer(os.getcwd() + self.edtPath.Text, save_dlg.FileName + ext)

            for capability in self.lp_out.Capabilities:
                self.cbFormat.ItemsAdd(capability.ToString())
                self.capabilities_list.append(capability)

            self.cbFormat.ItemIndex = 0

            self.groupBox3.Enabled = True
            self.btnExport.Enabled = True
        except Exception as e:
            pdk.TGIS_PvlMessages.ShowInfo(str(e), self.Context)
            
    def btnExport_click(self, _sender):
        if self.cbFormat.ItemIndex >= 0:
            capability = self.capabilities_list[self.cbFormat.ItemIndex].CreateCopy()
        else:
            capability = self.lp_out.DefaultSubFormat

        if self.rbExtentFull.Checked:
            self.extent = self.GIS.Extent
        elif self.rbExtentVisible.Checked:
            self.extent = self.GIS.VisibleExtent

        if self.rbBestQ.Checked:
            self.CalcInit()
        elif self.rbDocQ.Checked:
            self.ppi = self.DEFAULT_PPI_DOC
            self.expWidth = self.DEFAULT_WIDTH_DOC_INCH
            if (self.extent.XMax - self.extent.XMin) != 0:
                self.expHeight = ((self.extent.YMax - self.extent.YMin)
                                  / (self.extent.XMax - self.extent.XMin)
                                  * self.expWidth)
            else:
                self.expWidth = 2
                self.expHeight = 2

            self.CalcWHPixels()
        
        elif self.rbWebQ.Checked:
            self.ppi = self.DEFAULT_PPI_WEB
            self.pixWidth = self.DEFAULT_WIDTH_PX_WEB

            if (self.extent.XMax - self.extent.XMin) != 0:
                self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                                  / (self.extent.XMax - self.extent.XMin)
                                  * self.pixWidth)
            else:
                self.pixWidth = 2
                self.pixHeight = 2

            self.CalcWHUnits()

        lyr_in = self.GIS.Items[0]

        self.lp_out.ImportLayer(lyr_in, lyr_in.Extent, lyr_in.CS, int(self.pixWidth), int(self.pixHeight), capability)

        pdk.TGIS_PvlMessages.ShowInfo("File exported", self.Context)

    def CalcInit(self):
        density0 = 0
        density = density0
        self.ppi = self.DEFAULT_PPI
        j = 0
        for i in range(self.GIS.Items.Count-1, -1, -1):
            la = self.GIS.Items[i]

            if isinstance(la, pdk.TGIS_LayerPixel):
                ext_width = la.Extent.XMax - la.Extent.XMin

                density1 = la.BitWidth / ext_width
                if density1 > density0:
                    density = density1
                    j = i
                density0 = density1

        if density == 0:
            width_px = self.DEFAULT_WIDTH_PX
        else:
            la = self.GIS.Items[j]
            ext_width = la.Extent.XMax - la.Extent.XMin
            ext_delta = (self.extent.XMax - self.extent.XMin) / ext_width

            width_px = int(round(ext_delta * self.GIS.Items[j].BitWidth))

        self.pixWidth = width_px

        if (self.extent.XMax - self.extent.XMin) != 0:
            self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.pixWidth)
        else:
            self.pixWidth = 2
            self.pixHeight = 2

    def CalcWHUnits(self):
        self.expWidth = self.pixWidth / self.ppi

        if (self.extent.XMax - self.extent.XMin) != 0:
            self.expHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.expWidth)
        else:
            self.expWidth = 2
            self.expHeight = 2

    def CalcWHPixels(self):
        self.pixWidth = self.expWidth * self.ppi

        if (self.extent.XMax - self.extent.XMin) != 0:
            self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.pixWidth)
        else:
            self.pixWidth = 2
            self.pixHeight = 2
            

def main():
    frm = ExportToImageForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
