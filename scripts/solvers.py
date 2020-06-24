"""
Solvers

References:

"""

# Author: Shota Horii <sh.sinker@gmail.com>

from abc import ABC, abstractmethod
import math
import numpy as np

from scripts.util import supremum_eigen
from scripts.weight_initialisation import initialise_random, initialise_zero
from scripts.hyperparameter_optimisation import auto_learning_rate_se
from scripts.loss_functions import SquareError, L2Regularization, CrossEntropy
from scripts.activation_functions import Sigmoid, Softmax, Identity

class Solver(ABC):

    @abstractmethod
    def solve(self):
        pass


class PInv(Solver):
    """
    Analytical solution to the normal equation using Moore-Penrose pseudoinverse.

    Parameters
    ----------
    alpha: float >= 0
        l2 reguralisation parameter
    """

    def __init__(self, alpha=0):
        self.alpha = alpha

    def solve(self, X, y):
        """
        Solve Linear regression and Ridge regression.

        Parameters
        ----------
        X: np.ndarray (n, d) 
            predictor variables matrix
            n: number of samples
            d: number of features
        
        y: np.ndarray (n,)
            target variables
            n: number of samples
        """
        d = X.shape[1]
        return np.dot( np.dot(np.linalg.pinv( np.dot(X.T, X) + self.alpha * np.eye(d) ), X.T), y)


class GradientDescent(Solver):
    """
    Gradient Descent

    Parameters
    ----------
    alpha: float >= 0
        l2 reguralisation parameter
    """

    def __init__(self, activation, loss, alpha=0, max_iterations=1000, tol=1e-4, learning_rate=None):
        self.max_iterations = max_iterations
        self.tol = tol
        self.learning_rate = learning_rate

        self.activation = activation
        self.loss = loss
        self.l2 = L2Regularization(alpha)

    def solve(self, X, y):
        """
        Solve Linear regression and Ridge regression.

        Parameters
        ----------
        X: np.ndarray (n, d) 
            predictor variables matrix
            n: number of samples
            d: number of features
        
        y: np.ndarray (n,)
            target variables
            n: number of samples
        """

        # if learning rate is not given, set automatically
        lr = self.learning_rate if self.learning_rate else auto_learning_rate_se(X)
        # initialise the weights as zero
        if y.ndim > 1: # multi class classification
            w = initialise_zero(X.shape[1], y.shape[1])
        else:
            w = initialise_zero(X.shape[1])
        
        for _ in range(self.max_iterations):
            y_pred = self.activation(np.dot(X, w))
            grad_w = np.dot(X.T, self.loss.gradient(y, y_pred)) + self.l2.gradient(w)
            w_new = w - lr * grad_w

            if (np.abs(w_new - w) < self.tol).all():
                print('Converged.')
                return w_new
            w = w_new
        
        print('Not converged.')
        return w


class LeastSquareGD(GradientDescent):
    def __init__(self, alpha=0, max_iterations=1000, tol=1e-4, learning_rate=None):
        super().__init__(
            activation = Identity(), 
            loss = SquareError(), 
            alpha=alpha, 
            max_iterations=max_iterations, 
            tol=tol,
            learning_rate=learning_rate)

class CrossEntropyGD(GradientDescent):
    def __init__(self, alpha=0, max_iterations=1000, tol=1e-4, learning_rate=None):
        super().__init__(
            activation = Sigmoid(), 
            loss = CrossEntropy(), 
            alpha=alpha, 
            max_iterations=max_iterations, 
            tol=tol,
            learning_rate=learning_rate)

class CrossEntropyMultiGD(GradientDescent):
    def __init__(self, alpha=0, max_iterations=1000, tol=1e-4, learning_rate=None):
        super().__init__(
            activation = Softmax(), 
            loss = CrossEntropy(), 
            alpha=alpha, 
            max_iterations=max_iterations, 
            tol=tol,
            learning_rate=learning_rate)
    

class LassoISTA(Solver):
    """
    Lasso solver with ISTA (Iterative Shrinkage Thresholding Algorithm). 
    Ref (in JP): https://qiita.com/fujiisoup/items/f2fe3b508763b0cc6832

    Parameters
    ----------
    alpha: float > 0
        l1 reguralisation parameter
    
    max_iterations: int > 0
        max number of iterations
    
    tol: float >= 0
        conversion criterion. if delta of w is smaller than tol, 
        algorighm considers it's converged.
    """
    
    def __init__(self, alpha=0, max_iterations=1000, tol=1e-4):
        self.alpha = alpha
        self.max_iterations = max_iterations
        self.tol = tol

    def solve(self, X, y):
        """
        Solve Lasso.
        argmin_w ( 1/2 (y - Xw)^2 + alpha |w| )

        As this cannot be solved analytically, we solve this in iterative way. 
        In each step t, (call w of t-th step as w_t here),  we approximate
        L(w) = 1/2 (y-Xw)^2 with an another function G(w; w_t)
        so that we can solve argmin_w ( G(w; w_t) + alpha |w| ) in each step. 

        G(w; w_t) = L(w_t) + dL(w_t)/dw (w - w_t) + rho/2 |w - w_t|^2
                = rho/2 |(w_t - 1/rho dL(w_t)/dw) - w|^2 + const 
        where rho is the maximum eigen value of the square matrix X.T @ X

        Note that, always L(w) <= G(w; w_t) and L(w_t) == G(w_t; w_t)
        Hence, moving towards the direction of minimising G(w; w_t)
        is guaranteed to be the direction of minimising L(w) as well. 

        With G(w; w_t) above, we can solve argmin_w ( G(w; w_t) + alpha |w| )
        using the soft threshold function. 
        So each step, we can move on to optimise G(w; w_t), which is also 
        moving towards minimum of ( 1/2 (y - Xw)^2 + alpha |w| ).

        Parameters
        ----------
        X: np.ndarray (n, d) 
            predictor variables matrix
            n: number of samples
            d: number of features
        
        y: np.ndarray (n,)
            target variables
            n: number of samples
        """
        n_samples, n_features = X.shape
        
        # initialise w_t (w of t-th step)
        w_t = initialise_zero(n_features)
        # rho is the maximum eigen value of the square matrix X.T @ X
        rho = supremum_eigen(X.T @ X)
        # threshold of soft threshold function. weighted with num of samples.
        threshold = n_samples * self.alpha / rho

        for _ in range(self.max_iterations):
            
            # in each step t, with w_t, solve argmin_w (G(w; w_t) + alpha |w|)
            # G(w; w_t) = rho/2 |(w_t - 1/rho dL(w_t)/dw) - w|^2 + const 
            # L(w) = 1/2 (y - Xw)^2  =>  dL/dw = -X^T (y - Xw)
            dl_dw = -X.T @ (y - X @ w_t) 
            w_new = self._soft_threashold(w_t - dl_dw/rho, threshold)

            if (np.abs(w_new - w_t) < self.tol).all():
                print('Converged.')
                return w_new
            w_t = w_new
        
        print('Not converged.')
        return w_t

    def _soft_threashold(self, lw, threshold):
        """
        Soft threshold function

        Parameters
        ----------
        lw: np.ndarray (d,)
            d: number of features
            Array of values of w, which minimise L(w) without alpha*|w| factor

        threshold: float > 0
            the threshold of the soft threshold function

        Returns
        -------
        np.ndarray (d,)    
            if lw > threshold, return lw - threshold
            if lw < -threshold, return lw + threshold
            if -threshold <= lw <= threshold, reutrn 0
        """
        return np.sign(lw) * np.maximum(np.abs(lw) - threshold, 0.0)

