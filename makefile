clean:
	rm -rf dist/
	rm -rf build/
build:
	pip3 install build
	python3 -m build
upload:
	pip3 install twine
	python3 -m twine check --strict dist/*
	python3 -m twine upload dist/*.whl
deploy:
	make clean
	make build
	make upload
