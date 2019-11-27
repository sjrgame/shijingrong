import clr
import sys
import System
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import Form
from System import String
from System.Collections import *


from System.Windows.Forms import Application, Button



print(System.Environment.Version)

print('-----')

for p in sys.path:
    print(p)

print('-----')

form = Form(Text="Hello World")
button = Button(Text="Click Me")
form.Controls.Add(button)

def onClick(sender, event):
     print('Ouch! ' + __name__)
button.Click += onClick



clr.AddReference("DLT698_45.OOP")

from DLT698_45.OOP import *
from DLT698_45.OOP.DataType import DT_OAD,DT_OI,DT_LONG_UNSIGNED,DT_UNSIGNED
from DLT698_45.OOP.DataType import DT_Data,DT_OCTET_STRING
#from DLT698_45.OOP.APDUType import *
from DLT698_45.OOP.Frame import *


HData_remain = DT_OCTET_STRING('')
value = String("68170043050100000000001026F605010060120200001085166666")

frame1 = OOPFrame(DT_OCTET_STRING(value),HData_remain)

if frame1 !=None:
    str = frame1.HValue
    print(str)
frame1.A.SA.Addr='000000000002'
frame1.A.SA.AddrLogic=DT_UNSIGNED(System.Byte(1))   #DT_UNSIGNED('1')
frame1.A.CA = 16
oad =DT_OAD(DT_OCTET_STRING('60130200'))

frame1.UserDataRegion.UserData.APDUGetRequest.OAD=oad
frame1.UserDataRegion.UserData.APDUGetRequest.PIID.ServiceID=1
str = frame1.HValue
print(str)




