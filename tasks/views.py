from django.views.generic import (ListView, CreateView,
                                   UpdateView, DeleteView,
                                   DetailView)
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import Board, Task, TaskList
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import csv
from django.http import HttpResponse
import json
from django.core.mail import send_mail


class BoardListView(LoginRequiredMixin, ListView):
    model = Board
    template_name = 'tasks/board_list.html'
    context_object_name = 'boards'

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user)


class BoardDetailView(LoginRequiredMixin, DetailView):
    model = Board
    template_name = 'tasks/board_detail.html'
    context_object_name = 'board'

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasklists'] = self.object.tasklists.all()
        return context
    

class BoardCreateView(LoginRequiredMixin, CreateView):
    model = Board
    fields = ['name', 'description']
    template_name = 'tasks/board_form.html'
    success_url = reverse_lazy('board_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        TaskList.objects.create(
        name='Pendiente',
        position=0,
        board=self.object
        )

        TaskList.objects.create(
        name='En progreso',
        position=1,
        board=self.object
        )

        return response


class BoardUpdateView(LoginRequiredMixin, UpdateView):
    model = Board
    fields = ['name', 'description']
    template_name = 'tasks/board_form.html'
    success_url = reverse_lazy('board_list')

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user)


class BoardDeleteView(LoginRequiredMixin, DeleteView):
    model = Board
    template_name = 'tasks/board_confirm_delete.html'
    success_url = reverse_lazy('board_list')

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = [
        'title',
        'description',
        'assigned_to',
        'priority',
        'tags',
        'due_date'
    ]
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('board_list')

    def form_valid(self, form):
        tasklist = TaskList.objects.get(
        pk=self.kwargs['list_pk'],
        board__owner=self.request.user
    )

        form.instance.tasklist = tasklist

        response = super().form_valid(form)

        if self.object.assigned_to:
            send_mail(
            subject='Nueva tarea asignada en TaskFlow',
            message=(
                f'Hola {self.object.assigned_to.username}, '
                f'te han asignado una nueva tarea: '
                f'{self.object.title}'
            ),
            from_email=None,
            recipient_list=[self.object.assigned_to.email],
        )

        return response
    


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = [
        'title',
        'description',
        'tasklist',
        'assigned_to',
        'priority',
        'tags',
        'due_date'
    ]
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('board_list')

    def get_queryset(self):
        return Task.objects.filter(
            tasklist__board__owner=self.request.user
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tasklist'].queryset = TaskList.objects.filter(
            board__owner=self.request.user
        )
        return form

    def form_valid(self, form):
        previous_assigned = self.get_object().assigned_to

        response = super().form_valid(form)

        if (
            self.object.assigned_to
            and self.object.assigned_to != previous_assigned
        ):
            send_mail(
                subject='Nueva tarea asignada en TaskFlow',
                message=(
                    f'Hola {self.object.assigned_to.username}, '
                    f'te han asignado una tarea: '
                    f'{self.object.title}'
                ),
                from_email=None,
                recipient_list=[self.object.assigned_to.email],
            )

        return response


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('board_list')

    def get_queryset(self):
        return Task.objects.filter(
            tasklist__board__owner=self.request.user
        )


@login_required
@require_POST
def move_task(request):
    task_id = request.POST.get('task_id')
    list_id = request.POST.get('list_id')

    task = get_object_or_404(
        Task,
        pk=task_id,
        tasklist__board__owner=request.user
    )

    new_list = get_object_or_404(
        TaskList,
        pk=list_id,
        board__owner=request.user
    )

    if task.tasklist.board_id != new_list.board_id:
        return JsonResponse(
            {'error': 'No puedes mover tareas a otro tablero.'},
            status=400
        )

    task.tasklist = new_list
    task.save()

    return JsonResponse({'success': True})


@login_required
def export_tasks_csv(request, pk):
    board = get_object_or_404(
        Board,
        pk=pk,
        owner=request.user
    )

    response = HttpResponse(
        content_type='text/csv'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="tablero_{board.pk}.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        'Titulo',
        'Descripcion',
        'Lista',
        'Asignado a',
        'Prioridad',
        'Fecha de vencimiento',
        'Etiquetas'
    ])

    for tasklist in board.tasklists.all():
        for task in tasklist.tasks.all():
            writer.writerow([
                task.title,
                task.description,
                tasklist.name,
                task.assigned_to.username if task.assigned_to else '',
                task.get_priority_display(),
                task.due_date or '',
                ', '.join(tag.name for tag in task.tags.all())
            ])

    return response


@login_required
def export_tasks_json(request, pk):
    board = get_object_or_404(
        Board,
        pk=pk,
        owner=request.user
    )

    tasks_data = []

    for tasklist in board.tasklists.all():
        for task in tasklist.tasks.all():
            tasks_data.append({
                'titulo': task.title,
                'descripcion': task.description,
                'lista': tasklist.name,
                'asignado_a': (
                    task.assigned_to.username
                    if task.assigned_to else None
                ),
                'prioridad': task.get_priority_display(),
                'fecha_vencimiento': (
                    task.due_date.isoformat()
                    if task.due_date else None
                ),
                'etiquetas': [
                    tag.name for tag in task.tags.all()
                ]
            })

    response = HttpResponse(
        json.dumps(
            tasks_data,
            ensure_ascii=False,
            indent=4
        ),
        content_type='application/json'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="tablero_{board.pk}.json"'
    )

    return response