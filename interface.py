import serial
import time
import tkinter as tk

window =tk.Tk()
window.configure(background = "gray")
window.geometry("1136x768")
window.title("HAND OF GOD CONTROL - PYTHON GUI")

megaBoard = serial.Serial('COM13', 9600)

def hog_control():
    print(">>> HOG CONTROL PROGRAM <<< /n")
    def starting():
        print("CTRL -> start thinking")
        megaBoard.write(b'F')

    def stopping():
        print("CTRL -> STOP")
        megaBoard.write(b'S')

    def zero_gantry():
        print("ZEROING GANTRY")
        megaBoard.write(b'Z')


    def quit():
        print("\n** END OF PROGRAM**")
        megaBoard.write(b'Q')
        megaBoard.close()
        window.destroy()



    b1 = tk.Button(window, text = "START", command = starting, bg= "forest green", fg="gray7", font=("Comic Sans MS", 15))
    b2 = tk.Button(window, text = "STOP", command = stopping, bg= "firebrick2", fg="ghost white", font=("Comic Sans MS", 15))
    b3 = tk.Button(window, text = "RESET GANTRY", command = zero_gantry, bg= "firebrick2", fg="ghost white", font=("Comic Sans MS", 15))
    b4 = tk.Button(window, text = "QUIT", command = quit, bg= "gold", fg="gray7", font=("Comic Sans MS", 15))

    b1.grid(row=1, column=0, padx=5, pady=10)
    b2.grid(row=1, column=1, padx=5, pady=10)
    b4.grid(row=1, column=2, padx=5, pady=10)

    window.mainloop()

time.sleep(2)
hog_control()