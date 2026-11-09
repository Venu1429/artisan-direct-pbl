# Artisan-Direct: individual PBL submission (code + data)

Idea: a mobile app that connects traditional artisans directly to customers (maker profile + asking price, no middlemen).
The survey data is SIMULATED (seed 2026) because no real survey was run. Say this in your report.

## How to run (tested on Python 3.13; any 3.10+ should work)
    pip install -r requirements.txt
    python code/01_generate_survey_data.py     # makes data/survey_raw.csv (3,200 rows, 75 columns)
    python code/02_clean_and_analyze.py        # cleans + runs the 4 algorithms -> outputs/result_*.csv, data/survey_clean.csv
    python code/03_build_excel.py              # makes data/artisan_survey_dataset.xlsx
Run from any folder: paths are relative to this project folder. Whole pipeline takes a few minutes.
The ready-made data/ files are already included, so the professor can open them without running anything.

## Folders
- code/     the three scripts above
- data/     raw survey, cleaned survey, Excel workbook (raw, cleaned + model scores, column map, scorecard, cleaning log, outliers, descriptive stats)
- outputs/  every result table (result_*.csv) and summary.json
- docs/     column-to-algorithm map and study notes
- report/   YOUR written report goes here
- screenshots/  dashboard screenshots go here

## Which columns feed which algorithm
See docs/column_to_algorithm_map.md (or outputs/result_column_map.csv).
In short: association = only Q18_S1..S10 (the 10 services); classification = all feature columns, target = Q21 (4-5 = interested);
clustering = demographics, habits, attitudes and price beliefs (Q21 only used afterwards to rank segments);
regression = Q23 (price per item) and Q24 (yearly spend).

## Dashboard (Streamlit)
    streamlit run streamlit_app.py
Reads outputs/result_*.csv, so run code/02_clean_and_analyze.py first if you regenerate the data.
Deploy free on Streamlit Community Cloud: New app -> pick this repo -> main file `streamlit_app.py`.
