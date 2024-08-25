"""
Module for storing meta classes and functions related to process discovery.
"""

from abc import ABC, abstractmethod

class DiscoveryTechnique(ABC):
    """
    Metaclass for process discovery techniques.

    This metaclass enforces the implementation of the `discover` method 
    in any subclass, which when called should invoke the discovery 
    procedure for the technique.
    """

    @abstractmethod
    def discover(self, log) -> object:
        """
        Abstract method for calling the procedure to discovery a graph or 
        model for the discovery technique.

        Subclasses must implement this method.
        """
        pass