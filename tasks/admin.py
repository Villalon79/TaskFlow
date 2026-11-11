
from django.contrib import admin
from .models import Board, TaskList, Task, Tag

admin.site.register(Board)
admin.site.register(TaskList)
admin.site.register(Task)
admin.site.register(Tag)


