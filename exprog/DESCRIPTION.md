This folder contains example Xenon programs (exprog = EXample PROGrams). The .XOB (XenOn Binary) files contain the binary code making up these programs (obviously formatted as a string of "0"s and "1"s - not as the bits themselves).
The .XEN (XENon) files contain text encodings of the respective .XOB files, particularly via Latin-1. Some .XEN files contain control characters, so they may require you to press "view raw" rather than being able to simply view them in the web client.

- cat: reads user input from stdin and prints it back to stdout.
- helloworld: prints the string "Hello, World!" to stdout.
- leq: reads two unsigned numbers from stdin and checks if the first is at most the latter by only comparing individual bits.
