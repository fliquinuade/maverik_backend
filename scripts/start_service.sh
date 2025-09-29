cd maverik_backend
source .venv/bin/activate
python3 -m uvicorn maverik_backend.api:app --reload --host 0.0.0.0 --port 20240 

# run with: 
# nohup sh start_service.sh > service.log 2>&1 &
