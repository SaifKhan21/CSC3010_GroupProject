import gspread

class LinkFinishedSheet:
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('link_finished')

    # Add methods to interact with the finished links sheet
