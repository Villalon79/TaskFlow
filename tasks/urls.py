from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (BoardListView, BoardCreateView,
                    SignUpView, BoardUpdateView,
                    BoardDeleteView, TaskCreateView,
                    BoardDetailView, TaskUpdateView, 
                    TaskDeleteView, move_task,
                    export_tasks_csv, export_tasks_json)

urlpatterns = [
    path('', BoardListView.as_view(), name='board_list'),

    path('tableros/<int:pk>/', BoardDetailView.as_view(), name='board_detail'),

    path('tableros/crear/', BoardCreateView.as_view(), name='board_create'),

    
    path('tableros/<int:pk>/editar/', BoardUpdateView.as_view(), name='board_update'),

    path('tableros/<int:pk>/eliminar/', BoardDeleteView.as_view(), name='board_delete'),

    path('registro/', SignUpView.as_view(), name='signup'),

    path('login/', LoginView.as_view(template_name='registration/login.html', next_page='/'), name='login'),

    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('listas/<int:list_pk>/tareas/crear/', TaskCreateView.as_view(), name='task_create'),

    path('tareas/<int:pk>/editar/', TaskUpdateView.as_view(), name='task_update'),

    path('tareas/<int:pk>/eliminar/', TaskDeleteView.as_view(), name='task_delete'),

    path('tareas/mover/', move_task, name='task_move'),

    path('tableros/<int:pk>/exportar/csv/', export_tasks_csv, name='export_tasks_csv'),

    path('tableros/<int:pk>/exportar/json/', export_tasks_json, name='export_tasks_json'),
]