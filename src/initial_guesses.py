"""

Try different initial guesses for multiple indirect methods and see if they
converge.

indirect collocation

- all zeros
- all random numbers between 0 and 1
- measured states and zeros
- measured states and random numbers for gains
- measured states and known gains

indirect shooting

The only unknowns are the gains.

- all zeros
- random numbers
- close to the known gains (30% error or something)
- known gains

"""
import logbook
import numpy as np

from model import QuietStandingModel
from measured_data import DataGenerator
import indirect_collocation
import indirect_shooting

sample_rate = 100.0  # hz
duration = 60.0  # s
total_num_nodes = int(sample_rate * duration) + 1
time_interval = duration / (total_num_nodes - 1)

logbook.info('Defining the model.')
model = QuietStandingModel(scaled_gains=0.5)
model.derive()

NUM_GAINS = model.numerical_gains.size

logbook.info('Simulating.')
generator = DataGenerator(duration, total_num_nodes, 0.0, 0.05, model)
# These ranges were chosen by examining the plots of the values and then
# divided by 3 to get sigma.
accel_noise = (11.0 - 9.75) / 3.0
coord_noise = (0.157 - 0.118) / 3.0
speed_noise = (1.997 - 1.818) / 3.0
torque_noise = (120.898 - 105.078) / 3.0
generator.generate(accel_noise, coord_noise, speed_noise, torque_noise)

#prob = indirect_collocation.setup_problem(total_num_nodes, time_interval,
                                          #generator.measured['x'],
                                          #generator.measured['a'], model)
#prob.addOption('linear_solver', 'ma57')
#
#x_meas_vec = generator.measured['x'].T.flatten()
#
#initial_guesses = {'all zeros': np.zeros(prob.num_free),
                   #'all random': np.random.normal(scale=1.0 / 3.0, size=prob.num_free),
                   #'measured states + zeros': np.hstack((x_meas_vec,
                                                         #np.zeros(8))),
                   #'measured states + random': np.hstack((x_meas_vec,
                                                          #np.random.normal(scale=1.0 / 3.0, size=8))),
                   #'measured states + known': np.hstack((x_meas_vec,
                                                         #0.5 * np.ones(8)))}
#
#collocation_solutions = {}
#collocation_infos = {}
#
#
#for k, v in initial_guesses.items():
    #logbook.info('Identifiying with initial guess: {}.'.format(k))
    #solution, info = prob.solve(v)
    #collocation_solutions[k] = solution
    #collocation_infos[k] = info
#
#for k, v in collocation_solutions.items():
    #print(k)
    #print(v[-8:] * model.gain_scale_factors.flatten())


initial_guesses = {'all zeros': np.zeros(NUM_GAINS),
                   'all random': np.random.normal(scale=1.0 / 3.0, size=(NUM_GAINS,)),
                   'known': 0.5 * np.ones(NUM_GAINS)}

shooting_solutions = {}

for k, v in initial_guesses.items():
    logbook.info('Trying initial guess: {}.'.format(k))
    shooting_solutions[k] = \
        indirect_shooting.identify(generator.time, generator.measured['x'],
                                   generator.rhs, (generator.r,
                                                   generator.p), model,
                                   method='CMA', initial_guess=v)
