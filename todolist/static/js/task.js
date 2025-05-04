// Change checkmark icon on hover
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".checkmark").forEach(icon => {
        icon.addEventListener("mouseenter", function () {
            if (this.classList.contains("bi-circle")) {
                this.classList.replace("bi-circle", "bi-check-circle");
            }
        });
        icon.addEventListener("mouseleave", function () {
            if (this.classList.contains("bi-check-circle")) {
                this.classList.replace("bi-check-circle", "bi-circle");
            }
        });
    });
});

// Complete task
async function completeTask(taskId) {
	const url = `/task/${taskId}/complete/`;
	const success = await sendRequest(url, 'POST');

	if (success) {
		const sound = document.getElementById("completion-sound");
		sound.currentTime = 0;
		await sound.play();

		const taskElement = document.getElementById(`task-${taskId}`);
		const taskEditingOffcanvas = document.getElementById(`edit-task-${taskId}`);
		const taskElementParent = taskElement.parentElement;
		taskElement.remove();
		taskEditingOffcanvas.remove();
		if (taskElementParent.children.length === 1) {
			taskElementParent.remove();
		}
	}
}

// Edit task
async function editTask(taskId, formData) {
    const url = `/task/${taskId}/edit/`;
    const categories = [];
    formData.getAll('categories').forEach(value => {
        categories.push(value);
    });
    
    const requestBody = Object.fromEntries(formData.entries());
    requestBody.categories = categories;
    
    const success = await sendRequest(url, 'PATCH', JSON.stringify(requestBody));
    if (success) {
        window.location.reload();
    }
}

// Edit Task forms submission listeners
document.querySelectorAll('.edit-task-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editTask(id, formData);
    });
});

// Create Task
const createTaskForm = document.getElementById('create-task-form');
if (createTaskForm) {
    createTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
    
        const url = '/task/create/';
        const formData = new FormData(e.target);
        formData.delete('csrfmiddlewaretoken');
    
        const categories = [];
        formData.getAll('categories').forEach(value => {
            categories.push(value);
        });
    
        const requestBody = Object.fromEntries(formData.entries());
        requestBody.categories = categories;
    
        const success = await sendRequest(url, 'POST', JSON.stringify(requestBody));
        if (success) {
            window.location.reload();
        }
    });
}
