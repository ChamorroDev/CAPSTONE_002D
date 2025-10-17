document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    
    const form = document.getElementById('noticiaForm');
    const tituloInput = document.getElementById('titulo');
    const contenidoInput = document.getElementById('contenido');
    const esPublicaInput = document.getElementById('esPublica');
    const alertsContainer = document.getElementById('alertsContainer');
    const formSpinner = document.getElementById('formSpinner');

    function showAlert(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertsContainer.appendChild(alert);
        
        if (duration) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
    }

    function showLoading(button, show = true) {
        const spinner = button.querySelector('.loading-spinner') || formSpinner;
        if (spinner) {
            spinner.style.display = show ? 'inline-block' : 'none';
        }
        button.disabled = show;
        
        const textSpan = button.querySelector('span');
        if (textSpan) {
            textSpan.textContent = show ? 'Creando...' : 'Crear Noticia';
        }
    }

    function validateForm() {
        const titulo = tituloInput.value.trim();
        const contenido = contenidoInput.value.trim();

        if (!titulo) {
            showAlert('El título es obligatorio', 'warning');
            tituloInput.focus();
            return false;
        }

        if (!contenido) {
            showAlert('El contenido es obligatorio', 'warning');
            contenidoInput.focus();
            return false;
        }

        return true;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        const submitButton = event.target.querySelector('button[type="submit"]');
        showLoading(submitButton, true);

        try {
            const noticiaData = {
                titulo: tituloInput.value.trim(),
                contenido: contenidoInput.value.trim(),
                es_publica: esPublicaInput.checked
            };

            console.log('📤 Enviando datos:', noticiaData);

            const response = await fetch(`${URL_API}api/directivo/noticias/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(noticiaData)
            });

            const responseData = await response.json();
            console.log('📥 Respuesta del servidor:', responseData);

            if (response.ok) {
                showAlert('¡Noticia creada con éxito! Redirigiendo...', 'success');
                
                setTimeout(() => {
                    if (responseData.id) {
                        window.location.href = `/gestion_noticias/editar/${responseData.id}`;
                    } else {
                        window.location.href = '/gestion_noticias/';
                    }
                }, 1500);
                
            } else {
                console.error('❌ Error completo:', responseData);
                
                let errorMessage = 'Error al crear la noticia';
                
                if (responseData.detail) {
                    errorMessage = responseData.detail;
                } else if (responseData.error) {
                    errorMessage = responseData.error;
                } else if (typeof responseData === 'object') {
                    const fieldErrors = [];
                    for (const [field, errors] of Object.entries(responseData)) {
                        fieldErrors.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
                    }
                    errorMessage = fieldErrors.join(' | ') || errorMessage;
                }
                
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('💥 Error al crear la noticia:', error);
            showAlert(`Error al crear la noticia: ${error.message}`, 'danger');
        } finally {
            showLoading(submitButton, false);
        }
    });

    if (!token) {
        showAlert('Debes iniciar sesión para crear noticias. Redirigiendo...', 'danger');
        setTimeout(() => {
            window.location.href = '/login/';
        }, 2000);
        return;
    }
});