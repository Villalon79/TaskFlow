from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='boards'
    )

    def __str__(self):
        return self.name


class TaskList(models.Model):
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasklists'
    )

    def __str__(self):
        return self.name


class Task(models.Model):

    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    due_date = models.DateField(null=True, blank=True)

    tasklist = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    assigned_to = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assigned_tasks'
    )

    def __str__(self):
        return self.title

    tags = models.ManyToManyField(
    'Tag',
    blank=True,
    related_name='tasks'
    )

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name