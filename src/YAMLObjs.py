class YamlObj:
    def __init__(self, parameters_dict):
        self.__dict__ = parameters_dict

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.__dict__ > other.__dict__

    def __lt__(self, other):
        return self.__dict__ < other.__dict__


class Task(YamlObj):

    def __gt__(self, other):
        return self.__dict__['priority'] > other.__dict__['priority'] \
            if self.__dict__['priority'] != other.__dict__['priority'] \
            else self.__dict__['name'] > other.__dict__['name']

    def __lt__(self, other):
        return self.__dict__['priority'] < other.__dict__['priority'] \
            if self.__dict__['priority'] != other.__dict__['priority'] \
            else self.__dict__['name'] < other.__dict__['name']

    def execute_task(self, cu):
        f = getattr(cu, self.__dict__['name'])
        f(self) if 'string_for_find' in self.__dict__ else f()
