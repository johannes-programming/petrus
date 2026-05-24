.PHONY: clean build upload pypi

clean:
	rm -fr dist/

build:
	python -m build

upload:
	twine upload dist/*

pypi: clean build upload
