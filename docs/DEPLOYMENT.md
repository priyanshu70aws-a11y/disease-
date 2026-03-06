# Deployment Guide (Production Ready)

## Environment Variables
Create a `.env` file in project root:

```env
SECRET_KEY=change-me
DATABASE_URL=sqlite:///database.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_mail_user
MAIL_PASSWORD=your_mail_password
MAIL_DEFAULT_SENDER=noreply@healthpredict.ai
MAIL_SUPPRESS_SEND=true
FLASK_DEBUG=false
```

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
python app.py
```

## Render/Railway/Heroku
1. Add `Procfile`: `web: gunicorn wsgi:app`.
2. Set environment variables from `.env`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn wsgi:app`.

## Static Hosting Split (Vercel/Netlify + API Backend)
- Host templates/static as frontend if needed.
- Deploy Flask backend separately (Render/Railway).
- Point frontend API requests to backend domain.

## Recommended Production Improvements
- Use PostgreSQL instead of SQLite.
- Configure HTTPS and secure cookies.
- Add CSRF protection with Flask-WTF.
- Integrate Alembic migrations.
