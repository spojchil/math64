from p进制运算 import PBN,PBNF

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
print(num8)
num9=PBN(0)
print(num9)
num10=PBN("0")
print(num10)
