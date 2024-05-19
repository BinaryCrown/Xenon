import sys
import sscfcmp

fio = open(sys.argv[1], "rt")
string = fio.read()
fio.close()
n = len(string)+3
if n % 8 != 0:
    k = 8-(n%8)
else:
    k = 0
pbit = bin(k)[2:]
if len(pbit) < 3:
    pbit = "0"*(3-len(pbit)) + pbit
string = pbit + string + "0"*k
chunks = [string[8*n:8*n+8] for n in range(len(string)//8)]
out = []
for e in chunks:
    hx = hex(int(e,2))[2:]
    if len(hx) < 2:
        hx = "0"*(2-len(hx)) + hx
    hx = bytes.fromhex(hx).decode("sscfcmp")
    out.append(hx)
path = input("Place to store XEN: ")
fio = open(path, "wt")
fio.write("".join(out))
fio.close()