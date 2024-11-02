import unittest
from script import (
    parse_comments, 
    parse_constants, 
    evaluate_expression, 
    parse_tables, 
    convert_to_toml
)

class TestConfigParser(unittest.TestCase):
    def test_parse_comments(self):
        """Тест удаления комментариев"""
        input_text = "{{!-- This is a comment --}}content{{!-- Another comment --}}"
        expected = "content"
        self.assertEqual(parse_comments(input_text), expected)
        
        # Тест многострочного комментария
        input_text = """{{!-- Multi
        line
        comment --}}content"""
        expected = "content"
        self.assertEqual(parse_comments(input_text), expected)

    def test_parse_constants(self):
        """Тест парсинга констант"""
        # Тест простых числовых констант
        input_text = "set x = 5;\nset y = 10;"
        constants = parse_constants(input_text)
        self.assertEqual(constants['x'], 5)
        self.assertEqual(constants['y'], 10)
        
        # Тест констант с выражениями
        input_text = """
        set base = 100;
        set bonus = @{base 50 +};
        set abs_value = @{10 20 - abs};
        """
        constants = parse_constants(input_text)
        self.assertEqual(constants['base'], 100)
        self.assertEqual(constants['bonus'], 150)
        self.assertEqual(constants['abs_value'], 10)

    def evaluate_expression(expr, constants):
        """Обработка постфиксных выражений с поддержкой сложных операций"""
        if not expr.strip():
            raise ValueError("Пустое выражение")  # Обработка пустого выражения

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
    
        if len(stack) != 1:
            raise ValueError("Некорректное выражение: остались неиспользованные значения")
    
        return stack[0]


    def test_parse_tables(self):
        """Тест парсинга таблиц"""
        constants = {'port': 8080, 'timeout': 100}
        
        # Тест простой таблицы
        input_text = """
        table([
            name = "TestServer",
            port = @{port},
            timeout = @{timeout}
        ])
        """
        tables = parse_tables(input_text, constants)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['name'], "TestServer")
        self.assertEqual(tables[0]['port'], 8080)
        self.assertEqual(tables[0]['timeout'], 100)
        
        # Тест множественных таблиц
        input_text = """
        table([
            name = "Server1",
            port = @{port}
        ])
        table([
            name = "Server2",
            timeout = @{timeout}
        ])
        """
        tables = parse_tables(input_text, constants)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['name'], "Server1")
        self.assertEqual(tables[0]['port'], 8080)
        self.assertEqual(tables[1]['name'], "Server2")
        self.assertEqual(tables[1]['timeout'], 100)

    def test_convert_to_toml(self):
        """Тест полного преобразования в TOML"""
        input_text = """
        {{!-- Configuration for test server --}}
        set port = 8080;
        set timeout = @{port 20 +};
        
        table([
            name = "TestServer",
            port = @{port},
            timeout = @{timeout}
        ])
        """
        expected = """[table_0]
name = "TestServer"
port = 8080
timeout = 8100"""
        
        self.assertEqual(convert_to_toml(input_text).strip(), expected.strip())

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест неверного выражения
        with self.assertRaises(ValueError):
            evaluate_expression("", {})  # Пустое выражение
        
        # Тест неверного формата таблицы
        input_text = "table([invalid format])"
        tables = parse_tables(input_text, {})
        self.assertEqual(tables, [{}])
        
        # Тест неверного формата константы
        input_text = "set = invalid;"
        constants = parse_constants(input_text)
        self.assertEqual(constants, {})

if __name__ == '__main__':
    unittest.main()