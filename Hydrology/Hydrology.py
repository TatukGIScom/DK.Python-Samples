import tatukgis_pdk as pdk

def create_layer_pix(dem: pdk.TGIS_LayerPixel, name: str):
    res = pdk.TGIS_LayerPixel()
    res.Build(True, dem.CS, dem.Extent, dem.BitWidth, dem.BitHeight)
    res.Name = name
    res.Params.Pixel.Antialias = False
    res.Params.Pixel.GridShadow = False
    return res

def create_layer_vec(name, cs, shape_type):
    res = pdk.TGIS_LayerVector()
    res.Name = name
    res.Open()
    res.CS = cs
    res.DefaultShapeType = shape_type
    return res

class HydrologyForm(pdk.TGIS_PvlForm):
    dem = pdk.TGIS_LayerPixel()
    ext = pdk.TGIS_Extent()
    hydrologyToolset = pdk.TGIS_Hydrology()

    HYDRO_LAYER_SINK = "Sinks and flats"
    HYDRO_LAYER_DEM = "Hydrologically conditioned DEM"
    HYDRO_LAYER_DIRECTION = "Flow direction"
    HYDRO_LAYER_ACCUMULATION = "Flow accumulation"
    HYDRO_LAYER_STREAM_ORDER = "Stream order (Strahler)"
    HYDRO_LAYER_OUTLETS = "Outlets (pour points)"
    HYDRO_LAYER_WATERSHED = "Watersheds"
    HYDRO_LAYER_BASIN = "Basins"
    HYDRO_LAYER_STREAM_VEC = "Streams (vectorized)"
    HYDRO_LAYER_BASIN_VEC = "Basins (vectorized)"
    HYDRO_FIELD_ORDER = "ORDER"
    HYDRO_FIELD_BASIN = "BASIN_ID"

    def __init__(self, _owner):
        self.Caption = "Hydrology - TatukGIS DK Sample"
        self.ClientWidth = 949
        self.ClientHeight = 515
        self.OnShow = self.form_show

        self.toolbar_buttons = pdk.TGIS_PvlPanel(self.Context)
        self.toolbar_buttons.Place(197, 24, None, 0, None, 0)

        self.lblMethod = pdk.TGIS_PvlLabel(self.Context)
        self.lblMethod.Place(949, 24, None, 130, None, 0)
        # self.lblMethod.Font = pdk.TFont("Microsoft Sans Serif", 14, None)
        self.lblMethod.Caption = "This sample application is a step-by-step tutorial on how to perform common " \
                                 "hydrological analyzes."

        self.btnSink = pdk.TGIS_PvlButton(self.Context)
        self.btnSink.Place(197, 24, None, 0, None, 24)
        self.btnSink.Caption = "Identify DEM problems"
        self.btnSink.OnClick = self.btnSink_click

        self.btnFillSinks = pdk.TGIS_PvlButton(self.Context)
        self.btnFillSinks.Place(197, 24, None, 0, None, 48)
        self.btnFillSinks.Caption = "Fill sinks"
        self.btnFillSinks.OnClick = self.btnFillSinks_click
        self.btnFillSinks.Enabled = False

        self.btnFlowDirection = pdk.TGIS_PvlButton(self.Context)
        self.btnFlowDirection.Place(197, 24, None, 0, None, 72)
        self.btnFlowDirection.Caption = "Flow Direction"
        self.btnFlowDirection.OnClick = self.btnFlowDirection_click
        self.btnFlowDirection.Enabled = False

        self.btnFlowAccumulation = pdk.TGIS_PvlButton(self.Context)
        self.btnFlowAccumulation.Place(197, 24, None, 0, None, 96)
        self.btnFlowAccumulation.Caption = "Flow Accumulation"
        self.btnFlowAccumulation.OnClick = self.btnFlowAccumulation_click
        self.btnFlowAccumulation.Enabled = False

        self.btnAddOutlets = pdk.TGIS_PvlButton(self.Context)
        self.btnAddOutlets.Place(197, 24, None, 0, None, 120)
        self.btnAddOutlets.Caption = "Add outlets for Watershed"
        self.btnAddOutlets.OnClick = self.btnAddOutlets_click
        self.btnAddOutlets.Enabled = False

        self.btnWatershed = pdk.TGIS_PvlButton(self.Context)
        self.btnWatershed.Place(197, 24, None, 0, None, 144)
        self.btnWatershed.Caption = "Watershed"
        self.btnWatershed.OnClick = self.btnWatershed_click
        self.btnWatershed.Enabled = False

        self.btnBasin = pdk.TGIS_PvlButton(self.Context)
        self.btnBasin.Place(197, 24, None, 0, None, 168)
        self.btnBasin.Caption = "Basin"
        self.btnBasin.OnClick = self.btnBasin_click
        self.btnBasin.Enabled = False

        self.btnStreamOrderStrahler = pdk.TGIS_PvlButton(self.Context)
        self.btnStreamOrderStrahler.Place(197, 24, None, 0, None, 192)
        self.btnStreamOrderStrahler.Caption = "Stream Order (Strahler)"
        self.btnStreamOrderStrahler.OnClick = self.btnStreamOrderStrahler_click
        self.btnStreamOrderStrahler.Enabled = False

        self.btnVectorize = pdk.TGIS_PvlButton(self.Context)
        self.btnVectorize.Place(197, 24, None, 0, None, 216)
        self.btnVectorize.Caption = "Convert to vector"
        self.btnVectorize.OnClick = self.btnVectorize_click
        self.btnVectorize.Enabled = False

        self.btn3D = pdk.TGIS_PvlButton(self.Context)
        self.btn3D.Place(197, 24, None, 0, None, 240)
        self.btn3D.Caption = "View in 3D"
        self.btn3D.OnClick = self.btn3D_click
        self.btn3D.Enabled = False

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 197
        self.GIS.Top = 24
        self.GIS.Width = 583
        self.GIS.Height = 469
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(169, 491, None, 780, None, 23)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        self.progress_bar = pdk.TGIS_PvlLabel(self.Context)
        self.progress_bar.Place(583, 20, None, 197, None, 495)
        self.progress_bar.Visible = False
        self.progress_bar.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                                     pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

    def do_busy_event(self, _sender, pos, end, _abort):
        if end <= 0:
            self.progress_bar.Visible = False
        else:
            self.progress_bar.Visible = True
            self.progress_bar.Caption = str(pos/end * 100) + " %"

        self.GIS.ProcessMessages()

    def form_show(self, _sender):
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        self.GIS.RestrictedDrag = False
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() + "World/Countries/Poland/DEM/Bytowski_County.tif")

        self.dem = self.GIS.Items[0]
        self.ext = self.dem.Extent

        self.dem.Params.Pixel.Antialias = False
        self.dem.Params.Pixel.GridShadow = False
        self.GIS.InvalidateWholeMap()

        self.hydrologyToolset.BusyEvent = self.do_busy_event

    def get_layer_grd(self, name):
        return self.GIS.Get(name)

    def get_layer_vec(self, name):
        return self.GIS.Get(name)

    def btnSink_click(self, _sender):
        self.btnSink.Enabled = False

        # creating a grid layer for sinks
        sinks = create_layer_pix(self.dem, self.HYDRO_LAYER_SINK)

        # the Sink algorithm requires only a grid layer with DEM
        self.hydrologyToolset.Sink(self.dem, self.ext, sinks)

        self.GIS.Add(sinks)

        # coloring pixels with sinks (pits) and flats
        mn = str(sinks.MinHeight)
        mx = str(sinks.MaxHeight)
        sinks.Params.Pixel.AltitudeMapZones.Add("{0},{1},165:15:21:255,{2}-{3}".format(mn, mx, mn, mx))

        self.GIS.InvalidateWholeMap()
        self.btnFillSinks.Enabled = True

    def btnFillSinks_click(self, _sender):
        self.btnFillSinks.Enabled = False

        # turning off layers
        self.dem.Active = False
        self.get_layer_grd(self.HYDRO_LAYER_SINK).Active = False

        # creating a grid layer for a hydrologically conditioned DEM
        hydro_dem = create_layer_pix(self.dem, self.HYDRO_LAYER_DEM)

        # the Fill algorithm requires a grid layer with DEM
        self.hydrologyToolset.Fill(self.dem, self.ext, hydro_dem, True)

        self.GIS.Add(hydro_dem)

        # applying the layer symbology
        color_ramp = pdk.TGIS_Utils().GisColorRampList.ByName("YellowGreen")
        color_map = color_ramp.RealizeColorMap(pdk.TGIS_ColorMapMode().Continuous, 0, True)
        hydro_dem.GenerateRampEx(hydro_dem.MinHeight, hydro_dem.MaxHeight, color_map, None)
        hydro_dem.Params.Pixel.GridShadow = True
        hydro_dem.Params.Pixel.Antialias = True
        hydro_dem.Params.Pixel.ShowLegend = False

        self.GIS.InvalidateWholeMap()
        self.btnFlowDirection.Enabled = True

    def btnFlowDirection_click(self, _sender):
        self.btnFlowDirection.Enabled = False

        hydro_dem = self.get_layer_grd(self.HYDRO_LAYER_DEM)
        hydro_dem.Active = False

        # creating a grid layer for flow directions
        flow_dir = create_layer_pix(self.dem, self.HYDRO_LAYER_DIRECTION)

        # the FlowDirection algorithm requires a hydrologically conditioned DEM
        self.hydrologyToolset.FlowDirection(hydro_dem, self.ext, flow_dir, False)

        # applying a turbo color ramp for direction codes
        flow_dir.Params.Pixel.AltitudeMapZones.Add("1,1,48:18:59:255,1")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("2,2,71:117:237:255,2")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("4,4,29:206:214:255,4")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("8,8,98:252:108:255,8")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("16,16,210:232:53:255,16")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("32,32,254:154:45:255,32")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("64,64,217:56:6:255,64")
        flow_dir.Params.Pixel.AltitudeMapZones.Add("128,128,122:4:3:255,128")
        flow_dir.Params.Pixel.ShowLegend = True

        self.GIS.Add(flow_dir)
        self.GIS.InvalidateWholeMap()
        self.btnFlowAccumulation.Enabled = True

    def btnFlowAccumulation_click(self, _sender):
        self.btnFlowAccumulation.Enabled = False

        flow_dir = self.get_layer_grd(self.HYDRO_LAYER_DIRECTION)
        flow_dir.Active = False

        # creating a grid layer for flow accumulation
        flow_acc = create_layer_pix(self.dem, self.HYDRO_LAYER_ACCUMULATION)

        # the FlowAccumulation algorithm requires a flow accumulation grid
        self.hydrologyToolset.FlowAccumulation(flow_dir, self.ext, flow_acc)

        self.GIS.Add(flow_acc)

        # performing a geometric classification for a better result visualization
        classifier = pdk.TGIS_ClassificationPixel(flow_acc)
        classifier.Method = pdk.TGIS_ClassificationMethod().GeometricalInterval
        classifier.Band = "1"
        classifier.NumClasses = 5
        classifier.ColorRamp = pdk.TGIS_Utils().GisColorRampList.ByName("Bathymetry2")
        classifier.ColorRamp.DefaultReverse = True

        if classifier.MustCalculateStatistics():
            flow_acc.Statistics.Calculate()

        classifier.Classify()
        flow_acc.Params.Pixel.ShowLegend = True

        self.GIS.InvalidateWholeMap()
        self.btnAddOutlets.Enabled = True

    def btnAddOutlets_click(self, _sender):
        self.btnAddOutlets.Enabled = False

        # creating a grid layer for outlets (pour points)
        outlets = create_layer_vec(self.HYDRO_LAYER_OUTLETS, self.dem.CS, pdk.TGIS_ShapeType().Point)

        # adding point symbology
        outlets.Params.Marker.Style = pdk.TGIS_MarkerStyle().TriangleUp
        outlets.Params.Marker.SizeAsText = "SIZE:8pt"

        # adding two sample pour points
        # outlets should be located to cells of high accumulated flow
        shp = outlets.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Projection)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(375007.548333318, 696503.13358447))
        shp.Unlock()

        shp = outlets.CreateShape(pdk.TGIS_ShapeType().Point)
        shp.Lock(pdk.TGIS_Lock().Projection)
        shp.AddPart()
        shp.AddPoint(pdk.TGIS_Utils.GisPoint(399612.055851588, 706196.55502031))
        shp.Unlock()

        self.GIS.Add(outlets)
        self.GIS.InvalidateWholeMap()
        self.btnWatershed.Enabled = True

    def btnWatershed_click(self, _sender):
        self.btnWatershed.Enabled = False

        flow_dir = self.get_layer_grd(self.HYDRO_LAYER_DIRECTION)
        outlets = self.get_layer_vec(self.HYDRO_LAYER_OUTLETS)

        # creating a grid layer for watershed
        watershed = create_layer_pix(self.dem, self.HYDRO_LAYER_WATERSHED)

        # applying a symbology
        watershed.Params.Pixel.AltitudeMapZones.Add("1,1,62:138:86:255,1")
        watershed.Params.Pixel.AltitudeMapZones.Add("2,2,108:3:174:255,2")
        watershed.Transparency = 50

        watershed.Params.Pixel.ShowLegend = True

        # the Watershed algorithm requires Flow Direction grid and outlets
        # (can be a vector, or a grid)
        self.hydrologyToolset.Watershed(flow_dir, outlets, "GIS_UID", self.ext, watershed)

        self.GIS.Add(watershed)
        self.GIS.InvalidateWholeMap()
        self.btnBasin.Enabled = True

    def btnBasin_click(self, _sender):
        self.btnBasin.Enabled = False

        flow_dir = self.get_layer_grd(self.HYDRO_LAYER_DIRECTION)
        flow_acc = self.get_layer_vec(self.HYDRO_LAYER_ACCUMULATION)
        flow_acc.Active = False
        self.get_layer_grd(self.HYDRO_LAYER_DEM).Active = False
        self.get_layer_grd(self.HYDRO_LAYER_WATERSHED).Active = False
        self.get_layer_vec(self.HYDRO_LAYER_OUTLETS).Active = False

        # creating a grid layer for Basin
        basins = create_layer_pix(self.dem, self.HYDRO_LAYER_BASIN)

        # the Basin algorithm only requires a Flow Direction grid
        self.hydrologyToolset.Basin(flow_dir, self.ext, basins, int(round(flow_acc.MaxHeight / 100)))

        self.GIS.Add(basins)

        # classifying basin grid by unique values
        classifier = pdk.TGIS_ClassificationPixel(basins)
        classifier.Method = pdk.TGIS_ClassificationMethod().Unique
        classifier.Band = "Value"
        classifier.ShowLegend = False

        if classifier.MustCalculateStatistics():
            basins.Statistics.Calculate()

        classifier.EstimateNumClasses()
        classifier.ColorRamp = pdk.TGIS_Utils().GisColorRampList.ByName("UniquePastel")
        classifier.ColorRamp.DefaultColorMapMode = pdk.TGIS_ColorMapMode().Discrete
        classifier.Classify()

        self.GIS.InvalidateWholeMap()
        self.btnStreamOrderStrahler.Enabled = True

    def btnStreamOrderStrahler_click(self, _sender):
        self.btnStreamOrderStrahler.Enabled = False

        flow_dir = self.get_layer_grd(self.HYDRO_LAYER_DIRECTION)
        flow_acc = self.get_layer_grd(self.HYDRO_LAYER_ACCUMULATION)

        # creating a grid layer for stream order
        stream_order = create_layer_pix(self.dem, self.HYDRO_LAYER_STREAM_ORDER)

        # applying a symbology from the "Blues" color ramp
        stream_order.Params.Pixel.AltitudeMapZones.Add("1,1,78:179:211:255,1")
        stream_order.Params.Pixel.AltitudeMapZones.Add("2,2,43:140:190:255,2")
        stream_order.Params.Pixel.AltitudeMapZones.Add("3,3,8:104:172:255,3")
        stream_order.Params.Pixel.AltitudeMapZones.Add("4,4,8:64:129:255,4")
        stream_order.Params.Pixel.ShowLegend = True

        # the StreamOrder algorithm requires Flow Direction and Accumulation grids
        self.hydrologyToolset.StreamOrder(
            flow_dir,
            flow_acc,
            self.ext,
            stream_order,
            pdk.TGIS_HydrologyStreamOrderMethod().Strahler,
            -1
        )

        self.GIS.Add(stream_order)
        self.GIS.InvalidateWholeMap()
        self.btnVectorize.Enabled = True

    def btnVectorize_click(self, _sender):
        self.btnVectorize.Enabled = False

        flow_dir = self.get_layer_grd(self.HYDRO_LAYER_DIRECTION)
        streams = self.get_layer_grd(self.HYDRO_LAYER_STREAM_ORDER)
        basins = self.get_layer_grd(self.HYDRO_LAYER_BASIN)

        streams.Active = False
        basins.Active = False

        # 1. Converting basins to polygon
        # creating a vector polygon layer for basins
        basins_vec = create_layer_vec(self.HYDRO_LAYER_BASIN_VEC, self.dem.CS, pdk.TGIS_ShapeType().Polygon)
        basins_vec.AddField(self.HYDRO_FIELD_BASIN, pdk.TGIS_FieldType().Number, 10, 0)

        # using the GirdToPolygon vectorization tool
        vectorizator = pdk.TGIS_GridToPolygon()
        vectorizator.BusyEvent = self.do_busy_event
        vectorizator.Generate(basins, basins_vec, self.HYDRO_FIELD_BASIN)

        self.GIS.Add(basins_vec)

        # classifying a basins vector layer by unique value
        classifier = pdk.TGIS_ClassificationVector(basins_vec)
        classifier.Method = pdk.TGIS_ClassificationMethod().Unique
        classifier.Field = self.HYDRO_FIELD_BASIN
        classifier.ShowLegend = False

        if classifier.MustCalculateStatistics():
            basins_vec.Statistics.Calculate()
        classifier.EstimateNumClasses()

        classifier.ColorRamp = pdk.TGIS_Utils().GisColorRampList.ByName("Unique")
        classifier.ColorRamp.DefaultColorMapMode = pdk.TGIS_ColorMapMode().Discrete
        classifier.Classify()

        # 2. Converting streams to polylines
        # creating a vector layer for streams from Stream Order grid
        streams_vec = create_layer_vec(self.HYDRO_LAYER_STREAM_VEC, self.dem.CS, pdk.TGIS_ShapeType().Arc)
        streams_vec.AddField(self.HYDRO_FIELD_ORDER, pdk.TGIS_FieldType().Number, 10, 0)

        # applying a symbology and width based on a stream order value, and labeling
        streams_vec.Params.Line.WidthAsText = "RENDERER"
        streams_vec.Params.Line.ColorAsText = "ARGB:FF045A8D"
        streams_vec.Params.Render.Expression = self.HYDRO_FIELD_ORDER
        streams_vec.Params.Render.Zones = 4
        streams_vec.Params.Render.MinVal = 1.0
        streams_vec.Params.Render.MaxVal = 5.0
        streams_vec.Params.Render.StartSizeAsText = "SIZE:1pt"
        streams_vec.Params.Render.EndSizeAsText = "SIZE:4pt"
        streams_vec.Params.Labels.Value = "{HYDRO_FIELD_ORDER}"
        streams_vec.Params.Labels.FontSizeAsText = "SIZE:7pt"
        streams_vec.Params.Labels.FontColorAsText = "ARGB:FF045A8D"
        streams_vec.Params.Labels.ColorAsText = "ARGB:FFBDC9E1"
        streams_vec.Params.Labels.Alignment = pdk.TGIS_LabelAlignment().Follow

        self.hydrologyToolset.StreamToPolyline(flow_dir, streams, self.ext, streams_vec, self.HYDRO_FIELD_ORDER, 0)
        self.GIS.Add(streams_vec)
        self.GIS.InvalidateWholeMap()
        self.btn3D.Enabled = True

    def btn3D_click(self, _sender):
        if self.GIS.View3D:
            self.btn3D.Caption = "View in 3D"
            self.GIS.View3D = False
        else:
            self.btn3D.Caption = "View in 2D"

            basins = self.get_layer_vec(self.HYDRO_LAYER_BASIN_VEC)
            basins.Active = False

            hydro_dem = self.get_layer_grd(self.HYDRO_LAYER_DEM)
            hydro_dem.Active = True
            hydro_dem.Params.ScaleZ = 1.0
            hydro_dem.Params.NormalizedZ = pdk.TGIS_3DNormalizationType().Range

            streams = self.get_layer_vec(self.HYDRO_LAYER_STREAM_VEC)
            streams.Params.Labels.Visible = False
            streams.Layer3D = pdk.TGIS_3DLayerType().Off

            self.GIS.InvalidateWholeMap()
            self.GIS.View3D = True
            # self.GIS.Viewer3D.ShowLights = True
            # self.GIS.Viewer3D.ShadowsLevel = 40


def main():
    frm = HydrologyForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
