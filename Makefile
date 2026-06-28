.PHONY: lint type-check build clean

lint:
	flake8 ./mktvis

type-check:
	mypy --install-types --non-interactive ./mktvis

build:
	rm -rf dist/ && rm -rf build/ && python setup.py sdist bdist_wheel

check-build:
	twine check dist/*

clean:
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm -f coverage.xml .coverage