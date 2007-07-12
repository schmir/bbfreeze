all:: README.html MANIFEST.in

MANIFEST.in::
	./make_manifest.py

README.html: README.txt
	rst2html.py README.txt >README.html

www: README.html
	scp README.txt README.html root@systemexit.de:bbfreeze/

