CarGuru - Car Fault Diagnosis Expert System (Streamlit)
=======================================================

KNOWLEDGE BASE
  78 rules | 134 symptoms | 9 vehicle systems
  NEW system: Hybrid & Electric Drivetrain (11 expert rules, 25 symptoms) - hybrid battery degradation,
  cell imbalance, inverter / DC-DC converter faults, HV insulation faults, contactor faults,
  charging-port overheating, on-board charger and regenerative braking faults.

FILES
  app.py                  pages, top bar (Back / Restart / three-dot menu), navigation history
  ui.py                   design system: light + dark palettes, CSS, slider, Lucide icon helpers
  icons.py                embedded Lucide icons (offline, no extra package)
  engine.py               inference engine                          
  knowledge_base.py       rules + symptoms                         
  requirements.txt        streamlit>=1.50, pandas
  .streamlit/config.toml  base theme settings (keep this folder next to app.py)

INTERFACE CONTROLS
  Three-dot menu (top right)  Appearance: Light / Dark / System
  Back                        previous page; inside Diagnosis steps back (report -> questions -> setup)
  Restart                     resets everything (keeps your theme) and returns to the Dashboard
  Sidebar                     page navigation; if closed, press the blue ">>" button (top-left) to reopen
  Dashboard slider            4 slides (brand, how it works, coverage, features); autoplays every 8 s,
                              use the dots or arrows to move manually

RUN LOCALLY (Windows)
  1. Install Python 3.9+ (tick "Add Python to PATH")
  2. Extract the zip, open the folder, type  cmd  in the address bar, press Enter
  3. pip install -r requirements.txt
  4. streamlit run app.py          (or: python -m streamlit run app.py)
  5. Open http://localhost:8501

DEPLOY (Streamlit Community Cloud)
  Upload ALL files (including the .streamlit folder) to the ROOT of your GitHub repo,
  then deploy with main file path:  app.py

Icons: Lucide (https://lucide.dev), ISC License.
