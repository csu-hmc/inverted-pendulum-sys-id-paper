#!/usr/bin/env python

"""This tests the fast interpolator to make sure it gives the same result at
the SciPy version."""

import numpy as np
from scipy.interpolate import interp1d

from fast_interpolate import Interpolator

x = np.linspace(0.0, 10.0, 5000)
y = np.random.random((len(x), 4))

f = interp1d(x, y, axis=0)

i = Interpolator(x, y)
res = np.empty((4,))

x_new = 10.0 * np.random.random(1)[0]

np.testing.assert_allclose(f(x_new), i.interpolate(x_new, res))
