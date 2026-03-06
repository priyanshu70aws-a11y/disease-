# Run Instructions (Disease Prediction Project)

## 1) Setup virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Train machine learning models
```bash
python train_model.py
```

Generated artifacts:
- `models/best_model.pkl`
- `models/metrics.json`
- charts in `static/images/charts/`

## 4) Run website
```bash
python app.py
```
Open `http://127.0.0.1:5000`.

## 5) Default admin credentials
- Email: `admin@health.local`
- Username: `admin`
- Password: `admin123`

## 6) Key pages
- Home: `/`
- Login: `/login`
- Dashboard: `/dashboard`
- Prediction Workspace: `/predict-page`
- Symptoms Page: `/symptoms`
- About: `/about`
- Contact: `/contact`
- Admin dashboard: `/admin`

## 7) Production run with Gunicorn
```bash
gunicorn wsgi:app
```
