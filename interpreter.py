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
# Unpad it
padam = bi[:3]
padam = int(padam,2)
try:
  bi = bi[3:-padam]
except Exception:
  print("Invalid padding.")
  sys.exit()
print("Program unpadded. It will now be lexed.")

# Xenon constants
nio = ["00100", "01101", "10100"] # Opcodes without extra arguments
oio = ["00101", "01010", "01011", "01100", "10000", "10001", "10010", "10011", "10101", "10100"] # Opcodes with one argument
tio = ["00000", "00001", "00111", "01000", "01001", "01110", "01111"] # Opcodes with two arguments
thio = ["00010", "00011", "00110"]
opcodes = nio + oio + tio + thio

def lexer(bincode):
  global opcodes, nio
  try:
    opcode = bincode[:5]
  except Exception:
    print("Program invalid or too short.")
    sys.exit()
  print(f"First opcode is: {opcode}.")
  lexres = []
  if opcode in nio:
    lexres = [[int(opcode,2)]]
  else:
    # Get the arguments
    literalcheck = bincode[5:10]
    if literalcheck == "10111":
      # Scan for 11000
      i = 10
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
        lit = bincode[10:i]
        lexres = [[int(opcode,2),lit]]
    else:
      count = 0
      while bincode[5+count] == "1":
        count += 1
      if count == 0:
        print(f"Invalid input - operation {opcode} expected a register or literal but did not receive one.")
  return lexres

lexed = lexer(bi)
print(lexed)