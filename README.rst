Authors
=======

- Jason K. Moore
- Antonie J. van den Bogert

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

Plots
-----

- Decrease h and show how the gains get closer to the known gains.

Comparison
==========

- Maybe show something compares the computation time and accuracy of solution
  for all three methods.
