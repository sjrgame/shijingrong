# -*- coding: utf-8 -*-

def cmpc(s):
    n = s.find('%')
    if (n >= 0):
        c = s[n + 1:]
        return 1, int(c, 10)  # 百分比输入
    else:
        return 0, int(s, 10)  # 数据输入


def cmpdate(s, d, m, a, c):
    if (m == 'year:'):
        pass
    elif (m == 'month:'):
        pass
    elif (m == 'day:'):
        pass
    elif (m == 'hour:'):
        pass
    elif (m == 'minute:'):
        pass
    elif (m == 'second:'):
        pass
    elif (m == 'data'):
        sd = int(s, 10)
        dd = int(d, 10)
        dmax = dmin = 0
        if (0):
            dmax = dd + c
            dmin = dd - c
        else:
            if (c <= 100):
                dmax = dd * (1 + c / 100)
                dmin = dd * (1 - c / 100)
        if dmin <= sd <= dmax:
            return True
        else:
            return False


if __name__ == '__main__':
    s1 = 'data:1000:100,'  # 数据判断 900~1100 都算合格
    s2 = 'data:2000:%10,'  # 数据判断 1800~2200 都算合格
    s = s1 + s2



    a, c = cmpc('%10')
    print(a, c)

    s = '1000'
    d = '1100'
    m = 'data'

    f = cmpdate(s, d, m, a, c)
    print(f)
