## О проекте
Проект NoteApi -  api серивис заметок созданный на flask используя restfull подход.
Рабочий пример проекта на 
* v2 [heroku через swagger](https://noteapigeorge.herokuapp.com/swagger-ui/#/)
* v3 [heroku через swagger](https://noteapilatest.herokuapp.com/swagger-ui/)

В проекте реализованы:
```
авторизаци и аутентификация пользователя
возможность добавления ролей для будущего разделения прав доступа
возможность загрузки изображения
публичные и приватные заметки
возможность создания и добавления тегов к заметкам
всевозможный поиск по тегма/авторма/части текста и т.д.
а так же проект готов для деплоя на heroku
```
В проекте использовались:
```
SQLAlchemy в качестве бд
Marshmallow для сериализации
Swagger для генерации документации
Babel для локализации ошибок 
Flask Mail для отправки сообщений на gmail при запуске сервиса
```

## Run project
```
python3 -m venv note_venv
source note_venv/bin/activate
pip install -r requirements.txt
flask db upgrade
```
## Migration
```
flask db init
flask db migrate -m "comment"
flask db upgrade
```
## Babel localization
```
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d api/translations
pybabel compile -d api/translations
```
