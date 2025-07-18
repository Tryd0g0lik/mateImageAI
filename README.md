## .env
```
SECRET_KEY_DJ=< secret_cod_your_django >
POSTGRES_DB=< your_db_name >
POSTGRES_USER= < your_db_user_name >
POSTGRES_HOST=< your_db__hhost >
POSTGRES_PORT=< your_db_port >
POSTGRES_PASSWORD=< your_db_password>
DB_ENGINE=django.db.backends.postgresql
APP_PROTOCOL = http
APP_HOST = < basis_host_your_app > 
APP_PORT = < port_your_app >
DATABASE_URL=redis://83.166.245.209:6380/0
PORT=< port_your_redis >


EMAIL_HOST = <smtp.email_host_of_sender - example: smtp.yandex.ru >
EMAIL_HOST_USER=< own_email_adress_of_sender >
EMAIL_HOST_PASSWORD=< own_email_password_of_sender >

URL_REDIRECT_IF_NOTGET_AUTHENTICATION = < url_for_redirect_if_no_exists_athenticate >
URL_REDIRECT_IF_GET_AUTHENTICATION = < url_for_redirect_if_exists_athenticate >
```


DOCKER на "`HTTP`" "`83.166.245.209`"\
База данных postgres, работает через порт 5433\
"`DATABASE_URL=redis://83.166.245.209:6380/0`"\

Изменили таблицу User которую django предоставляет по умолчанию.\
Действующий шаблон Users.

CMS Django переключена на асинхронную работу.\
Работает на сервере daphne.


После изменений статических файлов \ 
команда "`py manage.py collectstatic --clear --noinput`"\
"`pre-commit install`" установка hook-ов из "`.pre-commit-config.yaml`" файла. На выходе должны получить "`pre-commit installed at .git\hooks\pre-commit`".
Если вы хотите запустить хуки на всех файлах проекта (например, при\
добавлении новых хуков), используйте команду "`pre-commit run --all-files`".\

Теперь будет  автоматически запускать перед каждым коммитомю\
Стоп проверка "`git commit -m "Your commit message" --no-verify`" - флаг "`--no-verify`"


При регистрации на почту отправляется сообщение, содержание\
![email_post](./img/email_post.png)


После того как пользователь кликает по ссылке (у себя на почте)\ 
"`user_activate`" Срабатывает (из "`person/urls.py`") по запросу урла который содержит подпись.\ 
Мы логиним пользователя и перебрасываем на страницу уже авторизованным.\
"`person/contribute/controler_activate.py`"

Шаблоны для писем \
"`templates/email`"
