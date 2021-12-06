import PySimpleGUI as sg
#close original window

#megaBoard = serial.Serial('COM13', 9600)

# Choose a Theme for the Layout
sg.theme('DarkAmber')

def starting():
    print("CTRL -> start thinking")
    megaBoard.write(b'F')

def stopping():
    print("CTRL -> STOP")
    megaBoard.write(b'S')

def zero_gantry():
    print("ZEROING GANTRY")
    megaBoard.write(b'Z')

layout = [ [sg.Button('Start', button_color=('white', 'green'))], 
[sg.Button('Stop', button_color=('white', 'red'))],
[sg.Button('Move to Position', button_color=('white', 'blue')),sg.InputText(size=(2, 1), key = 'pos_x'),sg.InputText(size=(2, 1), key = 'pos_y')],
[sg.Button('Reset Gantry', button_color=('white', 'orange'))],
[sg.Exit()]] 

window = sg.Window('HAND OF GOD',size=(1366, 768)).Layout(layout)

while True:             # Event Loop
    event, values = window.Read()
    if event in (None, 'Exit'):
        break
    if event == 'Start':
       starting()
    elif event == 'Stop':
        stopping()
    elif event == 'Move to Position':
       p_x = int(values['pos_x'])
       p_y = int(values['pos_y'])
      
      #if p_x or p_y 
       #moveposition(p_x,p_y)
    elif event == 'Reset Gantry':
        zero_gantry()
window.Close()

