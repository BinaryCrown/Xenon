import sys
import sscfcmp

# Get program
fio = open(sys.argv[1], "rt")
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
    n1 = "0"*(4-len(n1)) + n1
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
  global opcodes, nio, oio, tio, thio
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
  print("Syntax error: unbalanced instruction blocks; too many or not enough 10100's.")
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
  if len(x) == 0 or (len(x) == 1 and x[0] == "0"): return 0
  elif len(x) == 1 and x[0] == "1": return -1
  return int(x[1:],2) - int(x[0])*2**(len(x)-1)

def g2c(n): # Generate two's complement
  if n == 0: return "0"
  elif n > 0: return "0" + bin(n)[2:]
  else:
    ab = "0" + bin(abs(n))[2:]
    ab = "".join("1" if x == "0" else "0" for x in ab)
    ab = bin(int(ab,2)+1)[2:]
    return ab

# Internal state of the program during execution
Wreg = ""
queue = []
qspace = 0
eip = 0
halted = False

def intvar(n): # Interpret the variable using the global internal state
  global intstate
  if type(n) is int:
    return intstate[n]
  return n

def prepfb(n,m): # Perform padding to prepare n, m for boolean operations
  if len(n) < len(m):
    return ["0"*(len(m) - len(n)) + n, m]
  elif len(m) < len(n):
    return [n, "0"*(len(n) - len(m)) + m]
  return [n, m]

while eip < len(lexed):
  i = lexed[eip]
  opcode = bin(i[0])[2:]
  if len(opcode) < 5:
    opcode = "0"*(5-len(opcode)) + opcode
  if i[0] == 0: # Addition
    isn = False
    addend = intstate[i[1]]
    summand = intvar(i[2])
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
    A = prepfb(intstate[i[1]], intvar(i[2]))
    intstate[i[1]] = "".join("1" if x == "1" and y == "1" else "0" for x, y in zip(A[0],A[1]))
  elif i[0] == 2: # Comparison
    comparand = intvar(i[1])
    comparor = intvar(i[2])
    if comparand == "":
      comparand = "0"
    if comparor == "":
      comparor = "0"
    comparand = p2c(comparand)
    comparor = p2c(comparor)
    bo = str(int(comparand <= comparor))
    intstate[i[3]] = bo
  elif i[0] == 3: # Equality
    comparand = intvar(i[1])
    comparor = intvar(i[2])
    bo = str(int(comparand != comparor))
    intstate[i[3]] = bo
  elif i[0] == 4: # Halt
    halted = True
    break
  elif i[0] == 5: # If-else (meta!)
    Wreg = str(int("1" in intvar(i[1])))
  elif i[0] == 6: # Get bit
    index = intvar(i[2])
    if index == "":
      index = "0"
    index = int(index,2)
    try:
      intstate[i[3]] = intstate[i[1]][index]
    except:
      print(f"Runtime error: list index {index} in operation {opcode} out of bounds.")
      sys.exit()
  elif i[0] == 7: # Shift register
    shifter = intstate[i[1]]
    shifted = intvar(i[2])
    if shifted == "":
      shifted = "0"
    shifted = p2c(shifted)
    if shifted < 0:
      shifted = abs(shifted)
      intstate[i[1]] = shifter[shifted:] + "0"*min(shifted, len(shifter))
    elif shifted > 0:
      intstate[i[1]] = "0"*min(shifted, len(shifter)) + shifter[:-shifted]
  elif i[0] == 8: # Set value
    intstate[i[1]] = intvar(i[2])
  elif i[0] == 9: # OR
    A = prepfb(intstate[i[1]], intvar(i[2]))
    intstate[i[1]] = "".join("1" if x == "1" or y == "1" else "0" for x, y in zip(A[0],A[1]))
  elif i[0] == 10: # Enqueue
    if qspace == 0:
      print(f"Runtime error: not enough space remaining on queue for {intvar(i[1])} to be enqueued by operation {opcode}.")
      sys.exit()
    queue.append(intvar(i[1]))
    qspace -= 1
  elif i[0] == 11: # Dequeue
    intstate[i[1]] = queue[0]
    queue = queue[1:]
  elif i[0] == 12: # Allocate
    qspace += intvar(i[1])
  elif i[0] == 13: # Full pop
    for n in range(len(queue)):
      intstate[n] = queue[n]
  elif i[0] == 14: # XOR
    A = prepfb(intstate[i[1]], intvar(i[2]))
    intstate[i[1]] = "".join("1" if (x == "1" or y == "1") and not (x == "1" and y == "1") else "0" for x, y in zip(A[0],A[1]))
  elif i[0] == 15: # Get length
    res = intvar(i[2])
    while len(res) > 0:
      if res[0] == "0": res = res[1:]
      else: break
    intstate[i[1]] = len(res)
  elif i[0] == 16: # Get user input
    inp = input("")
    if inp != "":
      try:
        _ = int(inp,2)
      except:
        inp = inp.encode("utf-8").hex()
        s = []
        for e in range(0,len(inp)):
          n = bin(int(inp[e],16))[2:]
          if len(n) < 4:
            n = "0"*(4-len(n)) + n
          s.append(n)
        inp = "".join(s)
    intstate[i[1]] = inp
  elif i[0] == 17: # Print out
    print(intstate[i[1]])
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
  eip += 1

if not halted:
  while True:
    pass

print("Program halted.")