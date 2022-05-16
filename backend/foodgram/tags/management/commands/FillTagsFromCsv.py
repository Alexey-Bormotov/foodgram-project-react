import csv

from django.core.management.base import BaseCommand
from tags.models import Tag


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Tag'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        print('Заполнение модели Tag из csv запущено.')
        file_path = options['path'] + 'tags.csv'
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                try:
                    obj, created = Tag.objects.get_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2],
                    )
                    if not created:
                        print(f'Тег {obj} уже существует в базе данных.')
                except:
                    print(f'Ошибка в строке {row}')

        print('Заполнение модели Tag завершено.')
