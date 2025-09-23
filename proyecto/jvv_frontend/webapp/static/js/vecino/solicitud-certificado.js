document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('solicitudForm');
    const messageDiv = document.getElementById('certificado-message');

    // Cargar solicitudes previas al iniciar
    cargarSolicitudesPrevias();

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            messageDiv.innerHTML = '';

            const token = localStorage.getItem('access_token');
            if (!token) {
                showError('Debe iniciar sesión para solicitar un certificado');
                return;
            }

            const formData = {
                tipo: form.tipo.value,
                motivo: form.motivo.value
            };

            try {
                const response = await fetch(`${URL_API}api/certificados/solicitar/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess('Solicitud enviada correctamente');
                    form.reset();
                    cargarSolicitudesPrevias(); // Recargar la tabla
                } else {
                    const errorMsg = data.error || 'Error al enviar la solicitud';
                    showError(errorMsg);
                }
            } catch (error) {
                showError('Error de conexión: ' + error.message);
            }
        });
    }

    async function cargarSolicitudesPrevias() {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const response = await fetch(`${URL_API}api/certificados/mis-solicitudes/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const solicitudes = await response.json();
                actualizarTablaSolicitudes(solicitudes);
            }
        } catch (error) {
            console.error('Error cargando solicitudes:', error);
        }
    }

    function actualizarTablaSolicitudes(solicitudes) {
        const tbody = document.querySelector('#tabla-solicitudes tbody');
        
        if (solicitudes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No tienes solicitudes previas</td></tr>';
            return;
        }

        tbody.innerHTML = solicitudes.map(solicitud => `
            <tr>
                <td>${new Date(solicitud.fecha_solicitud).toLocaleDateString()}</td>
                <td>${solicitud.tipo}</td>
                <td>${solicitud.motivo.substring(0, 50)}${solicitud.motivo.length > 50 ? '...' : ''}</td>
                <td>
                    <span class="badge ${getBadgeClass(solicitud.estado)}">
                        ${solicitud.estado}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    function getBadgeClass(estado) {
        switch(estado) {
            case 'aprobado': return 'bg-success';
            case 'rechazado': return 'bg-danger';
            default: return 'bg-warning text-dark';
        }
    }

    function showSuccess(message) {
        messageDiv.innerHTML = `<div class="alert alert-success">${message}</div>`;
    }

    function showError(message) {
        messageDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
});