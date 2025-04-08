import tatukgis_pdk as pdk
from PIL import Image
import io

gis = pdk.TGIS_ViewerBmp(638, 424)
sample_data = pdk.TGIS_Utils.GisSamplesDataDirDownload()

# open raster with DEM
dem: pdk.TGIS_LayerPixel = pdk.TGIS_Utils().GisCreateLayer(
    "dem",
    f"{sample_data}/World/Countries/USA/States/California/San Bernardino/NED/w001001.adf")
gis.Add(dem)
gis.VisibleExtent = dem.Extent

# use the "DEMScreen" color ramp to make your visualization more attractive
color_ramp = pdk.TGIS_Utils().GisColorRampList.ByName(pdk.TGIS_ColorRampNames().DEMScreen)
dem.Params.Pixel.ColorRamp = color_ramp.RealizeColorMap(
    pdk.TGIS_ColorMapMode().Continuous, 0, False)

#  prepare slope layer
slope = pdk.TGIS_LayerPixel()
slope.Build(True, dem.CS, dem.Extent, dem.BitWidth, dem.BitHeight)
slope.Name = "slope layer"

#  run Slope tool
slope_tool = pdk.TGIS_SlopeMap()
slope_tool.Generate(dem, dem.Extent, slope, True)

gis.Add(slope)

# show map as png
gis.InvalidateWholeMap()
img = Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng()))
img.show()
