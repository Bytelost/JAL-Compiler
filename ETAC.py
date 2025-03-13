from lexico import lexic
import sys

# Get the contents of the file
def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return None

# Define the parsing table (from the previous step)
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

class SemanticAnalyzer:
    FUNCTION_ARG_COUNTS = {
        'ADD': 2, 'SUB': 2, 'MUL': 2, 'DIV': 2,
        'AND': 2, 'OR': 2, 'NOT': 1,
        'HIGH': 2, 'LOW': 2, 'EQUAL': 2
    }

    def __init__(self):
        self.scope_stack = [{}]
        self.current_decl_type = None
        self.type_stack = []  # (type, is_variable, value)
        self.function_stack = []
        self.assignment_target = None
        self.in_assignment = False
        self.control_stack = []
        self.in_loop_init = False
        self.etac_code = []
        self.temp_counter = 0

    # Helper methods
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    # Scope management
    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    # Variable declaration/checking
    def declare_variable(self, name, var_type):
        if name in self.scope_stack[-1]:
            raise Exception(f"Variable '{name}' already declared")
        self.scope_stack[-1][name] = var_type
        # Generate ETAC declaration
        default_values = {'int': '0', 'float': '0.0', 'bool': 'false'}
        self.etac_code.append(f"{name}: {var_type} = {default_values[var_type]}")

    def get_variable_type(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise Exception(f"Undefined variable '{name}'")

    # Type checking
    def check_conversion(self, target_type, source_type):
        allowed = {
            ('int', 'float'): True,
            ('float', 'int'): True,
            ('int', 'int'): True,
            ('float', 'float'): True,
            ('bool', 'bool'): True
        }
        if (source_type, target_type) not in allowed:
            raise Exception(f"Cannot convert {source_type} to {target_type}")

    # Function handling
    def handle_function_call(self, function_name):
        function_operators = {
            'ADD': '+',
            'SUB': '-',
            'MUL': '*',
            'DIV': '/',
            'LOW': '<',
            'HIGH': '>',
            'EQUAL': '==',
            'AND': 'and',
            'OR': 'or',
            'NOT': 'not' 
        }
        
        expected_args = self.FUNCTION_ARG_COUNTS.get(function_name, 0)
        args = []
        
        # Collect arguments
        for _ in range(expected_args):
            if not self.type_stack:
                raise Exception(f"Not enough arguments for {function_name}")
            entry = self.type_stack.pop()
            args.insert(0, entry)  # Reverse order

        # Type checking
        arg_types = [t for t, _, _ in args]
        
        # Special handling for NOT
        if function_name == 'NOT':
            if len(args) != 1:
                raise Exception("NOT requires exactly one argument")
            if arg_types[0] != 'bool':
                raise Exception("NOT requires a boolean argument")
            return_type = 'bool'
        else:
            # Existing type checks for other operators
            if function_name in ['ADD', 'SUB', 'MUL', 'DIV']:
                if not all(t in ['int', 'float'] for t in arg_types):
                    raise Exception(f"{function_name} requires numeric arguments")
                return_type = 'float' if 'float' in arg_types else 'int'
            elif function_name in ['AND', 'OR']:
                if not all(t == 'bool' for t in arg_types):
                    raise Exception(f"{function_name} requires boolean arguments")
                return_type = 'bool'
            elif function_name in ['HIGH', 'LOW', 'EQUAL']:
                if not all(t in ['int', 'float'] for t in arg_types):
                    raise Exception(f"{function_name} requires numeric arguments")
                return_type = 'bool'

        # Generate ETAC code with special NOT handling
        temp_var = self.new_temp()
        
        if function_name in function_operators:
            operator = function_operators[function_name]
            arg_values = [arg[2] for arg in args]
            
            if function_name == 'NOT':
                # Unary operator formatting
                self.etac_code.append(f"{temp_var} = {operator} {arg_values[0]}")
            else:
                # Binary operator formatting
                if len(arg_values) == 2:
                    self.etac_code.append(f"{temp_var} = {arg_values[0]} {operator} {arg_values[1]}")
                else:
                    raise Exception(f"Invalid arguments for {function_name}")
        else:
            args_str = ', '.join([arg[2] for arg in args])
            self.etac_code.append(f"{temp_var} = {function_name}({args_str})")

        self.type_stack.append((return_type, False, temp_var))

    # Control structure validation
    def validate_control_condition(self, var_name, struct_type):
        var_type = self.get_variable_type(var_name)
        if struct_type == 'while' and var_type != 'bool':
            raise Exception(f"WHILE condition must be boolean, got {var_type}")
        if struct_type == 'for' and var_type != 'int':
            raise Exception(f"FOR loop variable must be int, got {var_type}")

# Define non-terminals
non_terminals = set(parsing_table.keys())

# Input tokens
file_path = sys.argv[1]
code = read_file(file_path)
input_tokens = lexic(code)

# Extract the terminals from the input tokens
input_terminals = [token[1] for token in input_tokens] + ["$"]  # Add end marker

# Initialize the stack
stack = ["$", "program_start"]

# Initialize the input pointer
input_pointer = 0

# LL(1) Parsing Algorithm
def parse(input_tokens):
    input_terminals = [token[1] for token in input_tokens] + ["$"]
    input_pointer = 0
    stack = ["$", "program_start"]
    analyzer = SemanticAnalyzer()

    while stack:
        top = stack[-1]
        current_input = input_terminals[input_pointer] if input_pointer < len(input_terminals) else "$"
        current_lexeme = input_tokens[input_pointer][0] if input_pointer < len(input_tokens) else None

        # Terminal handling
        if top == current_input:
            # Handle semantic actions
            if top == 'char_esq':
                analyzer.enter_scope()
            elif top == 'char_dir':
                analyzer.exit_scope()
            elif top in ['int', 'float', 'bool']:
                analyzer.current_decl_type = top
            elif top == 'id':
                if analyzer.current_decl_type:
                    analyzer.declare_variable(current_lexeme, analyzer.current_decl_type)
                    analyzer.current_decl_type = None
                else:
                    var_type = analyzer.get_variable_type(current_lexeme)
                    analyzer.type_stack.append((var_type, True, current_lexeme))
            elif top == 'associacao':
                analyzer.in_assignment = True
                analyzer.assignment_target = analyzer.type_stack.pop()
            elif top == 'ponto-virgula':
                if analyzer.in_assignment:
                    source_type, _, source_val = analyzer.type_stack.pop()
                    target_type, _, target_var = analyzer.assignment_target
                    analyzer.check_conversion(target_type, source_type)
                    analyzer.etac_code.append(f"{target_var} = {source_val}")
                    analyzer.in_assignment = False
            elif top in ['num_int', 'nim_sin_int']:
                analyzer.type_stack.append(('int', False, current_lexeme))  # Add value
            elif top in ['num_float', 'nim_sin_float']:
                analyzer.type_stack.append(('float', False, current_lexeme))  # Add value
            elif top in ['true', 'false']:
                analyzer.type_stack.append(('bool', False, current_lexeme.lower()))  # Add value
            elif top in ['high', 'low', 'equal', 'add', 'sub', 'div', 'mul', 'and', 'or', 'not']:
                analyzer.function_stack.append(top.upper())
            elif top == 'par_dir' and analyzer.function_stack:
                analyzer.handle_function_call(analyzer.function_stack.pop())

            # Handle control structures
            if top == 'while':
                analyzer.control_stack.append(('while', analyzer.new_temp()))
            elif top == 'for':
                analyzer.control_stack.append(('for', analyzer.new_temp()))
            elif top == 'if':
                analyzer.control_stack.append(('if', analyzer.new_temp()))

            # Stack operations
            stack.pop()
            input_pointer += 1

        # Non-terminal handling
        elif top in parsing_table:
            production = parsing_table[top].get(current_input, None)
            if not production:
                raise Exception(f"Syntax error: Unexpected {current_input}")
            stack.pop()
            for symbol in reversed(production):
                if symbol != 'vazio':
                    stack.append(symbol)
        else:
            raise Exception(f"Syntax error: Unexpected {current_input}")

    # Final validation and output
    if input_pointer == len(input_terminals) and not stack:
        print("Compilation successful!\n")
        print("Generated ETAC Code:")
        for line in analyzer.etac_code:
            print(line)
    else:
        print("Compilation failed")

if __name__ == "__main__":
    file_path = sys.argv[1]
    code = read_file(file_path)
    if not code:
        print("File not found")
        sys.exit(1)
    input_tokens = lexic(code)
    try:
        parse(input_tokens)
    except Exception as e:
        print(f"Semantic Error: {e}")
        sys.exit(1)