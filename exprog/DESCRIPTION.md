This folder contains example Xenon programs (exprog = EXample PROGrams). The .XOB (XenOn Binary) files contain the binary code making up these programs (obviously formatted as a string of "0"s and "1"s - not as the bits themselves).
The .XEN (XENon) files contain text encodings of the respective .XOB files, particularly via Latin-1. Some .XEN files contain control characters, so they may require you to press "view raw" rather than being able to simply view them in the web client. Mojibake may also occur.

- cat: reads user input from stdin and prints it back to stdout.
- helloworld: prints the string "Hello, World!" to stdout.
- leq: reads two unsigned numbers from stdin and checks if the first is at most the latter by only comparing individual bits.

Below are descriptions of the algorithms which the more complex programs implement.

# leq

- Compute the lengths of our two numbers.
- If n is at least as long as m, continue to the next step. Else return <code>True</code>.
- See if n is exactly the same length as m. If not, return <code>False</code>, else continue.
- Create a counter C and store 0 in it.
- Get the C'th bit of n, b, and the C'th bit of m, c. If b < c, return <code>True</code>. Else, continue.
- Check if b = c. If not, return <code>False</code>, else continue.
- Increment C. Check if C is the same as length(n). If it is, return <code>True</code>. Else, jump back to step 5.
