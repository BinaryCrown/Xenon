read -p "Run XEN, or convert XOB to XEN (0/1)? " opt
if [ $opt == "0" ]
then
  read -p "XEN file to run: " xen
  python3 interpreter.py "$xen"
fi
if [ $opt == "1" ]
then
  read -p "XOB file to cnvert to XEN: " xob
  python3 padder.py "$xob"
fi