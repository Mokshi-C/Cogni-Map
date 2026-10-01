# CogniMap — A Data Science Approach to Personalized Academic Pathway Recommendation

Credit-aware academic pathway recommender for CSE-allied engineering branches
(CSE, AIML, AIDS, IT, Cyber Security, CSBS, IoT & Embedded Systems).

## Project Status

- [x] Dataset design & synthetic generation (7 linked tables, 2,000 students)
- [x] Phase 2: Feature engineering + EDA (`notebooks/Phase2_Feature_Engineering_EDA.ipynb`)
- [x] Baseline model: Linear Regression (`models/linear_regression_baseline.pkl`)
- [ ] Random Forest model + hyperparameter tuning + GroupKFold CV
- [ ] Model evaluation (RMSE/MAE + top-k ranking accuracy)
- [ ] Feature importance / explainability
- [ ] Knowledge base: branch → courses/skills/certifications lookup
- [ ] Streamlit app

## Folder Structure

```
CogniMap/
├── data/
│   ├── raw/            # 7 base tables: branches, courses, students, etc.
│   └── processed/       # phase2_feature_table.csv — the (student, branch) modeling table
├── notebooks/            # executed, numbered by phase
├── src/                  # reusable pipeline code
│   ├── reference_data.py   # curriculum/branch/skill/career definitions
│   ├── generate.py         # regenerates data/raw/ from reference_data.py
│   ├── pathway_scoring.py  # credit-aware scoring reference implementation
│   └── train_model.py      # [next] model training script
├── models/                # trained model artifacts (.pkl / .joblib) + feature list
├── knowledge_base/        # [next] branch -> courses/skills/certs mapping
├── app/                   # [next] Streamlit app
└── report/                # architecture doc, final write-up
```

## Setup

```bash
pip install -r requirements.txt
```

## Reproducing the data

```bash
cd src
python generate.py          # writes data/raw/*.csv from reference_data.py
```

## Model

Current baseline: `models/linear_regression_baseline.pkl`, trained on
`data/processed/phase2_feature_table.csv` using features listed in
`models/cognimap_features.json`:
`academic_fit, skill_match_pct, credit_completion_pct, prerequisite_satisfaction_pct`.

**Do not use** `preferred_specialization`, `career_interest`, or `is_current_branch`
as model features — see `report/CogniMap_Dataset_Architecture.md` Section 7 for why.

Trained with scikit-learn **1.6.1** — pin this version when reloading the model
elsewhere to avoid version-mismatch warnings.
