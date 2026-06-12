# =============================================================================
# ExportToImage sample - Python (TatukGIS PDK)
#
# Demonstrates how to export a GIS map layer to a raster image or a numeric
# elevation grid using the TatukGIS Python Developer Kernel (PDK / tatukgis_pdk).
#
# Key concepts shown:
#   - Loading raster imagery (JPEG) and DEM/elevation grids (ADF) into a
#     TGIS_ViewerWnd control hosted in a TGIS_PvlForm window.
#   - Creating a new output TGIS_LayerPixel via TGIS_Utils.GisCreateLayer,
#     which selects the appropriate driver from the file extension.
#   - Querying lp_out.Capabilities to discover the TGIS_LayerPixelSubFormat
#     options (pixel depth, compression, etc.) supported by the target format.
#   - Controlling export resolution via three strategies:
#       * Best quality  - pixel size matched to the highest-density source layer.
#       * For document  - fixed physical paper width at 300 DPI.
#       * For Web       - fixed pixel width (640 px) at 96 DPI.
#   - Controlling export spatial coverage through full or visible extent.
#   - Performing the raster conversion with TGIS_LayerPixel.ImportLayer, which
#     resamples the source layer into the target at the requested pixel size.
# =============================================================================

import tatukgis_pdk as pdk
import os


class ExportToImageForm(pdk.TGIS_PvlForm):
    """
    Main form for the ExportToImage sample.

    Inherits from TGIS_PvlForm, which is the TatukGIS Python cross-platform
    form base class (analogous to TForm in Delphi or System.Windows.Forms.Form
    in the .NET variants).  All UI controls are created programmatically in
    __init__ rather than through a visual designer.
    """

    # --- Resolution / dimension constants ---

    #: Default PPI for best-quality and document export modes.
    #: 300 DPI is the standard minimum for print-quality raster output.
    DEFAULT_PPI = 300

    #: Document print resolution in DPI.
    DEFAULT_PPI_DOC = 300

    #: Screen/web resolution in DPI. 96 PPI is the standard Windows screen DPI
    #: and produces compact images suitable for web display.
    DEFAULT_PPI_WEB = 96

    #: Fallback output width in pixels when no raster layer is present to derive
    #: a natural resolution. 4200 px at 300 DPI corresponds to a 14-inch wide image.
    DEFAULT_WIDTH_PX = 4200

    #: Default pixel width for the web export profile (640 px wide).
    DEFAULT_WIDTH_PX_WEB = 640

    #: Document page-width references used by the document preset.
    #: 160 mm / 16 cm / 6.3 inches is a typical A4 text-area width.
    DEFAULT_WIDTH_DOC_MM = 160
    DEFAULT_WIDTH_DOC_CM = 16
    DEFAULT_WIDTH_DOC_INCH = 6.3

    # Unit selector constants (reserved for potential future use)
    UNITS_MM   = 0
    UNITS_CM   = 1
    UNITS_INCH = 2

    # --- Instance field type hints ---
    capabilities_list: list   # Parallel list to cbFormat items; each entry is a
                              # TGIS_LayerPixelSubFormat deep copy
    lp_out: pdk.TGIS_LayerPixel  # Target pixel layer that writes to the output file
    extent: pdk.TGIS_Extent      # Geographic bounding box for the current export
    ppi:       int               # Pixels per inch for the current export mode
    expWidth:  float             # Physical output width in inches (document preset)
    expHeight: float             # Physical output height in inches (document preset)
    pixWidth:  float             # Output image width in pixels
    pixHeight: float             # Output image height in pixels

    def __init__(self, _owner):
        """
        Build all UI controls programmatically.

        TGIS_PvlForm does not use a separate .dfm/.resx resource; instead, every
        control is constructed and positioned here.  The Place(width, height,
        right, left, bottom, top) method sets size and position in one call.
        """
        self.Caption     = "ExportToImage - TatukGIS DK Sample"
        self.ClientWidth  = 560
        self.ClientHeight = 508
        self.OnShow = self.form_show

        # --- Viewer panel ---
        self.groupBox1 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox1.Place(517, 231, None, 25, None, 22)
        self.groupBox1.Caption = "Viewer"

        # rbImage / rbGrid toggle which sample dataset is loaded in the viewer
        self.rbImage = pdk.TGIS_PvlRadioButton(self.groupBox1.Context)
        self.rbImage.Place(54, 17, None, 438, None, 35)
        self.rbImage.Caption = "Image"
        self.rbImage.Checked = True
        self.rbImage.OnChange = self.rbImage_change

        self.rbGrid = pdk.TGIS_PvlRadioButton(self.groupBox1.Context)
        self.rbGrid.Place(44, 17, None, 438, None, 59)
        self.rbGrid.Caption = "Grid"
        self.rbGrid.OnChange = self.rbGrid_change

        # TGIS_ViewerWnd is the interactive map control; layers are opened directly
        # into it via GIS.Open()
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left   = 31
        self.GIS.Top    = 41
        self.GIS.Width  = 426
        self.GIS.Height = 198

        # --- File path panel ---
        self.groupBox2 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox2.Place(517, 55, None, 25, None, 277)
        self.groupBox2.Caption = "File"

        self.edtPath = pdk.TGIS_PvlEdit(self.groupBox2.Context)
        self.edtPath.Place(426, 20, None, 6, None, 20)
        self.edtPath.Enabled = False  # Read-only; path is set by the save dialog

        self.btnSelectFile = pdk.TGIS_PvlButton(self.groupBox2.Context)
        self.btnSelectFile.Place(35, 23, None, 438, None, 18)
        self.btnSelectFile.Caption = "..."
        self.btnSelectFile.OnClick = self.btnSelectFile_click

        # Radio button groups use a shared string key to enforce mutual exclusion
        self.rdbgrp1 = 'radiobuttongroupoptions'

        # --- Options panel (disabled until a destination file is chosen) ---
        self.groupBox3 = pdk.TGIS_PvlGroupBox(self.Context)
        self.groupBox3.Place(517, 123, None, 25, None, 349)
        self.groupBox3.Caption = "Options"
        self.groupBox3.Enabled = False

        self.lbFormat = pdk.TGIS_PvlLabel(self.groupBox3.Context)
        self.lbFormat.Place(39, 13, None, 21, None, 22)
        self.lbFormat.Caption = "Format"

        # cbFormat lists the TGIS_LayerPixelSubFormat options for the chosen output format
        self.cbFormat = pdk.TGIS_PvlComboBox(self.groupBox3.Context)
        self.cbFormat.Place(121, 21, None, 61, None, 18)

        self.lbExtent = pdk.TGIS_PvlLabel(self.groupBox3.Context)
        self.lbExtent.Place(37, 13, None, 20, None, 51)
        self.lbExtent.Caption = "Extent"

        # rbExtentFull / rbExtentVisible control whether the whole map or only
        # the current viewport is exported
        self.rbExtentFull = pdk.TGIS_PvlRadioButton(self.groupBox3.Context)
        self.rbExtentFull.Place(41, 17, None, 61, None, 51)
        self.rbExtentFull.Caption = "Full"
        self.rbExtentFull.Group = self.rdbgrp1

        self.rbExtentVisible = pdk.TGIS_PvlRadioButton(self.groupBox3.Context)
        self.rbExtentVisible.Place(55, 17, None, 61, None, 74)
        self.rbExtentVisible.Caption = "Visible"
        self.rbExtentVisible.Group = self.rdbgrp1

        self.rdbgrp2 = 'radiobuttongroupresolution'

        # --- Resolution sub-panel ---
        self.groupBox4 = pdk.TGIS_PvlGroupBox(self.groupBox3.Context)
        self.groupBox4.Place(260, 109, None, 251, None, 8)
        self.groupBox4.Caption = "Resolution"

        # Best quality: derive output size from the native density of the source layer
        self.rbBestQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbBestQ.Place(79, 17, None, 7, None, 37)
        self.rbBestQ.Caption = "Best quality"
        self.rbBestQ.Group = self.rdbgrp2

        # Document: fixed physical width (6.3 in) at 300 DPI
        self.rbDocQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbDocQ.Place(90, 17, None, 7, None, 60)
        self.rbDocQ.Caption = "For document"
        self.rbDocQ.Group = self.rdbgrp2

        # Web: fixed pixel width (640 px) at 96 DPI
        self.rbWebQ = pdk.TGIS_PvlRadioButton(self.groupBox4.Context)
        self.rbWebQ.Place(66, 17, None, 7, None, 83)
        self.rbWebQ.Caption = "For Web"
        self.rbWebQ.Group = self.rdbgrp2

        # Export button - disabled until a destination file has been chosen
        self.btnExport = pdk.TGIS_PvlButton(self.Context)
        self.btnExport.Place(75, 23, None, 237, None, 478)
        self.btnExport.Caption = "Export"
        self.btnExport.Enabled = False
        self.btnExport.OnClick = self.btnExport_click

    def form_show(self, _sender):
        """
        Called when the form becomes visible.

        Loads the default satellite image and sets the default radio button
        selections so the form is ready to export without further configuration.
        TGIS_Utils.GisSamplesDataDirDownload() resolves to the shared sample
        data directory, which is downloaded separately from the SDK.
        """
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/VisibleEarth/world_8km.jpg")
        self.rbBestQ.Checked    = True
        self.rbExtentFull.Checked = True

    def rbImage_change(self, _sender):
        """
        Switches the viewer to the sample satellite image (world_8km.jpg) and
        resets export controls to their disabled / empty state.

        The guard on rbImage.Checked prevents the handler from firing twice
        (once for the button that lost focus, once for the one that gained it).
        """
        if not self.rbImage.Checked:
            return

        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/VisibleEarth/world_8km.jpg")
        self.edtPath.Text = ""
        self.cbFormat.ItemsClear()
        # Disable export controls until a valid destination file is chosen
        self.groupBox3.Enabled = False
        self.btnExport.Enabled = False

    def rbGrid_change(self, _sender):
        """
        Switches the viewer to a DEM elevation grid (ADF format) and resets
        export controls.

        The hdr.adf is an ESRI Arc/Info Binary Grid header; DK11 opens the
        entire dataset by pointing at that file. Grid export supports formats
        such as Arc/Info FLT, ASCII GRD, and TatukGIS PixelStore (TTKPS).
        """
        if not self.rbGrid.Checked:
            return

        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload()
                      + "/World/Countries/USA/States/California/San Bernardino/NED/hdr.adf")
        self.edtPath.Text = ""
        self.cbFormat.ItemsClear()
        self.groupBox3.Enabled = False
        self.btnExport.Enabled = False

    def btnSelectFile_click(self, _sender):
        """
        Opens the platform save dialog, creates the output pixel layer via
        TGIS_Utils.GisCreateLayer, and populates the format combobox with the
        sub-formats supported by the chosen file format.

        TGIS_LayerPixelSubFormat describes properties like bit depth and
        compression that vary by format (e.g. TIFF supports LZW, DEFLATE;
        JPEG supports quality levels). Each combobox entry represents one valid
        combination for the selected output format extension.
        """
        save_dlg = pdk.TGIS_PvlSaveDialog(self.Context)

        # Configure the save dialog filter based on the current data-type selection
        if self.rbImage.Checked:
            ext = ".jpg"  # Default extension for the image preset
            save_dlg.Filter = ("JPEG File Interchange Format (*.jpg)|*.jpg|Portable Network Graphic (*.png)|*.png|"
                               + "Tag Image File Format (*.tif)|*.tif|Window Bitmap (*.bmp)|*.bmp|"
                               + "TatukGIS PixelStore (*.ttkps)|*.ttkps")
        elif self.rbGrid.Checked:
            ext = ".flt"  # Default extension for the grid preset
            save_dlg.Filter = ("Arc/Info Binary Grid (*.flt)|*.flt|Arc/Info ASCII Grid (*.grd)|"
                               + "*.grd|TatukGIS PixelStore (*.ttkps)|*.ttkps")

        if save_dlg.Execute() == "Cancel":
            return

        # Append the default extension so DK11 can identify the correct driver
        self.edtPath.Text = save_dlg.FileName + ext

        self.cbFormat.ItemsClear()
        self.capabilities_list = []  # Reset the parallel list before repopulating

        try:
            # GisCreateLayer inspects the file extension to choose the correct
            # TGIS_LayerPixel subclass and returns an empty layer ready to write
            if self.rbImage.Checked:
                self.lp_out = pdk.TGIS_Utils.GisCreateLayer(os.getcwd() + self.edtPath.Text, save_dlg.FileName + ext)
            else:
                self.lp_out = pdk.TGIS_Utils.GisCreateLayer(os.getcwd() + self.edtPath.Text, save_dlg.FileName + ext)

            # Capabilities returns all valid TGIS_LayerPixelSubFormat options for
            # this format. Populate the combobox and the parallel capabilities_list.
            for capability in self.lp_out.Capabilities:
                self.cbFormat.ItemsAdd(capability.ToString())
                self.capabilities_list.append(capability)  # The list holds references
                                                            # (CreateCopy called at export time)

            self.cbFormat.ItemIndex = 0

            # Enable export controls now that a valid destination and layer exist
            self.groupBox3.Enabled = True
            self.btnExport.Enabled = True

        except Exception as e:
            pdk.TGIS_PvlMessages.ShowInfo(str(e), self.Context)

    def btnExport_click(self, _sender):
        """
        Performs the raster export.

        Steps:
        1. Resolve the chosen TGIS_LayerPixelSubFormat from the combobox
           (CreateCopy() is called here to get a fresh deep copy), or fall
           back to lp_out.DefaultSubFormat.
        2. Set self.extent from the user's spatial coverage choice.
        3. Calculate pixWidth / pixHeight according to the resolution preset.
        4. Call lp_out.ImportLayer to resample the source into the output file.
        """
        # Retrieve the sub-format selected by the user (bit depth, compression, etc.)
        # CreateCopy() ensures the descriptor is independent of the combobox list
        if self.cbFormat.ItemIndex >= 0:
            capability = self.capabilities_list[self.cbFormat.ItemIndex].CreateCopy()
        else:
            capability = self.lp_out.DefaultSubFormat  # Format's natural default

        # Determine the geographic area to export
        if self.rbExtentFull.Checked:
            self.extent = self.GIS.Extent         # Full bounding box of all loaded layers
        elif self.rbExtentVisible.Checked:
            self.extent = self.GIS.VisibleExtent  # Current viewport in map coordinates

        # --- Resolution strategy ---
        if self.rbBestQ.Checked:
            # Match pixel density of the highest-resolution source layer
            self.CalcInit()

        elif self.rbDocQ.Checked:
            # Document preset: fixed physical width (6.3 inches), 300 DPI
            self.ppi      = self.DEFAULT_PPI_DOC
            self.expWidth = self.DEFAULT_WIDTH_DOC_INCH
            if (self.extent.XMax - self.extent.XMin) != 0:
                # Preserve geographic aspect ratio to avoid distortion
                self.expHeight = ((self.extent.YMax - self.extent.YMin)
                                  / (self.extent.XMax - self.extent.XMin)
                                  * self.expWidth)
            else:
                # Degenerate extent guard: use a minimal 2x2 pixel output
                self.expWidth  = 2
                self.expHeight = 2

            # Convert physical size (inches) * DPI -> pixel dimensions
            self.CalcWHPixels()

        elif self.rbWebQ.Checked:
            # Web preset: fixed pixel width (640 px), 96 DPI
            self.ppi      = self.DEFAULT_PPI_WEB
            self.pixWidth = self.DEFAULT_WIDTH_PX_WEB

            if (self.extent.XMax - self.extent.XMin) != 0:
                # Height derived from geographic aspect ratio
                self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                                  / (self.extent.XMax - self.extent.XMin)
                                  * self.pixWidth)
            else:
                self.pixWidth  = 2
                self.pixHeight = 2

            # Derive physical dimensions from pixel count / DPI (stored for reference)
            self.CalcWHUnits()

        # GIS.Items[0] is the primary (bottom-most) layer in the viewer
        lyr_in = self.GIS.Items[0]

        # ImportLayer resamples lyr_in (source) into lp_out (output file):
        #   lyr_in           - source TGIS_LayerPixel to read pixel data from
        #   lyr_in.Extent    - full geographic coverage of the source
        #   lyr_in.CS        - coordinate system, ensuring correct spatial referencing
        #   int(pixWidth/pixHeight) - output raster dimensions in pixels
        #   capability       - sub-format descriptor (bit depth, compression, etc.)
        self.lp_out.ImportLayer(lyr_in, lyr_in.Extent, lyr_in.CS,
                                int(self.pixWidth), int(self.pixHeight), capability)

        pdk.TGIS_PvlMessages.ShowInfo("File exported", self.Context)

    def CalcInit(self):
        """
        Calculates the optimal output pixel dimensions for the "Best quality" preset.

        Scans all pixel layers in the viewer to find the one with the highest pixel
        density (BitWidth / geographic extent width). The export pixel width is then
        scaled so the chosen export extent is rendered at that same native density,
        preserving the maximum detail available in the source data.  Falls back to
        DEFAULT_WIDTH_PX (4200 px) when no raster layer is loaded.
        """
        density0 = 0
        density  = density0
        self.ppi = self.DEFAULT_PPI
        j = 0

        # Iterate from the top layer downwards; keep the highest-density raster layer
        for i in range(self.GIS.Items.Count - 1, -1, -1):
            la = self.GIS.Items[i]

            if isinstance(la, pdk.TGIS_LayerPixel):
                ext_width = la.Extent.XMax - la.Extent.XMin

                # BitWidth is the layer's native pixel width over its full extent;
                # dividing by geographic width gives pixels per map unit.
                density1 = la.BitWidth / ext_width
                if density1 > density0:
                    density = density1
                    j = i       # Remember the index of the highest-density layer
                density0 = density1

        if density == 0:
            # No raster layers found; use the predefined fallback pixel width
            width_px = self.DEFAULT_WIDTH_PX
        else:
            la        = self.GIS.Items[j]
            ext_width = la.Extent.XMax - la.Extent.XMin

            # ext_delta is the fraction of the best layer's extent covered by self.extent.
            # Multiplying by BitWidth gives the source pixels in that region, which is
            # the ideal export width to preserve native resolution without upscaling.
            ext_delta = (self.extent.XMax - self.extent.XMin) / ext_width
            width_px  = int(round(ext_delta * self.GIS.Items[j].BitWidth))

        self.pixWidth = width_px

        # Preserve geographic aspect ratio so the exported image is not distorted
        if (self.extent.XMax - self.extent.XMin) != 0:
            self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.pixWidth)
        else:
            # Zero-width extent guard: produce a minimal valid raster
            self.pixWidth  = 2
            self.pixHeight = 2

    def CalcWHUnits(self):
        """
        Converts pixel dimensions to physical (inch) dimensions and preserves the
        geographic aspect ratio.

        expWidth  = pixWidth / ppi  (inches wide at the chosen DPI setting)
        expHeight = expWidth * (geographic height / geographic width)
        """
        self.expWidth = self.pixWidth / self.ppi

        if (self.extent.XMax - self.extent.XMin) != 0:
            self.expHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.expWidth)
        else:
            self.expWidth  = 2
            self.expHeight = 2

    def CalcWHPixels(self):
        """
        Converts physical (inch) dimensions to pixel dimensions and preserves the
        geographic aspect ratio.

        pixWidth  = expWidth * ppi  (pixels wide given physical width and DPI)
        pixHeight = pixWidth * (geographic height / geographic width)
        """
        self.pixWidth = self.expWidth * self.ppi

        if (self.extent.XMax - self.extent.XMin) != 0:
            self.pixHeight = ((self.extent.YMax - self.extent.YMin)
                              / (self.extent.XMax - self.extent.XMin)
                              * self.pixWidth)
        else:
            self.pixWidth  = 2
            self.pixHeight = 2


def main():
    """
    Application entry point.

    Creates and shows the form, then hands control to the TatukGIS PDK event
    loop (RunPvl) which processes UI events until the window is closed.
    """
    frm = ExportToImageForm(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
