# to add:
# remove multiline comments

import re
import sys

# symbol table
st = {'SP':0x0, 'LCL':0x1, 'ARG':0x2, 'THIS':0x3, 'THAT':0x4, 'R0':0x0, 
      'R1':0x1, 'R2':0x2, 'R3':0x3, 'R4':0x4, 'R5':0x5, 'R6':0x6, 
      'R7':0x7, 'R8':0x8, 'R9':0x9, 'R10':0xA, 'R11':0xB, 'R12':0xC, 
      'R13':0xD, 'R14':0xE, 'R15':0xF, 'SCREEN':0x4000, 'KBD':0x6000}

# jump table
jt = {'JGT':0x1, 'JEQ':0x2, 'JGE':0x3, 'JLT':0x4, 
      'JNE':0x5, 'JLE':0x6, 'JMP':0x7}

# destination table
dt = {'M':0x8, 'D':0x10, 'MD':0x18, 'A':0x20, 'AM':0x28, 
      'AD':0x30, 'ADM':0x38}

# computation table
ct = {'0':0xA80, '1':0xFC0, '-1':0xE80, 'D':0x300,
      'A':0xC00, '!D':0x340, '!A':0xC40, '-D':0x3C0,
      '-A':0xCC0, 'D+1':0x7C0, 'A+1':0xDC0, 'D-1':0x380,
      'A-1':0xC80, 'D+A':0x80, 'D-A':0x4C0, 'A-D':0x1C0,
      'D&A':0x0, 'D|A':0x540, 'M':0x1C00, '!M':0x1C40,
      '-M':0x1CC0, 'M+1':0x1DC0, 'M-1':0x1C80, 'D+M':0x1080,
      'D-M':0x14C0, 'M-D':0x11C0, 'D&M':0x1000, 'D|M':0x1540}

# patterns to recognize
a_inst = re.compile('@.+')
c_inst = re.compile('[ADM]{1,3}=[01ADM+\-%\|!]{1,3}')
jump = re.compile('[ADM0];J\w\w')
label = re.compile('\(.*\)')

#  initialize some counters and storage
instruction_counter = 0x0
address_counter = 0x10
label_indices = []

# remove whitespace and comments
def clean(asm):
    comment = re.compile('//.*?\n',re.DOTALL)
    asm_no_comment = [re.sub(comment, '', string) for string in asm]
    asm_no_whitespace = [re.sub('\s', '', string) for string in asm_no_comment]
    return asm_no_whitespace

# get filename from CLI arguments - note, should be of the form "ABC" rather than "ABC.xyz"
try:
    filename = sys.argv[1]
    if '.' in filename:
        print('Give me a filename of the form "ABC" rather than "ABC.xyz"')
        sys.exit()
except:
    print('No filename provided as argument. Please provide a filename of the form "ABC" rather than "ABC.xyz"')
    sys.exit()

# read file into list
try:
    with open('./{}.asm'.format(filename),'r') as file:
        asm = file.readlines()
except:
    print('No file was found matching provided filename')
    sys.exit()

# remove comments and whitespace
asm = list(filter(None, clean(asm)))

# create empty ROM list
ROM = [''] * len(asm)

# first pass - handle labels
for i,instruction in enumerate(asm):
    
    # if it's a label
    if bool(re.search(label,instruction)):
        if instruction[1:-1] not in st.keys():
            st[instruction[1:-1]] = instruction_counter
        else:
            print('Repeated label {}'.format(instruction))
        label_indices.append(i)
    
    # if it's any other instruction
    elif (bool(re.search(a_inst,instruction))\
      or bool(re.search(c_inst,instruction))\
      or bool(re.search(jump,instruction))):
        instruction_counter += 0x1
    
    # if it's not a valid instruction
    else:
        print("You done goofed --> {}: {}".format(i,instruction))
        sys.exit()

# remove labels from instructions
for i,index in enumerate(label_indices):
    del asm[index-i]

# second pass - generate machine instructions
for i,instruction in enumerate(asm):
    machine_instruction = 0x0
    
    # if it's a label
    if bool(re.search(label,instruction)):
        print('How did a label make it this far?')
        continue
    
    # if it's an A instruction
    elif bool(re.search(a_inst,instruction)):
        try:
            address = int(instruction[1:])
        except:
            address = instruction[1:]
        if type(address) == str and address not in st.keys():
            st[instruction[1:]] = address_counter
            address_counter += 0x1
        if type(address) == str:
            address = st[address]
        machine_instruction += address
        
    # if it's a C instruction
    elif bool(re.search(c_inst,instruction)):
        lhs,rhs = instruction.split('=')
        machine_instruction += 0xE000
        machine_instruction += ct[rhs]
        machine_instruction += dt[lhs]
        
    # if it's a jump instruction
    elif bool(re.search(jump,instruction)):
        lhs,rhs = instruction.split(';')
        machine_instruction += 0xE000
        machine_instruction += ct[lhs]
        machine_instruction += jt[rhs]
        
    else:
        print("You done goofed --> {}: {}".format(i,instruction))
        sys.exit()
        
    ROM[i] = '{0:016b}'.format(machine_instruction)
    
# write binary file
with open('./{}.hack'.format(filename),'w') as file:
    for instruction in ROM:
        file.write('{}\n'.format(instruction))