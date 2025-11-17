# user-service

## Run locally (Python 3.13)

# 1. Create virtual env and install
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Run
uvicorn app.main:app --reload --port 8000 --app-dir .

# 3. API docs
http://127.0.0.1:8000/docs
