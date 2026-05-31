from __future__ import annotations

from command.gmat_command import GmatCommand
from gmatpyplus import gmat
from gmatpyplus.utils import *

# class PropagateMulti(Propagate):
#     # TODO: consider making this a nested/inner class of Propagate, so would call Propagate.Multi()
#     """
#     Note: this command does not exist in standard GMAT. It is here to reduce ambiguity when propagating multiple
#      spacecraft. This class can only be used to propagate multiple spacecraft - to propagate a single spacecraft, use
#       Propagate (which only suports a single spacecraft).
#
#     """
#
#     def __init__(self, name: str = None, prop: gp.PropSetup = None, sat: gp.Spacecraft = None,
#                  stop_cond: Propagate.StopCondition = None, synchronized: bool = False):
#         if not name:  # make sure the new Propagate has a unique name
#             num_propagates: int = len(gmat.GetCommands('Propagate'))
#             name = f'PropagateMulti{num_propagates + 1}'
#
#         super().__init__(name, prop, sat, stop_cond, synchronized)
