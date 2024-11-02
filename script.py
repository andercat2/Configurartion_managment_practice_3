import re
import sys

# Шаблоны регулярных выражений
comment_pattern = re.compile(r"\{\{!--(.*?)--\}\}", re.DOTALL)
const_pattern = re.compile(r"set\s+([a-z][a-z0-9_]*)\s*=\s*(.*?);")
table_pattern = re.compile(r"table\(\[(.*?)\]\)", re.DOTALL)
expression_pattern = re.compile(r"@{(.*?)}")

def parse_comments(text):
    """Удаление многострочных комментариев"""
    return re.sub(comment_pattern, '', text)

def parse_constants(text):
    """Поиск констант и их значений"""
    constants = {}
    expressions = {}  # Отдельно храним выражения, которые нужно вычислить позже
    for match in const_pattern.finditer(text):
        name, value = match.groups()
        value = value.strip()
        if value.isdigit():  # Если значение — число, сразу сохраняем его
            constants[name] = int(value)
        elif expression_pattern.match(value):  # Если значение — выражение, сохраняем для последующего вычисления
            expressions[name] = value[2:-1].strip()
    # Теперь вычисляем выражения
    for name, expr in expressions.items():
        try:
            constants[name] = evaluate_expression(expr, constants.copy())  # Передаем копию словаря
        except ValueError as e:
            print(f"Ошибка при вычислении константы {name}: {e}", file=sys.stderr)
    return constants

def evaluate_expression(expr, constants):
    """Обработка постфиксных выражений с поддержкой сложных операций"""
    tokens = expr.split()
    stack = []
    
    for token in tokens:
        if token.isdigit():
            stack.append(int(token))
        elif token in constants:
            stack.append(constants[token])
        elif token == '+':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции +")
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)
        elif token == '-':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции -")
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif token == 'abs':
            if not stack:
                raise ValueError("Недостаточно операндов для операции abs")
            stack.append(abs(stack.pop()))
        else:
            raise ValueError(f"Неизвестный токен в выражении: {token}")
    
    if not stack:
        raise ValueError("Пустое выражение")
    if len(stack) > 1:
        raise ValueError("Некорректное выражение: остались неиспользованные значения")
    
    return stack[0]

def parse_tables(text, constants):
    """Парсинг таблиц с подстановкой значений констант и вычислением выражений"""
    tables = []
    for match in table_pattern.finditer(text):
        table_content = match.group(1).strip()
        table = {}
        for line in table_content.splitlines():
            line = line.strip()
            if line:
                if '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().rstrip(',')  # Remove trailing comma
                
                # Очистка значения от кавычек и запятых
                value = value.strip('"').strip(',').strip()
                
                if value.startswith('@{') and value.endswith('}'):
                    # Обработка выражений в формате @{...}
                    expr = value[2:-1].strip()
                    try:
                        if expr in constants:  # Check if it's a direct constant reference
                            value = constants[expr]
                        else:
                            value = evaluate_expression(expr, constants)
                    except ValueError as e:
                        print(f"Ошибка при вычислении выражения {expr}: {e}", file=sys.stderr)
                        continue
                elif value in constants:  # Подстановка значения, если это имя константы
                    value = constants[value]
                elif value.isdigit():  # Если значение — это число
                    value = int(value)
                
                table[key] = value
        tables.append(table)
    return tables

def convert_to_toml(text):
    """Основная функция преобразования в TOML формат с вложенными таблицами"""
    text = parse_comments(text)
    constants = parse_constants(text)
    tables = parse_tables(text, constants)

    # Формирование TOML-вывода
    toml_output = ""
    for i, table in enumerate(tables):
        toml_output += f"[table_{i}]\n"
        for key, value in table.items():
            if isinstance(value, str):
                toml_output += f'{key} = "{value}"\n'
            else:
                toml_output += f"{key} = {value}\n"
        toml_output += "\n"
    return toml_output.strip()

if __name__ == "__main__":
    input_text = sys.stdin.read()
    try:
        toml_text = convert_to_toml(input_text)
        print(toml_text)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)