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
        self.type_stack = []                # Stores (type, is_variable) tuples
        self.function_stack = []
        self.assignment_target = None
        self.in_assignment = False
        self.control_stack = []             # Track loop/control structures
        self.in_loop_init = False           # For FOR loop variable checking
        self.expecting_control_condition = False


    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def declare_variable(self, name, var_type):
        if name in self.scope_stack[-1]:
            raise Exception(f"Variable '{name}' already declared")
        self.scope_stack[-1][name] = var_type

    def get_variable_type(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise Exception(f"Undefined variable '{name}'")

    def check_function_args(self, function_name, arg_types):
        if function_name in ['ADD', 'SUB', 'MUL', 'DIV']:
            for arg_type in arg_types:
                if arg_type not in ['int', 'float']:
                    raise Exception(f"Function {function_name} requires numeric arguments, got {arg_type}")
            return 'float' if 'float' in arg_types else 'int'
        
        elif function_name in ['AND', 'OR', 'NOT']:
            for arg_type in arg_types:
                if arg_type != 'bool':
                    raise Exception(f"Function {function_name} requires boolean arguments, got {arg_type}")
            return 'bool'
        
        elif function_name in ['HIGH', 'LOW', 'EQUAL']:
            for arg_type in arg_types:
                if arg_type not in ['int', 'float']:
                    raise Exception(f"Function {function_name} requires numeric arguments, got {arg_type}")
            return 'bool'

    def check_conversion(self, target_type, source_info):
        source_type, is_source_var = source_info
        if source_type == target_type:
            return
        if is_source_var and {source_type, target_type} == {'int', 'float'}:
            return
        raise Exception(f"Cannot convert {source_type} to {target_type}")
    
    def validate_loop_condition(self, var_name, loop_type):
        var_type = self.get_variable_type(var_name)
        
        if loop_type == 'while':
            if var_type != 'bool':
                raise Exception(f"WHILE loop requires boolean variable, got {var_type}")
            
    def validate_loop_variable(self, var_name):
        var_type = self.get_variable_type(var_name)
        if var_type != 'int':
            raise Exception(f"FOR loop requires INT variable, got {var_type}")
            
    def check_loop_expression(self, expr_type, loop_type):
        if loop_type == 'for' and expr_type != 'int':
            raise Exception(f"FOR loop requires integer expressions, got {expr_type}")


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
            
            # Track loop types
            if top == 'while':
                analyzer.control_stack.append('while')
                analyzer.expecting_control_condition = True
                
            elif top == 'for':
                analyzer.control_stack.append('for')
                analyzer.in_loop_init = True
                
            elif top == 'id' and analyzer.control_stack:
                current_loop = analyzer.control_stack[-1]
                    
                # Loop condition validation
                if analyzer.expecting_control_condition:
                    analyzer.validate_loop_condition(current_lexeme, current_loop)
                    analyzer.expecting_control_condition = False
                    
            elif top == 'id' and analyzer.in_loop_init:
                analyzer.validate_loop_variable(current_lexeme)
                analyzer.in_loop_init = False

            # Handle FOR loop range expressions
            elif top in ['num_int', 'nim_sin_int'] and analyzer.control_stack == 'for':
                analyzer.type_stack.append('int')
                
            elif top in ['num_float', 'nim_sin_float'] and analyzer.control_stack == 'for':
                raise Exception("FOR loop range requires integer values")
            
            # Semantic actions
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
                    analyzer.type_stack.append((var_type, True))
            elif top == 'associacao':
                analyzer.in_assignment = True
                analyzer.assignment_target = None
                if analyzer.type_stack:
                    analyzer.assignment_target = analyzer.type_stack.pop()
            elif top == 'ponto-virgula':
                if analyzer.in_assignment and analyzer.assignment_target:
                    if analyzer.type_stack:
                        source_info = analyzer.type_stack.pop()
                        target_type, _ = analyzer.assignment_target
                        analyzer.check_conversion(target_type, source_info)
                    analyzer.in_assignment = False
            elif top in ['num_int', 'nim_sin_int']:
                analyzer.type_stack.append(('int', False))
            elif top in ['num_float', 'nim_sin_float']:
                analyzer.type_stack.append(('float', False))
            elif top in ['true', 'false']:
                analyzer.type_stack.append(('bool', False))
            elif top in ['add', 'sub', 'mul', 'div', 'and', 'or', 'not', 'high', 'low', 'equal']:
                analyzer.function_stack.append(top.upper())

            # Handle function returns
            if top == 'par_dir' and analyzer.function_stack:
                function_name = analyzer.function_stack.pop()
                expected_args = SemanticAnalyzer.FUNCTION_ARG_COUNTS.get(function_name, 0)
                args = []
                for _ in range(expected_args):
                    if not analyzer.type_stack:
                        raise Exception(f"Not enough arguments for {function_name}")
                    arg_type, _ = analyzer.type_stack.pop()
                    args.append(arg_type)
                args.reverse()
                return_type = analyzer.check_function_args(function_name, args)
                analyzer.type_stack.append((return_type, False))

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
                    
        # Non-terminal handling for loop ranges
        elif top == 'loop_range':
            # Validate all range components are integers
            while len(analyzer.type_stack) > 0:
                expr_type = analyzer.type_stack.pop()
                analyzer.check_loop_expression(expr_type, 'for')

        # Error case
        else:
            raise Exception(f"Syntax error: Unexpected {current_input}")

    # Final validation
    if input_pointer == len(input_terminals) and not stack:
        print("Compilation successful!")
    else:
        print("Compilation failed")
        
# Main execution
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