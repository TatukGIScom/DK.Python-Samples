import tatukgis_pdk as pdk

class MatchesForm(pdk.TGIS_PvlForm):
    def __init__(self, _owner):
        self.Caption = "Help"
        self.ClientWidth = 251
        self.ClientHeight = 308

        self.memo1 = pdk.TGIS_PvlMemo(self.Context)
        self.memo1.Place(251, 308, None, 0, None, 0)

    def ShowMatches(self, resolved_addresses, resolved_addresses2):
        self.memo1.Clear()
        if resolved_addresses is not None:
            for i in range(resolved_addresses.count):
                if i != 0:
                    self.memo1.AppendLine("------------------------\r\n")
                addresses = resolved_addresses[i]
                for address in addresses:
                    self.memo1.AppendLine(address)
        if resolved_addresses2 is not None:
            for i in range(resolved_addresses2.count):
                if i == 0:
                    self.memo1.AppendLine("========================\r\n")
                else:
                    self.memo1.AppendLine("------------------------\r\n")
                addresses = resolved_addresses2[i]
                for address in addresses:
                    self.memo1.AppendLine(address)
