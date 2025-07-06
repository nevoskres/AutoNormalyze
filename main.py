import re

import matplotlib.pyplot as plt
#import seaborn as sns
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tkinter import *
from tkinter import filedialog, messagebox
import re


# Функция для извлечения чисел из текста
def extractnums(lines):
    numrex = re.compile(r'[-+]?\d+\.?\d*')
    nums=[]
    for line in lines:
        matches = numrex.findall(line)
        nums.append(float(match) for match in matches if match)
    return np.array(nums,  dtype=np.float64)


# Функция для загрузки данных из файла
def getdatafile():
    filename = filedialog.askopenfilename(title="Выберите файл с данными")
    if filename:
        try:
            with open(filename, 'r') as f:
                d = f.read().splitlines()
            nums = extractnums(d)
            if not nums:
                messagebox.showwarning("Файл не содержит чисел")
                return None
            messagebox.showinfo(f"Найдено {len(nums)} чисел")
            return nums
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать файл:\n{str(e)}")
            return None


# Функция для ручного ввода данных
def getdatakeyboard():

    lbl_keyboard = Label(window,text="Введите числа через пробел:",bg="black",fg="red")
    lbl_keyboard.pack(pady=10)
    entry = Entry(window,font=("Arial", 12),fg="white",bg="#333333",insertbackground="red")
    entry.pack(pady=10)



def help():
    print("help")

def mainmenu(window):
    lbl = Label(window, text="Приложение для нормализации данных\n", bg="black", fg="red")
    lbl.pack()
    # lbl.grid(column=0, row=0)
    b1 = Button(window, text="Открыть файл с данными", bg="black", fg="red", command=getdatafile)
    b1.pack()
    b2 = Button(window, text="Ввести данные вручную", bg="black", fg="red", command=getdatakeyboard)
    b2.pack()
    b3 = Button(window, text="Помощь", bg="black", fg="red", command=help)
    b3.pack()


window = Tk()
window.title("AutoNormalyze")
window.geometry("400x400")
window.configure(bg="black")
mainmenu(window)
window.mainloop()