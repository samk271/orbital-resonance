from GUI import Canvas


class StateManger:
    """
    keeps track of any updates the user makes to any planets so that undo and redo can be applied
    """

    MAX_STATES = 1000

    def __init__(self):
        """
        creates the state manager object
        """

        self.undo_actions = []
        self.redo_actions = []
        self.canvas: Canvas = None  # set by canvas

    def add_state(self, functions: dict):
        """
        adds an undo action to the state manager. additionally clears the redo action list

        :param functions: the functions to perform when updating the state in the form:
            {"undo": (def, *args), "redo": (def, *args)}
        """

        # handles when max states has not been reached
        self.canvas.unsaved = True
        if len(self.undo_actions) < StateManger.MAX_STATES:
            self.undo_actions.append(functions)
            self.redo_actions.clear()

        # handles when max states has been reached
        else:
            self.undo_actions.pop(0)
            self.add_state(functions)

    def undo(self):
        """
        performs an undo action and removes it from the undo list. additionally adds a redo action
        """

        if len(self.undo_actions) != 0:
            action = self.undo_actions.pop()
            action["undo"][0](*action["undo"][1:])
            self.redo_actions.append(action)

    def redo(self):
        """
        performs a redo action and removes it from the redo list. additionally adds an undo action
        """

        if len(self.redo_actions) != 0:
            action = self.redo_actions.pop()
            action["redo"][0](*action["redo"][1:])
            self.undo_actions.append(action)
