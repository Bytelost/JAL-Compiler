from lexico import lexic
import sys

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = [{}]  # Stack of scopes
        self.current_scope = 0
        self.current_decl_type = None
        self.type_conversions = {
            ('int', 'float'): 'float',
            ('float', 'int'): 'float',
            ('int', 'bool'): 'bool',
            ('float', 'bool'): 'bool',
            ('bool', 'int'): 'int',
            ('bool', 'float'): 'float'
        }

    def enter_scope(self):
        self.symbol_table.append({})
        self.current_scope += 1
        print(f"Entered new scope (Line {self.current_scope})")

    def exit_scope(self):
        if self.current_scope > 0:
            self.symbol_table.pop()
            self.current_scope -= 1
            print(f"Exited scope (Line {self.current_scope})")

    def declare_variable(self, name, var_type, line):
        if name in self.symbol_table[self.current_scope]:
            print(f"Semantic Error (Line {line}): Redeclaration of '{name}'")
            return False
            
        self.symbol_table[self.current_scope][name] = var_type.lower()
        print(f"Declared '{name}' as {var_type.upper()} (Line {line})")
        return True

    def lookup_variable(self, name, line):
        """NEW METHOD: Check variable existence in current and parent scopes"""
        for i in range(self.current_scope, -1, -1):
            if name in self.symbol_table[i]:
                return self.symbol_table[i][name]
        print(f"Semantic Error (Line {line}): Undeclared variable '{name}'")
        return None

    def check_type_compatibility(self, target_type, source_type, line, is_assignment=False):
        target_type = target_type.lower()
        source_type = source_type.lower()

        if target_type == source_type:
            return True

        # Handle numeric to bool conversions
        if target_type == 'bool' and source_type in ['int', 'float']:
            print(f"Type Warning (Line {line}): Implicit conversion from {source_type} to bool")
            return True

        if (source_type, target_type) in self.type_conversions:
            if is_assignment and source_type == 'float' and target_type == 'int':
                print(f"Type Warning (Line {line}): Possible precision loss in float->int conversion")
            return True

        print(f"Type Error (Line {line}): Incompatible types {source_type}->{target_type}")
        return False

def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return None

parsing_table = {
    'program_start': {
        'start': ['start', 'char_esq', 'code', 'end', 'ponto-virgula', 'char_dir']
    },

    'code': {
        'int': ['stmt', 'code'],
        'float': ['stmt', 'code'],
        'bool': ['stmt', 'code'],
        'id': ['stmt', 'code'],
        'if': ['stmt', 'code'],
        'while': ['stmt', 'code'],
        'for': ['stmt', 'code'],
        'in': ['stmt', 'code'],
        'out': ['stmt', 'code'],
        'end': ['vazio'],
        'char_dir': ['char_dir'],
        'else': ['stmt', 'code']
    },

    'stmt': {
        'int': ['declaration'],
        'float': ['declaration'],
        'bool': ['declaration'],
        'id': ['command'],
        'if': ['command'],
        'else': ['command'],
        'while': ['command'],
        'for': ['command'],
        'in': ['command'],
        'out': ['command']
    },

    'declaration': {
        'int': ['type', 'variable'],
        'float': ['type', 'variable'],
        'bool': ['type', 'variable']
    },

    'type': {
        'int': ['int'],
        'float': ['float'],
        'bool': ['bool']
    },

    'variable': {
        'id': ['identifier', 'ponto-virgula']
    },

    'command': {
        'id': ['identifier_command'],
        'if': ['control_command'],
        'while': ['control_command'],
        'for': ['control_command'],
        'in': ['io_command', 'ponto-virgula'],
        'out': ['io_command', 'ponto-virgula'],
        'else': ['control_command']
    },

    'identifier_command': {
        'id': ['identifier', 'associacao', 'expression', 'ponto-virgula']
    },

    'control_command': {
        'if': ['if', 'par_esq', 'identifier', 'par_dir', 'char_esq', 'code'],
        'while': ['while', 'par_esq', 'identifier', 'par_dir', 'char_esq', 'code'],
        'for': ['for', 'par_esq', 'identifier', 'par_dir', 'char_esq', 'code'],
        'else': ['else', 'char_esq', 'code']
    },

    'function': {
        'high': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'low': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'equal': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'add': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'sub': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'div': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'mul': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'and': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'or': ['function_name', 'par_esq', 'argument_list', 'par_dir'],
        'not': ['function_name', 'par_esq', 'argument_list', 'par_dir']
    },

    'argument_list': {
        'num_int': ['expression', 'argument_tail'],
        'num_float': ['expression', 'argument_tail'],
        'nim_sin_int': ['expression', 'argument_tail'],
        'nim_sin_float': ['expression', 'argument_tail'],
        'true': ['expression', 'argument_tail'],
        'false': ['expression', 'argument_tail'],
        'id': ['expression', 'argument_tail'],
        'high': ['expression', 'argument_tail'],
        'low': ['expression', 'argument_tail'],
        'equal': ['expression', 'argument_tail'],
        'add': ['expression', 'argument_tail'],
        'sub': ['expression', 'argument_tail'],
        'div': ['expression', 'argument_tail'],
        'mul': ['expression', 'argument_tail'],
        'and': ['expression', 'argument_tail'],
        'or': ['expression', 'argument_tail'],
        'not': ['expression', 'argument_tail']
    },

    'argument_tail': {
        'virgula': ['virgula', 'argument_list'],
        'par_dir': ['vazio']
    },

    'expression': {
        'num_int': ['num_int'],
        'num_float': ['num_float'],
        'nim_sin_int': ['nim_sin_int'],
        'nim_sin_float': ['nim_sin_float'],
        'true': ['true'],
        'false': ['false'],
        'id': ['identifier'],
        'high': ['function'],
        'low': ['function'],
        'equal': ['function'],
        'add': ['function'],
        'sub': ['function'],
        'div': ['function'],
        'mul': ['function'],
        'and': ['function'],
        'or': ['function'],
        'not': ['function']
    },

    'identifier': {
        'id': ['id']
    },

    'function_name': {
        'high': ['high'],
        'low': ['low'],
        'equal': ['equal'],
        'add': ['add'],
        'sub': ['sub'],
        'div': ['div'],
        'mul': ['mul'],
        'and': ['and'],
        'or': ['or'],
        'not': ['not']
    },

    'io_command': {
        'in': ['in', 'par_esq', 'identifier', 'par_dir'],
        'out': ['out', 'par_esq', 'identifier', 'par_dir']
    }
}

# Define non-terminals
non_terminals = set(parsing_table.keys())

# Initialize analyzer and parse
file_path = sys.argv[1]
code = read_file(file_path)
input_tokens = lexic(code)
input_tokens.append(('$', '$', -1))

analyzer = SemanticAnalyzer()
stack = ["$", "program_start"]
input_pointer = 0

# Track expression types for semantic checks
expression_type_stack = []

while len(stack) > 0:
    top = stack[-1]
    current_token = input_tokens[input_pointer]
    current_input_type = current_token[1]
    lexeme = current_token[0]
    line = current_token[2]

    if top == current_input_type:
        # Handle semantic actions
        if top in ['int', 'float', 'bool']:
            analyzer.current_decl_type = lexeme
        elif top == 'id':
            if analyzer.current_decl_type:  # Declaration
                if analyzer.declare_variable(lexeme, analyzer.current_decl_type, line):
                    print(f"Declared '{lexeme}' as {analyzer.current_decl_type} (Line {line})")
                analyzer.current_decl_type = None
            else:  # Usage
                var_type = analyzer.lookup_variable(lexeme, line)
                if var_type:
                    expression_type_stack.append(var_type)
        elif top == 'char_esq':
            analyzer.enter_scope()
            print(f"Entered new scope (Line {line})")
        elif top == 'char_dir':
            analyzer.exit_scope()
            print(f"Exited scope (Line {line})")
        elif top == 'associacao':
            # Get last two types from expression stack (identifier and value)
            if len(expression_type_stack) >= 2:
                target_type = expression_type_stack[-2]
                value_type = expression_type_stack[-1]
                analyzer.check_type_compatibility(target_type, value_type, line, is_assignment=True)
                expression_type_stack = expression_type_stack[:-2] + [target_type]

        stack.pop()
        input_pointer += 1

    elif top in non_terminals:
        if current_input_type in parsing_table[top]:
            production = parsing_table[top][current_input_type]
            stack.pop()
            for symbol in reversed(production):
                if symbol != "vazio":
                    stack.append(symbol)
            
            # Handle expression type propagation
            if top == 'expression':
                if len(expression_type_stack) >= 1:
                    expr_type = expression_type_stack.pop()
                    expression_type_stack.append(expr_type)
        else:
            print(f"Syntax Error (Line {line}): Unexpected token '{lexeme}'")
            break
    else:
        print(f"Syntax Error (Line {line}): Unexpected token '{lexeme}'")
        break