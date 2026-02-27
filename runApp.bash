cd frontend
./buildFrontend.bash

cd ../
cd backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8084 --workers 1
