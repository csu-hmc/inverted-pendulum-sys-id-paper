import numpy as np
cimport numpy as np
cimport cython


cdef class Interpolator:

    cdef int n
    cdef int saved_j_low
    cdef int dj
    cdef int ascending
    cdef int cor
    cdef object x
    cdef object y

    def __init__(self,
                 np.ndarray[np.double_t, ndim=1, mode='c'] x,
                 np.ndarray[np.double_t, ndim=2, mode='c'] y):

        self.x = x
        self.y = y

        self.n = len(x)

        if self.n < 2:
            raise ValueError('x must contain more than one entry.')

        self.ascending = x[self.n - 1] >= x[0]

        self.saved_j_low = 0

        self.cor = 0
        self.dj = int(max(1, self.n**0.25))

    cdef int _locate(self, double x):

        cdef int j_low = 0
        cdef int j_up = self.n - 1
        cdef int jm
        cdef np.ndarray[np.double_t, ndim=1, mode='c'] xx

        xx = self.x

        while (j_up - j_low) > 1:

            jm = (j_up + j_low) / 2

            if (x >= xx[jm]) == self.ascending:
                j_low = jm
            else:
                j_up = jm

        self.cor = 0 if abs(j_low - self.saved_j_low) > self.dj else 1
        self.saved_j_low = j_low

        return j_low

    cdef int _hunt(self, x):

        cdef int j_low = self.saved_j_low
        cdef int j_up
        cdef int inc
        cdef int jm
        cdef np.ndarray[np.double_t, ndim=1, mode='c'] xx

        xx = self.x

        if j_low < 0 or j_low > self.n - 1:
            j_low = 0
            j_up = self.n - 1
        else:
            inc = 1
            if (x >= xx[j_low]) == self.ascending:
                while 1:
                    j_up = j_low + inc
                    if j_up >= self.n - 1:
                        j_up = self.n - 1
                        break
                    elif (x < xx[j_up]) == self.ascending:
                        break
                    else:
                        j_low = j_up
                        inc += inc
            else:
                j_up = j_low
                while 1:
                    j_low = j_low - inc
                    if j_low <=0:
                        j_low = 0
                        break
                    elif (x >= xx[j_low]) == self.ascending:
                        break
                    else:
                        j_up = j_low
                        inc += inc

        # TODO: This duplicates code in _locate, could refactor.
        while j_up - j_low > 1:

            j_m = (j_up + j_low) / 2

            if x >= xx[j_m]: # == self.ascending:
                j_low = j_m
            else:
                j_up = j_m

        self.cor = 0 if abs(j_low - self.saved_j_low) > self.dj else 1

        self.saved_j_low = j_low

        return j_low

    cdef int _find_idx(self, double x):

        if self.cor:
            return self._hunt(x)
        else:
            return self._locate(x)

    def interpolate(self, double x):

        cdef np.ndarray[np.double_t, ndim=1, mode='c'] xx
        cdef np.ndarray[np.double_t, ndim=2, mode='c'] yy
        cdef np.ndarray[np.double_t, ndim=1, mode='c'] m
        cdef np.ndarray[np.double_t, ndim=1, mode='c'] b
        cdef int first, second

        xx = self.x
        yy = self.y

        first = self._find_idx(x)
        second = first + 1

        m = (yy[first] - yy[second]) / (xx[first] - xx[second])
        b = yy[second] - m * xx[second]

        return m * x + b


@cython.boundscheck(False)
@cython.wraparound(False)
def interpolate(np.ndarray[np.double_t, ndim=1, mode='c'] x,
                np.ndarray[np.double_t, ndim=2, mode='c'] y,
                double x_new):
    """
    x : ndarray, shape(n,)
    y : ndarray, shape(n, m)

    Returns
    =======


    """

    cdef np.ndarray[np.double_t, ndim=1, mode='c'] m
    cdef np.ndarray[np.double_t, ndim=1, mode='c'] b

    cdef int n = len(x)
    cdef int jl = 0
    cdef int ju = n - 1

    while (ju - jl) > 1:

        jm = (ju + jl) / 2

        if (x_new >= x[jm]):
            jl = jm
        else:
            ju = jm

    cdef int first, second

    first = jl
    second = jl + 1

    m = (y[first] - y[second]) / (x[first] - x[second])
    b = y[second] - m * x[second]

    return m * x_new + b
