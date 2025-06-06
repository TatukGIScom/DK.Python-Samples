"""
Generates a pseudo-3D contour map from DEM raster data using the TatukGIS DK.Python package,
combining color ramp styling, vertical line offsets, and elevation-based transparency.
"""

import tatukgis_pdk as pdk
from PIL import Image
import io
import math

def opacity2alpha(opacity: int) -> int:
    return int(opacity / 100 * 255)

# Create an empty map
gis = pdk.TGIS_ViewerBmp(2000, 2000)

# Open a raster layer with DEM
dem: pdk.TGIS_LayerPixel = pdk.TGIS_Utils().GisCreateLayer(
    "dem",
    r"D:\GisData\SRTM\N46E010.SRTMGL1.hgt\N46E010_mean_11_3_filter.tif")
dem.Open()
dem_max = dem.MaxHeight
dem_min = dem.MinHeight

# Prepare the vector layer for contour lines
contours = pdk.TGIS_LayerVector()
contours.Name = 'contours'
contours.AddField("elevation", pdk.TGIS_FieldType().Float, 0, 0)
contours.Open()
contours.MultipassRendering = True

# Use ContourGenerator to create contour lines
contour_generator = pdk.TGIS_ContourGenerator()
contour_generator.ContourInterval = (dem_max - dem_min)/40
contour_generator.MinSize = math.sqrt((dem.Extent.XMax-dem.Extent.XMin) * (dem.Extent.XMax-dem.Extent.XMin))/100
contour_generator.Smoothen = True
contour_generator.SmoothFactor = int(contour_generator.ContourInterval)
contour_generator.Mode = pdk.TGIS_ContourGeneratorMode().Polylines
contour_generator.Generate(dem, contours,"elevation")
contours.AddField("offset", pdk.TGIS_FieldType().Float, 0, 0)
for shp in contours.Loop():
    elevation = float(shp.GetField("elevation"))
    shp.MakeEditable().SetField("offset", elevation / 30)

dem.Params.Pixel.GridShadow = False
dem.Transparency = 100
gis.Add(dem)
contours.Params.Line.Color = pdk.TGIS_Color.FromString("#663333")
contours.Params.Line.WidthAsText = "SIZE:2pt"
gis.Add(contours)
gis.FullExtent()
gis.Zoom = 4 * gis.Zoom
gis.InvalidateWholeMap()
with Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng())) as img:
    img.show()

dem.Active = False
contours.ParamsList.ClearAndSetDefaults()

# Prepare 'Earth' color ramp
color_ramp = pdk.TGIS_Utils().GisColorRampList.ByName(pdk.TGIS_ColorRampNames().Earth).RealizeColorMap(pdk.TGIS_ColorMapMode().Continuous, 0, False)

# Set common section parameters
contours.Params.Render.Expression = "elevation"
contours.Params.Render.MinVal = 0.99 * dem_min
contours.Params.Render.MaxVal = 1.01 * dem_max
contours.Params.Render.Zones = 5
contours.Params.Line.ColorAsText = "RENDERER"
contours.Params.Line.WidthAsText = "SIZE:2pt"
contours.Params.Line.OffsetPosition = pdk.TGIS_OffsetPosition().UpLeft
contours.Params.Line.OffsetYAsText = "FIELD:offset:1pt"

# The first section uses the color ramp
contours.Params.Render.ColorRamp = color_ramp

# The second section applies a lighting effect
contours.ParamsList.Add()
contours.Params.Render.ColorRamp = pdk.TGIS_ColorMapArray()
contours.Params.Render.StartColor = pdk.TGIS_Color.FromARGB(opacity2alpha(10),255,255,255)
contours.Params.Render.EndColor = pdk.TGIS_Color.FromARGB(opacity2alpha(30),255,255,255)
contours.Params.Line.WidthAsText = "SIZE:1.5pt"

# Move the extent vertically
gis.FullExtent()
gis.RestrictedDrag = False
extent = gis.VisibleExtent
delta_y = 0.05 * (extent.YMax - extent.YMin)
extent.YMin = extent.YMin + delta_y
extent.YMax = extent.YMax + delta_y
gis.VisibleExtent = extent

gis.Color = pdk.TGIS_Color.FromString("#242424")
gis.InvalidateWholeMap()
with Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng())) as img:
    img.show()
