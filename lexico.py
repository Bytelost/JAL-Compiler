import sys

# Token Table
token_table = [
    ("START", "start"),
    ("END", "end"),
    ("INT", "int"),
    ("FLOAT", "float"),
    ("BOOL", "bool"),
    ("ADD", "add"),
    ("SUB", "sub"),
    ("MUL", "mul"),
    ("DIV", "div"),
    ("HIGH", "high"),
    ("LOW", "low"),
    ("EQUAL", "equal"),
    ("NOT", "not"),
    ("AND", "and"),
    ("OR", "or"),
    ("IN", "int"),
    ("OUT", "out"),
    ("IF", "if"),
    ("ELSE", "else"),
    ("WHILE", "while"),
    ("FOR", "for"),
    ("TRUE", "true"),
    ("FALSE", "false"),
    ("(", "par_esq"),
    (")", "par_dir"),
    ("{", "cha_esq"),
    ("}", "cha_dir"),
    (",", "virgula"),
    (";", "ponto-virgula"),
    ("=", "associasao")
]

# Symbol list
symbols = ['(', ')', '{', '}', ',', ';', '=']

# Get the contents of the file
def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return None

def keywords_var(count, line, token_list, line_num, token_table):
    
    # Make the table into a dictionary
    token_dict = dict(token_table)
    
    # List o capture characters
    char_list = []
    
    # Mount the string
    while(line[count].isalpha() or line[count].isdigit()):
        char_list.append(line[count])
        count += 1
    string = ''.join(char_list)
    
    # See if its a keyword and put on the list
    if(string in token_dict):
        token_list.append((string, token_dict[string], line_num))
    else:
        token_list.append((string, 'id', line_num))
    
    # Return the pointer
    return count

def symbol_token(char, token_list, line_num, token_table):
    
    # Make the table into a dictionary
    token_dict = dict(token_table)
    
    if(char in token_dict):
        token_list.append((char, token_dict[char], line_num))

def number_token(count, line, token_list, line_num, token_table):
    
    # List o capture characters
    num_list = []
    
    # Mount the string
    while(line[count].isdigit() or line[count] == '.'):
        num_list.append(line[count])
        count += 1
    number = ''.join(num_list)
    
    # Check if the number is an float or int
    if('.' in number):
        # Put the number on token list
        token_list.append((number, 'num_float', line_num))
        
    else:
        # Put the number on token list
        token_list.append((number, 'num_int', line_num))
    
    # Return the pointer 
    return count

def number_token_sin(count, line, token_list, line_num, token_table):
    
    # List o capture characters
    num_list = []
    
    # Get the signal
    num_list.append(line[count])
    count += 1
    
    # Get the number
    while(line[count].isdigit() or line[count] == '.'):
        num_list.append(line[count])
        count += 1
    number = ''.join(num_list)
    
    # Check if the number is an float or int
    if('.' in number):
        # Put the number on token list
        token_list.append((number, 'num_float_sin', line_num))
        
    else:
        # Put the number on token list
        token_list.append((number, 'num_int_sin', line_num))
    
    # Return the pointer 
    return count
    
    

def main():
    file_path = sys.argv[1]
    code = read_file(file_path)
    tokens = []
    line_num = 1
    
    # Get each line of the code
    for line in code:
        
        # Control variables
        lenght = len(line)
        count = 0
        
        while(count < lenght):
            
            # Check if its a space
            if(line[count].isspace()):
                count += 1
                continue
            
            # Check if its a line break
            elif(line[count] == "\n"):
                break
            
            # Check if its a comment
            elif(line[count] == "#"):
                while(count < lenght and line[count] != "\n"):
                    count += 1
                
            # Check if its a keyword or variable
            elif(line[count].isalpha()):
                count = keywords_var(count, line, tokens, line_num, token_table) - 1
            
            # Check if its an symbol
            elif(line[count] in symbols):
                symbol_token(line[count], tokens, line_num, token_table)
                
            # Check if its an number
            elif(line[count].isdecimal()):
                count = number_token(count, line, tokens, line_num, token_table) - 1
            
            # Check if its an singnalized number
            elif(line[count] == '-'):
                if(line[count + 1].isdecimal()):
                    count = number_token_sin(count, line, tokens, line_num, token_table) - 1
            
            else:
                print("Erro encontrado na linha", line_num)
            
            count += 1
        
        # Next line
        line_num += 1
    
    print('\n', tokens)      
            
        
        
main()
