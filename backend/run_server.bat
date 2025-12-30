@echo off
cd /d "D:\FYPnew\ai-story-generator\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
