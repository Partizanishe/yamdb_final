# Проект YaMDb 
![yamdb_workflow](https://github.com/partizanishe/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
### Проект доступен по адресу: http://84.201.140.111/api/v1/

_**REST API для сервиса YaMDb**_

Проект YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории: «Книги», «Фильмы», «Музыка» и т.д., так же им может быть присвоен жанр.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется рейтинг. На одно произведение пользователь может оставить только один отзыв.

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

## Как запустить проект:

### Клонировать репозиторий
```
git clone git@github.com:Partizanishe/yamdb_final.git
```

#### Выполните вход на свой удаленный сервер

#### Установите docker на сервер

```
sudo apt install docker.io 
```

#### Установите docker-compose на сервер(актуальная версия [тут](https://github.com/docker/compose/releases))

```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
#### Скопируйте файлы docker-compose.yaml и nginx/default.conf из проекта на сервер

#### Добавьте в Secrets GitHub переменные окружения для работы

```
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_USER=postgres
SECRET_KEY =<SECRET_KEY>

DOCKER_PASSWORD=<DOCKER_PASSWORD>
DOCKER_USERNAME=<DOCKER_USERNAME>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ(cat ~/.ssh/id_rsa)>

TG_CHAT_ID=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```

#### Запушить на Github. После успешного деплоя зайдите на боевой сервер и выполните команды

#### Собрать статические файлы в STATIC_ROOT

```
docker-compose exec web python3 manage.py collectstatic --noinput
```

#### Создать и применить миграции

```
docker-compose exec web python3 manage.py makemigrations
docker-compose exec web python3 manage.py migrate --noinput
```
