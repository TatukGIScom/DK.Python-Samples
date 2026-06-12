# =============================================================================
# DataSet sample — demonstrates TGIS_DataSet as a live bridge between a GIS vector layer
# and a data grid (TGIS_PvlGrid).
#
# What the sample shows:
#   - Loading a vector shapefile (California Counties) into the GIS viewer
#   - Creating a TGIS_DataSet bound to the layer's attribute table
#   - Connecting the DataSet to a TGIS_PvlGrid for table display
#   - Bidirectional synchronization: grid rows ↔ map selection
#   - Clicking grid row auto-pans and zooms the viewer to the selected county
#   - Grid displays all shape attributes in editable columns
#   - Real-time map-to-grid and grid-to-map interaction
#   - AfterScroll event handles selection updates
#
# Key TatukGIS API concepts shown here:
#   TGIS_ViewerWnd              - main visual map control
#   TGIS_LayerVector            - vector layer backing the data
#   TGIS_DataSet                - attribute table bridge (implements IDataSource)
#   TGIS_PvlGrid                - Python data-aware grid control
#   GIS_DataSet.ActiveShape     - currently selected shape in grid
#   TGIS_Extent                 - geographic bounding box for zoom-to
#   Shape attributes            - grid columns bound to feature fields
#   GIS_UID field               - unique identifier for synchronization
# =============================================================================
import tatukgis_pdk as pdk

class DataSetForm(pdk.TGIS_PvlForm):
    """
    Main form for the DataSet sample.

    Left side: TGIS_ViewerWnd showing California Counties.
    Right side: TGIS_PvlGrid bound to the TGIS_DataSet.
    Scrolling the grid fires after_scroll which pans the map to the selected county.
    """
    def __init__(self, _owner):
        self.Caption = "DataSet - TatukGIS DK Sample"
        self.ClientWidth = 592
        self.ClientHeight = 466
        self.OnShow = self.form_show

        self.dataGrid1 = pdk.TGIS_PvlGrid(self.Context)
        self.dataGrid1.Place(354, 466, None, 238, None, 0)
        self.dataGrid1.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 0
        self.GIS.Top = 0
        self.GIS.Width = 233
        self.GIS.Height = 466
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top,
                            pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_DataSet = pdk.TGIS_DataSet(None)

    def form_show(self, _sender):
        """Loads the shapefile, opens the DataSet on the layer, and binds it to the grid."""
        self.GIS.Open(pdk.TGIS_Utils.GisSamplesDataDirDownload() +
                      "/World/Countries/USA/States/California/tl_2008_06_county.shp")
        self.GIS.Zoom = self.GIS.Zoom * 0.8

        ll = self.GIS.Items.Item(0)
        ll.Params.Labels.Field = "GIS_UID"
        self.GIS_DataSet.Open(self.GIS.Items.Item(0), self.GIS.Extent)
        self.GIS_DataSet.AfterScroll = self.after_scroll
        self.dataGrid1.RowsHeader = pdk.TGIS_PVlGridHeader().First
        self.dataGrid1.ColumnsHeader = pdk.TGIS_PVlGridHeader().Auto
        self.dataGrid1.RowSelect = True
        self.dataGrid1.DataSet = self.GIS_DataSet

    def after_scroll(self, _sender):
        """Pans and zooms the viewer to the county that was just selected in the grid."""
        if self.GIS_DataSet.ActiveShape is not None:
            self.GIS.Lock()
            self.GIS.VisibleExtent = self.GIS_DataSet.ActiveShape.Extent
            self.GIS.Zoom = self.GIS.Zoom * 0.8
            self.GIS.Unlock()


def main():
    frm = DataSetForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
