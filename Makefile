test:
	PYTHONPATH=".:./tests" pytest --capture=sys --cov-report term-missing --cov=sensu_handler_pagerduty_alternative ${PYTEST_FLAGS}

style: flake8 pylint

pylint:
	pylint --ignore-patterns="^.*pb2.*\.py, setup.py" sensu_handler_pagerduty_alternative.py

flake8:
	flake8 --exclude="*pb*py, tests, setup.py" --max-line-length=100
