import epics

class PvChannel:
    def __init__(self) -> None:
        self.channelDict = {}
        self.name = ""

    def push(self, variable_name, pv_name):
        self.name = variable_name
        return self.channelDict.setdefault(variable_name, epics.PV(pv_name))

    def remove(self, variable_name):
        if (self.exist(variable_name)):
            self.channelDict.pop(variable_name)

    def exist(self, variable_name):
        return variable_name in self.channelDict

    def get(self, variable_name):
        if (self.exist(variable_name)):
            return self.channelDict[variable_name].get()
        else:
            print('%s: PV %s does not exist! Please check out!' % (__file__, variable_name))

    def put(self, variable_name, value):
        if (self.exist(variable_name)):
            self.channelDict[variable_name].put(value)
        else:
            print('%s: PV %s does not exist! Please check out!' % (__file__, variable_name))