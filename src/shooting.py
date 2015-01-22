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

from scipy.integrate import odeint

from system_identification import sum_of_squares


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
                                    args=(rhs_args,))

    s = sum_of_squares(measured_state_trajectory, model_state_trajectory)

    print('Objective = {}'.format(s))

    return s
