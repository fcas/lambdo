__author__="Alexandr Savinov"

import json

from lambdo.utils import *
from lambdo.resolve import *
from lambdo.transform import *

from lambdo.Workflow import *
from lambdo.Table import *
from lambdo.Column import *

import logging
log = logging.getLogger('lambdo.topology')


class Topology:
    """
    The class represents a topology.
    Topology is a graph of operations on data where one operation is either a table population or column evaluation.
    """

    workflowNo = 0

    def __init__(self, workflow):

        self.workflow = workflow

        #
        # Create table objects
        #
        self.layers = self._build_layers()

    def _build_layers(self):
        """Build a graph of table population and column evaluation operations according to their dependencies"""

        # PRINCIPLE: Topology consists of operations which are performed on definitions (not specified columns/tables) which can produce multiple objects.
        # PRINCIPLES: Dependency is a data object (we need data to perform some operation), but this data object is generated by some operation (definition)

        # Topology to be built is a list of layers in the order of execution of their operations. First layer does not have dependencies.
        layers = []

        # Create a collection of all operations defined in the workflow
        all = []
        for t in self.workflow.tables:
            table_deps = t.get_all_own_dependencies()
            all.extend(table_deps)

        # Empty collection of already processed elements (they can be simultaniously removed from all)
        done = []

        while True:
            layer = []

            # We will build this new layer from the available (not added to previous layers) operations
            for elem in all:

                if elem in done:
                    continue

                #
                # Find dependencies of this operation
                #
                if isinstance(elem, (Table, Column)):
                    deps = elem.get_dependencies()  # Get all element definitions this element depends upon
                elif isinstance(elem, (tuple, list)) and isinstance(elem[0], Table):
                    deps = [elem[0]]  # Filter depends on its table
                    deps.extend(elem[0].columns)  # Filter is applied only after all columns have been evaluated
                else:
                    pass  # Error: unknown operation

                #
                # If all dependencies have been executed then add this element to the current layer
                #
                if set(deps) <= set(done):
                    layer.append(elem)

            if len(layer) == 0:
                break

            layers.append(layer)
            done.extend(layer)

        return layers