clean:
	rm -rf dist/
	rm -rf build/
build:
	pip3 install wheel
	python3 setup.py bdist_wheel
upload:
	pip3 install twine
	python3 -m twine upload dist/*.whl
deploy:
	make clean
	make build
	make upload
