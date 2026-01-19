# ai-math-tutor

full code will be updated soon.i retrained the model for better performance but it takes a while...

<img width="129" height="26" alt="image" src="https://github.com/user-attachments/assets/0bc0bd8c-49e6-4f2e-a46d-f7782da90af3" />


# MathDial Socratic Tutor (FastAPI + React)

## Run backend

1) Create venv + install:
```bash
cd backend
python -m venv .venv
```
# Windows: 
```
.\.venv\Scripts\Activate.ps1
```
# Linux/macOS: 
```
source .venv/bin/activate
```
```
pip install -U pip
pip install -r requirements.txt
```
Set model path (must contain config.json + weights):

Windows (PowerShell):
```
$env:MODEL_DIR="C:\path\to\checkpoint-or-exported-model-folder"
```
Linux/macOS:
```
export MODEL_DIR="/path/to/checkpoint-or-exported-model-folder"
```
Start API:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Check:

http://localhost:8000/health

Run frontend
```
cd frontend
npm install
npm run dev
```
Open:
```
http://localhost:5173
```
