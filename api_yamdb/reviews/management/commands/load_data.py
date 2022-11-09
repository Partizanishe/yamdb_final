import csv
import sqlite3
from csv import DictReader

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""
CSV_DICT = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    help = "Loads data from data.csv"

    def handle(self, *args, **options):
        db_is_exists = [model.objects.exists() for model in CSV_DICT]

        if True in db_is_exists:
            print('Data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        for model, file in CSV_DICT.items():
            print(file)
            with open(
                f'./static/data/{file}',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                data_reader = DictReader(csvfile)
                if file == 'titles.csv':
                    for row in data_reader:
                        category = Category.objects.get(
                            pk=row.pop('category_id'))
                        obj = model(category=category, **row)
                        obj.save()
                rev_com = ['review.csv', 'comments.csv']
                if file in rev_com:
                    for row in data_reader:
                        author = User.objects.get(pk=row.pop('author'))
                        obj = model(author=author, **row)
                        obj.save()
                model.objects.bulk_create(
                    model(**data) for data in data_reader)


connection = sqlite3.connect('db.sqlite3')
curs = connection.cursor()
with open('static/data/genre_title.csv', newline='', encoding='utf-8') as f:
    datareader = csv.DictReader(f, delimiter=',')
    data = [(i['id'], i['title_id'], i['genre_id'])
            for i in datareader]
    curs.executemany(
        'INSERT INTO reviews_title_genre (id, title_id, genre_id) '
        'VALUES (?, ?, ?);', data)
connection.commit()
connection.close()
