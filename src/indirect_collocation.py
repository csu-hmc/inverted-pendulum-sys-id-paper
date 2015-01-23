#!/usr/bin/env python

import numpy as np
from opty.direct_collocation import Problem


def nlp_obj(num_nodes, interval, measured_states):
    """Returns a function that evaluates the least square error between the
    simulated and measured states for the NLP problem.

    Parameters
    ==========
    num_nodes : integer
        The number of time nodes.
    interval : float
        The time interval between the nodes.
    measured_states : ndarray, shape(n-8,)
        The flattened measured state time trajectories.

    """
    def obj(free):
        """
        Parameters
        ==========
        free : ndarray, shape(n,)
            The vector of free parameters. These are ordered [state0, ...,
            state3, par0, ...., par7] where the states are vectors that span
            time.
        """
        return interval * np.sum((measured_states - free[:4 * num_nodes])**2)
    return obj


def nlp_obj_grad(num_nodes, interval, measured_states):
    """Returns a function that evaluates the gradient of the least square
    error between the simulated and measured states for the NLP problem.

    Parameters
    ==========
    num_nodes : integer
        The number of time nodes.
    interval : float
        The time interval between the nodes.
    measured_states : ndarray, shape(n-8,)
        The flattened measured state time trajectories.

    """
    def obj_grad(free):
        """
        Parameters
        ==========
        free : ndarray, shape(n,)
            The vector of free parameters. These are ordered [state0, ...,
            state3, par0, ...., par7] where the states are vectors that span
            time.
        """
        grad = np.zeros_like(free)
        grad[:4 * num_nodes] = 2.0 * interval * (free[:4 * num_nodes] -
                                                 measured_states)
        return grad
    return obj_grad


def identify(num_nodes, time_interval, measured_states,
             measured_platform_accel, model):
    """Returns the optimal gains using indirect identification via direct
    collocation.

    Parameters
    ==========
    num_nodes : integer
        The number of collocation nodes.
    time_interval : float
        The time in seconds between the nodes.
    measured_states : ndarray, shape(num_nodes, 4)
        The measured state trajectories.
    measured_platform_accel : ndarray, shape(num_nodes,)
        The measured platform acceleration.
    model : instance of QuietStandingModel
        This should be a model which has already be derived.

    Returns
    =======
    identified_gains : ndarray, shape(8,)
        The optimal gains found by direct collocation.

    """

    print('Setting up direct collocation optimization problem.')
    x_meas_vec = measured_states.T.flatten()

    obj = nlp_obj(num_nodes, time_interval, x_meas_vec)
    obj_grad = nlp_obj_grad(num_nodes, time_interval, x_meas_vec)

    bounds = {}
    for g in model.gain_symbols:
        bounds[g] = (0.0, 1.0)

    prob = Problem(obj,
                   obj_grad,
                   model.first_order_implicit(),
                   model.states(),
                   num_nodes,
                   time_interval,
                   known_parameter_map=model.closed_loop_par_map,
                   known_trajectory_map={
                       model.specifieds['platform_acceleration']:
                       measured_platform_accel},
                   bounds=bounds,
                   time_symbol=model.time,
                   integration_method='midpoint')

    initial_guess = np.zeros(prob.num_free)

    # TODO : Time this solve command.
    solution, info = prob.solve(initial_guess)

    identified_gains = model.gain_scale_factors.flatten() * solution[-8:]

    return identified_gains
