class ProyectosManager {
    constructor() {
        this.URL_PROYECTOS_API = `${URL_API}api/proyectos/`;
        this.proyectosData = [];
        this.init();
    }

    init() {
        console.log('Inicializando gestor de proyectos...');
        this.loadProyectosData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listeners for the search bar and filter
        document.getElementById('searchInput').addEventListener('input', this.filterAndRender.bind(this));
        document.getElementById('estadoFilter').addEventListener('change', this.filterAndRender.bind(this));
    }

    async loadProyectosData() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(this.URL_PROYECTOS_API, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Almacenamos todos los proyectos en una variable
                this.proyectosData = await response.json(); 
                this.filterAndRender(); // Llamar a la función de filtrado al cargar
            } else {
                console.error('Error al cargar proyectos:', response.status);
                this.mostrarMensaje('Error al cargar la lista de proyectos.', 'error');
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            this.mostrarMensaje('Error de conexión. Inténtalo de nuevo más tarde.', 'error');
        }
    }

    // Nueva función para filtrar los proyectos
    filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const estadoFilter = document.getElementById('estadoFilter').value;

        let filteredProyectos = this.proyectosData;

        // Filtrar por estado
        if (estadoFilter !== 'todos') {
            filteredProyectos = filteredProyectos.filter(p => p.estado === estadoFilter);
        }

        // Filtrar por término de búsqueda (título o solicitante)
        if (searchTerm) {
            filteredProyectos = filteredProyectos.filter(p => 
                p.titulo.toLowerCase().includes(searchTerm) || 
                p.solicitante_nombre.toLowerCase().includes(searchTerm)
            );
        }

        this.renderProyectos(filteredProyectos);
    }
    
    // El resto de la clase permanece igual
    renderProyectos(proyectos) {
        const container = document.getElementById('proyectos-list');
        if (!container) return; 

        if (proyectos.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-5">
                        <i class="bi bi-check-circle text-success" style="font-size: 2rem;"></i>
                        <p class="text-muted mt-2">No se encontraron proyectos que coincidan con la búsqueda.</p>
                    </td>
                </tr>
            `;
            return;
        }

        // Se genera el encabezado de la tabla dinámicamente como en el código anterior
        // ... (Tu código para el encabezado de la tabla)
        
        container.innerHTML = proyectos.map(proyecto => `
            <tr>
                <td>${proyecto.titulo || 'N/A'}</td>
                <td>${proyecto.solicitante_nombre || 'N/A'}</td>
                <td>${proyecto.estado || 'N/A'}</td>
                <td>${proyecto.fecha_creacion || 'N/A'}</td>
                <td>${proyecto.fecha_resolucion || 'N/A'}</td>
                <td>${proyecto.revisado_por || 'N/A'}</td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm">
                        <a href="/proyectos/${proyecto.id}/" class="btn btn-primary text-white">
                            <i class="bi bi-eye me-1"></i> Ver Detalles
                        </a>
                        ${proyecto.estado === 'pendiente' ? `
                            <button class="btn btn-success" onclick="window.proyectosManager.aprobarProyecto(${proyecto.id})">
                                <i class="bi bi-check-lg me-1"></i> Aprobar
                            </button>
                            <button class="btn btn-danger" onclick="window.proyectosManager.rechazarProyecto(${proyecto.id})">
                                <i class="bi bi-x-lg me-1"></i> Rechazar
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async aprobarProyecto(proyectoId) {
        this.enviarAccion(proyectoId, 'aprobar');
    }

    async rechazarProyecto(proyectoId) {
        this.enviarAccion(proyectoId, 'rechazar');
    }

    async enviarAccion(proyectoId, accion) {
        const token = localStorage.getItem('access_token');
        try {
            const urlAccion = `${URL_API}api/proyectos/${proyectoId}/${accion}/`;
            const response = await fetch(urlAccion, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const mensajeAccion = accion === 'aprobar' ? 'aprobado' : 'rechazado';
                this.mostrarMensaje(`El proyecto ha sido ${mensajeAccion} correctamente.`, 'success');
                await this.loadProyectosData();
            } else {
                this.mostrarMensaje(`Error al ${accion} el proyecto.`, 'error');
            }
        } catch (error) {
            this.mostrarMensaje(`Error al conectar con la API para ${accion}.`, 'error');
        }
    }

    mostrarMensaje(mensaje, tipo = 'success') {
        const messageContainer = document.getElementById('app-messages');
        if (messageContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'}`;
            messageElement.textContent = mensaje;
            messageContainer.appendChild(messageElement);
            setTimeout(() => {
                messageElement.remove();
            }, 5000);
        } else {
            console.log(`Mensaje: ${mensaje}`);
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.proyectosManager = new ProyectosManager();
});