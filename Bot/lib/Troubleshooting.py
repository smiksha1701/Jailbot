class RestoreTroubles():
    def __init__(self) -> None:
        self.minor_troubles = {0:"Unknown Minor Error occured", 1: "Lost your last mode. Your mode now set to: Normal", 2:"Your mode was lost. Now your mode set: Normal",3: "Your last path was corrupted", 4: "Your last path was lost"}
        self.major_troubles = {0:"Unknown Major Error occured", 1: "Lost last user id"}
        self.minor_occured = []
        self.major_occured = []
    def add_minor_troubles(self, id):
        self.minor_occured.append(self.minor_troubles[id])
    
    def add_major_troubles(self, id):
        self.major_occured.append(self.major_troubles[id])
