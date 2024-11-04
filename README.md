# Практическая работа 3 по Управлению Конфигурациями

Этот репозиторий содержит Python-проект, демонстрирующий практики модульного тестирования и принципы управления конфигурациями.

## Структура проекта

- `script.py` - Основной файл реализации
- `unit_tests.py` - Модульные тесты для основного функционала

## Начало работы

### Предварительные требования

- Python 3.x
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/Configurartion_managment_practice_3.git
cd Configurartion_managment_practice_3
```

## Запуск тестов

Для запуска модульных тестов:
```bash
python -m unittest unit_tests.py
```

## Примеры использования

### Пример 1: Вычисление квадрата числа
```python
from script import square_number
result = square_number(5)  # Вернёт 25
```

### Пример 2: Проверка на чётность
```python
from script import is_even
result = is_even(4)  # Вернёт True
result = is_even(7)  # Вернёт False
```

## Лицензия

Этот проект лицензирован под MIT License - подробности см. в файле LICENSE.