# AURA — Adaptive User Resilience & Analytics

This package keeps the existing AURA application structure and professional UI. Only the requested navigation/functionality changes were applied.

## Pages
- Home
- AURA Analysis (What-If Simulator embedded below the analysis)
- Treatment
- History
- About
- Admin Panel (administrator only)

## Theme
The sidebar contains the Light/Dark Mode button. The theme applies across the application, including text, cards, inputs and buttons.

## Models
Place the existing model files in `models/`:
- productivity_model.pkl
- burnout_model.pkl

The updated `app.py` resolves the model directory relative to the project structure.

## Run
```powershell
pip install -r requirements.txt
streamlit run app.py
```

The zip intentionally does not contain your local SQLite/CSV runtime data or model binaries because those files were not provided in the upload. Keep your existing `data/` and `models/` contents when replacing the project files.
