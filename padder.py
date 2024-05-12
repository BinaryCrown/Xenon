string = input("XOB program: ").replace(" ","")
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
print("".join(out))
