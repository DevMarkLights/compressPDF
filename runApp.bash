cd frontend
./buildFrontend.bash

cd ../
cd backend
# CMD ['uvicorn', 'main:app', '--host','0.0.0.0','--port','8084','--workers', '1']
source .venv/bin/activate
# .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8084 --workers 1
python -m uvicorn main:app --host 0.0.0.0 --port 8084 --workers 1
