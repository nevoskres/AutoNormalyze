import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import canberra
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, PowerTransformer
from scipy.stats import skew, normaltest
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoNormalyze")
        self.root.geometry("600x500")
        root.minsize(600, 250)
        root.maxsize(600, 1000)
        self.root.configure(bg="#F6F6EB")
        self.csv_df = None
        self.datasets = []
        self.current_index = None
        self.scaler = None
        #self.setup_styles()
        self.dark_mode = False
        self.day_setup_styles()
        self.show_main_menu()


    # Переключение темы
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.night_setup_styles()
            self.root.configure(bg="#20242B")
        else:
            self.day_setup_styles()
            self.root.configure(bg="#F6F6EB")
        self.show_main_menu()

    # Общий ночной стиль
    def night_setup_styles(self):
        self.style = {
            "bg": "black",
            "fg": "white",
            "font": ("Arial", 12),
            "activebackground": "#414650",
            "activeforeground": "white"
        }

        self.text_style = {
            "font": ("Consolas", 11),
            "fg": "white",
            "bg": "#222222",
            "insertbackground": "red",
            "selectbackground": "#555555"
        }

    # Дневной стиль
    def day_setup_styles(self):
        self.style = {
            "bg": "#F6F6EB",
            "fg": "black",
            "font": ("Arial", 12),
            "activebackground": "#F6F6EE",
            "activeforeground": "black"
        }
        self.text_style = {
            "font": ("Consolas", 11),
            "fg": "black",
            "bg": "#F6F6EB",
            "insertbackground": "black",
            "selectbackground": "aquamarine4"
        }


    # Функция для очищения окна
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Главное меню
    def show_main_menu(self):
        self.clear_window()
        Label(self.root,
              text="Нормализация числовых данных",**self.style).pack(pady=20)

        buttons = [
            ("Открыть файл", self.load_file),
            ("Ручной ввод", self.show_input_window),
            ("Выбрать из существующих", self.show_dataset_selector),
            ("Помощь", self.show_help),
            ("Ночной/Дневной режим",self.toggle_theme),
            ("Выход", self.root.quit)
        ]

        for text, command in buttons:
            Button(self.root, text=text, command=command, **self.style).pack(pady=5, fill=X, padx=50)

    # Извлечение чисел из текста
    @staticmethod
    def extract_numbers(text):
        numrex = re.compile(r'[-+]?\d+\.?\d*')
        matches = numrex.findall(text)
        return np.array([float(m) for m in matches], dtype=np.float64)

    # Загрузка файла
    def load_file(self):
        filename = filedialog.askopenfilename(title="Выберите файл с данными",filetypes=[("Текстовые файлы", "*.txt"),("CSV файлы", "*.csv")])
        if not filename:
            return
        if filename.lower().endswith('.csv'):
            self.open_csv_file(filename)
        else:
            self.open_text_file(filename)

    # Открытие файла .csv
    def open_csv_file(self, filename):
        try:
            df = pd.read_csv(filename, sep=',')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать CSV файл:\n{str(e)}")
            return
        if df.empty:
            messagebox.showwarning("Ошибка","Файл пустой")
            return
        self.csv_df=df
        self.show_split_options()

    # Выбор разделения таблицы на выборки
    def show_split_options(self):
        self.clear_window()
        Label(self.root,
              text="Выберите способ разделения данных", **self.style).pack(pady=20)

        buttons = [
            ("По столбцам", self.split_on_column),
            ("По строкам", self.split_on_row)
        ]
        for text, command in buttons:
            Button(self.root, text=text, command=command, **self.style).pack(pady=5, fill=X, padx=50)

    # Разделение по столбцам
    def split_on_column(self):
        try:
            added = 0
            for col in self.csv_df.columns:
                values = self.csv_df[col].dropna().values.astype(float)
                if values.size > 0:
                    self.datasets.append(values)
                    added += 1
            if added == 0:
                messagebox.showwarning("Ошибка", "Нет числовых данных в столбцах")
            else:
                messagebox.showinfo("Успех", f"Добавлено {added} выборок из столбцов")
                self.show_dataset_selector()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось разделить по столбцам:\n{str(e)}")

    # Разделение по строкам
    def split_on_row(self):
        try:
            added = 0
            for _, row in self.csv_df.iterrows():
                values = row.dropna().values.astype(float)
                if values.size > 0:
                    self.datasets.append(values)
                    added += 1
            if added == 0:
                messagebox.showwarning("Ошибка", "Нет числовых данных в строках")
            else:
                messagebox.showinfo("Успех", f"Добавлено {added} выборок из строк")
                self.show_dataset_selector()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось разделить по строкам:\n{str(e)}")

    # Открытие файла .txt
    def open_text_file(self,filename):
        try:
            with open(filename, 'r') as f:
                text = f.read()
            numbers = self.extract_numbers(text)
            if numbers.size == 0:
                messagebox.showwarning("Ошибка", "Файл не содержит чисел")
                return
            self.datasets.append(numbers)
            messagebox.showinfo("Успех", f"Добавлена выборка из {len(numbers)} чисел")
            self.show_dataset_selector()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать TXT файл:\n{str(e)}")

    # Окно ввода вручную
    def show_input_window(self):
        self.clear_window()
        Label(self.root, text="Введите числа через пробел:",**self.style).pack(pady=10)

        self.text_input = scrolledtext.ScrolledText(self.root, height=15, width=70, **self.text_style)
        self.text_input.pack(pady=10, padx=20)
        self.text_input.insert(END, "1.5 2 3.14\n-5 100 0.001")

        button_frame = Frame(self.root, bg="black")
        button_frame.pack(pady=10)

        Button(button_frame, text="Подтвердить", command=self.process_input, **self.style).pack(side=LEFT, padx=10)
        Button(button_frame, text="Назад", command=self.show_main_menu, **self.style).pack(side=LEFT, padx=10)

    # Обработка ввода вручную
    def process_input(self):
        text = self.text_input.get("1.0", END)
        numbers = self.extract_numbers(text)

        if numbers.size == 0:
            messagebox.showerror("Ошибка", "Введите хотя бы одно число!")
            return
        self.datasets.append(numbers)
        messagebox.showinfo("Успех", f"Добавлена выборка из {len(numbers)} чисел")
        self.show_dataset_selector()

    # Выбор выборки
    def show_dataset_selector(self):
        self.clear_window()
        Label(self.root, text="Выберите выборку:", **self.style).pack(pady=10)

        # для скроллбара нужно отдельное поле
        canvas = Canvas(root)
        sb = Scrollbar(canvas, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(anchor="center", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for i, dataset in enumerate(self.datasets):
            Button(scrollable_frame, text=f"Выборка #{i + 1} ({len(dataset)} чисел)",
                   command=lambda i=i: self.select_dataset(i),
                   **self.style).pack(pady=5, fill="both", padx=210)

        Button(self.root, text="Назад", command=self.show_main_menu, **self.style).pack(pady=10)

    def select_dataset(self, index):
        self.current_index = index
        self.show_data_options()

    # Опции с выборкой
    def show_data_options(self):
        self.clear_window()
        Label(self.root, text=f"Выборка #{self.current_index + 1}", **self.style).pack(pady=10)

        options = [
            ("Показать статистику", self.show_stats),
            ("Нормализовать", self.normalize_data),
            ("Визуализировать", self.plot_data),
            ("Назад к выборкам", self.show_dataset_selector),
            ("Назад в меню", self.show_main_menu)
        ]

        for text, command in options:
            Button(self.root, text=text, command=command, **self.style).pack(pady=5, fill=X, padx=50)

    # Показ статистики
    def show_stats(self):
        data = self.datasets[self.current_index]
        stats = f"""
Статистика данных:
Количество: {len(data)}
Минимум: {np.min(data):.4f}
Максимум: {np.max(data):.4f}
Среднее: {np.mean(data):.4f}
Стандартное отклонение: {np.std(data):.4f}
"""
        messagebox.showinfo("Статистика", stats)

    # Визуализация гистограммы
    def plot_data(self):
        data = self.datasets[self.current_index]

        # Устанавливка стиля графиков под тему
        if self.dark_mode:
            plt.style.use('dark_background')
            hist_color = 'cyan'
            scatter_color = 'yellow'
        else:
            plt.style.use('default')
            hist_color = 'red'
            scatter_color = 'blue'

        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        # Гистограмма
        axs[0].hist(data, bins=8, color=hist_color, alpha=0.7)
        axs[0].set_title(f"Гистограмма выборки #{self.current_index + 1}")
        axs[0].set_xlabel("Значения")
        axs[0].set_ylabel("Частота")
        axs[0].grid(True)

        # Точечный график
        axs[1].scatter(range(len(data)), data, color=scatter_color, alpha=0.7, s=40)
        axs[1].set_title("Точечный график значений")
        axs[1].set_xlabel("Индекс")
        axs[1].set_ylabel("Значение")
        axs[1].grid(True)

        plt.tight_layout()
        plt.show()

    # Авто-нормализация с выбором метода
    def normalize_data(self):
        try:
            data = self.datasets[self.current_index].reshape(-1, 1)

            # Проверка нормальности распределения (p-value > 0.05 — нормально)
            stat, p = normaltest(data)
            skewness = skew(data.flatten())
            iqr = np.percentile(data, 75) - np.percentile(data, 25)
            outlier_mask = (data < (np.percentile(data, 25) - 1.5 * iqr)) | (data > (np.percentile(data, 75) + 1.5 * iqr))
            outlier_ratio = np.sum(outlier_mask) / len(data)

            method_used = ""

            if outlier_ratio > 0.15:
                # Много выбросов — RobustScaler
                self.scaler = RobustScaler()
                method_used = "Robust Scaling (устойчив к выбросам)"
            elif abs(skewness) > 1:
                # Сильная асимметрия — PowerTransformer (Box-Cox или Yeo-Johnson)
                if np.all(data > 0):
                    self.scaler = PowerTransformer(method='box-cox')
                    method_used = "Box-Cox (асимметрия, положительные данные)"
                else:
                    self.scaler = PowerTransformer(method='yeo-johnson')
                    method_used = "Yeo-Johnson (асимметрия, отрицательные значения)"
            elif p > 0.05:
                # Нормальное распределение — StandardScaler (Z-преобразование)
                self.scaler = StandardScaler()
                method_used = "Z-преобразование (StandardScaler)"
            else:
                # Иначе Min-Max нормализация
                self.scaler = MinMaxScaler()
                method_used = "Min-Max нормализация"

            norm_data = self.scaler.fit_transform(data).flatten()
            self.datasets[self.current_index] = norm_data

            messagebox.showinfo("Нормализация завершена", f"Применено: {method_used}")
            self.show_stats()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка авто-нормализации:\n{str(e)}")

    # Помощь
    @staticmethod
    def show_help():
        help_text = """
Инструкция по использованию:

1. Загрузите данные из файла или введите вручную.
2. Выберите нужную операцию:
   - Показать статистику
   - Нормализовать данные (автоматически подбирается метод)
   - Визуализировать данные (гистограмма, точечный график)
3. Формат данных: числа, разделённые пробелами или переводами строки.
   Поддерживаются дробные и отрицательные числа.
"""
        messagebox.showinfo("Помощь", help_text)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
