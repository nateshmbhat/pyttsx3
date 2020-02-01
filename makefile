clean:
	rm -rf dist/
	rm -rf build/
build:
	pip3 install wheel --user
	python3 setup.py bdist_wheel
upload:
	pip3 install twine --user
	python3 -m twine upload dist/*.whl --verbose

deploy:
	make clean
	make build
	make upload
