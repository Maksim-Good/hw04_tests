from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Здесь нужно ввести основной текст поста.',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Здесь нужно ввести имя автора поста.',
    )
    group = models.ForeignKey(
        'Group',
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Здесь можно ввести имя группы.',
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Здесь нужно ввести имя группы.',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Тэг',
        help_text='Здесь нужно задать Тэг (уникальное имя).',
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Здесь должно быть описание группы.'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['title']

    def __str__(self):
        return self.title
