#!/bin/bash

# Start FastAPI
uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Wait (keeps container alive)
wait
