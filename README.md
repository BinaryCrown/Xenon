# Xenon
A nonsense-looking but sense-making esolang.

# Syntax

We have registers 0, 1, 2, 3, 4, ... There is also a register W, reserved specifically for outputs of if-else checks, and which can be used in special CWT & CWF instructions.
Variables are stored for safekeeping in a FIFO stack (more correctly, queue).

Operations: add, AND, jump to instruction, compare bits, halt, if...else..., get nth bit from register, shift register right by n bits, copy register or literal to another register, OR, push or pop to or from stack, allocate memory on stack, pop everything from stack, XOR, get size of register

Before pushing to the stack, one must allocate memory corresponding to how many elements one wants to push. Popping deallocates memory, so e.g. allocating 2 chunks, pushing twice, popping twice and attempting to push again produces an error. This is to make keeping track of how large the stack is easier. The main purpose of "pop everything from stack" is if one wants to use the queue as a FILO stack, i.e. to access a value one just pushed. It works by popping off the first element in the stack to register 0, the next to register 1, etc. One should make sure to store the values of these registers if they are currently in use. Note that the built-in add and compare size commands operate on signed numbers (via two's complement, so e.g. 1 < 0). Our last comment is the following: the size of an empty (i.e. unmodified) register is 0, and the interpreter automatically tracks its size over the course of the program. It's counted in bits, and the obtained value is stored in another register.

Literals and names of instruction blocks must have <code>10111</code> prepended and <code>11000</code> appended.

Register #n is encoded as 1^(n+1) 0. Register W can't be directly accessed in the code.
operations have 5-bit opcodes
  add is opcode 00000, and add X Y (add literal or register Y to register X) is encoded as 00000XY
  AND is opcode 00001, encoded similarly.
  compare size is opcode 00010, encoded as 00010XYZ, where Z is the register where the result of checking X > Y (as a bit) is to be stored.
  check equality is opcode 00011, encoded similarly.
  halt is opcode 00100, without any extra arguments.
  if-else is opcode 00101, encoded as 00101X, where X is the register or literal to check.
  get bit is opcode 00110, encoded as 00110XYZ, where X is the register to check, Y is the index, and Z is the register to store the output.
  shift register is opcode 00111, encoded as 00111XY, where X is the register to shift and Y is a literal representing how far to shift.
  copy value is opcode 01000, encoded as 01000XY, where X is the register to store Y.
  OR is opcode 01001, encoded similarly to AND.
  push to stack is opcode 01010, encoded as 01010X, where X is the register to push.
  pop from stack is opcode 01011, encoded as 010111X, where X is the register to pop to.
  allocate stack is opcode 01100, encoded as 01100X, where X is a literal representing how many chunks to allocate.
  pop all from stack is opcode 01101, without any extra arguments.
  XOR is opcode 01110, encoded similarly to AND.
  get register size is opcode 01111, encoded similarly to copy value.
  get user input is opcode 10000, encoded as 10000X, where X is the register to store input.
  print to screen is opcode 10001, encoded as 10001X, where X is the register to print.
  jump to instruction is opcode 10010, encoded as 10001X, where X is the name of the point to jump to.
  begin instruction block is opcode 10011, encoded as 10011X, where X is the name of the point being declared.
  end instruction block is opcode 10100, without any additional arguments.
  CWT (check register W true) is opcode 10101, encoded as 10101X, where X is the point to jump to if W = 0.
  CWF (check register W false) is opcode 10110, encoded similarly to CWT.
  all other opcodes are nops.

We can encode a program as a series of bytes via padding: if P is a program of length n, then we let k be the least integer so that n+3+k is a multiple of 8; then padding adds 3 bits representing k to the beginning, and k zeroes to the end. The addition of the 3 bits is to ensure one can distinguish padding bits from ordinary bits (by knowing how many of the former there are). 
