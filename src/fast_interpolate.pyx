import numpy as np
cimport numpy as np
cimport cython


cdef class Interpolator:
    """This class implements linear interpolation based on the algorithm
    described in the Numerical Recipes book."""

    cdef int n
    cdef int saved_j_low
    cdef int dj
    cdef int ascending
    cdef int cor
    # NOTE: Cython has a limitiation and can't store cdef'd ndarrays on the
    # class so these are stored as objects. Typed memory views may alleviate
    # having to type them inside the method calls below.
    cdef object x
    cdef object y

    def __init__(self,
                 np.ndarray[np.double_t, ndim=1, mode='c'] x,
                 np.ndarray[np.double_t, ndim=2, mode='c'] y):
        """
        Parameters
        ==========
        x : c contiguous ndarray, shape(n,)
            The monotonically increasing or decreasing abscissa of the data.
        y : c contiguous ndarray, shape(n, m)
            The ordinates of the data.
        """

        self.x = x
        self.y = y

        self.n = len(x)

        if self.n < 2:
            raise ValueError('x must contain more than one entry.')

        self.ascending = x[self.n - 1] >= x[0]

        self.saved_j_low = 0

        # These variables are used to determine if locate or hunt is called.
        self.cor = 0
        self.dj = int(max(1, self.n**0.25))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef int _locate(self, double x):
        """Returns the index from the abscissa just before the provde value
        x. Bisection is used to locate the index."""

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

        # If this value of x is near the last value computed with this
        # method, then use the _hunt method on the next value.
        self.cor = 0 if abs(j_low - self.saved_j_low) > self.dj else 1
        self.saved_j_low = j_low

        return j_low

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef int _hunt(self, x):
        """Returns the index from the abscissa just before the provde value
        x. The index is first determined by hunting around the last x value
        used, and finally bisection is used to home in on the index. There
        is a computation time penalty if x is far away from the last x value
        relative to the _locate method. This works well for firing inside a
        variable step solver, for example."""

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

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef int _find_idx(self, double x):
        """Returns the index just below x in the abscissa. Either _hunt or
        _locate is used depending on how close the last two values were each
        other."""

        if self.cor:
            return self._hunt(x)
        else:
            return self._locate(x)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def interpolate(self, double x,
                    np.ndarray[np.double_t, ndim=1, mode='c'] y):
        """Returns the linear interpolation of the ordinate values.

        Parameters
        ==========
        x : float
            The value of abscissa of the desired ordinate values.
        y : c contiguous ndarray, shape(m,)
            An empty array to store the result in.

        Returns
        =======
        y : c contiguous ndarray, shape(m,)
            The interpolated values of the ordinate.

        """

        cdef np.ndarray[np.double_t, ndim=1, mode='c'] xx
        cdef np.ndarray[np.double_t, ndim=2, mode='c'] yy
        xx = self.x
        yy = self.y

        cdef int first, second
        first = self._find_idx(x)
        second = first + 1

        cdef np.ndarray[np.double_t, ndim=1, mode='c'] y_first_row
        cdef np.ndarray[np.double_t, ndim=1, mode='c'] y_second_row
        y_first_row = yy[first]
        y_second_row = yy[second]

        cdef double xx_first = xx[first]
        cdef double xx_second = xx[second]

        cdef int i
        cdef int n_r, n_c
        n_r, n_c = self.y.shape
        cdef double m, b

        for i in range(n_c):
            m = (y_first_row[i] - y_second_row[i]) / (xx_first - xx_second)
            b = y_second_row[i] - m * xx_second
            y[i] = m * x + b

        return y
