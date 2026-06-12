# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Transform sample - Polynomial georeferencing of a raster image.
# Python / PDK edition.
#
# This sample demonstrates how to georeference (rectify) an unregistered
# raster image using the TatukGIS PDK polynomial transform API:
#
#   TGIS_TransformPolynomial
#     Maps pixel (source) coordinates to real-world (target) coordinates using
#     ground-control points (GCPs) and a fitted polynomial.  Order:
#       First (affine):    translation, rotation, scale, shear.  Min 3 GCPs.
#       Second:            corrects gentle curvature.  Min 6 GCPs.
#       Third:             corrects stronger distortions.  Min 10 GCPs.
#
#   TGIS_LayerPixel.Transform
#     Assigning a transform to a raster layer causes the DK to warp the image
#     on-the-fly at render time, without modifying the source file.
#
#   TGIS_TransformPolynomial.CuttingPolygon
#     Optional WKT polygon in source/pixel coordinates that masks the visible
#     area to a region of interest.
#
# Workflow:
#   btnTransform_click  - 4-GCP first-order polynomial + CRS assignment
#                         (EPSG 102748 = NAD83/Washington South State Plane).
#   btnCutting_click    - Same GCPs + CuttingPolygon masking the image.
#   btnSave_click       - Save current transform to a ".trn" sidecar file.
#   btnRead_click       - Reload a previously saved transform sidecar.
#
# Data: Samples/Rectify/satellite.jpg  (an unrectified aerial/satellite image)
# =============================================================================

import tatukgis_pdk as pdk


class TransformForm(pdk.TGIS_PvlForm):
    """
    Main form for the Transform sample.

    Demonstrates polynomial georeferencing of a raster image.
    Buttons trigger different stages of the georeferencing workflow.
    """

    # Extension for transform sidecar files: "<image_path>.trn"
    GIS_TRN_EXT = ".trn"

    def __init__(self, _owner):
        """Build the form layout and register event handlers."""
        self.Caption = "Transform - TatukGIS DK Sample"
        self.ClientWidth = 600
        self.ClientHeight = 500
        self.OnShow = self.form_show

        # Button: apply 4-GCP first-order polynomial transform
        self.btnTransform = pdk.TGIS_PvlButton(self.Context)
        self.btnTransform.Place(90, 25, None, 15, None, 10)
        self.btnTransform.Caption = "Transform"
        self.btnTransform.OnClick = self.btnTransform_click

        # Button: apply transform with CuttingPolygon mask
        self.btnCutting = pdk.TGIS_PvlButton(self.Context)
        self.btnCutting.Place(90, 25, None, 15, None, 45)
        self.btnCutting.Caption = "Cutting Polygon"
        self.btnCutting.OnClick = self.btnCutting_click

        # Button: save current transform to .trn sidecar file
        self.btnSave = pdk.TGIS_PvlButton(self.Context)
        self.btnSave.Place(90, 25, None, 15, None, 80)
        self.btnSave.Caption = "Save to File"
        self.btnSave.OnClick = self.btnSave_click

        # Button: load transform from .trn sidecar file
        self.btnRead = pdk.TGIS_PvlButton(self.Context)
        self.btnRead.Place(90, 25, None, 15, None, 115)
        self.btnRead.Caption = "Read From File"
        self.btnRead.OnClick = self.btnRead_click

        # Status label showing cursor map coordinates (anchored to bottom-left)
        self.lblCoordinates = pdk.TGIS_PvlLabel(self.Context)
        self.lblCoordinates.Place(200, 20, None, 140, None, 480)
        self.lblCoordinates.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        # Main map viewer control
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 130
        self.GIS.Top = 0
        self.GIS.Width = 480
        self.GIS.Height = 480
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS.OnMouseMove = self.GIS_MouseMove

    def form_show(self, _sender):
        """
        Called when the form first becomes visible.

        Opens the unrectified satellite image.  No transform is applied at
        startup; the user clicks buttons to georeference.
        """
        # GisSamplesDataDirDownload resolves the shared sample data folder
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "Samples/Rectify/satellite.jpg")

    def GIS_MouseMove(self, _sender, _shift, x, y):
        """
        Converts the cursor screen position to map coordinates and displays them.

        Gives real-time coordinate feedback as the user moves the mouse over
        the georeferenced image.  The coordinates update on every mouse-move
        event using the current view transform.
        """
        if self.GIS.IsEmpty:
            return

        # Convert screen pixel to map coordinate using the current view transform
        ptg = self.GIS.ScreenToMap(pdk.TPoint(int(x), int(y)))

        # Display to 4 decimal places
        self.lblCoordinates.Caption = f"X : {ptg.X:.4f} | Y : {ptg.Y:.4f}"

    def btnTransform_click(self, _sender):
        """
        Applies a first-order polynomial georeference to the satellite image.

        Steps:
          1. Create TGIS_TransformPolynomial and add four corner GCPs.
          2. Fit a first-order (affine) polynomial via Prepare().
          3. Assign the transform to the raster layer and activate warping.
          4. Declare the CRS via SetCSByEPSG(102748) - NAD83/Washington South
             State Plane in US survey feet.
          5. Recompute extent in the new CRS and zoom to show the whole image.

        Source coordinates are in image pixel convention (Y negative = image
        bottom).  Target coordinates are in State Plane feet (EPSG 102748).
        """
        # Access the first (and only) layer, which is the satellite image
        lp = self.GIS.Items[0]

        trn = pdk.TGIS_TransformPolynomial()

        # Four corner GCPs: source pixel -> target real-world coordinates.
        # AddPoint parameters: source point, target point, index, enabled.
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 239703.615056818),
                     0, True)  # top-left corner (pixel) -> bottom-left corner (world)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 244759.524147727),
                     1, True)  # bottom-left corner (pixel) -> top-left corner (world)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1279722.65909091, 245859.524147727),
                     2, True)  # bottom-right corner (pixel) -> top-right corner (world)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1279744.93181818, 239725.887784091),
                     3, True)  # top-right corner (pixel) -> bottom-right corner (world)

        # Fit the polynomial (First = affine: translation, rotation, scale, shear)
        trn.Prepare(pdk.TGIS_PolynomialOrder().First)

        # Assign the transform to the layer and activate on-the-fly warping
        lp.Transform = trn
        lp.Transform.Active = True

        # Declare the CRS so the viewer knows the real-world coordinate space
        lp.SetCSByEPSG(102748)

        # Recompute extent in the new CRS and zoom to show the whole image
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def btnCutting_click(self, _sender):
        """
        Applies a first-order polynomial transform with a CuttingPolygon mask.

        Identical GCPs to btnTransform_click but adds a CuttingPolygon
        defined as a WKT string in pixel (source) coordinates.  Only pixels
        inside the polygon are rendered after warping; the rest of the image is
        clipped at render time.

        The CRS is not set in this variant so the result is displayed in the
        warped target coordinate space without a named projection.
        """
        lp = self.GIS.Items[0]

        trn = pdk.TGIS_TransformPolynomial()

        # Four corner GCPs (same pixel-to-world mapping as btnTransform_click)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 239703.615056818),
                     0, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(-0.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1273285.84090909, 244759.524147727),
                     1, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, 0.5),
                     pdk.TGIS_Utils.GisPoint(1279722.65909091, 244759.524147727),
                     2, True)
        trn.AddPoint(pdk.TGIS_Utils.GisPoint(1246.5, -944.5),
                     pdk.TGIS_Utils.GisPoint(1279744.93181818, 239725.887784091),
                     3, True)

        # WKT polygon in SOURCE (pixel) coordinates that masks the visible region.
        # Pixels outside this polygon are not rendered after the warp is applied.
        trn.CuttingPolygon =\
            "POLYGON((421.508902077151 -320.017804154303,"\
            "518.161721068249 -223.364985163205,"\
            "688.725519287834 -210.572700296736,"\
            "864.974777448071 -254.635014836795,"\
            "896.244807121662 -335.652818991098,"\
            "894.823442136499 -453.626112759644,"\
            "823.755192878338 -615.661721068249,"\
            "516.740356083086 -607.13353115727,"\
            "371.761127596439 -533.222551928783,"\
            "340.491097922849 -456.46884272997,"\
            "421.508902077151 -320.017804154303))"

        # Fit the polynomial and activate the transform
        trn.Prepare(pdk.TGIS_PolynomialOrder().First)
        lp.Transform = trn
        lp.Transform.Active = True

        # Recompute extent and zoom to show the masked result
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()

    def btnSave_click(self, _sender):
        """
        Saves the current polynomial transform to a ".trn" sidecar file.

        The sidecar stores all GCPs and polynomial coefficients so the
        georeferencing solution can be reloaded later without re-entering data.
        The file path is derived from the layer's Path property.

        This is a no-op if no transform has been assigned to the layer yet.
        """
        lp = self.GIS.Items[0]

        # Guard: only save if a transform has been assigned
        if lp.Transform is not None:
            lp.Transform.SaveToFile(lp.Path + self.GIS_TRN_EXT)

    def btnRead_click(self, _sender):
        """
        Loads a polynomial transform from a ".trn" sidecar file and applies it.

        Creates a new TGIS_TransformPolynomial, populates it from the sidecar
        (identified by the layer's Path property), assigns it to the raster
        layer, activates warping, and zooms to fit.
        """
        lp = self.GIS.Items[0]

        # Create a new transform and load all GCPs and coefficients from the sidecar
        trn = pdk.TGIS_TransformPolynomial()
        trn.LoadFromFile(lp.Path + self.GIS_TRN_EXT)

        # Assign to the layer and activate on-the-fly warping
        lp.Transform = trn
        lp.Transform.Active = True

        # Recompute extent and zoom to show the georeferenced result
        self.GIS.RecalcExtent()
        self.GIS.FullExtent()


def main():
    """Application entry point: create and run the form."""
    frm = TransformForm(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
