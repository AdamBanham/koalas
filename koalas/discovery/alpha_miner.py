"""
This module is a implementation of the alpha miner (original).

See the following article for more information about the 
alpha miner process discovery technique:\n
W.M.P. van der Aalst, A.J.M.M. Weijters, and L. Maruster. 
Workflow Mining: Discovering Process Models from Event Logs. 
IEEE Transactions on Knowledge and Data Engineering,
16(9):1128–1142, 2004.
"""
from koalas.simple import EventLog

from typing import Set,Tuple


class AlphaMinerInstance():
    """
    This is a helper for the alpha miner using the same 
    parameters. The alpha miner has the following parameters:

    Parameters
    ----------    
    min_inst:`int=1`(default)\n
    The minimum number of times a relation must be seen to
    be counted as a alpha relation.
    """

    def __init__(self, min_inst:int=1):
        self._min_inst = min_inst

    def mine_footprint_matrix(self, log:EventLog) -> object:
        """
        Mines the footprint matrix of the alpha miner relations
        between process activities.
        """

        return

    def mine_model(self, log:EventLog) -> Tuple[Set,Set,Set]:
        """
        Mines a petri net based on the given event log, using
        the alpha miner discovery technique.

        Returns a Petri net, i.e. a set of places, a set of 
        transitions and a set of flow relations.
        """
        # find the essential elements 
        TL = self.__step_one(log)
        TI = self.__step_two(log)
        TO = self.__step_three(log)
        XL = self.__step_four(log)
        YL = self.__step_five(log, XL)
        # find the petri net components 
        PL = self.__step_six(log, YL)
        FL = self.__step_seven(log, YL, TI, TO)
        return (PL, TL, FL)


    def __step_one(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all process activities seen in the 
        event log.
        """
        return log.seen_activities()

    def __step_two(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all start process activities seen in 
        the event log.
        """
        return log.seen_start_activities()

    def __step_three(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all end process activities seen in 
        the event log.
        """
        return log.seen_end_activities()

    def __step_four(self, log:EventLog) -> Set:
        """
        
        """

        return set() 

    def __step_five(self, log:EventLog, XL:Set) -> Set:
        """
        
        """

        return set() 

    def __step_six(self, log:EventLog, YL:Set) -> Set:
        """
        
        """

        return set()

    def __step_seven(self, log:EventLog, YL:Set, TI:Set, 
        TO:Set) -> Set:
        """
        
        """

        return set()

    