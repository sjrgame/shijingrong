#coding=utf8
import logging
import os
from Lib.DealCsv import ExceptPropertyDic
from wxPython import wx
# 用于json数据的比较，包含属性、属性值的比较。''
#用于比较字符串、列表
PATH=lambda p:os.path.abspath(os.path.join(os.path.dirname(__file__), p))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=PATH('../Log/judgeProps.log'),filemode='w')
def CmpObj( reaResultl,exceptResult):
    try:
        if len(reaResultl)==len(exceptResult):
            if cmp(reaResultl,exceptResult)==0: return True
            else:return False
        else:
            return False
    except Exception as e:
        print(e)
#参数包含两个：
#containVar：查找包含的字符
#stringVar：所要查找的字符串
def containVarInString(containVar,stringVar):
    try:
        if isinstance(stringVar, str):
            if containVar in stringVar:
                return True
            else:
                return False
        else:return False
    except Exception as e:
        print(e)

def CmpValue(propsDic,exceptDic):
    try:
        containSeparatorList=[val for var in exceptDic.values() if containVarInString("|",var) for val in var.split("|")]
        notContainSeparatorList=[var for var in exceptDic.values() if not containVarInString("|",var)]
        exceptValueList=notContainSeparatorList+containSeparatorList
        FalseBool=list(set([False for var in propsDic.values() if var not in exceptValueList ]))
        if len(FalseBool):
            return False
        else:
            return True
    except Exception as e:
        print(e)

propsDic={'itemId ': 'XX','item' : 'track' ,'serviceId' : 'pageview' ,'srcSubModule' : '声音条' ,
          'srcPosition' : 'XX','srcPage' : '发现_推荐' ,'srcPageId' : 'XX' ,
          'srcModule' : '焦点图' , 'srcTitle' : '焦点图标题' ,'focusId' : '焦点图ID'}
ExpecDic={'itemId ': 'XX','item' : 'track' ,'serviceId' : 'pageview' ,'srcSubModule' : '声音条' ,
          'srcPosition' : 'XX','srcPage' : '发现_推荐|猜你喜欢|订阅' ,'srcPageId' : 'XX' ,
          'srcModule' : '焦点图' ,'srcTitle' : '焦点图标题' ,'focusId' : '焦点图ID'}

if __name__=="__main__":
    print("脚本之家测试结果：")
    if CmpValue(propsDic, ExpecDic):
        print("Equel")
    else:
        print("not equel")