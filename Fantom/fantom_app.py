import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import re
import sys
import io
from contextlib import redirect_stdout

# --- ЯДРО ЯЗЫКА FANTOM ---
KEYWORDS = {
    'функция': 'def',
    'пусть': '',
    'перем': '',
    'иначе если': 'elif',
    'если': 'if',
    'иначе': 'else',
    'пока': 'while',
    'для': 'for',
    'вернуть': 'return',
    'отобразить': 'fa_print',
    'ввод': 'input',
    'истина': 'True',
    'ложь': 'False',
    'и': 'and',
    'или': 'or',
    'не': 'not',
}

class FantomEngine:
    def translate(self, source):
        lines = source.splitlines()
        translated_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            # Обработка комментариев
            if '//' in line:
                line = line.split('//')[0].strip()
            
            if not line: continue
                
            # Закрытие блока
            if line.startswith('}'):
                indent_level -= 1
                line = line[1:].strip()
                if not line: continue

            # Замена ключевых слов (иначе если проверяется первым)
            for ru, en in KEYWORDS.items():
                line = re.sub(rf'\b{ru}\b', en, line)
            
            line = line.strip()

            # Открытие блока
            opens_block = False
            if line.endswith('{'):
                line = line[:-1].strip() + ':'
                opens_block = True
            
            translated_lines.append('    ' * max(0, indent_level) + line)
            
            if opens_block:
                indent_level += 1
            
        return '\n'.join(translated_lines)

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
class FantomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantom Studio v1.0.1")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        # Панель инструментов
        self.toolbar = tk.Frame(root, bg="#2d2d2d", pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_open = tk.Button(self.toolbar, text="Открыть", command=self.open_file, bg="#3d3d3d", fg="white")
        self.btn_open.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(self.toolbar, text="Сохранить", command=self.save_file, bg="#3d3d3d", fg="white")
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.btn_run = tk.Button(self.toolbar, text="ЗАПУСТИТЬ ▶", command=self.run_code, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_run.pack(side=tk.LEFT, padx=20)

        # Основной контейнер (редактор и консоль)
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#1e1e1e")
        self.paned.pack(expand=True, fill="both", padx=10, pady=10)

        # Редактор
        self.code_input = scrolledtext.ScrolledText(self.paned, font=("Consolas", 12), bg="#1e1e1e", fg="#dcdcdc", insertbackground="white", undo=True)
        self.paned.add(self.code_input)

        # ДОБАВЛЯЕМ ОБРАБОТЧИКИ ДЛЯ КОПИРОВАНИЯ/ВСТАВКИ
        self.code_input.bind("<Control-c>", self.copy_text)
        self.code_input.bind("<Control-x>", self.cut_text)
        self.code_input.bind("<Control-v>", self.paste_text)
        self.code_input.bind("<Button-3>", self.show_context_menu) # Правая кнопка мыши

        # Консоль вывода
        self.output_display = scrolledtext.ScrolledText(self.paned, font=("Consolas", 12), bg="#000000", fg="#00ff00", width=40)
        self.paned.add(self.output_display)
        self.output_display.config(state=tk.DISABLED)

        # Меню для правой кнопки мыши
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)

    def show_context_menu(self, event):
        """Показывает контекстное меню при нажатии правой кнопки мыши."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_text(self, event=None):
        """Копирует выделенный текст."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.code_input.selection_get())
        except tk.TclError:
            pass # Нет выделенного текста

    def cut_text(self, event=None):
        """Вырезает выделенный текст."""
        self.copy_text()
        self.code_input.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def paste_text(self, event=None):
        """Вставляет текст из буфера обмена."""
        try:
            self.code_input.insert(tk.INSERT, self.root.clipboard_get())
        except tk.TclError:
            pass # Буфер обмена пуст

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fantom Files", "*.fa"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.code_input.delete("1.0", tk.END)
                self.code_input.insert(tk.END, f.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".fa", filetypes=[("Fantom Files", "*.fa")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_input.get("1.0", tk.END))

    def run_code(self):
        source = self.code_input.get("1.0", tk.END)
        engine = FantomEngine()
        python_code = engine.translate(source)
        
        if "def главная" in python_code:
            python_code += "\n\nглавная()"

        self.output_display.config(state=tk.NORMAL)
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert(tk.END, ">>> Запуск программы Fantom...\n")
        
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                def fa_print(*args):
                    print(" ".join(map(str, args)))

                exec_globals = {
                    "fa_print": fa_print,
                    "input": input,
                    "int": int,
                    "float": float,
                    "str": str,
                    "__name__": "__main__"
                }
                exec(python_code, exec_globals)
                result = f.getvalue()
            except Exception as e:
                result = f.getvalue() + f"\n❌ Ошибка Fantom: {e}"
        
        self.output_display.insert(tk.END, result)
        self.output_display.insert(tk.END, "\n\n>>> Программа завершена.")
        self.output_display.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FantomApp(root)
    root.mainloop()