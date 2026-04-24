# Ethio Bucks

Ethio Bucks is a Django web application for task-based earning with referral rewards, proof submission, transaction tracking, and withdrawal requests.

## Live Demo
- Main App: `https://abdusalam.pythonanywhere.com/tasks/`
- Register: `https://abdusalam.pythonanywhere.com/tasks/register/`
- Login: `https://abdusalam.pythonanywhere.com/tasks/login/`
- Portfolio Showcase: `https://abdusalam.pythonanywhere.com/tasks/showcase/`

## Core Features
- Secure user registration/login/logout
- Task list with reward values
- Task detail flow with timer-based proof submission unlock
- Proof image upload and admin review flow
- Wallet balance and transaction history
- Referral system with reward crediting
- Withdrawal request workflow
- Daily bonus claim logic
- Mobile-first responsive UI polish

## Tech Stack
- Python 3
- Django
- SQLite
- Bootstrap 5
- Pillow (image upload support)
- PythonAnywhere (deployment)

## Local Setup
```bash
git clone https://github.com/oumersalah2-cmd/EthioBucks.git
cd EthioBucks
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deployment (PythonAnywhere)
```bash
cd ~/EthioBucks
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then reload the web app from the PythonAnywhere **Web** tab.

## Portfolio Notes
This project demonstrates:
- End-to-end full-stack feature development in Django
- Production debugging and deployment workflow
- Responsive design and UX polish for real users
- Iterative improvements from client feedback

## Developer
- **Abdusalam Oumer**
- Telegram: [@AfewSVS](https://t.me/AfewSVS)
