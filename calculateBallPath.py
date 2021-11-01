import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt


def parabola(x, a, b, c):
    return a*x**2 + b*x + c

def calc_parabola_vertex(x1, x2, x3, y1, y2, y3):
    '''
    Adapted and modifed to get the unknowns for defining a parabola:
    http://stackoverflow.com/questions/717762/how-to-calculate-the-vertex-of-a-parabola-given-three-points
    '''

    denom = (x1-x2) * (x1-x3) * (x2-x3);
    A = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom;
    B = (x3*x3 * (y1-y2) + x2*x2 * (y3-y1) + x1*x1 * (y2-y3)) / denom;
    C = (x2 * x3 * (x2-x3) * y1+x3 * x1 * (x3-x1) * y2+x1 * x2 * (x1-x2) * y3) / denom;
    return A,B,C

def plot_parabola(a,b,c):
    x_pos=np.arange(-30,30,1)
    y_pos=[]

    #Calculate y values 
    for x in range(len(x_pos)):
        x_val=x_pos[x]
        y=(a*(x_val**2))+(b*x_val)+c
        y_pos.append(y)


    plt.plot(x_pos, y_pos, linestyle='-.', color='black') # parabola line
    plt.scatter(x_pos, y_pos, color='gray') # parabola points
    plt.scatter(x1,y1,color='r',marker="D",s=50) # 1st known xy
    plt.scatter(x2,y2,color='g',marker="D",s=50) # 2nd known xy
    plt.scatter(x3,y3,color='k',marker="D",s=50) # 3rd known xy
    plt.show()

params = [-0.1, 0.5, 1.2]
x = np.linspace(-5, 5, 31)
y = parabola(x, params[0], params[1], params[2])
r = np.random.RandomState(42)
y_with_errors = y + r.uniform(-1, 1, y.size)


fit_params, pcov = scipy.optimize.curve_fit(parabola, x, y_with_errors)
y_fit = parabola(x, *fit_params)
plt.plot(x, y_with_errors, label='sample')
plt.plot(x, y_fit, label='fit')
plt.show()
x1, x2, x3, y1, y2, y3 = x[0], x[len(x)//2], x[len(x) - 1], y[0], y[len(x)//2], y[len(x) - 1]
a,b,c = calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
plot_parabola(a,b,c)
