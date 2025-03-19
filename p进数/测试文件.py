from p进制运算 import PBN

num1 = PBN(255)
print(num1) #255
num2 = PBN(255,5)
num5 = PBN("255",6)
print(num2) #2010
print(-num2) #-2010
print(num5.decimal_value) #107
num3 = PBN(-255,5)
print(num3) #-2010
num4=num1+num2
print(num1.decimal_value) #255
print(num2.decimal_value) #255
print(num4) #510
num6 = PBN("-255",7)
print(num6.decimal_value) #-138
num6 = PBN("25-5",7)
print(num6)#25-5 BUG 应该报错 不应支持字符串-号在中间
print(num6.decimal_value) #-138
num7 = PBN("2-5-5",7)
print(num7)#2-5-5 BUG
print(num7.decimal_value)#-138
num8=PBN("-10")
print(num8)#-10
print(num8.decimal_value)#-10
num8.to_base(7)
print(num8)#-10 没有正常工作
print(num8.decimal_value)#-10 疑似完全没有起作用
print(num8.jbiao)#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ 没有进行截断 BUG
print(PBN(9,base=3))#100
num11=PBN(9,base=3,jbiao="583")#855
print(num11.jbiao)#583
print(num11)#855
print(num11.p_base_value)#855
num12=PBN("33",base=3,jbiao="583")#855
print(num12.jbiao)#583
print(num12)#33
print(num12.p_base_value)#33
print(num12.decimal_value)#8
num9=PBN(0)
print(num9)#0
num10=PBN("0")
print(num10)#0

