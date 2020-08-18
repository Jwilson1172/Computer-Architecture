import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from cpu import CPU


class CpuMaths(object):
    """wrapper function for various maths from numpy, pandas, statistics"""
    def __init__(self, CPU=None):
        self.value = None
        self.cpu = CPU
        return

    def fnd_mean(self, ):
        return np.mean(a)

    def stddev(self, a):
        return np.std(a)


if __name__ == '__main__':
    cpu = CPU()
    m = CpuMaths()
    a = np.zeros((2, 512 * 512), dtype=np.float32)
    a[0, :] = 1.0
    a[1, :] = 0.1
    print(np.mean(a))
