
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

Samin's Parameters
==================

Samin used some numerical values that may be of interest:

http://hmc.csuohio.edu/projects/project_samin-askarian/matlab-files/direct-approach-linear-model/system_prop.m/view

She ran 100 second simulations with a variety of platform accelerations:

a   = 0:0.001:0.4;   % Platform acceleration

theta_1 = theta_ank
theta_2 = theta_hip

states = [theta_1, theta_1_d, theta_2, theta_2d]

She used these gains:

P.K = [950  185  175   50
        45   60  290   26];

P.M    = 85;                                    % Total human body mass(kg)
P.H    = 1.75;                                  % Human Height(m)


m1     = (2*0.161)*P.M;                         % Total leg mass 0.161*m is for one leg
m2     = 0.678*P.M;                             % HAT mass
L1     = 0.53*P.H;                              % Total leg length
L2     = (0.818-0.53)*P.H;                      % Height from hip to the shoulder
Lc1    = (1-0.447)*L1;
Lc2    = 0.626*L2;
J1     = m1*(0.326*L1)^2;                       % Moment of Inertia with respect to center of mass
J2     = m2*(0.496*L2)^2;

%% System Properties

P.L1  = L1;                                     % Length of first link
P.L2  = L2;                                     % Length of second link
P.l1  = Lc1;                                    % Distance from joint center to center of mass for first link
P.l2  = Lc2;                                    % Distance from joint center to center of mass for second link


P.m1  = m1;                                     % Mass of first link
P.m2  = m2;                                     % Mass of second link

P.J1  = J1;                                     % Moment of Inertia of first link
P.J2  = J2;                                     % Moment of Inertia of first link
P.g   = 9.8;                                    % Gravity accelaration

Controller noise:

Noise added to the torques:

c     = 0.5;                    % coefficent of dW2 and dW3 (controller noise)
Delta = 2^(-11);                % Euler-Maruyama timestep
delta = Delta;                  % Brownian path has timestep delta
dW2    = c*randn(M,1)./sqrt(delta);
dW3    = c*randn(M,1)./sqrt(delta);

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
