import math



class Runner:
    def __init__(self, delta_up, delta_down, d_star_up, d_star_down):
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.d_star_up = d_star_up
        self.d_star_down = d_star_down
        self.initialized = False
        self.mode = 1
        self.extreme = 0.0
        self.reference = 0.0
        self.expected_dc_level = 0.0
        self.expected_os_level = 0.0

    def run(self, price):
        # print(price.get_mid(), self.extreme, self.reference)
        if not self.initialized:
            self.initialized = True
            self.extreme = self.reference = price.get_mid()
            self.find_expected_dc_level()
            self.find_expected_os_level()
            return 0

        if self.mode == -1:
            if price.get_bid() >= self.expected_dc_level:
                self.mode = 1
                self.extreme = self.reference = price.get_bid()
                self.find_expected_dc_level()
                self.find_expected_os_level()
                return 1
            if price.get_ask() < self.extreme:
                self.extreme = price.get_ask()
                self.find_expected_dc_level()
                if price.get_ask() < self.expected_os_level:
                    self.reference = self.extreme
                    self.find_expected_os_level()
                    return -2

        elif self.mode == 1:
            if price.get_ask() <= self.expected_dc_level:
                self.mode = -1
                self.extreme = self.reference = price.get_ask()
                self.find_expected_dc_level()
                self.find_expected_os_level()
                return -1
            if price.get_bid() > self.extreme:
                self.extreme = price.get_bid()
                self.find_expected_dc_level()
                if price.get_bid() > self.expected_os_level:
                    self.reference = self.extreme
                    self.find_expected_os_level()
                    return 2

        return 0

    def find_expected_dc_level(self):
        if self.mode == -1:
            self.expected_dc_level = math.exp(math.log(self.extreme) + self.delta_up)
        else:
            self.expected_dc_level = math.exp(math.log(self.extreme) - self.delta_down)

    def find_expected_os_level(self):
        if self.mode == -1:
            self.expected_os_level = math.exp(math.log(self.reference) - self.d_star_down)
        else:
            self.expected_os_level = math.exp(math.log(self.reference) + self.d_star_up)

    def get_expected_dc_level(self):
        return self.expected_dc_level

    def get_expected_os_level(self):
        return self.expected_os_level

    def get_expected_upper_ie(self):
        return max(self.expected_dc_level, self.expected_os_level)

    def get_expected_lower_ie(self):
        return min(self.expected_dc_level, self.expected_os_level)

    def get_mode(self):
        return self.mode

    def get_delta_up(self):
        return self.delta_up

    def get_delta_down(self):
        return self.delta_down

    def get_d_star_up(self):
        return self.d_star_up

    def get_d_star_down(self):
        return self.d_star_down

    def get_upper_ie_type(self):
        return 1 if self.expected_dc_level > self.expected_os_level else 2

    def get_lower_ie_type(self):
        return 1 if self.expected_dc_level < self.expected_os_level else 2
