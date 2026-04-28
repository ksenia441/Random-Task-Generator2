import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Предопределённые задачи по категориям
        self.tasks = {
            "Учёба": [
                "Прочитать статью",
                "Решить 5 задач по математике",
                "Выучить 10 новых слов",
                "Посмотреть лекцию",
                "Сделать конспект"
            ],
            "Спорт": [
                "Сделать зарядку",
                "Пробежать 2 км",
                "Сделать 20 отжиманий",
                "Пойти на тренировку",
                "Растяжка 15 минут"
            ],
            "Работа": [
                "Ответить на письма",
                "Провести встречу",
                "Написать отчёт",
                "Разобрать задачи в Trello",
                "Сделать бэкап данных"
            ]
        }
        
        # История задач
        self.history = []
        self.history_file = "task_history.json"
        
        # Загрузка истории из файла
        self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Сохранение истории при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Основная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса столбцов и строк
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # === Блок генерации задачи ===
        generate_frame = ttk.LabelFrame(main_frame, text="Генерация задачи", padding="10")
        generate_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        generate_frame.columnconfigure(0, weight=1)
        
        self.generate_btn = ttk.Button(
            generate_frame, 
            text="🎲 Сгенерировать задачу", 
            command=self.generate_task,
            width=30
        )
        self.generate_btn.grid(row=0, column=0, pady=5)
        
        self.current_task_label = ttk.Label(
            generate_frame, 
            text="Нажмите кнопку, чтобы получить задачу",
            font=("Arial", 10),
            wraplength=550
        )
        self.current_task_label.grid(row=1, column=0, pady=5)
        
        # === Блок добавления новой задачи ===
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(0, weight=1)
        add_frame.columnconfigure(1, weight=0)
        
        ttk.Label(add_frame, text="Задача:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.new_task_entry = ttk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.category_var = tk.StringVar(value="Учёба")
        self.category_combo = ttk.Combobox(
            add_frame, 
            textvariable=self.category_var, 
            values=["Учёба", "Спорт", "Работа"],
            state="readonly",
            width=37
        )
        self.category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.add_btn = ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_task)
        self.add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # === Блок истории ===
        history_frame = ttk.LabelFrame(main_frame, text="История задач", padding="10")
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)
        
        # Фильтр истории
        filter_frame = ttk.Frame(history_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=(0, 10))
        self.filter_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["Все", "Учёба", "Спорт", "Работа"],
            state="readonly",
            width=37
        )
        self.filter_combo.grid(row=0, column=1, sticky=tk.W)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Список истории с прокруткой
        list_frame = ttk.Frame(history_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.history_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=12,
            font=("Arial", 9)
        )
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.history_listbox.yview)
        
        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="🗑️ Очистить историю", command=self.clear_history)
        clear_btn.grid(row=2, column=0, pady=(10, 0))
        
        # Обновление отображения истории
        self.update_history_display()
    
    def generate_task(self):
        """Генерация случайной задачи из всех категорий"""
        all_tasks = []
        for category, task_list in self.tasks.items():
            for task in task_list:
                all_tasks.append((task, category))
        
        if not all_tasks:
            messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу для генерации!")
            return
        
        task, category = random.choice(all_tasks)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Добавляем в историю
        history_entry = {
            "timestamp": timestamp,
            "task": task,
            "category": category
        }
        self.history.append(history_entry)
        
        # Отображаем текущую задачу
        self.current_task_label.config(
            text=f"✨ {task} ({category}) ✨",
            foreground="green"
        )
        
        # Сохраняем историю
        self.save_history()
        
        # Обновляем отображение
        self.update_history_display()
    
    def add_task(self):
        """Добавление новой задачи"""
        new_task = self.new_task_entry.get().strip()
        category = self.category_var.get()
        
        # Проверка на пустую строку
        if not new_task:
            messagebox.showerror("Ошибка", "Задача не может быть пустой!")
            return
        
        # Добавляем задачу в соответствующий список
        if category in self.tasks:
            self.tasks[category].append(new_task)
        else:
            self.tasks[category] = [new_task]
        
        # Очищаем поле ввода
        self.new_task_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Задача \"{new_task}\" добавлена в категорию \"{category}\"")
    
    def on_filter_change(self, event=None):
        """Обработка изменения фильтра"""
        self.update_history_display()
    
    def update_history_display(self):
        """Обновление отображения истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        
        filter_value = self.filter_var.get()
        
        for entry in reversed(self.history):  # Показываем новые сверху
            if filter_value == "Все" or entry["category"] == filter_value:
                display_text = f"[{entry['timestamp']}] {entry['task']} ({entry['category']})"
                self.history_listbox.insert(tk.END, display_text)
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена")
    
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении истории: {e}")
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке истории: {e}")
                self.history = []
    
    def on_closing(self):
        """Обработка закрытия окна"""
        self.save_history()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()