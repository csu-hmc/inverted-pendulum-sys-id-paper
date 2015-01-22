import numpy as np
cimport numpy as np
cimport cython

cdef extern from "fast_rhs_h.h":
    void rhs(double* constants,
             double* states,
             double* specifieds,
             double* xdot)

@cython.boundscheck(False)
@cython.wraparound(False)
def eval_rhs(np.ndarray[np.double_t, ndim=1, mode='c'] constants,
             np.ndarray[np.double_t, ndim=1, mode='c'] states,
             np.ndarray[np.double_t, ndim=1, mode='c'] specifieds,
             np.ndarray[np.double_t, ndim=1, mode='c'] xdot):

    rhs(<double*> constants.data,
        <double*> states.data,
        <double*> specifieds.data,
        <double*> xdot.data)

    return xdot
