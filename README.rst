Authors
=======

- Jason K. Moore
- Antonie J. van den Bogert
- Sandra K. Hnat

Problem introduction
====================

- Show n-link pendulum on cart diagram.
- Describe LQR controller.
- Closed loop system dyanmics.
- Describe noise inputs (process and measurement).
- Describe simulation, use same data for all methods below.
- System ID cost function, same for all problems.

Direct Approach
===============

- Describe direct approach, cite van der Kooij, guy from McGill, and Ljung.
- Describe the mathematical formulation
- Show a plot that shows the error in parameters as a function of the ratio of
  the two types of noise.
- Say something about speed of computation.

Indirect Approach: Shooting
===========================

- Describe shooting.
- Cite Tom's homotopy stuff.
- What algorithm should I use? Maybe the Python version of the CMAES alg would
  be good to use.
- The main points here will probably be:

  - how long it takes to find the solution
  - sensitivity to initial guesses
  - It doesn't matter how much you perturb??

Indirect Approach: Direct Collocation
=====================================

- Should we show the single pendulum id problem?
- Describe how we setup the problem

  - Backward Euler
  - Constraints
  - Free variables
  - Initial guess

- Describe software

  - SymPy
  - NLP solver: IPOPT

- Things

  - Sensitivity to initial guess
  - Speed of computation

- Can we solve a 9 link pendulum? (same # dof's as basic walking model)

Data Collection/Testing Protocol
=====================================

-Perturbation Signals
	-Simulink diagrams and MATLAB code
		-twice integrated white noise into high pass Butterworth and saturated
	-signals generated around ~8-10% standard dev. of the average speed
		-done ad hoc through coding, also done "experimentally"
		
-Equipment
	-Cortex 3 for motion capture (marker coordinate locations and GRF)
	-D.Flow 3.15-3.16 for VR program, treadmill manipulation, and data recording
	-Forcelink R-mill for the treadmill (+/- 0.05 meters mediolateral displacement 
	and +/- 10 degrees sagittal pitch
	-10 Osprey cameras 
	-Data recorded (GRF, marker coordinates, belt speed, etc) at 100 Hz
	
-Protocol
	-describe the testing procedure for each subject and how that was handled
	with event timing in D-Flow 
	-describe briefly in words the D-Flow program and what it's doing
	-47 marker set, maybe include diagram in supplementary material
	-harness on subject, etc.
	
-Compensation Techniques (maybe)
	-inertial artifacts due to platform movement
		-did not use platform movement, but implemented in code because we intended to move
		the platform 
		
-code stuff
	-all signals filtered at 6 Hz low-pass Butterworth filter
	-joint angles and moments calculated from 2D inverse dynamics program 

Plots
-----

- Decrease h and show how the gains get closer to the known gains.

Comparison
==========

- Maybe show something compares the computation time and accuracy of solution
  for all three methods.
