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
        self.unsaved = False

    def add_state(self, functions: dict, modify: bool = False):
        """
        adds an undo action to the state manager. additionally clears the redo action list

        :param functions: the functions to perform when updating the state in the form:
            {"undo": [(def, (*args), {**kwargs})], "redo": [(def, (*args), {**kwargs})]}
            ** note: kwargs do not need to be passed but args are needed so if no args are to be passed an empty tuple
                should be given like so: (def, (, ))
        :param modify: determines if the functions should be added to the previous state rather than adding a new state
        """

        # handles when max states has been reached
        self.unsaved = True
        if len(self.undo_actions) >= StateManger.MAX_STATES:
            self.undo_actions.pop(0)
            self.add_state(functions)
            return

        # handles modifying previous state
        if modify:
            self.undo_actions[-1]["undo"].extend(functions["undo"])
            self.undo_actions[-1]["redo"].extend(functions["redo"])

        # handles creating new state
        else:
            self.undo_actions.append(functions)
            self.redo_actions.clear()

    def undo(self):
        """
        performs an undo action and removes it from the undo list. additionally adds a redo action
        """

        # adds action to redo list
        if len(self.undo_actions) != 0:
            action = self.undo_actions.pop()
            self.redo_actions.append(action)

            # ensures remaining actions are performed if one fails
            for func in action["undo"]:
                try:
                    func[0](*(func[1]), **func[2]) if len(func) == 3 else func[0](*(func[1]))
                except:
                    pass

    def redo(self):
        """
        performs a redo action and removes it from the redo list. additionally adds an undo action
        """

        # adds action to undo list
        if len(self.redo_actions) != 0:
            action = self.redo_actions.pop()
            self.undo_actions.append(action)

            # ensures remaining actions are performed if one fails
            for func in action["redo"]:
                try:
                    func[0](*(func[1]), **func[2]) if len(func) == 3 else func[0](*(func[1]))
                except:
                    pass
