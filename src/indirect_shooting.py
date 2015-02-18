"""

1. Build a function for non-linear closed loop ODEs and cache it to disk in
   binary form. Maybe use joblib and/or Bjorn's stuff. The model constants
   can be hard coded. This function should evaluate as fast as possible.
2. Choose and initial guess for the gains.
3. Create an objective function: minimize difference in angles (and angular
   rates?). The args are the gains (and the initial state?), the function
   then simulates the system and computes the objective value.
4. Use scipy.optimize.minimize and try out different methods.


"""

import multiprocessing as mp

import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize
import cma

# TODO : Make sure that we are simulating with the MEASURED platform
# acceleration. The identification simluations should be using the measured
# values not the actual values.


def sum_of_squares(measured_states, simulated_states, interval=1.0):
    """Returns the sum of the squares of the difference in the measured
    states and the simulated states.

    Parameters
    ----------
    measured_states : array_like, shape(n, 4)
        The measured state trajectories.
    simulated_states : array_like, shape(n, 4)
        The simulated state trajectories.

    Returns
    -------
    sum_of_squares : float
        The sum of the squares in the difference between the measured and
        simulated states.

    """

    return interval * np.sum((measured_states - simulated_states) ** 2)


def objective(gain_matrix, model, rhs, initial_conditions, time_vector,
              rhs_args, measured_state_trajectory):
    """
    Parameters
    ==========
    gain_matrix : array_like, shape(2, 4)

    K = [k_00, k_01, k_02, k_03]
        [k_10, k_11, k_12, k_13]

    """
    print('Shooting...')
    print('Trying gains: {}'.format(gain_matrix))

    if len(gain_matrix.shape) == 1:
        gain_matrix = gain_matrix.reshape(2, 4)

    model.scaled_gains = gain_matrix

    model_state_trajectory = odeint(rhs,
                                    initial_conditions,
                                    time_vector,
                                    args=rhs_args)

    s = sum_of_squares(measured_state_trajectory, model_state_trajectory)

    print('Objective = {}'.format(s))

    return s


def identify(time, measured_states, rhs, rhs_args, model, method='SLSQP',
             initial_guess=None, tol=1e-8):
    """
    Parameters
    ==========
    time : ndarray, shape(n,)
        The monotonically increasing time vector.
    measured_states : ndarray, shape(n, 4)
        The measured state variables.
    rhs : function
        A function, f(x, t, r, p), that evaluates the right hand side of the
        ordinary differential equations describing the closed loop system.
    rhs_args : tuple
        The specified input and the constants.
    model : QuietStandingModel
    method : string, optional
        Any method available in scipy.optimize.minimize or 'CMA'.
    initial_guess : ndarray, shape(8,), optional
        The initial guess for the gains.

    Returns
    =======
    gains : ndarray, shape(8,)
        The flattend gain matrix.

    """

    x0 = np.zeros(4)

    if initial_guess is None:
        initial_guess = np.zeros_like(model.scaled_gains.copy())
        #initial_guess = model.scaled_gains.copy()

    if method == 'CMA':
        sigma = 0.125

        # NOTE : The objective function needs to be importable from this
        # module to work with multiprocessing. Making it a global allows it
        # to inherit all the variables from inside the identify function and
        # be importable. This shows a more elegant solution than making the
        # function a global: http://stackoverflow.com/a/16071616/467314
        global obj
        def obj(gains):
            return objective(gains, model, rhs, x0, time, rhs_args,
                             measured_states)

        # This method of parallelization is taken from the cma.py docstring
        # for CMAEvolutionStrategy.
        es = cma.CMAEvolutionStrategy(initial_guess.flatten(), sigma,
                                      {'tolx': tol})

        pool = mp.Pool(es.popsize)

        while not es.stop():
            # TODO : This gains is a group of gains for each iteration.
            gains = es.ask()
            f_values = pool.map_async(obj, gains).get()
            es.tell(gains, f_values)
            es.disp()
            es.logger.add()
    else:
        result = minimize(objective,
                          initial_guess,
                          method=method,
                          args=(model, rhs, x0, time, rhs_args,
                                measured_states),
                          tol=tol,
                          options={'disp': True})
        gains = result.x.flatten()

    return model.gain_scale_factors.flatten() * gains
