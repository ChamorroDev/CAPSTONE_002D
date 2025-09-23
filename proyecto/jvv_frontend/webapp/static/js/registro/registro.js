

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}

document.addEventListener('DOMContentLoaded', () => {
    const registroForm = document.getElementById('registroForm');
    const messageContainer = document.getElementById('message-container');

    if (registroForm) {
        registroForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 1. Crear un objeto FormData
            const formData = new FormData();

            // 2. Obtener los valores de los campos y añadirlos al FormData
            formData.append('nombre', document.getElementById('nombre').value);
            formData.append('apellido', document.getElementById('apellido').value);
            formData.append('email', document.getElementById('email').value);
            formData.append('rut', document.getElementById('rut').value);
            formData.append('telefono', document.getElementById('telefono').value);
            formData.append('direccion', document.getElementById('direccion').value);
            formData.append('fecha_nacimiento', document.getElementById('fecha_nacimiento').value);
            formData.append('password', document.getElementById('password').value);

            // 3. Obtener el archivo y añadirlo
            const documentoInput = document.getElementById('documento_verificacion');
            if (documentoInput.files.length > 0) {
                formData.append('documento_verificacion', documentoInput.files[0]);
            }

            try {
                const response = await fetch(`${URL_API}api/registro/vecino/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: formData // Enviar el objeto FormData directamente
                });

                const data = await response.json();

                if (response.ok) {
                    messageContainer.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    registroForm.reset();
                } else {
                    const errors = Object.values(data).flat().join('<br>');
                    messageContainer.innerHTML = `<div class="alert alert-danger">${errors}</div>`;
                }

            } catch (error) {
                console.error('Error:', error);
                messageContainer.innerHTML = `<div class="alert alert-danger">Error de conexión con el servidor. Por favor, intente de nuevo.</div>`;
            }
        });
    }
});