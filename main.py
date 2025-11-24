import sys
import argparse
import json
import re


class ConfigError(Exception):
    pass


class ConfigParser:
    def __init__(self, text):
        self.text = self._remove_comments(text)
        self.pos = 0
        self.env = {}

    def _remove_comments(self, text):
        return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    def parse(self):
        results = []
        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break

            if self._peek_word() == "var":
                self._parse_var()
            else:
                results.append(self._parse_value())

        return results[0] if len(results) == 1 else results

    def _parse_var(self):
        self._consume_word("var")
        name = self._read_name()
        value = self._parse_value()
        self.env[name] = value

    def _parse_value(self):
        self._skip_whitespace()

        if self._peek() == "'":
            return self._parse_array()
        elif self._peek() == "{":
            return self._parse_const_expr()
        elif self._peek() and (self._peek().isdigit() or self._peek() == "-"):
            return self._parse_number()
        else:
            raise ConfigError(f"Неожиданный символ: {self._peek()}")

    def _parse_array(self):
        self._consume("'")
        self._consume("(")
        elements = []

        while True:
            self._skip_whitespace()
            if self._peek() == ")":
                break
            elements.append(self._parse_value())

        self._consume(")")
        return elements

    def _parse_number(self):
        pattern = r"-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
        match = re.match(pattern, self.text[self.pos:])
        if not match:
            raise ConfigError("Ожидалось число")

        num_str = match.group(0)
        self.pos += len(num_str)

        if "." in num_str or "e" in num_str.lower():
            return float(num_str)
        return int(num_str)

    def _parse_const_expr(self):
        self._consume("{")
        result = self._parse_expr()
        self._consume("}")
        return result

    def _parse_expr(self):
        self._skip_whitespace()
        left = self._parse_term()

        while True:
            self._skip_whitespace()
            if self._peek() == "+":
                self._consume("+")
                right = self._parse_term()
                left = left + right
            else:
                break

        return left

    def _parse_term(self):
        self._skip_whitespace()

        if self._peek() == "(":
            self._consume("(")
            result = self._parse_expr()
            self._consume(")")
            return result

        name = self._read_name()

        self._skip_whitespace()
        if self._peek() == "(":
            return self._parse_function(name)

        if name not in self.env:
            raise ConfigError(f"Неизвестная переменная: {name}")
        return self.env[name]

    def _parse_function(self, name):
        self._consume("(")
        args = []

        while True:
            self._skip_whitespace()
            if self._peek() == ")":
                break

            args.append(self._parse_expr())

            self._skip_whitespace()
            if self._peek() == ",":
                self._consume(",")

        self._consume(")")

        if name == "min":
            return min(args)
        elif name == "concat":
            result = []
            for arg in args:
                if isinstance(arg, list):
                    result.extend(arg)
                else:
                    result.append(arg)
            return result
        else:
            raise ConfigError(f"Неизвестная функция: {name}")

    def _read_name(self):
        self._skip_whitespace()
        match = re.match(r"[A-Z]+", self.text[self.pos:])
        if not match:
            raise ConfigError("Ожидалось имя")
        name = match.group(0)
        self.pos += len(name)
        return name

    def _peek_word(self):
        self._skip_whitespace()
        match = re.match(r"[A-Z]+", self.text[self.pos:])
        return match.group(0) if match else None

    def _consume_word(self, word):
        self._skip_whitespace()
        if not self.text[self.pos:].startswith(word):
            raise ConfigError(f"Ожидалось: {word}")
        self.pos += len(word)

    def _peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def _consume(self, char):
        self._skip_whitespace()
        if self._peek() != char:
            raise ConfigError(f"Ожидался символ: {char}")
        self.pos += 1

    def _skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1


def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык -> JSON")
    parser.add_argument("-o", "--output", required=True, help="Путь к выходному JSON-файлу")
    args = parser.parse_args()

    source = sys.stdin.read()

    try:
        config_parser = ConfigParser(source)
        result = config_parser.parse()
    except ConfigError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()