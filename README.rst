Journal
=======

Jason would like to submit this to PLoS One.

Authors
=======

- Jason K. Moore
- Antonie J. van den Bogert

Software
========

All of the source code for the analysis is currently in this repository:

https://github.com/csu-hmc/inverted-pendulum-sys-id

Outline
=======

Introduction
------------

- cite direct collocation for open loop optimal controls

   - just some textbooks I guess, e.g. betts

- cite direct collocation for parameter estimation? along side open loop
  controls?

   - Need to do some research here.

- cite methods for open loop control identification for humans

   - CMC
   - Ton's work

- cite work on control identification

   - balance control: van der Kooij, Park and Kuo, etc, etc
   - bicycle/motorcycle stuff: van lunteren and stassen, eaton, doyle, de
     Lange, my diss
   - There is control id in the aircraft world, mostly simple linear systems I
     think.
   - There is stuff in the automobile world


The system
----------

- Show n-link pendulum on cart diagram.
- Describe LQR controller.
- Closed loop system dynamics.
- Describe noise inputs (process and measurement).
- Describe simulation, use same data for all methods below.
- System ID cost function, same for all problems.

Direct Approach
---------------

- Describe direct approach, cite van der Kooij, guy from McGill, and Ljung.
- Describe the mathematical formulation
- Show a plot that shows the error in parameters as a function of the ratio of
  the process and measurement.
- Say something about speed of computation.

Indirect Approach: Shooting
---------------------------

- Describe shooting.
- Cite Tom Uchida's homotopy stuff.
- What algorithm should I use? Maybe the Python version of the CMAES alg would
  be good to use.
- The main points here will probably be:

  - How long it takes to find the solution (computation time)?
  - Sensitivity to initial guesses
  - It doesn't matter how much you perturb??

Indirect Approach: Direct Collocation
-------------------------------------

- Should we show the single pendulum id problem that Ton did which came from
  Tom's paper?
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

- What is the largest number of pendulum links we can get a solution for? I've
  only done a 4 link pendulum (40 unknown gains) from a close guess.
- Can it find the solution from random gain guesses? How often does it get
  stuck in a local minima?
- Can it find the solution from initial random gain guesses and setting the
  states equal to zero?
- Is this sensitive to the process and measurement noise ratio?
- What is the appropriate size of h to get an accurate-enough solution?

Plots
~~~~~

- For the one link pendulum run optimizations with the known gains as the
  initial guess and decrease h to show how the gains converge to the known
  gains and h gets smaller.

Comparison
----------

- Maybe show something that compares the computation time and accuracy of
  solution for all three methods.
