# Run project
```
python3 -m venv note_venv
source note_venv/bin/activate
pip install -r requirements.txt
flask db upgrade
```
# Migration
```
flask db init
flask db migrate -m "comment"
flask db upgrade
```
# Babel localization
```
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d api/translations
pybabel compile -d api/translations
```