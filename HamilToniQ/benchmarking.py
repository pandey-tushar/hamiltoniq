"""
This Class is defined to give an overall score of the QAOA performance on a quantum hardware
"""

from typing import Callable, List, Any

import random
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path
from scipy.optimize import minimize
from qiskit import QuantumCircuit, Aer
from qiskit.primitives import Sampler, Estimator, BackendSampler
from qiskit.algorithms.minimum_eigensolvers import QAOA
from qiskit.algorithms.optimizers import COBYLA
from functools import partial
import matplotlib.pyplot as plt
import pandas as pd

from utility import Q_to_paulis
from matrices import *

Matrix = Any
Counts = Any
Circuit = Any
Hardware_Backend = Any


class Toniq:
    def __init__(self) -> None:
        pass

    def get_Q_matirx(
        self, dim: int, lower: float = 0.0, upper: float = 10.0
    ):
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
    
    def get_ground_state(self, Q) -> int:
        """
        Find the ground state of a Q matrix
        """
        pass

    def run_QAOA(self, backend, Q: Matrix, n_layers: int, options=None, n_reps: int = 1):
        """
        Run QAOA on a given backend.
        args:
            backend: Qiskit backend or simulator
            Q: Q matrix
            n_layers: the number of layers
            options:
            n_reps: for how many times does QAOA run
        return:

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

    def get_reference(self, Q: Matrix, n_layers: int, n_reps: int = 10000, n_points: int = 1000) -> list:
        """
        Calculate the scoring function.
        The scoring function is represented by uniform sampling.
        args:
            Q:
            n_layers:
            n_reps: number of repetation by which the QAOA run on a simulator
            n_points: number of points in sampling percedure
        """
        pass

    def build_scoring_function(self, data: list) -> Callable:
        """
        Calculate the scoring function according to the sampling result.
        """
        pass

    def run(self, backend, n_layers):
        pass