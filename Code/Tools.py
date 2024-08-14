import math


class tools:
    @staticmethod
    def cum_norm(x):
        # protect against overflow
        if x > 6.0:
            return 1.0
        if x < -6.0:
            return 0.0

        b1 = 0.31938153
        b2 = -0.356563782
        b3 = 1.781477937
        b4 = -1.821255978
        b5 = 1.330274429
        p = 0.2316419
        c2 = 0.3989423
        a = abs(x)
        t = 1.0 / (1.0 + a * p)
        b = c2 * math.exp((-x) * (x / 2.0))
        n = ((((b5 * t + b4) * t + b3) * t + b2) * t + b1) * t
        n = 1.0 - b * n

        if x < 0.0:
            n = 1.0 - n

        return n
