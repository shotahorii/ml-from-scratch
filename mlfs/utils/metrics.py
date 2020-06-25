"""
Metrics

References:

"""

# Author: Shota Horii <sh.sinker@gmail.com>

import math
import numpy as np

#############################
# Metrics for data impurity #
#############################

def entropy(y):
    """ 
    Computes entropy 
    
    Parameters
    ----------
    y: np.ndarray 
        Target variable of classification problems.
        This can be a 1d array indicating 0/1 for a binary classification,
        Or a multi-dimensional array, indicating a one-hot encoded 
        target variable for a multi-class classification. 

        When 1d array:
            Num of elements is the num of samples. each value is 0 or 1.

        When multi-dimensional array
            Num of rows (y.shape[0]) is the num of samples.
            Num of columns (y.shape[1]) is the num of classes.
            Each value is either 0 or 1.
            Sum of values in a single row is always 1.

    Returns
    -------
    float
        entropy
    """

    n_total = len(y)

    if n_total==0:
        raise ValueError('input must not be empty')
    
    if y.ndim==1:
        n_class_1 = y.sum()
        n_each_class = np.array([n_class_1, n_total - n_class_1])
    else:
        n_each_class = y.sum(axis=0)

    p_each_class = n_each_class/n_total    
    i_each_class = [p*np.log(p) for p in p_each_class if p != 0.0]
    return -np.sum(i_each_class)


def gini_impurity(y):
    """ 
    Computes gini impurity
    
    Parameters
    ----------
    y: np.ndarray 
        Target variable of classification problems.
        This can be a 1d array indicating 0/1 for a binary classification,
        Or a multi-dimensional array, indicating a one-hot encoded 
        target variable for a multi-class classification. 

        When 1d array:
            Num of elements is the num of samples. each value is 0 or 1.

        When multi-dimensional array
            Num of rows (y.shape[0]) is the num of samples.
            Num of columns (y.shape[1]) is the num of classes.
            Each value is either 0 or 1.
            Sum of values in a single row is always 1.

    Returns
    -------
    float
        gini impurity
    """

    n_total = len(y)

    if n_total==0:
        raise ValueError('input must not be empty')
    
    if y.ndim==1:
        n_class_1 = y.sum()
        n_each_class = np.array([n_class_1, n_total - n_class_1])
    else:
        n_each_class = y.sum(axis=0)

    p_each_class = n_each_class/n_total
    return 1 - np.sum(p_each_class**2)


def classification_error(y):
    """ 
    Computes classification error
    
    Parameters
    ----------
    y: np.ndarray 
        Target variable of classification problems.
        This can be a 1d array indicating 0/1 for a binary classification,
        Or a multi-dimensional array, indicating a one-hot encoded 
        target variable for a multi-class classification. 

        When 1d array:
            Num of elements is the num of samples. each value is 0 or 1.

        When multi-dimensional array
            Num of rows (y.shape[0]) is the num of samples.
            Num of columns (y.shape[1]) is the num of classes.
            Each value is either 0 or 1.
            Sum of values in a single row is always 1.

    Returns
    -------
    float
        classification error 
    """

    n_total = len(y)

    if n_total==0:
        raise ValueError('input must not be empty')
    
    if y.ndim==1:
        n_class_1 = y.sum()
        n_max_class = max(n_class_1, n_total - n_class_1)
    else:
        n_max_class = np.max(y.sum(axis=0))

    return 1 - n_max_class/n_total


def variance(y):
    """ 
    Computes variance of the given list of real numbers.
    
    Parameters
    ----------
    y: np.ndarray (1d array)
        a 1d array of real numbers.

    Returns
    -------
    float
        variance
    """
    mu = np.mean(y)
    var = np.mean(np.power(y-mu,2))
    return var


def mean_deviation(y):
    """ 
    Computes mean deviation of the given list of real numbers.
    
    Parameters
    ----------
    y: np.ndarray (1d array)
        a 1d array of real numbers.

    Returns
    -------
    float
        mean deviation
    """
    mu = np.mean(y)
    md = np.mean(np.abs(y-mu))
    return md

##########################
# Metrics for regression #
##########################

def mse(y, y_pred):
    """ 
    Computes mean squared error.
    
    Parameters
    ----------
    y: np.ndarray (1d array)
        Target variable of regression problems.
        Number of elements is the number of data samples. 
    
    y_pred: np.ndarray (1d array)
        Predicted values for the given target variable. 
        Number of elements is the number of data samples. 

    Returns
    -------
    float
        mean squared error 
    """
    return np.mean(np.power(y-y_pred,2))

def rmse(y, y_pred):
    """ 
    Computes root mean squared error.
    
    Parameters
    ----------
    y: np.ndarray (1d array)
        Target variable of regression problems.
        Number of elements is the number of data samples. 
    
    y_pred: np.ndarray (1d array)
        Predicted values for the given target variable. 
        Number of elements is the number of data samples. 

    Returns
    -------
    float
        root mean squared error 
    """
    return np.sqrt(mse(y, y_pred))



def mae(y, y_pred):
    """ 
    Computes mean absolute error.
    
    Parameters
    ----------
    y: np.ndarray (1d array)
        Target variable of regression problems.
        Number of elements is the number of data samples. 
    
    y_pred: np.ndarray (1d array)
        Predicted values for the given target variable. 
        Number of elements is the number of data samples. 

    Returns
    -------
    float
        mean absolute error 
    """
    return np.mean(np.abs(y-y_pred))

def rss(y, y_pred):
    """ residual sum of squares """
    return np.sum(np.power(y-y_pred,2))

def r_squqred(y, y_pred):
    denom = np.sum(np.power(y-y.mean(),2))
    return 1 - rss(y, y_pred)/denom

##############################
# Metrics for classification #
##############################

def accuracy(y, y_pred):
    num_errors = np.sum(np.abs(y - y_pred))/2
    return 1 - num_errors/len(y)

def false_positive(y, y_pred):
    pass

def true_positive(y, y_pred):
    pass

def false_negative(y, y_pred):
    pass

def true_negative(y, y_pred):
    pass