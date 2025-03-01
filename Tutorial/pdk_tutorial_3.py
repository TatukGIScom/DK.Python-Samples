import tatukgis_pdk as pdk
from PIL import Image
import io

gis = pdk.TGIS_ViewerBmp(1024, 1024)
sample_data = pdk.TGIS_Utils.GisSamplesDataDirDownload()

# open basemap raster
gis.Open(f"{sample_data}/World/VisibleEarth/world_8km.jpg")

# open layer with California counties
counties_layer: pdk.TGIS_LayerVector = pdk.TGIS_Utils().GisCreateLayer(
    "counties", f"{sample_data}/World/Countries/USA/States/California/Counties.shp")
gis.Add(counties_layer)
gis.VisibleExtent = counties_layer.Extent
counties_layer.Params.Area.OutlineColor = pdk.TGIS_Color().Black
counties_layer.Transparency = 90

# classify data by "POPULATION" field
classifier = pdk.TGIS_ClassificationVector(counties_layer)
classifier.NumClasses = 5
classifier.Method = pdk.TGIS_ClassificationMethod().Quantile
classifier.Field = "POPULATION"
classifier.ColorRampName = pdk.TGIS_ColorRampNames().PurpleBlue
classifier.Classify()

# show map as png
gis.InvalidateWholeMap()
img = Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng()))
img.show()
