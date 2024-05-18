import sys
import sscfcmp

# Get program
inp = input("XEN file to run: ")
fio = open(inp, "rt")
prog = fio.read()
fio.close()
# Convert into binary
try:
  prog = prog.encode("sscfcmp").hex()
except:
  print("Program could not be decoded using SSCfCMP.")
  sys.exit()
bi = []
for e in range(0,len(prog),2):
  n1 = int(prog[e],16)
  n2 = int(prog[e+1],16)
  n1 = bin(n1)[2:]
  n2 = bin(n2)[2:]
  if len(n1) < 4:
    n1 = "0"*(4-len(n1)) + n1 # strings  can be multiplied?
  if len(n2) < 4:
    n2 = "0"*(4-len(n2)) + n2
  bi.append(n1 + n2)
bi = "".join(bi)
# Unpad it
padam = bi[:3]
padam = int(padam,2)
try:
  bi = bi[3:-padam]
except:
  print("Invalid padding.")
  sys.exit()

# -----------------
# ----- LEXER -----
# -----------------

# Xenon constants
nio = ["00100", "01101", "10100"] # Opcodes without extra arguments
oio = ["00101", "01010", "01011", "01100", "10000", "10001", "10010", "10011", "10101", "10110"] # Opcodes with one argument
tio = ["00000", "00001", "00111", "01000", "01001", "01110", "01111"] # Opcodes with two arguments
thio = ["00010", "00011", "00110"]
opcodes = nio + oio + tio + thio

def literalscan(bincode, sindex, opcode): # Get literal starting at code index sindex
  # Scan for 11000
  i = sindex+5
  literalcheck = False
  while bincode[i:i+5] != "":
    if bincode[i:i+5] == "11000":
      literalcheck = True
      break
    i += 1
  if not literalcheck:
    print(f"Syntax error: literal after operation {opcode} opened with 10111 but never closed with 11000.")
    sys.exit()
  else:
    return [bincode[sindex+5:i], i]

def registerscan(bincode, sindex, opcode): # Get register index starting at code index sindex
  count = 0
  while bincode[sindex+count] == "1":
    count += 1
  if count == 0:
    print(f"Syntax error: operation {opcode} expected input but did not receive any.")
    sys.exit()
  return [count-1, sindex+count+1]

def argscan(bincode, sindex, opcode): # Checks if the argument at sindex is a literal or register, and parses accordingly
  literalcheck = bincode[sindex:sindex+5]
  if literalcheck == "10111":
    lit = literalscan(bincode, sindex, opcode)[0]
    stopindex = literalscan(bincode, sindex, opcode)[1]+5
    return [lit, stopindex]
  else:
    return registerscan(bincode, sindex, opcode)

def lexer(bincode):
  global opcodes, nio
  stopindex = 0
  if len(bincode) < 5:
    print("Program invalid or too short.")
    sys.exit()
  opcode = bincode[:5]
  if opcode not in opcodes:
    lexres = []
    stopindex = 5
  elif opcode in nio:
    lexres = [[int(opcode,2)]]
    stopindex = 5
  else:
    # Get the arguments
    farg = argscan(bincode, 5, opcode)
    if type(farg[0]) == str:
      stopindex = farg[1]
      lexres = [[int(opcode,2),farg[0]]]
    else:
      if opcode in oio:
        stopindex = farg[1]
        lexres = [[int(opcode,2),farg[0]]]
      elif opcode in tio:
        scount = argscan(bincode, farg[1], opcode)
        stopindex = scount[1]
        lexres = [[int(opcode,2),farg[0],scount[0]]]
      elif opcode in thio:
        scount = argscan(bincode, farg[1], opcode)
        tcount = argscan(bincode, scount[1], opcode)
        stopindex = tcount[1]
        lexres = [[int(opcode,2),farg[0],scount[0],tcount[0]]]
  if len(bincode[stopindex:]) < 5:
    return lexres
  else:
    return lexres + lexer(bincode[stopindex:])

lexed = lexer(bi)

# -----------------------------
# ----- SYNTACTIC ANALYSI -----
# -----------------------------

# More Xenon constants

robo = [0, 1, 7, 8, 9, 11, 14, 15, 16, 17]
rthbo = [2, 3, 6]

# Checking arguments

for i in lexed:
  opcode = bin(i[0])[2:]
  if len(opcode) < 5:
    opcode = "0"*(5-len(opcode)) + opcode
  if i[0] in robo and type(i[1]) != int:
    print(f"Syntax error: operation {opcode} expected a register as its first operand but received a literal.")
    sys.exit()
  if i[0] in rthbo and type(i[3]) != int:
    print(f"Syntax error: operation {opcode} expected a register as its third operand but received a literal.")
    sys.exit()

# Checking instruction blocks

blockcount = 0
blocks = []
for i in lexed:
  if i[0] == 19:
    blockcount += 1
    if i[1] in blocks:
      print(f"Syntax error: instruction block {i[1]} is declared multiple times.")
      sys.exit()
    blocks.append(i[1])
  elif i[0] == 20:
    blockcount -= 1

if blockcount != 0:
  print(f"Syntax error: unbalanced instruction blocks; too many or not enough 10100's.")
  sys.exit()

for i in lexed:
  if i[0] in [18, 21, 22] and i[1] not in blocks:
    print(f"Syntax error: instruction block {i[1]} is not declared but program attempts to jump to it.")
    sys.exit()

# ------------------------------------
# ----- SYMBOL TABLE CONSTRUCTOR -----
# ------------------------------------

table = []

for i in lexed:
  for j in range(1,len(i)):
    if type(i[j]) is int and i[j] not in table:
      table.append(i[j])

intstate = {e: "" for e in table}

# ---------------------
# ----- EXECUTION -----
# ---------------------

def p2c(x): # Parse two's complement
  sign = x[0]
  return int(x[1:],2) - int(x[0])*2**(len(x)-1)

def g2c(n): # Generate two's complement
  if n == 0: return "0"
  elif n > 0: return "0" + bin(n)[2:]
  else:
    ab = "0" + bin(abs(n))[2:]
    ab = "".join("1" if x == "0" else "0" for x in ab)
    ab = bin(int(ab,2)+1)[2:]
    return ab

for i in lexed:
  if i[0] == 0: # Addition
    isn = False
    addend = intstate[i[1]]
    if type(i[2]) is int:
      summand = intstate[i[2]]
    else:
      summand = i[2]
    if summand == "" or addend == "":
      isn = True
    elif int(summand,2) == 0 or int(addend,2) == 0:
        isn = True
    if isn:
      res = summand + addend
    else:
      addend = p2c(addend)
      summand = p2c(summand)
      res = g2c(addend + summand)
    intstate[i[1]] = res
  elif i[0] == 1: # AND
    pass
  elif i[0] == 2: # Comparison
    pass
  elif i[0] == 3: # Equality
    pass
  elif i[0] == 4: # Halt
    break
  elif i[0] == 5: # If-else (meta!)
    pass
  elif i[0] == 6: # Get bit
    pass
  elif i[0] == 7: # Shift register
    pass
  elif i[0] == 8: # Set value
    pass
  elif i[0] == 9: # OR
    pass
  elif i[0] == 10: # Enqueue
    pass
  elif i[0] == 11: # Dequeue
    pass
  elif i[0] == 12: # Allocate
    pass
  elif i[0] == 13: # Full pop
    pass
  elif i[0] == 14: # XOR
    pass
  elif i[0] == 15: # Get length
    pass
  elif i[0] == 16: # Get user input
    pass
  elif i[0] == 17: # Print out
    pass
  elif i[0] == 18: # Jump to block
    pass
  elif i[0] == 19: # Start instruction block
    pass
  elif i[0] == 20: # End instruction block
    pass
  elif i[0] == 21: # Jump-if-true
    pass
  elif i[0] == 22: # Jump-if-false
    pass
  else: # Nop
    continue

print("Program halted.")