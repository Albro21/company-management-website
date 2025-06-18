// Change displayed profile picture after upload
document.getElementById('profile_picture_input').addEventListener('change', function(event) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile_picture').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('theme-switch').addEventListener('change', async function () {
    const url = '/switch-theme/';
    const data = await sendRequest(url, 'PATCH');

    if (data.success) {
        queueToast('Theme changed', 'success');
        window.location.reload();
    }
});

document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = `/edit-user/`;
    const formData = new FormData(e.target);
    formData.delete('csrfmiddlewaretoken');

    const data = await sendRequest(url, 'POST', formData);

    if (data.success) {
        queueToast('User settings updated', 'success');
        window.location.reload();
    } else {
        const errorElement = document.getElementById('error');
        let errors = data.error;

        if (errors.some(msg => msg.includes("email"))) {
            document.getElementById('email').classList.add('is-invalid');
        }

        errorElement.textContent = errors.join('\n');
    }
});
