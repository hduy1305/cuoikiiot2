class Shop:
    def __init__(self, customers_entering, customers_exiting):
        self.customers_entering = customers_entering
        self.customers_exiting = customers_exiting
        self.time = None
        self.date = None

    def set_time(self, time):
        self.time = time

    def set_date(self, date):
        self.date = date

    def to_dict(self):
        return {
            "customers_entering": self.customers_entering,
            "customers_exiting": self.customers_exiting,
            "time": self.time,
            "date": self.date
        }
