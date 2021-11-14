import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt

def parabola(x, a, b, c):
    return a*x**2 + b*x + c

def linear(x, a, b):
    return a*x + b

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

def calc_linear_line(x1, x2, y1, y2):
    """https://moonbooks.org/Articles/
    How-to-calculate-the-slope-and-the-intercept
    -of-a-straight-line-with-python-/"""
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1     
    return m,b


def find_parabola(a,b,c):
    x_pos=np.arange(0,1000,1)
    y_pos=[]

    #Calculate y values 
    for x in range(len(x_pos)):
        x_val=x_pos[x]
        y=(a*(x_val**2))+(b*x_val)+c
        y_pos.append(y)
    return [x_pos,y_pos]

def find_line(m,b):
    x_pos=np.arange(0,1000,1)
    y_pos=[]

    #Calculate y values 
    for x in range(len(x_pos)):
        x_val=x_pos[x]
        y=m*x_val+b
        y_pos.append(y)
    return [x_pos,y_pos]


def plot_parabola(a,b,c):
    x_pos=np.arange(0,1000,1)
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





