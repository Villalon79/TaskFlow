let draggedTask = null;

// Cuando empezamos a arrastrar una tarea
document.querySelectorAll('.task').forEach(task => {
    task.addEventListener('dragstart', function () {
        draggedTask = this;
    });
});

// Cuando soltamos una tarea sobre una lista
document.querySelectorAll('.task-list').forEach(list => {
    list.addEventListener('dragover', function (event) {
        event.preventDefault();
    });

    list.addEventListener('drop', function (event) {
        event.preventDefault();

        if (!draggedTask) {
            return;
        }

        const taskId = draggedTask.dataset.taskId;
        const listId = this.dataset.listId;

        moveTask(taskId, listId, this);
    });
});


function moveTask(taskId, listId, destinationList) {
    const csrfToken = document.querySelector(
        '[name=csrfmiddlewaretoken]'
    ).value;

    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('list_id', listId);

    fetch('/tareas/mover/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('No se pudo mover la tarea');
        }

        return response.json();
    })
    .then(data => {
         if (data.success) {
             // Eliminar el mensaje de lista vacía del destino
             const destinationMessage = destinationList.querySelector('.empty-message');

            if (destinationMessage) {
                destinationMessage.remove();
            }

            // Guardar la lista de origen
            const originList = draggedTask.closest('.task-list');

            // Mover la tarea
            destinationList.appendChild(draggedTask);

            // Comprobar si la lista de origen se ha quedado vacía
            if (!originList.querySelector('.task')) {
                const message = document.createElement('p');
                message.classList.add('empty-message');
                message.textContent = 'No hay tareas en esta lista.';
                originList.appendChild(message);
            }

            draggedTask = null;
        }
    })
    .catch(error => {
        console.error(error);
        alert('Error al mover la tarea.');
    });
}