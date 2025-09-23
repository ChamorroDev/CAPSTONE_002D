let allCertificados = [];

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Inicializando gestión de certificados...');
    await fetchCertificados();

    // Añadir event listeners para el buscador y el filtro
    document.getElementById('search-input').addEventListener('input', filterAndRender);
    document.getElementById('estado-filter').addEventListener('change', filterAndRender);
});

async function fetchCertificados() {
    const certificadosListContainer = document.getElementById('certificados-list');
    certificadosListContainer.innerHTML = '';

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/certificados/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Error en la respuesta de la API: ${response.status}`);
        }

        allCertificados = await response.json(); // Guardar los datos en la variable global
        filterAndRender(); // Renderizar con los datos completos
    } catch (error) {
        console.error('Error al obtener los certificados:', error);
        certificadosListContainer.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <p class="text-danger">Error al cargar las solicitudes.</p>
                </td>
            </tr>
        `;
    }
}

function filterAndRender() {
    const searchInput = document.getElementById('search-input').value.toLowerCase();
    const estadoFilter = document.getElementById('estado-filter').value;

    const filteredCertificados = allCertificados.filter(solicitud => {
        const matchesSearch = solicitud.usuario.nombre_completo.toLowerCase().includes(searchInput) ||
                              (solicitud.motivo && solicitud.motivo.toLowerCase().includes(searchInput));
        
        const matchesFilter = estadoFilter === '' || solicitud.estado === estadoFilter;
        
        return matchesSearch && matchesFilter;
    });

    renderCertificados(filteredCertificados);
}

function renderCertificados(certificados) {
    const certificadosListContainer = document.getElementById('certificados-list');
    certificadosListContainer.innerHTML = ''; // Limpiar la tabla antes de renderizar

    if (certificados.length === 0) {
        certificadosListContainer.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <p class="text-muted">No se encontraron solicitudes que coincidan con los filtros.</p>
                </td>
            </tr>
        `;
        return;
    }

    certificados.forEach(solicitud => {
        const row = document.createElement('tr');
        
        let estadoBadge = '';
        if (solicitud.estado === 'pendiente') {
            estadoBadge = 'bg-warning text-dark';
        } else if (solicitud.estado === 'aprobado') {
            estadoBadge = 'bg-success';
        } else if (solicitud.estado === 'rechazado') {
            estadoBadge = 'bg-danger';
        }

        row.innerHTML = `
            <td>${solicitud.id}</td>
            <td>${solicitud.usuario.nombre_completo}</td>
            <td>${solicitud.tipo_certificado}</td>
            <td><span class="badge ${estadoBadge}">${solicitud.estado}</span></td>
            <td>${solicitud.motivo || 'N/A'}</td>
            <td>${new Date(solicitud.fecha_solicitud).toLocaleDateString('es-ES')}</td>
            <td>
                <div class="btn-group btn-group-sm" id="acciones-${solicitud.id}">
                </div>
            </td>
        `;

        const accionesCell = row.querySelector(`#acciones-${solicitud.id}`);

        // Muestra los botones solo si el estado es 'pendiente'
        if (solicitud.estado === 'pendiente') {
            // Botón de Aprobar
            const aprobarBtn = document.createElement('button');
            aprobarBtn.textContent = 'Aprobar';
            aprobarBtn.className = 'btn btn-success btn-action';
            aprobarBtn.onclick = () => aprobarCertificado(solicitud.id);
            accionesCell.appendChild(aprobarBtn);

            // Botón de Rechazar
            const rechazarBtn = document.createElement('button');
            rechazarBtn.textContent = 'Rechazar';
            rechazarBtn.className = 'btn btn-danger btn-action';
            rechazarBtn.onclick = () => rechazarCertificado(solicitud.id);
            accionesCell.appendChild(rechazarBtn);
        }
        
        certificadosListContainer.appendChild(row);
    });
}

// --- Funciones para los botones de aprobar/rechazar (EXISTENTES) ---

async function aprobarCertificado(id) {
    if (confirm('¿Estás seguro de aprobar esta solicitud de certificado?')) {
        try {
            const token = localStorage.getItem('access_token');
            const csrfToken = getCookie('csrftoken');

            const response = await fetch(`${URL_API}api/directivo/certificados/${id}/aprobar/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                alert('Solicitud aprobada correctamente.');
                await fetchCertificados();
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            alert('Ocurrió un error al procesar la solicitud.');
            console.error(error);
        }
    }
}
async function rechazarCertificado(id) {
    if (confirm('¿Estás seguro de rechazar esta solicitud de certificado?')) {
        try {
            const token = localStorage.getItem('access_token');
            const csrfToken = getCookie('csrftoken'); 

            const response = await fetch(`${URL_API}api/directivo/certificados/${id}/rechazar/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, 
                }
            });

            if (response.ok) {
                alert('Solicitud rechazada correctamente.');
                await fetchCertificados();
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            alert('Ocurrió un error al procesar la solicitud.');
            console.error(error);
        }
    }
}

// Asegúrate de que esta función esté definida
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}