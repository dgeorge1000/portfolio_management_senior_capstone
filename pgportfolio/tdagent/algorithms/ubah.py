from ..tdagent import TDAgent
import numpy as np

class UBAH(TDAgent):

    def __init__(self, b = None):
        super(UBAH, self).__init__()
        self.b = b

    def decide_by_history(self, x, last_b):
        '''return new portfolio vector
        :param x: input matrix
        :param last_b: last portfolio weight vector
        '''
        #print(x, last_b, self.b)
        if self.b is None:
            self.b = np.ones(len(last_b))/len(last_b)
        else:
            self.b = last_b
        return self.b
