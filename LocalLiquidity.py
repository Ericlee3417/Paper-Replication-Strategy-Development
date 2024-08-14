import math
from Tools import tools


class LocalLiquidity:
    def __init__(self, d, delta_star, alpha):
        self.type = -1
        self.delta_up = self.delta_down = d
        self.delta_star = delta_star
        self.delta = d
        self.initialized = False
        self.alpha = alpha
        self.alpha_weight = math.exp(-2.0 / (alpha + 1.0))
        self.compute_h1_h2_exp()
        self.liq = 0.0
        self.surp = 0.0

    def compute_h1_h2_exp(self):
        exp_delta_star_over_delta = math.exp(-self.delta_star / self.delta)
        self.h1 = (-exp_delta_star_over_delta * math.log(exp_delta_star_over_delta) -
                   (1.0 - exp_delta_star_over_delta) * math.log(1.0 - exp_delta_star_over_delta))
        self.h2 = (exp_delta_star_over_delta * math.pow(math.log(exp_delta_star_over_delta), 2.0) -
                   (1.0 - exp_delta_star_over_delta) * math.pow(math.log(1.0 - exp_delta_star_over_delta), 2.0) -
                   self.h1 * self.h1)

    def computation(self, price):
        event = self.run(price)
        if event != 0:
            surp_value = 0.08338161 if abs(event) == 1 else 2.525729
            self.surp = self.alpha_weight * surp_value + (1.0 - self.alpha_weight) * self.surp
            self.liq = 1.0 - tools.cum_norm(math.sqrt(self.alpha) * (self.surp - self.h1) / math.sqrt(self.h2))
        return self.liq

    def run(self, price):
        if price is None:
            return 0

        if not self.initialized:
            self.type = -1
            self.initialized = True
            self.extreme = self.reference = price.get_mid()
            return 0

        if self.type == -1:
            if math.log(price.get_bid() / self.extreme) >= self.delta_up:
                self.type = 1
                self.extreme = price.get_bid()
                self.reference = price.get_bid()
                return 1
            if price.get_ask() < self.extreme:
                self.extreme = price.get_ask()
            if math.log(self.reference / self.extreme) >= self.delta_star:
                self.reference = self.extreme
                return -2
        elif self.type == 1:
            if math.log(price.get_ask() / self.extreme) <= -self.delta_down:
                self.type = -1
                self.extreme = price.get_ask()
                self.reference = price.get_ask()
                return -1
            if price.get_bid() > self.extreme:
                self.extreme = price.get_bid()
            if math.log(self.reference / self.extreme) <= -self.delta_star:
                self.reference = self.extreme
                return 2
        return 0
