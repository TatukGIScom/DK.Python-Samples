import tatukgis_pdk as pdk

class OnlineServicesForm(pdk.TGIS_PvlForm):
    LOCAL_LAYER_TILES = "tiles"
    shpList = pdk.TGIS_PvlListBox

    def __init__(self, _owner):
        self.Caption = "OnlineServices - TatukGIS DK Sample"
        self.ClientWidth = 1113
        self.ClientHeight = 640
        # self.BorderStyle = "Single"
        self.OnShow = self.form_show

        self.grpbxMap = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxMap.Caption = "Map style"
        self.grpbxMap.Place(242, 57, None, 8, None, 8)

        self.cmbbxMap = pdk.TGIS_PvlComboBox(self.grpbxMap.Context)
        self.cmbbxMap.Place(222, 21, None, 11, None, 22)
        names = ("International",
                 "English",
                 "International with hillshade",
                 "English with hillshade")
        for name in names:
            self.cmbbxMap.ItemsAdd(name)
        self.cmbbxMap.ItemIndex = 1
        self.cmbbxMap.OnChange = self.cmbbxMap_change

        self.grpbxGeocoding = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxGeocoding.Caption = "Geocoding"
        self.grpbxGeocoding.Place(242, 89, None, 8, None, 71)

        self.lblGeocodingAddress = pdk.TGIS_PvlLabel(self.grpbxGeocoding.Context)
        self.lblGeocodingAddress.Place(45, 13, None, 8, None, 27)
        self.lblGeocodingAddress.Caption = "Address"

        self.edtGeocodingAddress = pdk.TGIS_PvlEdit(self.grpbxGeocoding.Context)
        self.edtGeocodingAddress.Place(174, 20, None, 59, None, 24)
        self.edtGeocodingAddress.Text = "Gdynia, Plac Kaszubski 8"

        self.lblGeocodingLimit = pdk.TGIS_PvlLabel(self.grpbxGeocoding.Context)
        self.lblGeocodingLimit.Place(28, 13, None, 8, None, 57)
        self.lblGeocodingLimit.Caption = "Limit"

        self.cmbbxGeocodingLimit = pdk.TGIS_PvlComboBox(self.grpbxGeocoding.Context)
        self.cmbbxGeocodingLimit.Place(45, 21, None, 42, None, 54)
        names = ("1", "5", "10")
        for name in names:
            self.cmbbxGeocodingLimit.ItemsAdd(name)
        self.cmbbxGeocodingLimit.ItemIndex = 0

        self.btnGeocoding = pdk.TGIS_PvlButton(self.grpbxGeocoding.Context)
        self.btnGeocoding.Place(75, 23, None, 158, None, 52)
        self.btnGeocoding.Caption = "Find"
        self.btnGeocoding.OnClick = self.btnGeocoding_click

        self.grpbxRouting = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxRouting.Caption = "Routing"
        self.grpbxRouting.Place(242, 295, None, 8, None, 166)
        self.grpbxRouting.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.lblRoutingProfile = pdk.TGIS_PvlLabel(self.grpbxRouting.Context)
        self.lblRoutingProfile.Place(39, 13, None, 11, None, 24)
        self.lblRoutingProfile.Caption = "Profile"

        self.rdbgrp1 = 'radiobuttongroupresolution'

        self.rbtnRoutingProfileCar = pdk.TGIS_PvlRadioButton(self.grpbxRouting.Context)
        self.rbtnRoutingProfileCar.Place(46, 17, None, 56, None, 22)
        self.rbtnRoutingProfileCar.Caption = "Car"
        self.rbtnRoutingProfileCar.Checked = True
        self.rbtnRoutingProfileCar.Group = self.rdbgrp1

        self.rbtnRoutingProfileBike = pdk.TGIS_PvlRadioButton(self.grpbxRouting.Context)
        self.rbtnRoutingProfileBike.Place(46, 17, None, 103, None, 22)
        self.rbtnRoutingProfileBike.Caption = "Bike"
        self.rbtnRoutingProfileBike.Group = self.rdbgrp1

        self.rbtnRoutingProfileFoot = pdk.TGIS_PvlRadioButton(self.grpbxRouting.Context)
        self.rbtnRoutingProfileFoot.Place(46, 17, None, 155, None, 22)
        self.rbtnRoutingProfileFoot.Caption = "Foot"
        self.rbtnRoutingProfileFoot.Group = self.rdbgrp1

        self.grdRouting = pdk.TGIS_PvlGrid(self.grpbxRouting.Context)
        self.grdRouting.Place(222, 206, None, 11, None, 45)
        self.grdRouting.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.btnRoutingAdd = pdk.TGIS_PvlButton(self.grpbxRouting.Context)
        self.btnRoutingAdd.Place(23, 23, None, 11, None, 257)
        self.btnRoutingAdd.Caption = "+"
        self.btnRoutingAdd.OnClick = self.btnRoutingAdd_click
        self.btnRoutingAdd.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.btnRoutingDelete = pdk.TGIS_PvlButton(self.grpbxRouting.Context)
        self.btnRoutingDelete.Place(23, 23, None, 40, None, 257)
        self.btnRoutingDelete.Caption = "-"
        self.btnRoutingDelete.OnClick = self.btnRoutingDelete_click
        self.btnRoutingDelete.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.btnRouting = pdk.TGIS_PvlButton(self.grpbxRouting.Context)
        self.btnRouting.Place(75, 23, None, 158, None, 257)
        self.btnRouting.Caption = "Find"
        self.btnRouting.OnClick = self.btnRouting_click
        self.btnRouting.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.grpbxIsochrone = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxIsochrone.Caption = "Isochrone"
        self.grpbxIsochrone.Place(242, 161, None, 8, None, 467)
        self.grpbxIsochrone.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Bottom)

        self.lblIsochroneProfile = pdk.TGIS_PvlLabel(self.grpbxIsochrone.Context)
        self.lblIsochroneProfile.Place(39, 13, None, 11, None, 24)
        self.lblIsochroneProfile.Caption = "Profile"

        self.rdbgrp2 = 'radiobuttongroupresolution'

        self.rbtnIsochroneProfileCar = pdk.TGIS_PvlRadioButton(self.grpbxIsochrone.Context)
        self.rbtnIsochroneProfileCar.Place(46, 17, None, 56, None, 22)
        self.rbtnIsochroneProfileCar.Caption = "Car"
        self.rbtnIsochroneProfileCar.Checked = True
        self.rbtnIsochroneProfileCar.Group = self.rdbgrp2

        self.rbtnIsochroneProfileBike = pdk.TGIS_PvlRadioButton(self.grpbxIsochrone.Context)
        self.rbtnIsochroneProfileBike.Place(46, 17, None, 103, None, 22)
        self.rbtnIsochroneProfileBike.Caption = "Bike"
        self.rbtnIsochroneProfileBike.Group = self.rdbgrp2

        self.rbtnIsochroneProfileFoot = pdk.TGIS_PvlRadioButton(self.grpbxIsochrone.Context)
        self.rbtnIsochroneProfileFoot.Place(46, 17, None, 155, None, 22)
        self.rbtnIsochroneProfileFoot.Caption = "Foot"
        self.rbtnIsochroneProfileFoot.Group = self.rdbgrp2

        self.lblIsochroneTime = pdk.TGIS_PvlLabel(self.grpbxIsochrone.Context)
        self.lblIsochroneTime.Place(107, 13, None, 11, None, 48)
        self.lblIsochroneTime.Caption = "Time limit (seconds)"

        self.edtIsochroneTime = pdk.TGIS_PvlEdit(self.grpbxIsochrone.Context)
        self.edtIsochroneTime.Place(107, 20, None, 126, None, 45)
        self.edtIsochroneTime.Text = "600"

        self.lblIsochroneBuckets = pdk.TGIS_PvlLabel(self.grpbxIsochrone.Context)
        self.lblIsochroneBuckets.Place(107, 13, None, 11, None, 74)
        self.lblIsochroneBuckets.Caption = "Number of buckets"

        self.cmbbxIsochroneBuckets = pdk.TGIS_PvlComboBox(self.grpbxIsochrone.Context)
        self.cmbbxIsochroneBuckets.Place(107, 21, None, 126, None, 71)
        names = ("1", "5", "10")
        for name in names:
            self.cmbbxIsochroneBuckets.ItemsAdd(name)
        self.cmbbxIsochroneBuckets.ItemIndex = 1

        self.lblIsochroneAddress = pdk.TGIS_PvlLabel(self.grpbxIsochrone.Context)
        self.lblIsochroneAddress.Place(45, 13, None, 11, None, 101)
        self.lblIsochroneAddress.Caption = "Address"

        self.edtIsochroneAddress = pdk.TGIS_PvlEdit(self.grpbxIsochrone.Context)
        self.edtIsochroneAddress.Place(171, 20, None, 62, None, 98)
        self.edtIsochroneAddress.Text = "Gdynia, Plac Kaszubski 8"

        self.btnIsochrone = pdk.TGIS_PvlButton(self.grpbxIsochrone.Context)
        self.btnIsochrone.Place(75, 23, None, 158, None, 124)
        self.btnIsochrone.Caption = "Find"
        self.btnIsochrone.OnClick = self.btnIsochrone_click

        self.grpbxRoutingDir = pdk.TGIS_PvlGroupBox(self.Context)
        self.grpbxRoutingDir.Caption = "Routing directions"
        self.grpbxRoutingDir.Place(203, 620, None, 902, None, 8)
        self.grpbxRoutingDir.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.lblRoutingDirDist = pdk.TGIS_PvlLabel(self.grpbxRoutingDir.Context)
        self.lblRoutingDirDist.Place(186, 13, None, 16, None, 22)
        self.lblRoutingDirDist.Caption = "Total distance: ?"

        self.lblRoutingDirTime = pdk.TGIS_PvlLabel(self.grpbxRoutingDir.Context)
        self.lblRoutingDirTime.Place(165, 13, None, 16, None, 44)
        self.lblRoutingDirTime.Caption = "Total time: ?"

        self.lblRoutingDirInfo = pdk.TGIS_PvlLabel(self.grpbxRoutingDir.Context)
        self.lblRoutingDirInfo.Place(109, 13, None, 16, None, 63)
        self.lblRoutingDirInfo.Caption = "Click to zoom:"

        self.grdRoutingDirections = pdk.TGIS_PvlGrid(self.grpbxRoutingDir.Context)
        self.grdRoutingDirections.Place(180, 527, None, 12, None, 79)
        self.grdRoutingDirections.SelectEvent = self.strgrdRoutingDir_click
        self.grdRoutingDirections.Anchors = (pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS = pdk.TGIS_ViewerWnd(self.Context)
        self.GIS.Left = 256
        self.GIS.Top = 0
        self.GIS.Width = 640
        self.GIS.Height = 640
        self.GIS.Mode = pdk.TGIS_ViewerMode().Zoom
        self.GIS.Anchors = (pdk.TGIS_PvlAnchor().Left, pdk.TGIS_PvlAnchor().Top, pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)

        self.GIS_ControlScale = pdk.TGIS_PvlControlScale(self.Context)
        self.GIS_ControlScale.GIS_Viewer = self.GIS
        self.GIS_ControlScale.Anchors = (pdk.TGIS_PvlAnchor().Right, pdk.TGIS_PvlAnchor().Bottom)
        self.GIS_ControlScale.Place(185, 40, None, 455, None, 597)

        self.shpList = []

    def form_show(self, _sender):
        col1 = self.grdRouting.AddColumn()
        col1.Width = 70
        col1.ReadOnly = True
        col1.Align = pdk.TGIS_PvlGridCellAlignment().Left

        col2 = self.grdRouting.AddColumn()
        col2.FitWidth = True
        col2.Align = pdk.TGIS_PvlGridCellAlignment().Left

        for i in range(3):
            row = self.grdRouting.AddRow()

        self.grdRouting.Cell(1, 1, "From")
        self.grdRouting.Cell(2, 1, "Gdynia")
        self.grdRouting.Cell(1, 2, "Through")
        self.grdRouting.Cell(2, 2, "Czestochowa")
        self.grdRouting.Cell(1, 3, "To")
        self.grdRouting.Cell(2, 3, "Wroclaw")

        tmp_style = "English"
        self.load_tiles(tmp_style)

    def load_tiles(self, style):
        layer_tiles_exist = self.GIS.Get(self.LOCAL_LAYER_TILES) is not None

        if layer_tiles_exist:
            self.GIS.Delete(self.LOCAL_LAYER_TILES)

        lwt = pdk.TGIS_LayerWebTiles()
        path = pdk.TGIS_Utils.GisSamplesDataDirDownload() + "Samples\\WebServices\\"
        if style == "International":
            path += "TatukGIS OpenStreetMap Tiles.ttkwp"
        elif style == "English":
            path += "TatukGIS OpenStreetMap Tiles (English).ttkwp"
        elif style == "InternationalHillshade":
            path += "TatukGIS OpenStreetMap Hillshade Tiles.ttkwp"
        elif style == "EnglishHillshade":
            path += "TatukGIS OpenStreetMap Hillshade Tiles (English).ttkwp"

        lwt.Path = path
        lwt.Open()
        lwt.Name = self.LOCAL_LAYER_TILES

        self.GIS.Add(lwt)
        lwt.Move(999)

        if layer_tiles_exist:
            self.GIS.InvalidateWholeMap()
        else:
            #        self.GIS.VisibleExtent = lwt.Extent
            self.GIS.FullExtent()

    @staticmethod
    def exit_number(s):
        _s = s[-1]
        if _s == '1':
            return s + 'st'
        elif _s == '2':
            return s + 'nd'
        elif _s == '3':
            return s + 'rd'
        else:
            return s + 'th'

    def add_dir(self, direction, uid):
        self.grdRoutingDirections.AddRow()
        self.grdRoutingDirections.Cell(1, self.grdRoutingDirections.RowsCount, direction)
        self.shpList.append(uid)

    @staticmethod
    def sign2dir(sign):
        if sign == -99:
            res = "[unknown]"
        elif sign == -98:
            res = "Make a u-turn"
        elif sign == -8:
            res = "Make a left u-turn"
        elif sign == -7:
            res = "Keep left"
        elif sign == -6:
            res = "Exit roundabout"
        elif sign == -3:
            res = "Sharp turn left"
        elif sign == -2:
            res = "Turn left"
        elif sign == -1:
            res = "Slight turn left"
        elif sign == 0:
            res = "Continue"
        elif sign == 1:
            res = "Slight turn right"
        elif sign == 2:
            res = "Turn right"
        elif sign == 3:
            res = "Sharp turn right"
        elif sign == 4:
            res = "Finish"
        elif sign == 5:
            res = "Reach the intermediate destination"
        elif sign == 6:
            res = "Enter roundabout and take the "
        elif sign == 7:
            res = "Keep right"
        elif sign == 8:
            res = "Make a right u-turn"
        elif sign == 101:
            res = "Start trip"
        elif sign == 102:
            res = "Transfer"
        elif sign == 103:
            res = "End trip"
        else:
            res = "Ignore"

        return res

    @staticmethod
    def grow_extent(extent, factor):
        ctr = pdk.TGIS_Utils.GisPoint(0.5 * (extent.XMin + extent.XMax), 0.5 * (extent.YMin + extent.YMax))
        x_size = 0.5 * factor * (extent.XMax - extent.XMin)
        y_size = 0.5 * factor * (extent.YMax - extent.YMin)

        return pdk.TGIS_Utils.GisExtent(ctr.X - x_size, ctr.Y - y_size, ctr.X + x_size, ctr.Y + y_size)

    @staticmethod
    def resize_extent(extent, size):
        x_size = extent.XMax - extent.XMin
        y_size = extent.YMax - extent.YMin

        if x_size > size or y_size > size:
            return extent

        ctr = pdk.TGIS_Utils.GisPoint(0.5 * (extent.XMin + extent.XMax), 0.5 * (extent.YMin + extent.YMax))
        half_size = 0.5 * size
        return pdk.TGIS_Utils.GisExtent(ctr.X-half_size, ctr.Y-half_size, ctr.X+half_size, ctr.Y+half_size)

    def reset_layers(self):
        if self.GIS.Get("fgeocoding") is not None:
            self.GIS.Delete("fgeocoding")
        if self.GIS.Get("route") is not None:
            self.GIS.Delete("route")
        if self.GIS.Get("isochrone") is not None:
            self.GIS.Delete("isochrone")

    def cmbbxMap_change(self, _sender):
        if self.cmbbxMap.ItemIndex == 0:
            self.load_tiles("International")
        elif self.cmbbxMap.ItemIndex == 1:
            self.load_tiles("English")
        elif self.cmbbxMap.ItemIndex == 2:
            self.load_tiles("InternationalHillshade")
        elif self.cmbbxMap.ItemIndex == 3:
            self.load_tiles("EnglishHillshade")

    def btnGeocoding_click(self, _sender):
        self.reset_layers()

        if not self.edtGeocodingAddress.Text:
            pdk.TGIS_PvlMessages.ShowInfo("Address not specified.", self.Context)
            return

        osm_geocoding = pdk.TGIS_OSMGeocoding()

        osm_geocoding.Limit = int(self.cmbbxGeocodingLimit.Text)
        layer_geocoding = osm_geocoding.Forward(self.edtGeocodingAddress.Text)
        if layer_geocoding.GetLastUid() > 0:

            self.lblRoutingDirDist.Caption = "Total distance: ?"
            self.lblRoutingDirTime.Caption = "Total time: ?"
            self.grdRoutingDirections.Clear()

            self.GIS.Add(layer_geocoding)

            ext = self.resize_extent(layer_geocoding.ProjectedExtent, 500.0)
            ext = self.grow_extent(ext, 1.2)

            self.GIS.VisibleExtent = ext

        else:
            pdk.TGIS_PvlMessages.ShowInfo("Address not found.", self.Context)

    def btnRoutingAdd_click(self, _sender):
        self.grdRouting.Cell(1, self.grdRouting.RowsCount, 'Through')
        row = self.grdRouting.AddRow()
        row.Column(1, "To")
        row.Column(2, "")

    def btnRoutingDelete_click(self, _sender):
        if self.grdRouting.RowsCount == 3:
           return
        self.grdRouting.Cell(1, self.grdRouting.RowsCount - 1, "To")
        self.grdRouting.DeleteRow(self.grdRouting.RowsCount)

    def btnRouting_click(self, _sender):
        self.reset_layers()

        for i in range(1, self.grdRouting.RowsCount):
            if not self.grdRouting.Row(i).Column(2):
                pdk.TGIS_PvlMessages.ShowInfo('Address not specified.', self.Context)
                return

        names = pdk.TGIS_StringList()
        osm_routing = pdk.TGIS_OSMRouting()

        if self.rbtnRoutingProfileCar.Checked:
            osm_routing.Profile = pdk.TGIS_OSMRoutingProfile().Car
        elif self.rbtnRoutingProfileBike.Checked:
            osm_routing.Profile = pdk.TGIS_OSMRoutingProfile().Bike
        elif self.rbtnRoutingProfileFoot.Checked:
            osm_routing.Profile = pdk.TGIS_OSMRoutingProfile().Foot

        for i in range(1, self.grdRouting.RowsCount + 1):
            names.Add(self.grdRouting.Cell(2, i))

        layer_routing = osm_routing.Route(names)
        if layer_routing is not None:
            loop_done = False
            dist = 0
            time = 0
            for shp in layer_routing.Loop():
                try:
                    dist += int(shp.GetField("distance"))
                except ValueError:
                    pass

                try:
                    time += int(shp.GetField("time"))
                except ValueError:
                    pass

                loop_done = True

            self.GIS.Add(layer_routing)
            ext = self.resize_extent(layer_routing.ProjectedExtent, 500.0)
            self.GIS.VisibleExtent = self.grow_extent(ext, 1.2)

            if loop_done:
                uid = 0

                if dist < 1000:
                    dist_str = str(dist) + " m"
                else:
                    dist_str = f"{dist / 1000.0:.2f} km"

                self.lblRoutingDirDist.Caption = "Total distance: " + dist_str

                hrs = int(time / 3600)
                mns = int((time / 60) - hrs * 60)
                if hrs == 0:
                    dist_str = str(mns) + " min"
                else:
                    dist_str = str(hrs) + " h " + str(mns) + " min"

                self.lblRoutingDirTime.Caption = "Total time: " + dist_str

                final_destination = False
                self.grdRoutingDirections.Clear()

                col1 = self.grdRoutingDirections.AddColumn()
                col1.Width = 384
                col1.ReadOnly = True
                col1.Align = pdk.TGIS_PvlGridCellAlignment().Left

                self.shpList.clear()
                self.grdRoutingDirections.BeginUpdate()
                try:
                    for shp in layer_routing.Loop(layer_routing.Extent, "( type = 'route' )"):
                        uid = shp.Uid
                        try:
                            i = int(shp.GetField("sign"))
                        except ValueError:
                            i = 0
                        dist_str = shp.GetField("name")

                        direction = ""
                        if i == -98:
                            pass
                        elif i == -8:
                            pass
                        elif i == 8:
                            pass
                        elif i == 5:
                            direction = self.sign2dir(i)
                        elif i == 6:
                            direction = self.sign2dir(i) + self.exit_number(str(shp.GetField("exit"))) + " exit"
                        else:
                            direction = self.sign2dir(i)
                            if dist_str is not None and dist_str != "":
                                if i == 0:
                                    direction += " on " + dist_str
                                else:
                                    direction += " onto " + dist_str

                        if i == 5:
                            self.add_dir(direction, uid)
                            final_destination = True
                            continue

                        try:
                            dist = int(shp.GetField("distance"))
                        except ValueError:
                            dist = 0
                        if dist < 1000:
                            direction += " (" + str(dist) + " m, "
                        else:
                            direction += f" ({dist / 1000.0:.2f} km"

                        time = int(shp.GetField("time"))
                        hrs = int(time / 3600)
                        mns = int((time / 60) - hrs * 60)
                        if hrs == 0:
                            if mns == 0:
                                direction += "<1 min)"
                            else:
                                direction += str(mns) + " min)"
                        else:
                            direction += str(hrs) + " h " + str(mns) + " min)"

                        self.add_dir(direction, uid)

                    if final_destination:
                        self.add_dir("Reach the final destination", uid)
                    else:
                        self.add_dir("Reach the destination", uid)
                finally:
                    self.grdRoutingDirections.EndUpdate()
            else:
                pdk.TGIS_PvlMessages.ShowInfo("Route not found.", self.Context)

    def btnIsochrone_click(self, _sender):
        self.reset_layers()

        if not self.edtIsochroneAddress.Text:
            pdk.TGIS_PvlMessages.ShowInfo("Address not specified.", self.Context)
            return

        time = int(self.edtIsochroneTime.Text)
        if type(time) is not int:
            pdk.TGIS_PvlMessages.ShowInfo("'" + self.edtIsochroneTime.Text + "' is not a positive number.",
                                          self.Context)
            return

        osm_isochrone = pdk.TGIS_OSMIsochrone()

        if self.rbtnIsochroneProfileCar.Checked:
            osm_isochrone.Profile = pdk.TGIS_OSMRoutingProfile().Car
        elif self.rbtnIsochroneProfileBike.Checked:
            osm_isochrone.Profile = pdk.TGIS_OSMRoutingProfile().Bike
        elif self.rbtnIsochroneProfileFoot.Checked:
            osm_isochrone.Profile = pdk.TGIS_OSMRoutingProfile().Foot

        tmp = self.cmbbxIsochroneBuckets.Text
        osm_isochrone.Buckets = int(tmp)
        osm_isochrone.TimeLimit = time
        liso = osm_isochrone.Isochrone(self.edtIsochroneAddress.Text)

        if liso.GetLastUid() > 0:
            self.lblRoutingDirDist.Caption = "Total distance: ?"
            self.lblRoutingDirTime.Caption = "Total time: ?"

            self.grdRoutingDirections.Clear()

            self.GIS.Add(liso)

            ext = self.resize_extent(liso.ProjectedExtent, 500.0)
            ext = self.grow_extent(ext, 1.2)

            self.GIS.VisibleExtent = ext
        else:
            pdk.TGIS_PvlMessages.ShowInfo("Address not found.", self.Context)

    def strgrdRoutingDir_click(self, _sender):
        layer_routing = self.GIS.Get("route")
        if layer_routing is None:
            return

        row = self.grdRoutingDirections.ActiveCell.Y
        shp = layer_routing.GetShape(self.shpList[row-1])
        if shp is None:
            return

        self.GIS.VisibleExtent = self.resize_extent(shp.ProjectedExtent, 500.0)


def main():
    frm = OnlineServicesForm(None)
    frm.Show()
    pdk.RunPvl(frm)

if __name__ == '__main__':
    main()
