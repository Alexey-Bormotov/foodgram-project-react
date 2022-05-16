from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Название тега',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет для тега',
        help_text='Цвет для тега',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор тега',
        help_text='Идентификатор тега',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
