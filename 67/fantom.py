import re
import sys

# Добавляем 'ввод' в список ключевых слов
KEYWORDS = {
    'функция': 'def',
    'пусть': '',
    'перем': '',
    'если': 'if',
    'иначе': 'else',
    'пока': 'while',
    'для': 'for',
    'вернуть': 'return',
    'отобразить': 'fa_print', # Теперь используем нашу умную функцию
    'ввод': 'input',
    'истина': 'True',
    'ложь': 'False',
    'и': 'and',
    'или': 'or',
    'не': 'not',
}

# Умная функция для вывода, чтобы не писать str()
def fa_print(*args):
    # Превращаем все аргументы в строки и соединяем их через пробел
    print(" ".join(map(str, args)))

class FantomCompiler:
    def __init__(self, source_code):
        self.source = source_code

    def translate(self):
        lines = self.source.splitlines()
        translated_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if '//' in line:
                parts = line.split('//', 1)
                line = parts[0].strip()
                comment = ' # ' + parts[1]
            else:
                comment = ''

            if not line and not comment:
                continue
                
            if line.startswith('}'):
                indent_level -= 1
                line = line[1:].strip()
                if not line:
                    if comment:
                        translated_lines.append('    ' * max(0, indent_level) + comment)
                    continue

            for ru, en in KEYWORDS.items():
                line = re.sub(rf'\b{ru}\b', en, line)
            
            line = line.strip()

            opens_block = False
            if line.endswith('{'):
                line = line[:-1].strip() + ':'
                opens_block = True
            
            final_line = ('    ' * max(0, indent_level)) + line + comment
            translated_lines.append(final_line)
            
            if opens_block:
                indent_level += 1
            
        return '\n'.join(translated_lines)

    def run(self):
        python_code = self.translate()
        if "def главная" in python_code:
            python_code += "\n\nглавная()"
            
        try:
            # Передаем fa_print в окружение, чтобы код её видел
            exec(python_code, {"fa_print": fa_print, "__name__": "__main__", **globals()})
        except Exception as e:
            print(f"\n❌ Ошибка исполнения Fantom: {e}")

if __name__ == "__main__":
    print("--- Fantom Compiler v0.6 ---")
    if len(sys.argv) < 2:
        print("Ошибка: Не указан файл. Используй: python fantom.py test.fa")
    else:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8-sig') as f:
                code = f.read()
                compiler = FantomCompiler(code)
                compiler.run()
        except FileNotFoundError:
            print(f"Ошибка: Файл {sys.argv[1]} не найден.")