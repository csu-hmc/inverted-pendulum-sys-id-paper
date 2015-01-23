
::

   identify(solver, gain_initial_guess, acceleration_amplitude,
            reference_noise, state_measurement_noise, torque_measurement_noise)

``solver``
   indirect with direct collocation, direct, indirect with shooting
``initial_guess``
   shooting and direct collocation need initial guess for gains, in direct
   collocation initial guess for state trajectories will be from the measured
   values
``acceleration_amplitude``
   the standard deviation of the sum of sines
``reference_noise``
   error applied added to the reference (zero) which is like the error in the
   controller's ability to sense the correct state deviation
``state_measurement_noise``
   the standard deviation for each of measurement state values
``input_measurement_noise``
   the standard devation for each of the measured joint torques and
   acceleration

We need a simulator that generates two data sets: the identification data set
and the validation data set. This will also be used in the shooting alg to
simulate the system. This should be pretty fast for the shooting method to be
reasonable.

::

   x, u = simulate(gains, acceleration_amp, reference_noise)

- x are the state trajectories
- x_meas, u_meas = measurement_noise()

Figure 1
--------

Simulate M times for each of N increasing platform accelerations. This will
give M x N simulations. These simulations should be long enough for the longest
duration needed + validation data for each.

Reference noise = 0
Measurement noise should be 0 or the same for all.

Now using each identification method, identify the gains for all M x N
simulations. Now plot the identified gains versus increasing platform
acceleration.

Figure 2
--------

Computation speed. During the above M x N identifications, measure the
computation speed for each one.

Figure 3
--------

Does the duration of the measured data matter?

Use the M x N simulations above to identify with each method using decreasing
duration. Have a fixed platform accel that is a good choice for the direct id.

Initial_guess? Something close to the true solution maybe.

Plot three graphs, one for each method that shows gains versus duration.

Figure 4
--------

Sensitivity to intial guesses in the identification. Choose a bunch of initial
guesses and see how well they do for each identification. Show some kind of
plot that compares the likelihood of getting the correct result for the two
idirect methods.
