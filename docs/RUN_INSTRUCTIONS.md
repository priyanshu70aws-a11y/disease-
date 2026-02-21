# Run Instructions (Disease Prediction Project)

## 1) Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Train ML models
```bash
python train_model.py
```

This generates:
- `models/best_model.pkl`
- `models/metrics.json`
- charts in `static/images/charts/`

## 4) Start Flask app
```bash
python app.py
```

Open browser at:
- `http://127.0.0.1:5000`

## 5) Default admin login
- Email: `admin@health.local`
- Password: `admin123`

## 6) Typical workflow
1. Register/login as Patient or Doctor.
2. Go to dashboard and submit symptoms.
3. View top-3 disease predictions and confidence.
4. Download PDF report.
5. Admin can manage users and dataset from `/admin`.

## Notes
If you cannot install packages in your environment, ensure your machine has internet access or a configured Python package mirror.
