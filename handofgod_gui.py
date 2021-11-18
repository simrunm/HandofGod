import PySimpleGUI as sg
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

layout = [ [sg.Button('Start')], 
[sg.Button('Stop')],
[sg.Button('Reset Gantry')],
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
    elif event == 'Reset Gantry':
        zero_gantry()
window.Close()

