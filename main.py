import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Файл истории
        self.history_file = "history.json"
        self.history = self.load_history()
        
        # Переменные
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.update_history_table()
    
    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                       variable=self.password_length, command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, padx=10, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2)
        
        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&* etc)", variable=self.use_symbols).grid(row=3, column=0, sticky="w")
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Кнопка генерации
        generate_btn = ttk.Button(self.root, text="Сгенерировать пароль", command=self.generate_password)
        generate_btn.pack(pady=10)
        
        # Поле отображения пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), justify="center")
        password_entry.pack(fill="x", padx=10, pady=5)
        
        # Кнопка копирования
        copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)
        
        # Таблица истории
        ttk.Label(self.root, text="История паролей:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        
        frame_tree = ttk.Frame(self.root)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(frame_tree, columns=("password", "length", "date"), show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("date", text="Дата создания")
        self.tree.column("password", width=300)
        self.tree.column("length", width=70)
        self.tree.column("date", width=200)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Кнопки управления историей
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить историю", command=self.save_history).pack(side="left", padx=5)
    
    def update_length_label(self, event=None):
        self.length_label.config(text=str(int(self.password_length.get())))
    
    def generate_password(self):
        length = int(self.password_length.get())
        
        # Проверка корректности длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 32 символа")
            return
        
        # Проверка выбора хотя бы одного набора символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return
        
        # Формирование пула символов
        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        
        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)
        
        # Сохранение в историю
        record = {
            "password": password,
            "length": length,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(record)
        self.save_history()
        self.update_history_table()
    
    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.password_var.get())
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self, event=None):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def update_history_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Заполнение
        for record in self.history:
            self.tree.insert("", "end", values=(record["password"], record["length"], record["date"]))
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
