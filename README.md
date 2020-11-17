# mini-amazon-cs316

**MINI-AMAZON**
Visit at http://better-amazon.colab.duke.edu:5000/

**How to run (Paul's method, assuming Mac):**

1. clone and cd into folder
2. run `python3 -m venv test-venv` (if test-venv does not already exist)
3. `source test-venv/bin/activate` (this will activate the virtual environment)
4. `pip install -r requirements.txt` (installs dependencies)
5. `export FLASK_APP=app.py` (exports the main flask app)
6. **If running locally** `flask run` and go to local url provided  
**If running on VM** `flask run --host 0.0.0.0` (inside `tmux`), then navigate to http://better-amazon.colab.duke.edu:5000/ 

NOTE: if on VM, the app may already be running. If so, you may need to:
 - run `ps -a` which will list running processes
 - get the pid of whichever process is listed as Flask
 - `kill [pid]`
