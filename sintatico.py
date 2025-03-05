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


# Define non-terminals
non_terminals = set(parsing_table.keys())

# Input tokens
file_path = sys.argv[1]
code = read_file(file_path)
input_tokens = lexic(code)
print(input_tokens)

# Extract the terminals from the input tokens
input_terminals = [token[1] for token in input_tokens] + ["$"]  # Add end marker

# Initialize the stack
stack = ["$", "program_start"]

# Initialize the input pointer
input_pointer = 0

# LL(1) Parsing Algorithm
print("Initial Stack:", stack)
while len(stack) > 0:
    top = stack[-1]
    current_input = input_terminals[input_pointer]

    if top == current_input:
        
        # Pop the stack and move the input pointer
        stack.pop()
        input_pointer += 1
        
    elif top in non_terminals:
        
        # Look up the parsing table
        if current_input in parsing_table[top]:
            production = parsing_table[top][current_input]
            stack.pop()
            
            # Push the production in reverse order
            for symbol in reversed(production):
                if symbol != "vazio":  # Skip empty productions
                    stack.append(symbol)
        else:
            break
    else:
        break


# Check if parsing was successful
if input_pointer == len(input_terminals) and len(stack) == 0:
    print("\nParsing successful!")
else:
    print("\nParsing failed.")