class Coffee:
    def __init__(self,name, description,id=None):
        self.id = id
        self.name = name
        self.description = description

    def __str__(self):
        return "{}".format(self.id)


class Machine:
    def __init__(self, state, type, id = None, name=None):
        self.id = id
        self.name = name
        self.state = state
        self.type = type


class Preparation:
    def __init__(self, coffee, creation_date, last_update, machine, id, next_time, saved, state):
        self.coffee = coffee
        self.creation_date = creation_date
        self.last_update = last_update
        self.machine = machine
        self.id = id
        self.next_time = next_time
        self.saved = saved
        self.state = state


class PreparationPlanned(Preparation):

    def __init__(self, coffee, creation_date, last_update, machine, name, id, next_time, saved, state, days_of_week, hours, last_time):
        super().__init__(coffee, creation_date, last_update, machine, name, id, next_time, saved, state)
        self.days_of_week = days_of_week
        self.hours = hours
        self.last_time = last_time