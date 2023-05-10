from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    """
    Модельный менеджер для Post.
    """
    def get_queryset(self):
        return (super().get_queryset()
                .filter(status=Post.Status.PUBLISHED))


class Post(models.Model):
    """
    Модель для таблицы Post.
    """
    class Status(models.TextChoices):
        """
        Статус поста. Черновик / Публикация.
        """
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(
        help_text='Введите заголовок',
        verbose_name='Заголовок',
        max_length=250)
    slug = models.SlugField(
        help_text='Введите slug-идентификатор',
        verbose_name='Идентификатор',
        unique_for_date='publish',
        max_length=250)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='blog_posts')
    body = models.TextField(
        help_text='Введите текст поста',
        verbose_name='Текст',
    )
    publish = models.DateTimeField(
        verbose_name='Дата публикации',
        default=timezone.now)
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True)
    updated = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True)
    status = models.CharField(
        help_text='Укажите статус поста',
        verbose_name='Статус',
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        """
        Метаданные модели.
        """
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
            ]

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.publish.year,
                  self.publish.month,
                  self.publish.day,
                  self.slug])


class Comment(models.Model):
    """
    Модель для таблицы Comment.
    """
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    name = models.CharField(
        verbose_name='Имя',
        max_length=80)
    email = models.EmailField(
        verbose_name='Email адрес'
    )
    body = models.TextField(
        verbose_name='Текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True)
    updated = models.DateTimeField(
        verbose_name='Дата редактивирования комментария',
        auto_now=True
    )
    active = models.BooleanField(
        verbose_name='Статус комментария',
        default=True
    )

    class Meta:
        """
        Метаданные модели.
        """
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
