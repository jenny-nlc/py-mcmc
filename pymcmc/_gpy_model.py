"""
A generic wrapper for a GPy model.

Author:
    Ilias Bilionis
"""

from . import Model
from . import assign_priors_to_gpy_model
import numpy as np


__all__ = ['GPyModel']


class GPyModel(Model):

    """
    A generic wrapper for GPy model.

    :param model:       A GPy model.
    :type model:        :class:`GPy.core.Model`
    :param name:        A name for the model.
    :type name:         str
    :param compute_grad:    Compute gradients of the log probability or not.
    :type compute_grad:     bool
    :param assign_priors:   If ``True`` then uninformative priors are assigned
                            to the underlying GPyModel.
    :type assign_priors:    bool
    """

    def __init__(self, model, name='GPy model wrapper', compute_grad=True,
                 assign_priors=True):
        """
        Initialize the object.
        """
        if assign_priors:
            assign_priors_to_gpy_model(model)
        self.model = model
        super(GPyModel, self).__init__(name=name)
        self._compute_grad = compute_grad
        self._eval_state()

    def _eval_state(self):
        """
        Evaluates the state of the model in order to avoid redundant calculations.
        """
        self._state = {}
        self._state['log_likelihood'] = self.model.log_likelihood()
        self._state['log_prior'] = self.model.log_prior()
        if self._compute_grad:
            g = self.model._log_likelihood_gradients()
            self._state['grad_log_likelihood'] = self.model._transform_gradients(g)
            g = self.model._log_prior_gradients()
            if isinstance(g, float):
                g = np.array([g] * self.num_params)
            self._state['grad_log_prior'] = self.model._transform_gradients(g)
        self._state['params'] = self.model.optimizer_array.copy()

    def __getstate__(self):
        return self._state

    def __setstate__(self, state):
        self._state = state

    @property
    def log_likelihood(self):
        return self._state['log_likelihood']

    @property
    def log_prior(self):
        return self._state['log_prior']

    @property
    def num_params(self):
        return self.model.num_params_transformed()

    @property
    def params(self):
        return self._state['params']

    @params.setter
    def params(self, value):
        self.model.optimizer_array = value
        self._eval_state()

    @property
    def param_names(self):
        return self.model._get_param_names()

    @property
    def grad_log_likelihood(self):
        return self._state['grad_log_likelihood']

    @property
    def grad_log_prior(self):
        return self._state['grad_log_prior']
