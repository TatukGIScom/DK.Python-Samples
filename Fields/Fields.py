# =============================================================================
# This source code is a part of TatukGIS Developer Kernel.
# =============================================================================
#
# Fields Sample - Demonstrates how to use field (attribute) properties of a layer.
#
# This sample shows:
#   - How to define custom attribute fields on an in-memory vector layer using
#     TGIS_LayerVector.AddField, specifying name, type (TGIS_FieldType), width,
#     and decimal precision.
#   - How to write field values to individual shapes using TGIS_Shape.SetField.
#   - How to use the special "FIELD:<name>" expression syntax in rendering
#     parameters (Params.Marker, Params.Line, Params.Area, Params.Labels) so
#     that each shape is rendered using its own per-attribute color, size,
#     rotation, label text, and label position.
#   - How to expose a layer's attribute table through TGIS_DataSet and display
#     it in a data grid; editing a field value and posting it triggers a map
#     redraw via the AfterPost callback.
#   - The difference between locking a shape with TGIS_Lock.Projection (keeps
#     coordinates in the layer's own projection space) vs TGIS_Lock.Extent
#     (coordinates are treated as plain world/extent coordinates).
#
# Supported shape types demonstrated: Point, Arc (polyline), Polygon.
# =============================================================================

import tatukgis_pdk as pdk
import math
from random import randint


class FieldsForm(pdk.TGIS_PvlForm):
    """
    Main form for the Fields sample.

    Lays out the UI (button, checkbox, map viewer, legend, data grid, status
    label) using the PDK portable visual layer (TGIS_Pvl*) widgets, then
    connects the "Create Layer" button to the main demonstration logic.
    """

    def __init__(self, _owner):
        # Set form caption and initial dimensions.
        self.Caption = "Fields - TatukGIS DK Sample"
        self.ClientWidth = 624
        self.ClientHeight = 514

        # Top toolbar panel — hosts the "Create Layer" button and "Use Symbols" checkbox.
        self.pnlButtons = pdk.TGIS_PvlPanel(self.Context)
        self.pnlButtons.Place(624, 514, None, 0, None, 0)

        # "Create Layer" button: triggers btnCreateLayer_click which builds the
        # in-memory layer, adds fields, populates shapes, and configures rendering.
        self.btnCreateLayer = pdk.TGIS_PvlButton(self.pnlButtons.Context)
        self.btnCreateLayer.Place(75, 23, None, 0, None, 0)
        self.btnCreateLayer.Caption = "Create Layer"
        self.btnCreateLayer.OnClick = self.btnCreateLayer_click

        # Checkbox: when checked, CGM vector symbols are loaded from the
        # sample data directory and used instead of plain geometric markers.
        self.chkUseSymbols = pdk.TGIS_PvlCheckBox(self.pnlButtons.Context)
        self.chkUseSymbols.Place(87, 17, None, 81, None, 4)
        self.chkUseSymbols.Caption = "Use Symbol"
        self.chkUseSymbols.Checked = False

        # Main interactive map viewer control.
        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 141
        self.GIS.Top = 27
        self.GIS.Width = 483
        self.GIS.Height = 320
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # Legend panel: shows the layer tree and rendering parameters.
        # GIS_Viewer must be set so the legend knows which viewer to reflect.
        self.GIS_legend = pdk.TGIS_PvlControlLegend(self.Context)
        self.GIS_legend.Mode = pdk.TGIS_ControlLegendMode().Layers
        self.GIS_legend.GIS_Viewer = self.GIS
        self.GIS_legend.Place(141, 320, None, 0, None, 27)
        self.GIS_legend.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Bottom)

        # Attribute table grid: displays each shape's field values.
        # Bound to GIS_DataSet1 after the layer is created.
        self.dataGrid = pdk.TGIS_PvlGrid(self.Context)
        self.dataGrid.Place(624, 145, None, 0, None, 347)
        self.dataGrid.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        # TGIS_DataSet bridges the vector layer to the grid widget.
        # AfterPost fires when a row edit is committed, so the map can redraw.
        self.GIS_DataSet1 = pdk.TGIS_DataSet(None)
        self.GIS_DataSet1.AfterPost = self.GIS_DataSet1_afterPost

        # Status bar panel at the bottom of the form.
        self.pnlStatus = pdk.TGIS_PvlPanel(self.Context)
        self.pnlStatus.Place(624, 22, None, 0, None, 492)
        self.pnlStatus.Align = "Bottom"

        # Hint label inside the status panel.
        self.lblMessage = pdk.TGIS_PvlLabel(self.pnlStatus.Context)
        self.lblMessage.Place(400, 19, None, 3, None, 0)
        self.lblMessage.Caption = "Open a layer properties form to change parameters"

    def btnCreateLayer_click(self, _sender):
        """
        Handles the "Create Layer" button click.

        Each invocation:
          1. Closes any existing map content.
          2. Creates a new in-memory TGIS_LayerVector named "Fields".
          3. Defines eight attribute fields that will drive the layer's appearance.
          4. Populates the layer with Point, Arc, and Polygon shapes carrying
             randomly-generated per-shape field values.
          5. Configures the layer's rendering parameters to read color, size,
             rotation, and label text directly from fields via "FIELD:<name>" tokens.
          6. Displays the layer in the viewer, refreshes the legend, and binds
             the attribute table to the data grid.
        """
        self.GIS.Close()  # Discard any previously loaded layers before rebuilding

        # Create a new in-memory vector layer.  No file path is given, so
        # the layer lives entirely in RAM and is not persisted to disk.
        lv = pdk.TGIS_LayerVector()
        lv.Name = "Fields"
        lv.Open()  # Must be opened before adding fields or shapes

        # -----------------------------------------------------------------
        # Field definitions
        # AddField(name, type, width, decimals)
        #   TGIS_FieldType().Float  : floating-point value stored with decimal places
        #   TGIS_FieldType().Number : integer-compatible numeric field (decimals=0)
        #   TGIS_FieldType().String : text field; width is the character count
        #
        # These fields are later referenced in rendering-parameter
        # "FIELD:<name>" expressions so the DK renderer reads their values
        # per shape at draw time.
        # -----------------------------------------------------------------
        lv.AddField("rotateLabel",  pdk.TGIS_FieldType().Float,  10, 4)  # Label rotation (degrees)
        lv.AddField("rotateSymbol", pdk.TGIS_FieldType().Float,  10, 4)  # Symbol/marker rotation (degrees)
        lv.AddField("color",        pdk.TGIS_FieldType().Number, 10, 0)  # Fill/stroke color as packed RGB integer
        lv.AddField("outlinecolor", pdk.TGIS_FieldType().Number, 10, 0)  # Outline color as packed RGB integer
        lv.AddField("size",         pdk.TGIS_FieldType().Number, 10, 0)  # Symbol or line width size value
        lv.AddField("label",        pdk.TGIS_FieldType().String,  1, 0)  # Text to display as the shape label
        lv.AddField("position",     pdk.TGIS_FieldType().String,  1, 0)  # Encoded label placement position
        lv.AddField("scale",        pdk.TGIS_FieldType().Float,  10, 4)  # Scale factor (pi/180 for deg->rad)

        # -----------------------------------------------------------------
        # Create 11 Point shapes at random locations within [0,20] x [0,20].
        # Each point receives its own random color, rotation, label, and
        # label-position value.
        # TGIS_Lock().Projection: coordinates are interpreted in the layer's CRS.
        # -----------------------------------------------------------------
        for i in range(11):
            shp = lv.CreateShape(pdk.TGIS_ShapeType().Point)
            shp.Lock(pdk.TGIS_Lock().Projection)  # Coordinates are in the layer's coordinate system
            shp.AddPart()                          # A Point shape requires exactly one part
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20), randint(0, 20)))

            an = randint(0, 360)  # One random angle drives both label and symbol rotation

            # SetField(name, value) writes the attribute for the current shape.
            shp.SetField("rotateLabel",  an)
            shp.SetField("rotateSymbol", an)

            # Pack three 8-bit random channel values: 0x00RRGGBB
            shp.SetField("color",        (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("label",        "Point" + str(i))
            shp.SetField("size",         randint(0, 400))

            # Build the full list of TGIS_LabelPosition enum values so a random
            # one can be picked and encoded via ConstructParamPosition into the
            # string token that the renderer's PositionAsText parameter expects.
            ar = [pdk.TGIS_LabelPosition().UpLeft,    pdk.TGIS_LabelPosition().UpCenter,
                  pdk.TGIS_LabelPosition().UpRight,
                  pdk.TGIS_LabelPosition().MiddleLeft, pdk.TGIS_LabelPosition().MiddleCenter,
                  pdk.TGIS_LabelPosition().MiddleRight,
                  pdk.TGIS_LabelPosition().DownLeft,   pdk.TGIS_LabelPosition().DownCenter,
                  pdk.TGIS_LabelPosition().DownRight]
            shp.SetField("position", pdk.TGIS_Utils.ConstructParamPosition([ar[randint(0, 8)]]))

            # pi/180 is stored so the renderer can convert raw degree values
            # from rotateLabel/rotateSymbol fields to radians when needed.
            shp.SetField("scale", math.pi / 180)
            shp.Unlock()  # Commit geometry and attributes; shape joins the layer

        # -----------------------------------------------------------------
        # One multi-vertex Arc (open polyline) with 11 random vertices
        # spread around the origin [-10,10] x [-10,10].
        # TGIS_Lock().Extent: coordinates are in world/extent space.
        # -----------------------------------------------------------------
        shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        for i in range(11):
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20) - 10, randint(0, 20) - 10))
        an = randint(0, 360)
        shp.SetField("rotateLabel",  an)
        shp.SetField("rotateSymbol", an)
        shp.SetField("color",        (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("label",        "Point" + str(1))
        shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("scale",        math.pi / 180)
        shp.Unlock()

        # -----------------------------------------------------------------
        # 12 two-vertex Arc shapes with incrementing "size" field values,
        # arranged in a horizontal row (X = [22,42+], Y = 0..10).
        # This group demonstrates that "FIELD:size" drives line width so
        # each segment is drawn progressively thicker.
        # -----------------------------------------------------------------
        for i in range(12):
            shp = lv.CreateShape(pdk.TGIS_ShapeType().Arc)
            shp.Lock(pdk.TGIS_Lock().Extent)
            shp.AddPart()
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(20 + 2 * i, 0))
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(30 + 2 * i, 10))
            an = randint(0, 360)
            shp.SetField("rotateLabel",  an)
            shp.SetField("rotateSymbol", an)
            shp.SetField("size",         i)  # Increasing size produces visibly thicker lines
            shp.SetField("color",        (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
            shp.SetField("scale",        math.pi / 180)
            shp.Unlock()

        # -----------------------------------------------------------------
        # One Polygon with 4 random vertices near the origin.
        # -----------------------------------------------------------------
        shp = lv.CreateShape(pdk.TGIS_ShapeType().Polygon)
        shp.Lock(pdk.TGIS_Lock().Extent)
        shp.AddPart()
        for i in range(4):
            shp.AddPoint(pdk.TGIS_Utils.GisPoint(randint(0, 20) - 10, randint(0, 20) - 10))
        an = randint(0, 360)
        shp.SetField("rotateLabel",  an)
        shp.SetField("rotateSymbol", an)
        shp.SetField("color",        (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("outlinecolor", (randint(0, 256) << 16) + (randint(0, 256) << 8) + randint(0, 256))
        shp.SetField("label",        "Point" + str(2))
        shp.Unlock()

        # =================================================================
        # Rendering parameter configuration
        #
        # The "FIELD:<fieldname>" token in any *AsText property tells the
        # DK renderer to evaluate the named field on each shape at draw time
        # instead of using a single static value.  An optional unit suffix
        # (":1 dip", ":1 deg") converts the raw numeric value to the
        # expected rendering unit.
        # =================================================================

        # --- Point / Marker rendering ---
        lv.Params.Marker.ColorAsText        = "FIELD:color"        # Per-shape fill color
        lv.Params.Marker.OutlineColorAsText = "FIELD:outlinecolor" # Per-shape outline color
        lv.Params.Marker.OutlineWidth       = 1                    # Static 1-pixel outline
        lv.Params.Marker.Size               = 20 * 20  # Size in twips; 1 point = 20 twips

        if self.chkUseSymbols.Checked:
            # Prepare() registers the CGM file in the SymbolList cache and
            # returns a handle used by the renderer to look up the symbol.
            lv.Params.Marker.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/2267.cgm"
            )
            lv.Params.Marker.SizeAsText         = "FIELD:size:1 dip"   # Size from field, device-independent pixels
            lv.Params.Marker.SymbolRotateAsText = "FIELD:rotateSymbol" # Symbol rotation from field

        # --- Label rendering ---
        lv.Params.Labels.Field              = "label"              # Field that supplies label text
        lv.Params.Labels.Allocator          = False                # Disable automatic conflict avoidance
        lv.Params.Labels.ColorAsText        = "FIELD:color"        # Label background color from field
        lv.Params.Labels.OutlineColorAsText = "FIELD:outlinecolor" # Label outline color from field
        lv.Params.Labels.PositionAsText     = "FIELD:position"    # Label anchor position from field
        lv.Params.Labels.FontColorAsText    = "FIELD:color"        # Font color from field
        lv.Params.Labels.RotateAsText       = "FIELD:rotateLabel:1 deg"  # Label rotation from field, in degrees

        # --- Line / Arc rendering ---
        if self.chkUseSymbols.Checked:
            lv.Params.Line.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/1301.cgm"
            )
            lv.Params.Line.SymbolRotateAsText = "FIELD:rotateSymbol:1 deg"

        lv.Params.Line.ColorAsText        = "FIELD:color"
        lv.Params.Line.OutlineColorAsText = "FIELD:outlinecolor"
        lv.Params.Line.WidthAsText        = "FIELD:size:1 dip"  # Line width from "size" field

        # --- Area / Polygon rendering ---
        lv.Params.Area.SymbolRotateAsText = "FIELD:rotateSymbol:1 deg"
        if self.chkUseSymbols.Checked:
            lv.Params.Area.Symbol = pdk.TGIS_Utils().SymbolList.Prepare(
                pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Symbols/1301.cgm"
            )
        lv.Params.Area.ColorAsText        = "FIELD:color"
        lv.Params.Area.OutlineColorAsText = "FIELD:outlinecolor"

        # Add the finished layer to the viewer, zoom to fit all shapes, refresh
        # the legend panel, then open the attribute table via TGIS_DataSet and
        # bind it to the data grid so field values are visible and editable.
        self.GIS.Add(lv)
        self.GIS.FullExtent()
        self.GIS_legend.GIS_Layer = lv
        self.GIS_DataSet1.Open(lv, lv.Extent)
        self.dataGrid.DataSet = self.GIS_DataSet1

    def GIS_DataSet1_afterPost(self, _sender):
        """
        Called by TGIS_DataSet after the user commits an edited row in the grid.
        Invalidating the whole map forces a redraw so any field value changes
        (color, size, label text, etc.) are immediately reflected in the viewer.
        """
        self.GIS.InvalidateWholeMap()


def main():
    """Entry point: create and show the Fields form, then start the event loop."""
    frm = FieldsForm(None)
    frm.Show()
    pdk.RunPvl(frm)


if __name__ == '__main__':
    main()
