Journal
=======

Jason would like to submit this to PLoS One.

Notes on editing the files
==========================

- The README is in RestructuredText format. See
  http://docutils.sourceforge.net/docs/user/rst/quickref.html for tips on the
  syntax.

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

- why we do this: (1) in humans, nobody designed the controller so we need to identify it,
  (2) in humans, we can't disconnect the controller so all testing is in closed loop
  
- cite well known problems with closed loop sys-id & potential solutions. van der Kooij.  most work in engineering
  is linear systems which is not appropriate here.  maybe cite some of these
   - bicycle/motorcycle stuff: van lunteren and stassen, eaton, doyle, de
     Lange, my diss
   - There is control id in the aircraft world, but mostly simple linear systems.
   - There is stuff in the automobile world

- justify our choice of assuming a plant model.  related work: Park & Kuo (human standing), Uchida.
  these were done with shooting

- cite shooting (Anderson & Pandy) & direct collocation which is much more efficient for finding open loop optimal controls (Ackermann & van den Bogert)

- shooting has been extended towards closed loop controls (e.g. Wang or Dorn's work) with performance based cost function
  so it would be straightforward to extend this towards (1) collocation, and (2) a tracking cost function to find controllers
  that are human-like

- state the aims of this paper


Methods
-------

- Model system and data collection
  - Show n-link pendulum on cart diagram.  Ton: Is it sufficient to do it on a 2-link system?
    And should this have human-like dimensions?  If so, we're basically replicating Park & Kuo's problem which
    could be solved quite well without these new methods.
  - Describe LQR controller.
  - Closed loop system dynamics.
  - Describe noise inputs (process and measurement).
  - Describe simulation, use same data for all methods below.
- System ID cost function, same for all problems.

- Direct approach
  - TvdB: It would be good if we could leave this out.  Talk about it in Introduction and move past it.
    Alternatively, if we include this, I think it is OK to just do this on data from one instance of the noise and perturbation
    to demonstrate the problem.  Then use the same data for the indirect work.
  - Describe direct approach, cite van der Kooij, guy from McGill, and Ljung.
  - Describe the mathematical formulation
  - Show a plot that shows the error in parameters as a function of the ratio of
    the process and measurement.
  - Say something about speed of computation.

- Indirect Approach: Shooting
  - Same here: I would prefer to talk about this in Introduction (with citations) and conclude there that you don't want to do this.
  - Describe shooting.
  - Cite Tom Uchida's homotopy stuff.
  - What algorithm should I use? Maybe the Python version of the CMAES alg would
    be good to use.
  - The main points here will probably be:
    - How long it takes to find the solution (computation time)?
    - Sensitivity to initial guesses
    - It doesn't matter how much you perturb??

- Indirect Approach: Direct Collocation
  - Should we show the single pendulum id problem that Ton did which came from
    Tom's paper?  Neither.
  - Describe how we setup the problem
    - Cost function (Park & Kuo included joint torque tracking in the cost function - better not do that, torques are
      unreliable, if they can be measured at all.
    - Backward Euler
    - Constraints
    - Free variables
    - Initial guess

- Describe software and implementation
  - SymPy
  - NLP solver: IPOPT

- Describe "experimental" protocol and data collected (should match the aims stated at the end of Introduction)
  - Sensitivity to initial guess
  - Speed of computation - how does it scale with number of nodes and (maybe) number of links. for the same initial guess,
    of course.
  - Do we want to test how robust the estimated gains are with respect to model errors? This would be important if you were to
    interpret results as human gains.  This would not be important if you asked the question what control the model
    requires to make it behave like a human.
  - Make sure to design "experiments" to answer these questions
    - What is the largest number of pendulum links we can get a solution for? I've
      only done a 4 link pendulum (40 unknown gains) from a close guess.  Ton: I suggest to leave this out.
    - Can it find the solution from random gain guesses? How often does it get
      stuck in a local minima?
    - Can it find the solution from initial random gain guesses and setting the
      states equal to zero?
    - Is this sensitive to the process and measurement noise ratio?
    - What is the appropriate size of h to get an accurate-enough solution?
      Do a mesh refinement experiment (only for one condition) run optimizations with the known gains as the
      initial guess and decrease h to show how the gains converge to the known
      gains and h gets smaller.

Results
-------

- Should match exactly the final section of Methods

- I'd like to know if increasing the amount of data increases the likelihood of
  getting the correct answer, as I don't necessarily see that with random
  experiments. But that is anecdotal.  Ton: Not here, if you can't design an experiment to answer this question,
  it's better to report such anecdotal findings in the Discussion.

Discussion
----------

- Computation time.  If we did not present results from shooting, it would be hard to wow the reader
  with how much faster this is and less sensitive to initial guess.  So maybe do shooting after all,
  especially if code already exists.
  
- Sensitivity to initial guess.   Also compare to shooting (if we did that).  Provide general recommendations (if we can)
  for generating an initial guess that works.
  
- The collocation method scales well to long duration movement data, so we can potentially identify controllers
  with many parameters.  For example neural networks.

- Our results show that this approach is computationally feasible and gives accurate results.  We are ready to
  apply this to human control.  Human motion has slightly more complexity and nonlinearity which may affect convergence.
