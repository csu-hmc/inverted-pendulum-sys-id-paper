#!/usr/bin/env python

from scipy.linalg import lstsq


class ControllerIdentifier(object):

    def __init__(self, input_traj, state_traj, copy=True,
                 check_finite=False):
        """This class is able to identify a state feedback controller for a
        system that tracks the zero vector given estimates of state
        trajectories and the plant input trajectories.

        Parameters
        ==========
        input_traj : array_like, shape(N, m)
            The N time steps of the m inputs.
        state_traj : array_like, shape(N, n)
            The N time steps of the n states.
        copy : boolean, optional, default=True
            If true a copy of the provided data will be made for increased
            speed of computation at the sacrafice of memory.
        check_finite : boolean, optional, default=False
            If false the data will not be checked for nan's and some gain in
            computation speed may be gained. See scipy.linalg.lstsq.

        """

        self.copy = copy
        self.check_finite = check_finite

        if self.copy:
            self.input_traj = input_traj.copy()
            self.state_traj = state_traj.copy()
        else:
            self.input_traj = input_traj
            self.state_traj = state_traj

    def identify(self):
        """Returns the least square estimates of the state feedback
        controller gains.

        """

        res = lstsq(-self.state_traj, self.input_traj,
                    overwrite_a=self.copy, overwrite_b=self.copy,
                    check_finite=self.check_finite)

        self.solution = res[0]
        self.residuals = res[1]
        self.rank_of_a = res[2]
        self.singular_values = res[3]

        return res[0].T
