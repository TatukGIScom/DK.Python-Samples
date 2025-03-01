import tatukgis_pdk as pdk
from PIL import Image
import io

# create an empty map
gis = pdk.TGIS_ViewerBmp(768, 1024)
sample_data = pdk.TGIS_Utils.GisSamplesDataDirDownload()

# open basemap raster
gis.Open(f"{sample_data}/World/VisibleEarth/world_8km.jpg")

# open vector layers and add to map
world_layer: pdk.TGIS_LayerVector = pdk.TGIS_Utils().GisCreateLayer(
    "world", f"{sample_data}/World/WorldDCW/world.shp")
cities_layer: pdk.TGIS_LayerVector = pdk.TGIS_Utils().GisCreateLayer(
    "cities", f"{sample_data}/World/WorldDCW/cities.shp")
gis.Add(world_layer)
gis.Add(cities_layer)

# switch raster to grayscale
raster: pdk.TGIS_LayerPixel = gis.Get("world_8km")
raster.Params.Pixel.GrayScale = True
raster.Params.Pixel.Brightness = 10

# simple polygon symbology
world_layer.Params.Area.PatternAsText = 'STOCK:TRANSPARENT'
world_layer.Params.Area.OutlineColor = pdk.TGIS_Color.FromString("#3c3351")

# advanced point symbology with multiple sections
cities_layer.MultipassRendering = True
cities_layer.Params.Marker.StyleAsText = "STOCK:CIRCLE"
cities_layer.Params.Marker.SizeAsText = "SIZE:10pt"
cities_layer.Params.Marker.Color = pdk.TGIS_Color.FromARGB(102, 243, 98, 98)
cities_layer.ParamsList.Add()
cities_layer.Params.Marker.SizeAsText = "SIZE:5pt"
cities_layer.Params.Marker.Color = pdk.TGIS_Color.FromARGB(204, 234, 188, 58)

# set World Robinson projection and zoom to South America
gis.SetCSByEPSG(102015)
gis.VisibleExtent = pdk.TGIS_Utils().GisExtent(-2500000, -3000000, 3000000, 5000000)
gis.InvalidateWholeMap()

img = Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng()))
img.show()