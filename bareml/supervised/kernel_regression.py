"""
Kernel Regression

Author: Shota Horii <sh.sinker@gmail.com>

References:
"""


import math
import numpy as np

from bareml import Regressor
from bareml.utils.manipulators import StandardScaler
from bareml.utils.solvers import LeastSquareGD
from bareml.utils.kernels import LinearKernel, PolynomialKernel, RBFKernel, SigmoidKernel


class KernelRegression(Regressor):

    def __init__(self, kernel='rbf', kernel_params={}, solver='pinv', alpha=0, max_iterations=1000, tol=1e-4, learning_rate=None):
        self.solver = solver
        self.alpha = alpha
        self.max_iterations = max_iterations
        self.tol = tol
        self.learning_rate = learning_rate

        self.scaler = StandardScaler()

        self.X = None
        self.w = None

        if kernel == 'rbf':
            self.kernel = RBFKernel(**kernel_params)
        elif kernel == 'linear':
            self.kernel = LinearKernel(**kernel_params)
        elif kernel == 'polynomial':
            self.kernel = PolynomialKernel(**kernel_params)
        elif kernel == 'sigmoid':
            self.kernel = SigmoidKernel(**kernel_params)
        else:
            raise ValueError('Invalid Kernel.')

    def _fit(self, X, y):

        X = self.scaler.fit(X).transform(X)
        self.X = X

        N = X.shape[0]
        K = np.array([[self.kernel(X[i],X[j]) for i in range(N)] for j in range(N)])

        if self.solver == 'pinv':
            self.w = np.linalg.pinv(K + self.alpha * np.eye(N)) @ y
        elif self.solver == 'gradient_descent':
            gd = LeastSquareGD(self.alpha, self.max_iterations, self.tol, self.learning_rate)
            self.w = gd.solve(K, y, has_intercept=False)

        return self

    def _predict(self, X):

        X = self.scaler.transform(X)
        
        N = self.X.shape[0]
        M = X.shape[0]
        K = np.array([[self.kernel(X[i],self.X[j]) for i in range(M)] for j in range(N)])

        return np.dot(self.w, K.T)


