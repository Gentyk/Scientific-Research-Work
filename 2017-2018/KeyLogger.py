from pynput import mouse
import time
from datetime import datetime
import ActiveWindiws
import win32gui
import pywinauto
import uiautomation as automation


def callback():
    """
    Функция обнаруживающая активное окно и его координаты
    :return:  {text = <текст из окна>, coordinates = [<четыре координаты>]}
    """
    hwnd=win32gui.GetForegroundWindow()

    try:
        rect = win32gui.GetWindowRect(hwnd)
        x1 = rect[0]
        y1 = rect[1]
        x2 = rect[2]
        y2 = rect[3]
        result = dict()
        result.update(text = win32gui.GetWindowText(hwnd))
        result.update(coordinates = [x1,y1,x2,y2])
        return result
    except:
        return None

def on_click(x, y, button, pressed):
    #функция, которая выводит состояние кнопки(нажата/отпущена) и координаты
    print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    rez = callback()

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))

with mouse.Listener(
        on_click=on_click,
        on_scroll=on_scroll) as listener:
    listener.join()
