document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('proyectoForm');
    const messageDiv = document.getElementById('proyecto-message');
    const proyectosTableBody = document.getElementById('proyectos-table-body');


    function renderizarProyectos(proyectos) {
        proyectosTableBody.innerHTML = ''; 
        if (proyectos.length === 0) {
            proyectosTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Aún no has postulado ningún proyecto.</td></tr>';
            return;
        }

        proyectos.forEach(proyecto => {
            const row = document.createElement('tr');
            
            let estadoBadge = '';
            const estadoDisplay = proyecto.estado.charAt(0).toUpperCase() + proyecto.estado.slice(1);

            if (proyecto.estado === 'aprobado') {
                estadoBadge = `<span class="badge bg-success">${estadoDisplay}</span>`;
            } else if (proyecto.estado === 'rechazado') {
                estadoBadge = `<span class="badge bg-danger">${estadoDisplay}</span>`;
            } else if (proyecto.estado === 'completado') {
                estadoBadge = `<span class="badge bg-info text-dark">${estadoDisplay}</span>`;
            } else {
                estadoBadge = `<span class="badge bg-warning text-dark">${estadoDisplay}</span>`;
            }
            
            const fechaCreacion = new Date(proyecto.fecha_creacion).toLocaleDateString('es-CL');
            const fechaRevision = proyecto.fecha_revision ? new Date(proyecto.fecha_revision).toLocaleDateString('es-CL') : 'Pendiente';

            row.innerHTML = `
                <td>${proyecto.titulo}</td>
                <td>${fechaCreacion}</td>
                <td>${estadoBadge}</td>
                <td>${fechaRevision}</td>
            `;
            proyectosTableBody.appendChild(row);
        });
    }

    async function cargarProyectosUsuario() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            proyectosTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Debe iniciar sesión para ver sus proyectos.</td></tr>';
            return;
        }

        try {
            const response = await fetch(`${URL_API}api/proyectos/vecino-proyectos/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                renderizarProyectos(data);
            } else {
                proyectosTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Error al cargar proyectos: ${JSON.stringify(data.error || data)}</td></tr>`;
            }
        } catch (error) {
            proyectosTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Error de conexión con la API.</td></tr>`;
        }
    }

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            messageDiv.innerHTML = '';
            
            const token = localStorage.getItem('access_token');
            if (!token) {
                messageDiv.innerHTML = `<div class="alert alert-danger">Debe iniciar sesión para postular un proyecto.</div>`;
                return;
            }

            const formData = {
                titulo: form.titulo.value,
                descripcion: form.descripcion.value,
            };

            try {
                const response = await fetch(`${URL_API}api/proyectos/postular/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]') ? form.querySelector('[name=csrfmiddlewaretoken]').value : ''
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    messageDiv.innerHTML = `<div class="alert alert-success">¡Proyecto postulado correctamente!</div>`;
                    form.reset();
                    setTimeout(() => window.location.reload(), 4000);
                } else {
                    let errorMsg = data.error ? JSON.stringify(data.error) : 'Error al postular el proyecto.';
                    messageDiv.innerHTML = `<div class="alert alert-danger">${errorMsg}</div>`;
                }
            } catch (error) {
                messageDiv.innerHTML = `<div class="alert alert-danger">Error de conexión.</div>`;
            }
        });
    }

    cargarProyectosUsuario();
});