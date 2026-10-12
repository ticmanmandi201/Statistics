@echo off
cd /d D:\Statistics
call venv\Scripts\activate
python -m streamlit run app.py
pause
