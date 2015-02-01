import numpy as np
cimport numpy as np
cimport cython


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

    cdef int i = np.argmin(np.abs(x - x_new))
    cdef int first, second
    cdef np.ndarray[np.double_t, ndim=1, mode='c'] m
    cdef np.ndarray[np.double_t, ndim=1, mode='c'] b

    if i == 0:
        return y[0]
    elif i == y.shape[0] - 1:
        return y[-1]
    else:
        if x[i] < x_new:
            first = i
            second = i + 1
        else:
            first = i -1
            second = i

        m = (y[first] - y[second]) / (x[first] - x[second])
        b = y[second] - m * x[second]

        return m * x_new + b
