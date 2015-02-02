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
