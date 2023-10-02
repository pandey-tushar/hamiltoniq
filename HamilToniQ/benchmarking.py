"""
This Class is defined to give an overall score of the QAOA performance on a quantum hardware
"""

from typing import Callable, List, Any

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import interpolate
from pathlib import Path
from scipy.optimize import minimize
from qiskit import QuantumCircuit, Aer
from qiskit.primitives import Sampler, Estimator, BackendSampler
from qiskit.algorithms.minimum_eigensolvers import QAOA
from qiskit.algorithms.optimizers import COBYLA
from functools import partial

from utility import Q_to_paulis, all_quantum_states
from matrices import *

Matrix = Any
Counts = Any
Circuit = Any
Hardware_Backend = Any


class Toniq:
    def __init__(self) -> None:
        self.backend_list = []
        self.n_reps = 1000
        pass

    def get_Q_matirx(self, dim: int, lower: float = 0.0, upper: float = 10.0):
        """
        Generate a random symmetric matrix with a give dimension.
        args:
            dim: the dimension of Q matrix
            lower: the lower boundary of each random element
            upper: the upper boundary of each random element
            print_hardness: print out the hardness of generated Q matrix
        return:
            mat: a symmetric matrix
        """
        mat = np.array([random.uniform(lower, upper) for _ in range(dim**2)])
        mat = mat.reshape(dim, dim)
        mat = np.triu(mat)
        mat += mat.T - np.diag(mat.diagonal())

        # print the hardness
        normalized_covariance = [
            mat[i, j] / np.sqrt(mat[i, i] * mat[j, j])
            for i in range(len(mat))
            for j in range(i + 1)
        ]
        print(f"the hardness is {np.var(normalized_covariance)}")

        return mat

    def get_ground_state(self, Q) -> dict:
        """
        Find the ground state information of a Q matrix
        args:
            Q: the Q matrix
        return:
            ground: a dict including the ground state in binary form (string), decimal form (int)
            and the corresponding energy (float).
        """
        n_qubits = np.shape(Q)[0]
        energy_list = []
        for state in all_quantum_states(n_qubits):
            energy_list.append(np.dot(state, np.dot(Q, state)))
        dec_min = np.argmin(energy_list)  # ground state in binary form
        ground = {
            "bin_state": f"{bin(dec_min)[2:]:0>{n_qubits}}",
            "dec_state": dec_min,
            "energy": energy_list[dec_min],
        }
        return ground

    def get_results(
        self, backend, Q: Matrix, n_layers: int, options=None, n_reps: int = 1
    ):
        """
        Run QAOA on a given backend.
        args:
            backend: Qiskit backend or simulator
            Q: Q matrix
            n_layers: the number of layers
            options:
            n_reps: for how many times does QAOA run
        return:
            a list of MinimumEigensolverResult
        """
        sampler = BackendSampler(backend=backend, options=options)
        optimizer = COBYLA(maxiter=self.maxiter)
        self.param_list = []
        self.energy_list = []
        qaoa = QAOA(
            sampler=sampler,
            optimizer=optimizer,
            reps=self.n_layers,
        )
        op, _ = Q_to_paulis(self.Q)
        return [qaoa.compute_minimum_eigenvalue(op) for _ in range(n_reps)]

    def get_reference(
        self, Q: Matrix, n_layers: int, n_reps: int = 10000, n_points: int = 1000
    ) -> list:
        """
        Calculate the scoring function.
        The scoring function is represented by uniform sampling.

        args:
            Q:
            n_layers:
            n_reps: number of repetation by which the QAOA run on a simulator
            n_points: number of points in sampling percedure
        return:
            scoring_curve_sampling: A list of uniform sampling of the scoring curve. It has 201 elements.
            The corresponding x-axis is build using `np.linspace(0, 1, 201)`.
        """
        ground_state_info = self.get_ground_state(Q)
        dec_ground_state = ground_state_info["dec_state"]
        backend = Aer.get_backend("aer_simulator")

        # get the distribution of accuracy
        results = self.get_results(backend, Q, n_layers, n_reps=n_points)
        accuracy_list = []
        for i in results:
            try:
                accuracy_list.append(i.eigenstate[dec_ground_state])
            except:
                accuracy_list.append(0)
        n_boxes = 200
        hist_x = np.linspace(0, 1, n_boxes + 1)
        hist_y, _ = np.histogram(accuracy_list, bins=hist_x)
        hist_y = np.divide(hist_y, accuracy_list.size)

        # build the scoring function
        cumulative_score = np.cumsum(hist_y)
        scoring_curve_sampling = np.append(np.zeros(1), cumulative_score)
        return scoring_curve_sampling

    def build_scoring_function(
        self, data: list | pd.Series, n_boxes: int = 100
    ) -> Callable:
        """
        Calculate the scoring function according to the sampling result.
        The default number of boxes is 200. We do recommand not to change it throught the benchmarking

        args:
            data: the accuracy data collected from a simulator. We always use data with 10,000 elements.
            n_boxed: number of boxes when building histogram.
        return:
            f: a function that can used to score an accuracy.
        """
        n_boxes = 200
        hist_x = np.linspace(0, 1, n_boxes + 1)
        hist_y, _ = np.histogram(data, bins=hist_x)
        hist_y = np.divide(hist_y, np.shape(data)[0])
        cumulative_score = np.cumsum(hist_y)
        f = interpolate.interp1d(
            hist_x, np.append([0], cumulative_score), kind="linear"
        )
        return f

    def run(self, backend, n_layers_list: list):
        for n_layer in n_layers_list:
            results_list = self.run_QAOA(backend, dim_4)
            for result in results_list:
                pass

    def show_ladder_diagram(self, dim: int, n_layers: int, backends=None):
        f"""
        Show the benchmarking results obtained by us.
        {self.backend_list}
        """
        if backends in self.backend_list:
            pass
        pass