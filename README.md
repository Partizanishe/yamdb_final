# Проект YaMDb
_**REST API для сервиса YaMDb**_
![yamdb_workflow](https://github.com/partizanishe/yamdb_final/actions/workflows/yamdb_workflow/badge.svg)
Проект YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории: «Книги», «Фильмы», «Музыка» и т.д., так же им может быть присвоен жанр.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется рейтинг. На одно произведение пользователь может оставить только один отзыв.

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

## Как запустить проект:

### Клонировать репозиторий
```
git clone git@github.com:Partizanishe/infra_sp2.git
```
Перейти в папку infra_sp2/infra.

Создать в ней файл .env с переменными окружения, необходимыми для работы приложения.

_**Пример заполнения .env**_
```

DB_ENGINE=django.db.backends.postgresql

DB_NAME=postgres

POSTGRES_USER=postgres

POSTGRES_PASSWORD=postgres

DB_HOST=db

DB_PORT=5432

SECRET_KEY=key
```
### Запустить docker compose
```

docker-compose up -d
```
### Выполнить последовательно команды
```
docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --no-input
```
Проект будет доступен по адресу http://localhost/

## Заполнение базы данных
Авторизоваться по адресу http://localhost/admin/, внести записи в базу данных через админку.

## Создание резервной копии
Бекап можно создать командой
```
docker-compose exec web python manage.py dumpdata > fixtures.json
```
## Восстановление данных из фикстур

### Скопировать фикстуры в  контейнер
```
docker-compose cp fixtures.json web:/app                        
docker-compose exec web python manage.py shell  
```

### Выполнить в открывшемся терминале:
```
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
quit()
```

### Импортировать данные из фикстур
```
docker-compose exec web python manage.py loaddata fixtures.json  
```
