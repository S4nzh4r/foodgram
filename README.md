`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL`

# **_Foodgram_**
Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**_Ссылка на [проект](https://foodgram.undo.it/recipes "Гиперссылка к проекту.")_**


### _Развернуть проект на удаленном сервере:_

**_Клонировать репозиторий:_**
```
git@github.com:S4nzh4r/foodgram.git
```
**_Установить на сервере Docker, Docker Compose:_**
Поочерёдно выполните на сервере команды для установки Docker и Docker Compose для Linux. Наберитесь терпения: установка займёт некоторое время. Выполнять их лучше в домашней директории пользователя (переместиться в неё поможет команда cd без аргументов).

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```
**_Скопировать на сервер файлы docker-compose.production.yml_**
```
# Команду выполнять в папке /infra

scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram/docker-compose.production.yml

# path_to_SSH — путь к файлу с SSH-ключом;
# SSH_name — имя файла с SSH-ключом (без расширения);
# username - имя пользователя на сервере;
# IP - публичный IP сервера;
```

Есть и другой вариант: создайте на сервере пустой файл docker-compose.production.yml и с помощью редактора nano добавьте в него содержимое из локального docker-compose.production.yml.

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
SSH_PASSPHRASE          - пароль фраза от ssh-ключа
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере**_

**Перед запуском скопируйте файл .env на сервер, в директорию foodgram/.**

Для запуска Docker Compose в режиме демона команду docker compose up нужно запустить с флагом -d.
Название файла конфигурации надо указать явным образом, ведь оно отличается от дефолтного. Имя файла указывается после ключа -f
```
sudo docker compose -f docker-compose.production.yml up -d
```
**_Проверьте, что все нужные контейнеры запущены:_**
```
sudo docker compose -f docker-compose.production.yml ps
```
**_Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend\_static/static/:_**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
**_Создать суперпользователя:_**
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose -f docker-compose.production.yml down -v      - с их удалением
sudo docker compose -f docker-compose.production.yml stop         - без удаления
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Локальный запуск проекта:

**_Склонировать репозиторий к себе_**

**_В директории в .env заполнить своими данными:_**
```
SECRET_KEY='Секретный ключ джанго'
ALLOWED_HOSTS='127.0.0.1 localhost' # При запуске на удаленном сервере добавить свой домен и IP удаленного сервера
BASE_URL='https://foodgram.undo.it'

POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432
```
**_Для локального запуска использовать `docker-compose.yml` в папке infra/._**

**_Создать и запустить контейнеры Docker, как указано выше._**

**_После запуска проект будут доступен по адресу: http://localhost:указанный порт/_**
