run:
	source venv/bin/activate && python3 main.py

setup: install install-dev

install:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

install-dev:
	source venv/bin/activate && pip install -r requirements-dev.txt

freeze:
	source venv/bin/activate && pip freeze > requirements.txt

format:
	source venv/bin/activate && black app

lint:
	source venv/bin/activate && pylint app

test:
	source venv/bin/activate && pytest tests -v

test-cov:
	source venv/bin/activate && pytest tests -v --cov=app --cov-report=term-missing

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

setup-clean: clean setup

check:
	@echo "Running server health check..."
	source venv/bin/activate && python3 -c "from app.main import app; print('✓ Server imports working')"
	@echo "\n✨ Health check successful! ✨"

build-strict: format lint test check
	@echo "\n✨ Strict build successful! ✨"

build: format check
	@echo "\n✨ Basic build successful! ✨"
