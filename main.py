class Memory:
    def __init__(self, size=256):
        self.cells = [0] * size

    def set(self, address, value):
        self.cells[address] = value

    def get(self, address):
        return self.cells[address]

class Parser:
    def __init__(self, code):
        self.lines = code.strip().splitlines()
        self.ast = []

    def parse(self):
        for line in self.lines:
            tokens = line.split()
            if not tokens:  # Пропускаем пустые строки
                continue
            if tokens[0] == "int":
                self.ast.append(("declare_int", tokens[1], int(tokens[2])))
            elif tokens[0] == "bool":
                self.ast.append(("declare_bool", tokens[1], tokens[2] == "true"))
            elif tokens[0] == "string":
                self.ast.append(("declare_string", tokens[1], ' '.join(tokens[2:]).strip('"')))  # Храним строку в виде текста
            elif tokens[0] == "je":
                self.ast.append(("je", tokens[1], tokens[2]))
            elif tokens[0] == "charArr":
                self.ast.append(("declare_array", tokens[1], int(tokens[2])))
            elif tokens[0] == "sys":
                self.ast.append(("sys", tokens[1], int(tokens[2])))
            elif tokens[0] == "from":
                self.ast.append(("move", tokens[1], tokens[3]))
            elif tokens[0] == "add":
                self.ast.append(("add", tokens[1], tokens[2], tokens[3]))  # Добавляем третий аргумент
            elif tokens[0] == "sub":
                self.ast.append(("sub", tokens[1], tokens[2], tokens[3]))
            elif tokens[0] == "mul":
                self.ast.append(("mul", tokens[1], tokens[2], tokens[3]))
            elif tokens[0] == "dev":
                self.ast.append(("dev", tokens[1], tokens[2], tokens[3]))
            elif tokens[0] == "if":
                self.ast.append(("if", tokens[1], tokens[2]))
            elif tokens[0] == "else":
                self.ast.append(("else",))
            elif tokens[0] == "print":
                self.ast.append(("print", ' '.join(tokens[1:])))  # Поддержка печати строк
        return self.ast

class Interpreter:
    def __init__(self, ast, memory):
        self.ast = ast
        self.memory = memory
        self.variables = {}

    def run(self):
        current_else = False  # Переменная для отслеживания else
        for command in self.ast:
            if command[0] == "declare_int":
                var_name, value = command[1], command[2]
                address = len(self.variables)
                self.memory.set(address, value)
                self.variables[var_name] = address
            elif command[0] == "declare_bool":
                var_name, value = command[1], command[2]
                address = len(self.variables)
                self.memory.set(address, int(value))  # Преобразуем True/False в 1/0
                self.variables[var_name] = address
            elif command[0] == "declare_string":
                var_name, value = command[1], command[2]
                address = len(self.variables)
                self.memory.set(address, value)  # Сохраняем строку
                self.variables[var_name] = address
            elif command[0] == "je":
                var_name, label = command[1], command[2]
                address = self.variables.get(var_name)
                if self.memory.get(address) != 0:
                    continue  # Пропускаем если условие истинно
                else:
                    break  # Иначе выходим из цикла
            elif command[0] == "if":
                var_name, label = command[1], command[2]
                address = self.variables.get(var_name)
                if self.memory.get(address) != 0:
                    current_else = False
                else:
                    current_else = True  # Устанавливаем флаг else
            elif command[0] == "else":
                current_else = not current_else  # Меняем флаг else
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
            elif command[0] == "add":
                var1, var2, result = command[1], command[2], command[3]
                if var1 in self.variables and var2 in self.variables:
                    self.memory.set(self.variables[result], self.memory.get(self.variables[var1]) + self.memory.get(self.variables[var2]))
                else:
                    print(f"Error: Undefined variable(s) {var1} or {var2}.")
            elif command[0] == "sub":
                var1, var2, result = command[1], command[2], command[3]
                if var1 in self.variables and var2 in self.variables:
                    self.memory.set(self.variables[result], self.memory.get(self.variables[var1]) - self.memory.get(self.variables[var2]))
                else:
                    print(f"Error: Undefined variable(s) {var1} or {var2}.")
            elif command[0] == "mul":
                var1, var2, result = command[1], command[2], command[3]
                if var1 in self.variables and var2 in self.variables:
                    self.memory.set(self.variables[result], self.memory.get(self.variables[var1]) * self.memory.get(self.variables[var2]))
                else:
                    print(f"Error: Undefined variable(s) {var1} or {var2}.")
            elif command[0] == "dev":
                var1, var2, result = command[1], command[2], command[3]
                if var1 in self.variables and var2 in self.variables:
                    divisor = self.memory.get(self.variables[var2])
                    if divisor == 0:
                        print("Error: Division by zero.")
                    else:
                        self.memory.set(self.variables[result], self.memory.get(self.variables[var1]) // divisor)
                else:
                    print(f"Error: Undefined variable(s) {var1} or {var2}.")
            elif command[0] == "print":
                message = command[1]
                if message.startswith('"') and message.endswith('"'):
                    # Это строка
                    print(message.strip('"'))
                elif message in self.variables:
                    address = self.variables[message]
                    print(self.memory.get(address))
                else:
                    print(f"Undefined variable: {message}")

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
