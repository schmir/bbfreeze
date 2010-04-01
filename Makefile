all:: README.html MANIFEST.in egg sdist

GENFILES = README.html MANIFEST.in

MANIFEST.in::
	./make_manifest.py

README.html: README.rst
	rst2html.py README.rst >README.html

www: README.html
	scp README.rst README.html root@systemexit.de:bbfreeze/

egg:: $(GENFILES)
	python setup.py build bdist_egg

sdist:: $(GENFILES)
	python setup.py build sdist

clean::
	rm -rf build dist
