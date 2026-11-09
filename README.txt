AutoDoc - Car Fault Diagnosis Expert System (Streamlit)
=======================================================

FILES
  app.py             -> GUI (run this one)
  engine.py          -> inference engine
  knowledge_base.py  -> 67 rules + 109 symptoms
  requirements.txt   -> libraries needed

HOW TO RUN (Windows)
  1. Install Python 3.9+ from python.org  (tick "Add Python to PATH")
  2. Extract this zip into a folder
  3. Open the folder, click the address bar, type  cmd  and press Enter
  4. Run:   pip install -r requirements.txt
  5. Run:   streamlit run app.py
  6. Browser opens at http://localhost:8501

If "streamlit" is not recognized, use:  python -m streamlit run app.py
Press Ctrl + C in the terminal to stop the app.
