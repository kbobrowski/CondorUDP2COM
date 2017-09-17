rm build dist -rf
pyinstaller -w -i ico.ico CondorUDP2COM.py
cp LICENSE.txt dist/CondorUDP2COM
cp ico.ico dist/CondorUDP2COM
