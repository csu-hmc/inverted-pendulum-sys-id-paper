"""This is a pure Python (NumPy) version of the basic interpolation routine
in Numerical Recipes."""


class Interpolator(object):

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.n = len(x)

        if self.n < 2:
            raise ValueError('x must contain more than one entry.')

        self.ascending = x[self.n - 1] >= x[0]

        self.saved_j_low = 0

        self.cor = False
        self.dj = int(max(1, self.n**0.25))

    def _locate(self, x):

        j_low = 0
        j_up = self.n - 1

        while (j_up - j_low) > 1:

            jm = (j_up + j_low) / 2

            if (x >= self.x[jm]) == self.ascending:
                j_low = jm
            else:
                j_up = jm

        self.cor = False if abs(j_low - self.saved_j_low) > self.dj else True
        self.saved_j_low = j_low

        return j_low

    def _hunt(self, x):

        j_low = self.saved_j_low

        if j_low < 0 or j_low > self.n - 1:

            j_low = 0
            j_up = self.n - 1
        else:
            inc = 1
            if (x >= self.x[j_low]) == self.ascending:
                while True:
                    j_up = j_low + inc
                    if j_up >= self.n - 1:
                        j_up = self.n - 1
                        break
                    elif (x < self.x[j_up]) == self.ascending:
                        break
                    else:
                        j_low = j_up
                        inc += inc
            else:
                j_up = j_low
                while True:
                    j_low = j_low - inc
                    if j_low <=0:
                        j_low = 0
                        break
                    elif (x >= self.x[j_low]) == self.ascending:
                        break
                    else:
                        j_up = j_low
                        inc += inc

        # TODO: This duplicates code in _locate, could refactor.
        while j_up - j_low > 1:

            j_m = (j_up + j_low) / 2

            if x >= self.x[j_m]: # == self.ascending:
                j_low = j_m
            else:
                j_up = j_m

        self.cor = False if abs(j_low - self.saved_j_low) > self.dj else True

        self.saved_j_low = j_low

        return j_low

    def _find_idx(self, x):

        if self.cor:
            return self._hunt(x)
        else:
            return self._locate(x)
