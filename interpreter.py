import sys

# Get program
inp = input("XEN file to run: ")
fio = open(inp, "rb")
prog = fio.read()
fio.close()
# Convert into binary
print(f"Program is: {prog.decode('latin-1')}")
prog = prog.hex()
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
print(bi)
# Unpad it
padam = bi[:3]
padam = int(padam,2)
try:
  bi = bi[3:-padam]
except Exception:
  print("Invalid padding.")
  sys.exit()
print(bi)
# Xenon constants
nio = ["00100", "01101", "10100"] # Opcodes without extra arguments
oio = ["00101", "01010", "01011", "01100", "10000", "10001", "10010", "10011", "10101", "10100"] # Opcodes with one argument
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
    print(f"Literal after operation {opcode} opened with 10111 but never closed with 11000.")
    sys.exit()
  else:
    return [bincode[sindex+5:i], i]

def registerscan(bincode, sindex, opcode): # Get register index starting at code index sindex
  count = 0
  while bincode[sindex+count] == "1":
    count += 1
  if count == 0:
    print(f"Invalid input - operation {opcode} expected a register or literal but did not receive one.")
  return [count, sindex+count+1]

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
    literalcheck = bincode[5:10]
    if literalcheck == "10111":
      lit = literalscan(bincode, 5, opcode)[0]
      stopindex = literalscan(bincode, 5, opcode)[1]+5
      lexres = [[int(opcode,2),lit]]
    else:
      count = registerscan(bincode, 5, opcode)
      if opcode in oio:
        stopindex = count[1]
        lexres = [[int(opcode,2),count[0]]]
      elif opcode in tio:
        scount = registerscan(bincode, count[1], opcode)
        stopindex = scount[1]
        lexres = [[int(opcode,2),count[0],scount[0]]]
      elif opcode in thio:
        scount = registerscan(bincode, count[1], opcode)
        tcount = registerscan(bincode, scount[1], opcode)
        stopindex = tcount[1]
        lexres = [[int(opcode,2),count[0],scount[0],tcount[0]]]
  if len(bincode[stopindex:]) < 5:
    return lexres
  else:
    return lexres + lexer(bincode[stopindex:])

lexed = lexer(bi)
print(lexed)