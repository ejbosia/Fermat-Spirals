'''
FillPattern
This is a super class for all fill patterns. These objects must provide a "get_path" function
'''

import abc

class FillPattern:

    @abc.abstractmethod
    def get_path(self):
        pass
