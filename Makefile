README.html: README.txt
	rst2html.py README.txt >README.html

www: README.html
	scp README.txt README.html root@systemexit.de:bbfreeze/

