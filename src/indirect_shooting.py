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


def identify(time, measured_states, rhs, rhs_args, model, method='SLSQP'):

    x0 = np.zeros(4)

    #initial_guess = np.zeros_like(model.scaled_gains.copy())
    initial_guess = model.scaled_gains.copy()

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
        es = cma.CMAEvolutionStrategy(initial_guess.flatten(), sigma)

        pool = mp.Pool(es.popsize)

        while not es.stop():
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
                          options={'disp': True})
        gains = result.x.flatten()

    return model.gain_scale_factors.flatten() * gains
