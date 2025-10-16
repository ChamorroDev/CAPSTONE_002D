class GestionEspacios {
    constructor() {
        this.espacios = [];
        this.espacioAEliminar = null;
        this.init();
    }

    async init() {
        await this.cargarEspacios();
        this.setupEventListeners();
        this.actualizarEstadisticas();
    }

    setupEventListeners() {
        // Botón guardar espacio
        document.getElementById('btn-guardar-espacio').addEventListener('click', () => this.guardarEspacio());
        
        // Botón confirmar eliminar
        document.getElementById('btn-confirmar-eliminar').addEventListener('click', () => this.eliminarEspacioConfirmado());
        
        // Búsqueda en tiempo real
        document.getElementById('buscar-espacio').addEventListener('input', () => this.filtrarEspacios());
        
        // Filtros
        document.getElementById('filtro-tipo').addEventListener('change', () => this.filtrarEspacios());
        document.getElementById('filtro-disponible').addEventListener('change', () => this.filtrarEspacios());
        
        // Enter en formulario
        document.getElementById('formEspacio').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.guardarEspacio();
            }
        });
        
        // Limpiar formulario cuando se cierra el modal
        document.getElementById('modalCrearEspacio').addEventListener('hidden.bs.modal', () => {
            this.limpiarFormulario();
        });
    }

    async cargarEspacios() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/directivo/gestion_espacios/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.espacios = data.espacios || data || [];
                this.renderizarEspacios();
                this.actualizarEstadisticas();
            } else {
                this.mostrarError('Error al cargar los espacios');
            }
        } catch (error) {
            console.error('Error cargando espacios:', error);
            this.mostrarError('Error de conexión al cargar espacios');
        }
    }

    renderizarEspacios(espaciosFiltrados = null) {
        const espacios = espaciosFiltrados || this.espacios;
        const container = document.getElementById('lista-espacios');
        const estadoVacio = document.getElementById('estado-vacio');
        const contador = document.getElementById('contador-espacios');

        if (!espacios || espacios.length === 0) {
            container.innerHTML = '';
            estadoVacio.classList.remove('d-none');
            contador.textContent = '0 espacios';
            return;
        }

        estadoVacio.classList.add('d-none');
        contador.textContent = `${espacios.length} espacio${espacios.length !== 1 ? 's' : ''}`;

        const html = espacios.map(espacio => `
            <tr>
                <td>
                    <strong>${this.escapeHtml(espacio.nombre)}</strong>
                </td>
                <td>
                    <span class="badge badge-tipo badge-${espacio.tipo}">
                        ${this.obtenerNombreTipo(espacio.tipo)}
                    </span>
                </td>
                <td>
                    <small class="text-muted">${this.escapeHtml(espacio.descripcion || 'Sin descripción')}</small>
                </td>
                <td>
                    <span class="estado-${espacio.disponible ? 'disponible' : 'no-disponible'}">
                        <i class="bi bi-${espacio.disponible ? 'check-circle' : 'x-circle'} me-1"></i>
                        ${espacio.disponible ? 'Disponible' : 'No disponible'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-action btn-editar" onclick="gestionEspacios.editarEspacio(${espacio.id})" 
                                title="Editar espacio">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-action btn-eliminar" onclick="gestionEspacios.solicitarEliminar(${espacio.id})" 
                                title="Eliminar espacio">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        container.innerHTML = html;
    }

    obtenerNombreTipo(tipo) {
        const tipos = {
            'cancha': 'Cancha',
            'sala': 'Sala Común',
            'plaza': 'Plaza',
            'otro': 'Otro'
        };
        return tipos[tipo] || tipo;
    }

    actualizarEstadisticas() {
        const total = this.espacios.length;
        const disponibles = this.espacios.filter(e => e.disponible).length;
        const noDisponibles = total - disponibles;

        document.getElementById('total-espacios').textContent = total;
        document.getElementById('espacios-disponibles').textContent = disponibles;
        document.getElementById('espacios-no-disponibles').textContent = noDisponibles;
        
        // Para reservas activas, necesitarías una API que las cuente
        document.getElementById('reservas-activas').textContent = '0';
    }

    filtrarEspacios() {
        const texto = document.getElementById('buscar-espacio').value.toLowerCase();
        const tipo = document.getElementById('filtro-tipo').value;
        const disponible = document.getElementById('filtro-disponible').value;

        const filtrados = this.espacios.filter(espacio => {
            // Filtro por texto
            if (texto && !espacio.nombre.toLowerCase().includes(texto) && 
                !(espacio.descripcion || '').toLowerCase().includes(texto)) {
                return false;
            }
            
            // Filtro por tipo
            if (tipo && espacio.tipo !== tipo) {
                return false;
            }
            
            // Filtro por disponibilidad
            if (disponible !== '' && espacio.disponible.toString() !== disponible) {
                return false;
            }
            
            return true;
        });

        this.renderizarEspacios(filtrados);
    }

    nuevoEspacio() {
        document.getElementById('modal-titulo').textContent = 'Crear Nuevo Espacio';
        document.getElementById('espacio-id').value = '';
        this.limpiarFormulario();
        
        const modal = new bootstrap.Modal(document.getElementById('modalCrearEspacio'));
        modal.show();
    }

    editarEspacio(id) {
        const espacio = this.espacios.find(e => e.id === id);
        if (!espacio) return;

        document.getElementById('modal-titulo').textContent = 'Editar Espacio';
        document.getElementById('espacio-id').value = espacio.id;
        document.getElementById('nombre').value = espacio.nombre;
        document.getElementById('tipo').value = espacio.tipo;
        document.getElementById('descripcion').value = espacio.descripcion || '';
        document.getElementById('disponible').checked = espacio.disponible;

        const modal = new bootstrap.Modal(document.getElementById('modalCrearEspacio'));
        modal.show();
    }

    async guardarEspacio() {
        const form = document.getElementById('formEspacio');
        if (!form.reportValidity()) return;

        const datos = {
            nombre: document.getElementById('nombre').value.trim(),
            tipo: document.getElementById('tipo').value,
            descripcion: document.getElementById('descripcion').value.trim(),
            disponible: document.getElementById('disponible').checked
        };

        // Validaciones
        if (!datos.nombre || !datos.tipo) {
            this.mostrarError('Nombre y tipo son campos obligatorios');
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const espacioId = document.getElementById('espacio-id').value;
            const url = espacioId ? 
                `${window.URL_API || 'http://127.0.0.1:8000/'}api/directivo/gestion_espacios/${espacioId}/` :
                `${window.URL_API || 'http://127.0.0.1:8000/'}api/directivo/gestion_espacios/`;
            
            const method = espacioId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datos)
            });

            if (response.ok) {
                this.mostrarExito(espacioId ? 'Espacio actualizado correctamente' : 'Espacio creado correctamente');
                await this.cargarEspacios();
                
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearEspacio'));
                modal.hide();
            } else {
                const errorData = await response.json();
                this.mostrarError(errorData.detail || errorData.message || 'Error al guardar el espacio');
            }
        } catch (error) {
            console.error('Error guardando espacio:', error);
            this.mostrarError('Error de conexión al guardar el espacio');
        }
    }

    solicitarEliminar(id) {
        const espacio = this.espacios.find(e => e.id === id);
        if (!espacio) return;

        this.espacioAEliminar = id;
        document.getElementById('nombre-espacio-eliminar').textContent = espacio.nombre;
        
        const modal = new bootstrap.Modal(document.getElementById('modalConfirmarEliminar'));
        modal.show();
    }

    async eliminarEspacioConfirmado() {
        if (!this.espacioAEliminar) return;

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/directivo/gestion_espacios/${this.espacioAEliminar}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                this.mostrarExito('Espacio eliminado correctamente');
                await this.cargarEspacios();
            } else {
                this.mostrarError('Error al eliminar el espacio');
            }
        } catch (error) {
            console.error('Error eliminando espacio:', error);
            this.mostrarError('Error de conexión al eliminar el espacio');
        } finally {
            this.espacioAEliminar = null;
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmarEliminar'));
            modal.hide();
        }
    }

    limpiarFormulario() {
        document.getElementById('formEspacio').reset();
        document.getElementById('espacio-id').value = '';
        document.getElementById('disponible').checked = true;
    }

    // Utilidades
    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe.replace(/[&<"'>]/g, m => 
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]
        );
    }

    mostrarExito(mensaje) {
        this.mostrarMensaje(mensaje, 'success');
    }

    mostrarError(mensaje) {
        this.mostrarMensaje(mensaje, 'error');
    }

    mostrarMensaje(mensaje, tipo) {
        const container = document.getElementById('app-messages');
        const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
        const icon = tipo === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle';

        const alertHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="bi ${icon} me-2"></i>${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        container.innerHTML = alertHTML;
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                bootstrap.Alert.getInstance(alert).close();
            }
        }, 5000);
    }
}

// Inicializar la aplicación
let gestionEspacios;

document.addEventListener('DOMContentLoaded', function() {
    gestionEspacios = new GestionEspacios();
    
    // Hacer la función nuevoEspacio global para que funcione desde el botón
    window.nuevoEspacio = function() {
        gestionEspacios.nuevoEspacio();
    };
});