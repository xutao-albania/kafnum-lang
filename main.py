# Модель памяти
class Memory:
    def __init__(self, size=256):
        self.cells = [0] * size  # Инициализация ячеек памяти значением 0

    def set(self, address, value):
        self.cells[address] = value

    def get(self, address):
        return self.cells[address]

# Парсер команд
class Parser:
    def __init__(self, code):
        self.lines = code.strip().splitlines()
        self.ast = []  # Абстрактное синтаксическое дерево (AST)

    def parse(self):
        for line in self.lines:
            tokens = line.split()
            if tokens[0] == "int":
                self.ast.append(("declare_int", tokens[1], int(tokens[2])))
            elif tokens[0] == "je":
                self.ast.append(("je", tokens[1], tokens[2]))
            elif tokens[0] == "charArr":
                self.ast.append(("declare_array", tokens[1], int(tokens[2])))
            elif tokens[0] == "sys":
                self.ast.append(("sys", tokens[1], int(tokens[2])))
            elif tokens[0] == "from":
                self.ast.append(("move", tokens[1], tokens[3]))
            elif tokens[0] == "print":
                self.ast.append(("print", tokens[1]))  # Добавляем команду print
        return self.ast

# Интерпретатор
class Interpreter:
    def __init__(self, ast, memory):
        self.ast = ast
        self.memory = memory
        self.variables = {}  # Словарь для хранения адресов переменных

    def run(self):
        for command in self.ast:
            if command[0] == "declare_int":
                var_name, value = command[1], command[2]
                address = len(self.variables)  # Простая адресация
                self.memory.set(address, value)
                self.variables[var_name] = address
            elif command[0] == "je":
                var_name, label = command[1], command[2]
                address = self.variables.get(var_name)
                if self.memory.get(address) <= 0:
                    break  # Прерываем выполнение, если значение не положительное
            elif command[0] == "declare_array":
                array_name, size = command[1], command[2]
                base_address = len(self.variables)
                for i in range(size):
                    self.memory.set(base_address + i, 0)
                self.variables[array_name] = base_address
            elif command[0] == "sys":
                if command[1] == "out":
                    exit_code = command[2]
                    print(f"Exit with code {exit_code}")
                    break
            elif command[0] == "move":
                from_var, to_array = command[1], command[2]
                from_address = self.variables.get(from_var)
                to_address = self.variables.get(to_array)
                self.memory.set(to_address, self.memory.get(from_address))
            elif command[0] == "print":
                var_name = command[1]
                if var_name in self.variables:
                    address = self.variables[var_name]
                    print(self.memory.get(address))  # Выводим значение переменной
                else:
                    print(f"Undefined variable: {var_name}")

def load_file(filename):
	with open(filename, "r") as file:
		return file.read()

def main(filename):
	code = load_file(filename)
	memory = Memory()
	parser = Parser(code)
	ast = parser.parse()
	interpreter = Interpreter(ast, memory)
	interpreter.run()

if __name__ == "__main__":
	import sys

	if len(sys.argv) <= 1:
		print(f"usage kafnum <filename>.kaf")
	else:
		main(sys.argv[1])