num1 = int(input("Enter the first number: "))
num2 = int(input("Enter the second number: "))
num3 = int(input("Enter the third number: "))

sum = num1 + num2 + num3
product = num1 * num2 * num3
average = sum/3

numbers = [num1, num2, num3]
if (num1 > num2):
    max1 = num1
else: 
    max1 = num2

if (max1 > num3):
    max = max1
else:
    max = num3

if (num1 < num2):
    min1 = num1
else: 
    min1 = num2

if (min1 < num3):
    min = min1
else:
    min = num3

print("The sum is " + str(sum))
print("The product is " + str(product))
print("The max is " + str(max))
print("The min is " + str(min))