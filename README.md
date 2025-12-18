# Отчет: Парсер учебного конфигурационного языка

## Описание
Проект представляет собой парсер для учебного конфигурационного языка, написанный на Python. Программа считывает конфигурацию из стандартного ввода, парсит её согласно заданной грамматике и сохраняет результат в JSON-файл.

## Основные возможности
1. **Объявление констант** с помощью ключевого слова `var`
2. **Поддерживаемые типы данных**:
   - Целые и дробные числа (включая экспоненциальную запись)
   - Массивы значений
   - Константные выражения
3. **Математические операции**: сложение (`+`)
4. **Встроенные функции**:
   - `min()` - поиск минимального значения среди чисел и массивов
   - `concat()` - конкатенация массивов и значений
5. **Комментарии**: многострочные комментарии в формате `<!-- комментарий -->`
6. **Имена констант**: только заглавные латинские буквы (`[A-Z]+`)

## Грамматика языка
```
program     = (var_decl | expression)*
var_decl    = "var" NAME value
expression  = const_expression | value
value       = number | array | const_expression
const_expression = "{" expression "}"
array       = "'(" value* ")"
number      = -?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?
```

## Параметры командной строки
- `-o, --output` - путь к выходному JSON-файлу (обязательный параметр)

## Примеры работы

### Пример 1: Простые константы
**Входные данные:**
```
var A 10
var B 20
{ A + B }
```

**Результат (output.json):**
```json
{
  "A": 10,
  "B": 20,
  "_result": 30
}
```

### Пример 2: Массивы и функции
**Входные данные:**
```
var ARR1 '( 1 2 3 )
var ARR2 '( 4 5 )
{ concat(ARR1, ARR2, 6) }
```

**Результат:**
```json
{
  "ARR1": [1, 2, 3],
  "ARR2": [4, 5],
  "_result": [1, 2, 3, 4, 5, 6]
}
```

### Пример 3: Функция min()
**Входные данные:**
```
var A 5
var B 3
var MINIMUM {min(A, B)}
```

**Результат:**
```json
{
  "A": 5,
  "B": 3,
  "MINIMUM": 3
}
```

### Пример 4: Только выражение без констант
**Ввод:**
```
{ 5 + 3.14 + 2e2 }
```

**Вывод:**
```json
{
  "_result": 208.14
}
```

## Тесты
### Пример описания конфигураций из разных предметных областей
#### Параметры персонажа
**Ввод:**
````
python main.py -o output.json << 'EOF'
<!-- Параметры персонажа -->
var BASEHEALTH 100
var BONUSHEALTH 25
var HEALTH {BASEHEALTH + BONUSHEALTH}
var SKILLS '( 10 15 20 )
var BUFFS '( 5 10 )
var ALLBONUSES {concat(SKILLS, BUFFS)}
EOF
````

**Вывод (output.json):**
```json
{
  "BASEHEALTH": 100,
  "BONUSHEALTH": 25,
  "HEALTH": 125,
  "SKILLS": [10, 15, 20],
  "BUFFS": [5, 10],
  "ALLBONUSES": [10, 15, 20, 5, 10]
}
```

#### Конфигурация веб-сервера
**Ввод:**
````
python main.py -o output.json << 'EOF'
<!-- Конфигурация веб-сервера -->
var PORT 8080
var MAXCONN 100
var TIMEOUT 30
var MINTHREADS 4
var MAXTHREADS 16
var THREADS {min(MAXCONN, MAXTHREADS)}
EOF
````
**Вывод (output.json):**
```json
{
  "PORT": 8080,
  "MAXCONN": 100,
  "TIMEOUT": 30,
  "MINTHREADS": 4,
  "MAXTHREADS": 16,
  "THREADS": 16
}
```

## Тестовые команды для проверки функциональности

### Базовые тесты чисел
```bash
# Целые числа
echo "var X 42" | python main.py -o output.json

# Отрицательные числа
echo "var X -15" | python main.py -o output.json

# Дробные числа
echo "var X 3.14159" | python main.py -o output.json

# Экспоненциальная запись
echo "var X 2.5e-3" | python main.py -o output.json
```

### Тесты массивов
```bash
# Простой массив
echo "var ARR '( 1 2 3 4 5 )" | python main.py -o output.json

# Вложенные массивы
echo "var ARR '( 1 '( 2 3 ) 4 )" | python main.py -o output.json

# Пустой массив
echo "var ARR '( )" | python main.py -o output.json
```

### Тесты констант и выражений
```bash
# Константы с сложением
python main.py -o output.json << 'EOF'
var A 10
var B 20
var SUM {A + B}
EOF


# Множественные операции
python main.py -o output.json << 'EOF'
var A 5
var B 3
var C 7
var RESULT {A + B + C}
EOF

```

### Тесты функции min()
```bash
# Простой min
python main.py -o output.json << 'EOF'
var A 5
var B 3
var MINIMUM {min(A, B)}
EOF


# min с несколькими аргументами
python main.py -o output.json << 'EOF'
var X 100
var Y 50
var Z 75
var MINVAL {min(X, Y, Z)}
EOF

# min с массивом
python main.py -o output.json << 'EOF'
var ARR '( 10 5 20 15 )
var MINVAL {min(ARR)}
EOF


# min с массивами и числами
python main.py -o output.json << 'EOF'
var ARR1 '( 25 50 )
var ARR2 '( 10 30 )
var MINVAL {min(ARR1, ARR2, 5)}
EOF
```

### Тесты функции concat()
```bash
# Простой concat
python main.py -o output.json << 'EOF'
var ARR1 '( 1 2 )
var ARR2 '( 3 4 )
var MERGED {concat(ARR1, ARR2)}
EOF


# concat с числами
python main.py -o output.json << 'EOF'
var SKILLS '( 10 15 20 )
var BUFFS '( 5 10 )
var ALLBONUSES {concat(SKILLS, BUFFS, 25)}
EOF


# concat с несколькими массивами
python main.py -o output.json << 'EOF'
var ARR1 '( 1 2 )
var ARR2 '( 3 4 )
var ARR3 '( 5 6 )
var ALL {concat(ARR1, ARR2, ARR3)}
EOF
```

### Комбинированные тесты
```bash
# Комбинация min + concat
python main.py -o output.json << 'EOF'
var MAXCONN 100
var MAXTHREADS 16
var THREADS {min(MAXCONN, MAXTHREADS)}
var ARR1 '( 1 2 3 )
var ARR2 '( 4 5 )
var COMBINED {concat(ARR1, ARR2)}
EOF

# Комплексный пример
python main.py -o output.json << 'EOF'
var A 100
var B 200
var C 50
var ARR1 '( 25 75 150 )
var ARR2 '( 10 20 30 )
var MIN1 { min(A, B, C) }
var MIN2 { min(ARR1) }
var COMBINED { concat(ARR1, ARR2, MIN1, MIN2) }
EOF
```

### Тесты с комментариями
```bash
# Конфигурация с комментариями
python main.py -o output.json << 'EOF'
<!-- Это главный заголовок -->
var BASE 100 <!-- базовое значение -->
var BONUS 25 <!-- дополнительный бонус -->
<!-- Итоговый результат -->
var TOTAL { BASE + BONUS }
EOF

# Многострочные комментарии
python main.py -o output.json << 'EOF'
<!--
  Это многострочный комментарий
  который занимает несколько строк
-->
var X 10
var Y 20
EOF
```

## Обработка ошибок
Программа корректно обрабатывает:
- Синтаксические ошибки в конфигурации
- Неопределённые константы
- Неправильно закрытые скобки и комментарии
- Ошибки в формате чисел

## Структура проекта
- `ConfigParser` - основной класс парсера
- Рекурсивный спуск для разбора выражений
- Поддержка инфиксных операций
- Контекст хранения констант