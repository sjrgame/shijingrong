# import logging
# import sys
# import os
#
#
# points = [{'x': 2, 'y': 3},{'x': 4, 'y': 1},{'x': 6, 'y': 5}]
# points.sort(key=lambda i: i['y'])
# print(points)
#



import matplotlib.pyplot as plt#约定俗成的写法plt
#首先定义两个函数（正弦&余弦）
import numpy as np

X=np.linspace(-np.pi,np.pi,256,endpoint=True)#-π to+π的256个值
C,S=np.cos(X),np.sin(X)
plt.plot(X,C)
plt.plot(X,S)

plt.show()