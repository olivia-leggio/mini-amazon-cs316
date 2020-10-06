# mini-amazon-cs316

**How to run locally (Paul's method, assuming Mac):**

1. clone into folder
2. run `python3 -m venv test-venv` (creates a virtual environment)
3. `source test-venv/bin/activate` (this will activate the virtual environment)
4. `pip install -r requirements.txt` (installs dependencies)
5. `export FLASK_APP=app.py` (exports the main flask app)
6. `python3 init_test.py` (initializes the database to a test with just two items, for now)
7. `flask run` and go to local url provided
