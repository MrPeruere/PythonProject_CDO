import sys
import re
import json
import argparse


class ConfigParser:
    """Парсер учебного конфигурационного языка."""

    def __init__(self):
        self.constants = {}
        self.pos = 0
        self.text = ""

    def parse(self, text):
        """Основной метод парсинга."""
        self.text = text
        self.pos = 0
        self.constants = {}
        result = {}

        while self.pos < len(self.text):
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.text):
                break

            if self.match_keyword("var"):
                name, value = self.parse_var_declaration()
                self.constants[name] = value
                result[name] = value
            elif self.pos < len(self.text):
                # Если это не var, пробуем распарсить как значение
                value = self.parse_value()
                result["_result"] = value

        return result

    def skip_whitespace_and_comments(self):
        """Пропуск пробелов и комментариев."""
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                self.pos += 1
            elif self.text[self.pos:self.pos+4] == "<!--":
                end = self.text.find("-->", self.pos + 4)
                if end == -1:
                    raise SyntaxError(f"Незакрытый комментарий на позиции {self.pos}")
                self.pos = end + 3
            else:
                break

    def match_keyword(self, keyword):
        """Проверка и потребление ключевого слова."""
        self.skip_whitespace_and_comments()
        if self.pos < len(self.text) and self.text[self.pos:self.pos+len(keyword)] == keyword:
            if self.pos + len(keyword) >= len(self.text) or not self.text[self.pos + len(keyword)].isalnum():
                self.pos += len(keyword)
                return True
        return False

    def parse_var_declaration(self):
        """Парсинг объявления константы: var имя значение"""
        self.skip_whitespace_and_comments()
        name = self.parse_name()
        self.skip_whitespace_and_comments()
        value = self.parse_value()
        return name, value

    def parse_name(self):
        """Парсинг имени: [A-Z]+"""
        self.skip_whitespace_and_comments()
        match = re.match(r'[A-Z]+', self.text[self.pos:])
        if not match:
            raise SyntaxError(f"Ожидалось имя (заглавные буквы) на позиции {self.pos}")
        name = match.group()
        self.pos += len(name)
        return name

    def parse_value(self):
        """Парсинг значения: число, массив или константное выражение."""
        self.skip_whitespace_and_comments()

        if self.pos >= len(self.text):
            raise SyntaxError("Неожиданный конец ввода при парсинге значения")

        if self.text[self.pos] == '{':
            return self.parse_const_expression()
        elif self.text[self.pos:self.pos+2] == "'(":
            return self.parse_array()
        else:
            return self.parse_number()

    def parse_number(self):
        """Парсинг числа: -?(\d+|\d+\.\d*|\.\d+)([eE][-+]?\d+)?"""
        self.skip_whitespace_and_comments()
        pattern = r'-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?'
        match = re.match(pattern, self.text[self.pos:])
        if not match:
            raise SyntaxError(f"Ожидалось число на позиции {self.pos}")
        num_str = match.group()
        self.pos += len(num_str)

        if '.' in num_str or 'e' in num_str.lower():
            return float(num_str)
        return int(num_str)

    def parse_array(self):
        """Парсинг массива: '( значение значение ... )"""
        self.skip_whitespace_and_comments()

        if self.text[self.pos:self.pos+2] != "'(":
            raise SyntaxError(f"Ожидалось '(' на позиции {self.pos}")
        self.pos += 2

        values = []
        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.text):
                raise SyntaxError("Незакрытый массив")
            if self.text[self.pos] == ')':
                self.pos += 1
                break
            values.append(self.parse_value())

        return values

    def parse_const_expression(self):
        """Парсинг константного выражения: {выражение}"""
        self.skip_whitespace_and_comments()

        if self.text[self.pos] != '{':
            raise SyntaxError(f"Ожидалось '{{' на позиции {self.pos}")
        self.pos += 1

        result = self.parse_expression()

        self.skip_whitespace_and_comments()
        if self.pos >= len(self.text) or self.text[self.pos] != '}':
            raise SyntaxError(f"Ожидалось '}}' на позиции {self.pos}")
        self.pos += 1

        return result

    def parse_expression(self):
        """Парсинг выражения (инфиксная форма с операцией +)."""
        self.skip_whitespace_and_comments()
        left = self.parse_term()

        while True:
            self.skip_whitespace_and_comments()
            if self.pos < len(self.text) and self.text[self.pos] == '+':
                self.pos += 1
                self.skip_whitespace_and_comments()
                right = self.parse_term()
                left = left + right
            else:
                break

        return left

    def parse_term(self):
        """Парсинг терма: число, имя константы или вызов функции."""
        self.skip_whitespace_and_comments()

        if self.pos >= len(self.text):
            raise SyntaxError("Неожиданный конец выражения")

        if self.text[self.pos:self.pos+4] == "min(":
            return self.parse_min_function()
        elif self.text[self.pos:self.pos+7] == "concat(":
            return self.parse_concat_function()
        elif self.text[self.pos:self.pos+2] == "'(":
            return self.parse_array()
        elif re.match(r'[A-Z]', self.text[self.pos:]):
            name = self.parse_name()
            if name not in self.constants:
                raise SyntaxError(f"Неизвестная константа: {name}")
            return self.constants[name]
        else:
            return self.parse_number()

    def parse_min_function(self):
        """Парсинг функции min()."""
        self.pos += 4
        args = self.parse_function_args()

        if not args:
            raise SyntaxError("min() требует хотя бы один аргумент")

        all_numbers = []
        for arg in args:
            if isinstance(arg, list):
                all_numbers.extend(arg)
            else:
                all_numbers.append(arg)

        return min(all_numbers)

    def parse_concat_function(self):
        """Парсинг функции concat()."""
        self.pos += 7
        args = self.parse_function_args()

        result = []
        for arg in args:
            if isinstance(arg, list):
                result.extend(arg)
            else:
                result.append(arg)

        return result

    def parse_function_args(self):
        """Парсинг аргументов функции."""
        args = []

        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.text):
                raise SyntaxError("Незакрытая функция")
            if self.text[self.pos] == ')':
                self.pos += 1
                break
            if self.text[self.pos] == ',':
                self.pos += 1
                continue
            args.append(self.parse_expression())

        return args


def main():
    arg_parser = argparse.ArgumentParser(
        description="Парсер учебного конфигурационного языка"
    )
    arg_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Путь к выходному JSON файлу"
    )

    args = arg_parser.parse_args()
    input_text = sys.stdin.read()
    parser = ConfigParser()

    try:
        result = parser.parse(input_text)

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Результат записан в {args.output}")

    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()