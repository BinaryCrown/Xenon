inp = input("XOB file to convert to XEN: ")
fio = open(inp, "rt")
string = fio.read()
fio.close()
n = len(string)+3
if n % 8 != 0:
    k = 8-(n%8)
else:
    k = 0
string = bin(k)[2:] + string + "0"*k
chunks = [string[8*n:8*n+8] for n in range(len(string)//8)]
out = []
for e in chunks:
    hx = hex(int(e,2))[2:]
    if len(hx) == 1:
        hx = "0" + hx
    hx = bytes.fromhex(hx).decode("latin-1")
    out.append(hx)
path = input("Place to store XEN: ")
fio = open(path, "wt")
fio.write("".join(out))
fio.close()