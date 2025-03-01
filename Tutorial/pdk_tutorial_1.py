import tatukgis_pdk as pdk
from PIL import Image
import io

gis = pdk.TGIS_ViewerBmp(1024, 1024)
gis.AutoStyle = True

layer_point = pdk.TGIS_LayerVector()
layer_point.Name = "point"
gis.Add(layer_point)
shp = pdk.TGIS_Utils().GisCreateShapeFromWKT("POINT (0 20)")
layer_point.AddShape(shp)

layer_line = pdk.TGIS_LayerVector()
layer_line.Name = "line"
gis.Add(layer_line)
shp = pdk.TGIS_Utils().GisCreateShapeFromWKT("LINESTRING (0 40, 10 15, 30 10)")
layer_line.AddShape(shp)

layer_polygon = pdk.TGIS_LayerVector()
layer_polygon.Name = "polygon"
gis.Add(layer_polygon)
shp = pdk.TGIS_Utils().GisCreateShapeFromWKT(
    "POLYGON ((35 10,45 45,15 40,10 20,35 10),(20 30,35 35,30 20,20 30))"
)
layer_polygon.AddShape(shp)

gis.FullExtent()

img = Image.open(io.BytesIO(gis.GIS_Bitmap.AsPng()))
img.show()
