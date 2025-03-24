class StateManger:
    """
    keeps track of any updates the user makes to any planets so that undo and redo can be applied
    """

    def __init__(self):
        """
        creates the state manager object
        """

        self.undo_actions = []
        self.redo_actions = []

    def add_undo(self, function):
        """
        adds an undo action to the state manager

        :param function: the function to perform when the undo function is performed
        """

        self.undo_actions.append(function)

    def add_redo(self, function):
        """
        adds a redo action to the state manager

        :param function: the function to perform when the redo function is performed
        """

        self.redo_actions.append(function)

    def undo(self):
        """
        performs an undo action and removes it from the undo list. additionally adds a redo action
        """

        self.add_redo(self.undo_actions.pop()())

    def redo(self):
        """
        performs a redo action and removes it from the redo list
        """

        self.redo_actions.pop()()
