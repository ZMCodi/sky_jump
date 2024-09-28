#task 6.1

num1 = int(input("Enter a number: "))
num2 = int(input("Enter another number: "))

sum = num1 + num2
product = num1 * num2
ratio = num1 / num2
exp = num1 ** num2
mod = num1 % num2

print("The sum is " + str(sum))
print("The product is " + str(product))
print("The ratio is " + str(ratio))
print(str(num1) + "^" + str(num2) + " is " + str(exp))
print(str(num1) + " % " + str(num2) + " is " + str(mod))
print('\n')
#task 6.2

celcius = int(input("Enter a temperature in Celcius: "))

fahrenheit = (celcius * (9 / 5)) + 32

print(str(celcius) + "°C is " + str(fahrenheit) + "°F")
print('\n')

#task 6.3

from math import pi

radiusCirc = int(input("Enter the radius of a cirle: "))

circum = 2 * pi * radiusCirc
area = pi * (radiusCirc ** 2)

print("The circumference of the circle is {:.2f}".format(circum))
print("The area of the circle is {:.2f}".format(area))
print('\n')

#task 6.4

radiusSphere = int(input("Enter the radius of a sphere: "))

surfAreaSphere = 4 * pi * (radiusSphere ** 2)

print("The surface area of the sphere is {:.2f}".format(surfAreaSphere))
print('\n')

#task 6.5

height = int(input("Enter the height of a cylinder: "))
radiusCyl = int(input("Enter the radius of a cylinder: "))

surfAreaCyl = (2 * pi * radiusCyl * height) + (2 * pi * (radiusCyl ** 2))

print("The surface area of the cylinder is {:.2f}".format(surfAreaCyl))
print('\n')

#task 6.6

firstName = str(input("Enter your first name: ")).capitalize()
surName = str(input("Enter your surname: ")).capitalize()

print("Your initials are " + firstName[0] + "." + surName[0] +".")
print('\n')

#task 6.7

age = int(input("Enter your age: "))

print(age > 17)
print('\n')
