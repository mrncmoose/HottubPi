mkdir .venv
python3 -m venv .venv
.venv\Scripts\activate.bat
pip3 install -r requirements.txt
django-admin startproject hot_tub
cd hot_tub
python manage.py startapp hot_tub_ui
python manage.py startapp hot_tub_api
