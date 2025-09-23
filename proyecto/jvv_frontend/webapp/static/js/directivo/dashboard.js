class DirectivoDashboard {
    constructor() {
        // La URL de la API del dashboard es la única que necesitamos
        this.URL_DASHBOARD_API = 'http://127.0.0.1:8000/api/directivo/dashboard/';
        this.init();
    }

    async init() {
        console.log('Inicializando Dashboard Directivo...');
        await this.loadDashboardData();
        this.setupEventListeners();
    }

    async loadDashboardData() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(this.URL_DASHBOARD_API, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDashboard(data);
                this.initCharts(data.solicitudes_mes_a_mes || []);
            } else {
                console.error('Error cargando dashboard:', response.status);
                // Opcional: mostrar un mensaje de error en el UI
            }
        } catch (error) {
            console.error('Error:', error);
            // Opcional: mostrar un mensaje de error en el UI
        }
    }

    updateDashboard(data) {
        // Actualizar estadísticas de las tarjetas
        document.getElementById('total-vecinos').textContent = data.total_vecinos || 0;
        document.getElementById('pending-users-count').textContent = data.pendientes_aprobacion || 0;
        document.getElementById('pending-certificados').textContent = data.certificados_pendientes || 0;
        document.getElementById('pending-badge').textContent = data.pendientes_aprobacion || 0;

        // Agregar actualización de proyectos
        document.getElementById('pending-proyectos').textContent = data.proyectos_pendientes || 0;
        document.getElementById('pending-proyectos-badge').textContent = data.proyectos_pendientes || 0;

        // Actualizar lista de pendientes
        this.renderPendingUsers(data.usuarios_pendientes || []);

        // Actualizar proyectos pendientes 
        this.renderProyectosPendientes(data.proyectos_pendientes_lista || []);

        // Actualizar eventos
        this.renderProximosEventos(data.proximos_eventos || []);

        // Actualizar noticias
        this.renderNoticiasRecientes(data.noticias_recientes || []);
    }


    renderPendingUsers(usuarios) {
        const container = document.getElementById('pending-users-list');
        this.usuariosPendientesData = usuarios; // Guardar la data para el nuevo método
        
        if (usuarios.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4">
                        <i class="bi bi-check-circle text-success" style="font-size: 2rem;"></i>
                        <p class="text-muted mt-2">No hay usuarios pendientes de aprobación</p>
                    </td>
                </tr>
            `;
            return;
        }

        container.innerHTML = usuarios.map(user => `
            <tr>
                <td>${user.nombre_completo || 'N/A'}</td>
                <td>${user.rut || 'N/A'}</td>
                <td>${user.email || 'N/A'}</td>
                <td>${new Date(user.fecha_registro).toLocaleDateString('es-ES')}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-primary btn-action" 
                                onclick="window.directivoDashboard.verDocumentacion(${user.id})"
                                ${user.documento_verificacion ? '' : 'disabled'}
                                title="${user.documento_verificacion ? 'Ver documento de verificación' : 'No hay documento adjunto'}">
                            <i class="bi bi-eye"></i> Ver
                        </button>
                        <button class="btn btn-success btn-action" onclick="window.directivoDashboard.aprobarUsuario(${user.id})">
                            <i class="bi bi-check-lg"></i> Aprobar
                        </button>
                        <button class="btn btn-danger btn-action" onclick="window.directivoDashboard.rechazarUsuario(${user.id})">
                            <i class="bi bi-x-lg"></i> Rechazar
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    verDocumentacion(userId) {
        // La URL base del backend.
        const BACKEND_BASE_URL = 'http://127.0.0.1:8000';

        const usuario = this.usuariosPendientesData.find(u => u.id === userId);

        if (usuario && usuario.documento_verificacion) {
            // Construimos la URL completa. Nota que ahora añadimos "/media".
            const documentoUrl = `${BACKEND_BASE_URL}/media/${usuario.documento_verificacion}`;
            window.open(documentoUrl, '_blank');
        } else {
            this.mostrarMensaje('No se encontró documentación para este usuario', 'info');
        }
    }


    renderProximosEventos(eventos) {
        const container = document.getElementById('proximos-eventos');
        
        if (eventos.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay eventos próximos</p>';
            return;
        }

        // Limita la lista a los 3 eventos más recientes
        const eventosRecientes = eventos.slice(0,2);

        container.innerHTML = eventosRecientes.map(evento => `
            <div class="border-bottom pb-3 mb-3">
                <h6 class="mb-1">${evento.titulo}</h6>
                <p class="text-muted small mb-1">
                    <i class="bi bi-calendar"></i>
                    ${new Date(evento.fecha).toLocaleDateString('es-ES')}
                </p>
                <p class="small">${evento.descripcion?.substring(0, 60)}...</p>
                <a href="/actividades/${evento.id}/" class="btn btn-sm btn-outline-primary">Ver detalles</a>
            </div>
        `).join('');
    }

    renderNoticiasRecientes(noticias) {
        const container = document.getElementById('noticias-recientes');
        
        if (noticias.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay noticias recientes</p>';
            return;
        }

        // Limita la lista a las 3 noticias más recientes
        const noticiasRecientes = noticias.slice(0, 2);

        container.innerHTML = noticiasRecientes.map(noticia => `
            <div class="border-bottom pb-3 mb-3">
                <h6 class="mb-1">${noticia.titulo}</h6>
                <p class="text-muted small mb-2">
                    ${new Date(noticia.fecha_creacion).toLocaleDateString('es-ES')}
                </p>
                <p class="mb-2">${noticia.contenido?.substring(0, 100)}...</p>
                <a href="/noticias/${noticia.id}/" class="btn btn-sm btn-outline-primary">Leer más</a>
            </div>
        `).join('');
    }

    renderProyectosPendientes(proyectos) {
        const container = document.getElementById('pending-proyectos-list');

        if (!proyectos || proyectos.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">
                        <i class="bi bi-check-circle text-success" style="font-size: 2rem;"></i>
                        <p class="text-muted mt-2">No hay proyectos pendientes</p>
                    </td>
                </tr>
            `;
            return;
        }

        container.innerHTML = proyectos.map(proyecto => `
            <tr>
                <td>${proyecto.titulo}</td>
                <td>${proyecto.proponente__nombre || 'N/A'}</td>
                <td>${new Date(proyecto.fecha_creacion).toLocaleDateString('es-ES')}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="/proyectos/${proyecto.id}/" class="btn btn-primary">
                            <i class="bi bi-eye"></i> Ver
                        </a>
                    </div>
                </td>
            </tr>
        `).join('');
    }


    initCharts(chartData) {
        const ctx = document.getElementById('solicitudesChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.map(item => item.mes),
                    datasets: [{
                        label: 'Solicitudes',
                        data: chartData.map(item => item.total),
                        backgroundColor: 'rgba(37, 99, 235, 0.8)',
                        borderColor: 'rgba(37, 99, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    setupEventListeners() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        document.querySelector('.sidebar-toggle')?.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    async aprobarUsuario(userId) {
        if (confirm('¿Estás seguro de aprobar este usuario?')) {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`http://127.0.0.1:8000/api/usuarios/${userId}/aprobar/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    this.mostrarMensaje('Usuario aprobado correctamente', 'success');
                    await this.loadDashboardData();
                } else {
                    throw new Error('Error al aprobar usuario');
                }
            } catch (error) {
                this.mostrarMensaje('Error al aprobar usuario', 'error');
            }
        }
    }

    async rechazarUsuario(userId) {
        if (confirm('¿Estás seguro de rechazar este usuario?')) {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`http://127.0.0.1:8000/api/usuarios/${userId}/rechazar/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    this.mostrarMensaje('Usuario rechazado correctamente', 'success');
                    await this.loadDashboardData();
                } else {
                    throw new Error('Error al rechazar usuario');
                }
            } catch (error) {
                this.mostrarMensaje('Error al rechazar usuario', 'error');
            }
        }
    }

    mostrarMensaje(mensaje, tipo = 'success') {
        alert(`${tipo.toUpperCase()}: ${mensaje}`);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.directivoDashboard = new DirectivoDashboard();
});