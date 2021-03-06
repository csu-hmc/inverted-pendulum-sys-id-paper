Authors
=======

- Jason K. Moore
- Antonie J. van den Bogert

Introduction
============

- Why we do this: (1) in humans, nobody designed the controller so we need to
  identify it, (2) in humans, we can't disconnect the controller so all testing
  is in closed loop.
- cite well known problems with closed loop sys-id & potential solutions. van
  der Kooij. Most work in engineering is linear systems. Maybe cite some of these:

   - bicycle/motorcycle stuff: van lunteren and stassen, eaton, doyle, de
     Lange, my diss
   - There is control id in the aircraft world, but mostly simple linear systems.
   - There is stuff in the automobile world, but likely also linear systems.

- justify our choice of assuming a plant model. related work: Park & Kuo
  (human standing), Uchida. these were done with shooting
- Cite the Betts et. al 2003 paper.
- Gait is nonlinear, can't use frequency domain methods. Cite shooting
  (Anderson & Pandy) & direct collocation which is much more efficient for
  finding open loop optimal controls (Ackermann & van den Bogert)
- shooting has been extended towards closed loop controls (e.g. Wang or Dorn's
  work) with performance based cost function so it would be straightforward to
  extend this towards (1) collocation, and (2) a tracking cost function to find
  controllers that are human-like
- state the aims of this paper: (1) develop a method to ... (2) evaluate it
  on... and compare to direct approach

(it's not quite a logical sequence yet, we may need to remove things that don't
fit well)

Methods
=======

- Model system and data collection

  - Show two link planar standing human on moving platform diagram. (Park 2004
    model).
  - Describe the plant (even show the equations).
  - Describe controller, state feedback, and gains chosen from Park 2004.
  - Describe noise inputs (reference noise, platform acceleration, and
    measurement noise).

    Measurement noise should be added to the states, torques, and acceleration
    before introduced into the two algorithms.

  - Describe the simulations.

    - We need N simulations with increasing platform perturbation. How long? 30
      seconds? At what sample rate?
    - Simulate the non-linear model with reference noise.

- Direct approach

  - Describe direct approach, cite van der Kooij, guy from McGill, and Ljung.
  - Describe the mathematical formulation and the objective function.
  - Show a plot that shows the error in parameters identification as a function
    of perturbation magnitude.
  - Say something about speed of computation.

- Indirect Approach: Shooting
  - Straightforward method.  Avoid clever tricks like Uchida and Samin did to
    avoid local optima.  We want to show that this is slow and sensitive to
    initial guess.

- Indirect Approach: Direct Collocation

  - Objective function: minimize error in joint angles.
  - Constraints: equations of motion
  - Bounds
  - Backward Euler
  - Free variables
  - Initial guess (let's use one method to generate an initial guess that works
    well for us, alternatives, and how they worked, can be mentioned in
    Discussion)
  - mesh refinement

- Describe software and implementation

  - SymPy + opty (sympy based direct collocator)
  - NLP solver: IPOPT

Results
=======

Direct Approach
---------------

- Show and example parameter identification result.

  - This should have a simluation against a validation data set.

- Show the effect of the perturbation on the parameter id.
- Show the effect of longer duration data.
- Computational cost.

Maybe the last two can be a 3D graph with input data duration and perturbation
magnitude as vs the identified parameters (8 parameters... so 8 graphs?).

(two gains in two joints should be 4 parameters?)

(Will results show that we need long duration?  Probably yes, if the external
perturbation is small enough.  In fact, Park & Kuo used a very large
perturbation and found that feedback gains depended on the magnitude of
perturbation.  Which casts some doubt on whether they are identifying the
actual control law. It should always be the same, right?)

Indirect Approach
-----------------

- Show and example parameter identification result.

  - Include the identified numbers (and their uncertainties?).
  - This should have a simluation against a validation data set.

- Show the effect of the perturbation on the parameter id.
- Show the effect of longer duration data.
- Computational cost.

Discussion
==========

- Computation time. If we did not present results from shooting, it would be
  hard to wow the reader with how much faster this is and less sensitive to
  initial guess. So maybe do shooting after all, especially if code already
  exists.
- Sensitivity to initial guess. Also compare to shooting (if we did that).
  Provide general recommendations (if we can) for generating an initial guess
  that works.
- The collocation method scales well to long duration movement data, so we can
  potentially identify controllers with many parameters. For example neural
  networks.
- Our results show that this approach is computationally feasible and gives
  accurate results. We are ready to apply this to human control. Human motion
  has slightly more complexity and nonlinearity which may affect convergence.

Questions
=========

- Describe "experimental" protocol and data collected (should match the aims
  stated at the end of Introduction)

  - Sensitivity to initial guess
  - Speed of computation - how does it scale with number of nodes and (maybe)
    number of links. for the same initial guess, of course.
  - Do we want to test how robust the estimated gains are with respect to model
    errors? This would be important if you were to interpret results as human
    gains. This would not be important if you asked the question what control
    the model requires to make it behave like a human.
  - Make sure to design "experiments" to answer these questions:

    - What is the largest number of pendulum links we can get a solution for?
      I've only done a 4 link pendulum (40 unknown gains) from a close guess.
      Ton: I suggest to leave this out.
    - Can it find the solution from random gain guesses? How often does it get
      stuck in a local minima?
    - Can it find the solution from initial random gain guesses and setting the
      states equal to zero?
    - Is this sensitive to the process and measurement noise ratio?
    - What is the appropriate size of h to get an accurate-enough solution?  Do
      a mesh refinement experiment (only for one condition) run optimizations
      with the known gains as the initial guess and decrease h to show how the
      gains converge to the known gains and h gets smaller.

- I'd like to know if increasing the amount of data increases the likelihood of
  getting the correct answer, as I don't necessarily see that with random
  experiments. But that is anecdotal. We can mention anecdotal
  findings in the Discussion.
