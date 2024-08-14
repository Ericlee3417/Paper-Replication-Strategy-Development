class Price:
    def __init__(self, bid=0.0, ask=0.0, time=0):
        self.bid = bid
        self.ask = ask
        self.mid = self.get_mid()
        self.time = time

    def clone(self):
        return Price(self.bid, self.ask, self.time)

    def get_mid(self):
        return (self.bid + self.ask) / 2

    def get_spread(self):
        return self.ask - self.bid

    def get_bid(self):
        return self.bid

    def get_ask(self):
        return self.ask

    def get_gpa_percentage(self):
        return (self.ask-self.bid)/self.bid
