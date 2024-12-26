import tatukgis_pdk as pdk

class HelpForm(pdk.TGIS_PvlForm):

    def __init__(self, _owner):
        self.Caption = "Help"
        self.ClientWidth = 451
        self.ClientHeight = 308

        self.memo1 = pdk.TGIS_PvlMemo(self.Context)
        self.memo1.Place(451, 308, None, 0, None, 0)
        self.memo1.Text =\
            """Below follow all possible forms of the address string:

  06066                                      (zip code)
  06066-3481
  CT 06076                                (state code & zip code)
  CT 06238-2040
  Storrs                                      (city)
  Storrs, 06268
  Storrs, 06268-2022
  Storrs, CT
  Storrs, CT 06268
  Storrs, CT 06268-2022
  E                                             (street suffix)
  E, 06076
  E, 06076-3137
  E, CT
  E, CT 06076
  E, CT 06076-3138
  E, Storrs
  E, Storrs, 06268
  E, Storrs, 06268-2022
  E, Storrs, CT
  E, Storrs, CT 06268
  E, Storrs, CT 06268-2022
  Rd E                                       (street type & street suffix)
  Rd E, 06268
  Rd E, 06268-2022
  Rd E, CT
  Rd E, CT 06268
  Rd E, CT 06268-2022
  Dunham Pond                        (street name)
  Dunham Pond, 06076
  Dunham Pond, 06076-2022
  Dunham Pond, CT
  Dunham Pond, CT 06268
  Dunham Pond, CT 06268-2022
  Dunham Pond, Storrs
  Dunham Pond, Storrs, 06268
  Dunham Pond, Storrs, 06268-2022
  Dunham Pond, Storrs, CT
  Dunham Pond, Storrs, CT 06268
  Dunham Pond, Storrs, CT 06268-2022
  Dunham Pond E
  Dunham Pond E, 06268
  Dunham Pond E, 06268-2022
  Dunham Pond E, CT
  Dunham Pond E, CT 06268
  Dunham Pond E, CT 06268-2022
  Dunham Pond E, Storrs
  Dunham Pond E, Storrs, 06268
  Dunham Pond E, Storrs, 06268-2022
  Dunham Pond E, Storrs, CT
  Dunham Pond E, Storrs, CT 06268
  Dunham Pond E, Storrs, CT 06268-2022
  Dunham Pond Rd
  Dunham Pond Rd, 06268
  Dunham Pond Rd, 06268-2022
  Dunham Pond Rd, CT
  Dunham Pond Rd, CT, 06268
  Dunham Pond Rd, CT, 06268-2022
  Dunham Pond Rd, Storrs
  Dunham Pond Rd, Storrs, 06268
  Dunham Pond Rd, Storrs, 06268-2022
  Dunham Pond Rd, Storrs, CT
  Dunham Pond Rd, Storrs, CT, 06268
  Dunham Pond Rd, Storrs, CT, 06268-2022
  Dunham Pond Rd E
  Dunham Pond Rd E, 06268
  Dunham Pond Rd E, 06268-2022
  Dunham Pond Rd E, CT
  Dunham Pond Rd E, CT, 06268
  Dunham Pond Rd E, CT, 06268-2022
  Dunham Pond Rd E, Storrs
  Dunham Pond Rd E, Storrs, 06268
  Dunham Pond Rd E, Storrs, 06268-2022
  Dunham Pond Rd E, Storrs, CT
  Dunham Pond Rd E, Storrs, CT, 06268
  Dunham Pond Rd E, Storrs, CT, 06268-2022
  W                                           (street prefix)
  W, 06066
  W, 06066-3481
  W, CT
  W, CT 06066
  W, CT 06066-3481
  W, Rockville
  W, Rockville, 06066
  W, Rockville, 06066-3481
  W, Rockville, CT
  W, Rockville, CT 06066
  W, Rockville, CT 06066-3481
  W St
  W St, 06066
  W St, 06066-3481
  W St, CT
  W St, CT 06066
  W St, CT 06066-3481
  W St, Rockville
  W St, Rockville, 06066
  W St, Rockville, 06066-3481
  W St, Rockville, CT
  W St, Rockville, CT 06066
  W St, Rockville, CT 06066-3481
  W Main
  W Main, 06066
  W Main, 06066-3481
  W Main, CT
  W Main, CT 06066
  W Main, CT 06066-3481
  W Main, Rockville
  W Main, Rockville, 06066
  W Main, Rockville, 06066-3481
  W Main, Rockville, CT
  W Main, Rockville, CT 06066
  W Main, Rockville, CT 06066-3481
  W Main St
  W Main St, 06066
  W Main St, 06066-3481
  W Main St, CT
  W Main St, CT 06066
  W Main St, CT 06066-3481
  W Main St, Rockville
  W Main St, Rockville, 06066
  W Main St, Rockville, 06066-3481
  W Main St, Rockville, CT
  W Main St, Rockville, CT 06066
  W Main St, Rockville, CT 06066-3481

All address patterns with explicit street names can contain also the house number at the 
beginning.
Some examples:

  74 Dunham Pond
  74 Dunham Pond, Storrs
  74 Dunham Pond Rd, CT
  237 Main St
  237 W Main
  237 W Main St, Rockville, 06066-3481


The option 'Exact street- and city names' makes the street names are searched exactly as 
they were entered, otherwise they are searched with the like-operator. It means that 'Park' 
can give also 'Park' or 'Parker Bridge' as results."""
