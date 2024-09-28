from decimal import *

number = float(input("Enter a floating point decimal: "))

numberString = str(number)
numberDecimal = Decimal(numberString)

print("The number to 2 decimal places is {:.2f}".format(number))
print("The number in scientific notation is {:.2E}".format(number))
print("The number in percentage format is {:.2%}".format(number))