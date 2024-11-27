import argparse
import re
import sys
import toml

COMMENT_START = r"#="
COMMENT_END = r"=#"
DICTIONARY_START = r"\$\["
DICTIONARY_END = r"\]"
CONSTANT_DECLARATION = r"([_a-z]+)\s*:=\s*(.+)"
CONSTANT_EVALUATION = r"@\(([_a-z]+)\)"
STRING_VALUE = r"'([^']*)'"
NUMBER_VALUE = r"\d+"
KEY_VALUE_PAIR = r"([_a-z]+)\s*:\s*(.+)"

class SyntaxError(Exception):
    pass

class Translator:
    def __init__(self):
        self.constants = {}

    def parse_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        return self.parse(content)
    def parse(self, text):
        text = self.remove_comments(text)
        lines = text.splitlines()
        result = {}
        while lines:
            line = lines.pop(0).strip()
            if not line:
                continue
            if match := re.match(CONSTANT_DECLARATION, line):
                self.handle_constant_declaration(match)
            elif re.match(DICTIONARY_START, line):
                dict_lines = []
                while lines:
                    dict_line = lines.pop(0).strip()
                    dict_lines.append(dict_line)
                    if dict_line == "]":
                        break
                result.update(self.parse_dictionary(dict_lines))
            else:
                raise SyntaxError(f"Invalid syntax: {line}")
        return result


    def remove_comments(self, text):
        return re.sub(f"{COMMENT_START}.*?{COMMENT_END}", "", text, flags=re.DOTALL)

    def handle_constant_declaration(self, match):
        name, value = match.groups()
        self.constants[name] = self.evaluate_value(value)

    def evaluate_value(self, value):
        value = value.strip()
        if re.fullmatch(NUMBER_VALUE, value):
            return int(value)
        elif match := re.match(STRING_VALUE, value):
            return match.group(1)
        elif match := re.match(CONSTANT_EVALUATION, value):
            name = match.group(1)
            if name in self.constants:
                return self.constants[name]
            else:
                raise SyntaxError(f"Undefined constant: {name}")
        elif value in ["true", "false"]: 
            return value == "true"
        else:
            raise SyntaxError(f"Invalid value: {value}")

    def parse_dictionary(self, lines):
        result = {}
        while lines:
            line = lines.pop(0).strip()
            if line == "]": 
                break
            if line.endswith(","):
                line = line[:-1].strip()
            if match := re.match(KEY_VALUE_PAIR, line):
                key, value = match.groups()
                result[key] = self.evaluate_value(value)
            else:
                raise SyntaxError(f"Invalid dictionary syntax: {line}")
        return result

    def to_toml(self, data):
        return toml.dumps(data)

def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык -> TOML")
    parser.add_argument("input_file", help="Путь к входному файлу конфигурации")
    args = parser.parse_args()

    translator = Translator()
    try:
        data = translator.parse_file(args.input_file)
        print(translator.to_toml(data))
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
