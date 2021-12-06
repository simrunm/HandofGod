import math
import numpy as np
import matplotlib.pyplot as plt
g = 9.8
angle = math.pi/6  #in rad
vel = 5
#x = vel*math.cos(angle)
#y = vel*math.sin(angle)


coeff_1 = math.tan(angle)
coeff_2 = g/(2*(vel**2)*(math.cos(angle)**2))

time = np.arange(0, 100, 1)
y = 0
x = 0

x = np.linspace(0, 100, 1000)
print(x)
# calculate the y value for each element of the x vector
y = x*coeff_1 - x**2*coeff_2

fig, ax = plt.subplots()
ax.plot(x, y)

#ax.show()
plt.show()