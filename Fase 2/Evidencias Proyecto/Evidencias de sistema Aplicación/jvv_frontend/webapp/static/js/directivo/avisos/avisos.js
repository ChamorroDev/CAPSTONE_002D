

document.addEventListener('DOMContentLoaded', () => {
    // Referencias a los elementos del DOM
    const avisoForm = document.getElementById('avisoForm');
    const feedbackMessage = document.getElementById('feedbackMessage');
    const tituloInput = document.getElementById('titulo');
    const contenidoTextarea = document.getElementById('contenido');
    const emailCheck = document.getElementById('email_check');
    const whatsappCheck = document.getElementById('whatsapp_check');

    // Manejador del evento de envío del formulario
    avisoForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Determinar el tipo de aviso basado en las casillas de verificación
        let tipoAviso = '';
        if (emailCheck.checked && whatsappCheck.checked) {
            tipoAviso = 'ambos';
        } else if (emailCheck.checked) {
            tipoAviso = 'email';
        } else if (whatsappCheck.checked) {
            tipoAviso = 'whatsapp';
        } else {
            showMessage('Por favor, selecciona al menos un canal de distribución.', 'warning');
            return;
        }

        // 2. Recopilar los datos del formulario
        const data = {
            titulo: tituloInput.value,
            contenido: contenidoTextarea.value,
            tipo_aviso: tipoAviso,
        };

        // 3. Obtener el token de autenticación
        const token = localStorage.getItem('access_token');
        if (!token) {
            showMessage('No estás autenticado. Por favor, inicia sesión de nuevo.', 'danger');
            return;
        }

        // 4. Enviar la solicitud a la API de Django
        try {
            const response = await fetch(`${URL_API}api/directivo/enviar_aviso_masivo/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(result.message, 'success');
                // Limpiar el formulario después del envío exitoso
                avisoForm.reset();
            } else {
                showMessage(result.error || 'Hubo un problema al enviar el aviso.', 'danger');
            }

        } catch (error) {
            console.error('Error:', error);
            showMessage('Ocurrió un error inesperado. Inténtalo de nuevo más tarde.', 'danger');
        }
    });

    // Función para mostrar mensajes de feedback
    function showMessage(message, type) {
        feedbackMessage.innerHTML = `<div class="alert alert-${type} text-center" role="alert">${message}</div>`;
        setTimeout(() => {
            feedbackMessage.innerHTML = '';
        }, 5000); // El mensaje desaparece después de 5 segundos
    }
});