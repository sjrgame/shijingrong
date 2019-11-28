#!/usr/bin/python
from time import clock

l = [(x, x) for x in xrange(100)]
print(l)
d = dict(l)
print(d)
t0 = clock()
# 1
for i in d:
    n = d[i]
t1 = clock()
# 2
for k, v in d.items():
    n = v
t2 = clock()
# 3
for k, v in d.iteritems():
    n = v
    print(k, v)

t3 = clock()
# 4
for k, v in zip(d.iterkeys(), d.itervalues()):
    n = v

t4 = clock()

print(t1 - t0)
print(t2 - t1)
print(t3 - t2)
print(t4 - t3)
