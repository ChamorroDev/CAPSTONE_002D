/* gestion_eventos.js
   Versión corregida y mejorada
*/

class GestionEventos {
    constructor() {
        this.URL_API = window.URL_API || 'http://127.0.0.1:8000/';
        this.eventos = [];
        this.eventoSeleccionado = null;
        this.inscritosData = null;
        this.init();
    }

    async init() {
        try {
            await this.cargarEventos();
            this.setupEventListeners();
            this.setupResponsive();
        } catch (e) {
            console.error('Error inicializando GestionEventos', e);
            this.mostrarError('Error al inicializar la gestión de eventos');
        }
    }

    setupEventListeners() {
        // Búsqueda y filtro
        const buscar = document.getElementById('buscarEvento');
        const filtro = document.getElementById('filtroEstado');
        if (buscar) buscar.addEventListener('input', () => this.filtrarEventos());
        if (filtro) filtro.addEventListener('change', () => this.filtrarEventos());

        // Crear evento
        const btnCrear = document.getElementById('btnCrearEvento');
        if (btnCrear) btnCrear.addEventListener('click', () => this.crearEvento());

        // Exportar inscritos
        const btnExport = document.getElementById('btnExportarInscritos');
        if (btnExport) btnExport.addEventListener('click', () => this.exportarInscritos());

        // Delegación de eventos para botones de acción
        document.addEventListener('click', (e) => {
            const verBtn = e.target.closest('.btn-ver-inscritos');
            const editBtn = e.target.closest('.btn-editar-evento');
            const delBtn = e.target.closest('.btn-eliminar-evento');

            if (verBtn) {
                const id = verBtn.dataset.eventoId;
                if (id) this.verInscritos(id);
            }
            if (editBtn) {
                const id = editBtn.dataset.eventoId;
                if (id) this.editarEvento(id);
            }
            if (delBtn) {
                const id = delBtn.dataset.eventoId;
                if (id) this.eliminarEvento(id);
            }
        });

        // Event listener para el modal de edición (cuando se cierra)
        const editarModal = document.getElementById('editarEventoModal');
        if (editarModal) {
            editarModal.addEventListener('hidden.bs.modal', () => {
                this.limpiarFormularioEdicion();
            });
        }
    }

    setupResponsive() {
        this.ajustarTablaResponsive();
        window.addEventListener('resize', () => this.ajustarTablaResponsive());
    }

    ajustarTablaResponsive() {
        const tabla = document.getElementById('tablaEventos');
        if (!tabla) return;
        tabla.classList.toggle('table-sm', window.innerWidth < 768);
    }

    async cargarEventos() {
        try {
            const token = this.getToken();
            if (!token) {
                this.mostrarError('No se encontró token de autenticación');
                return;
            }

            const res = await fetch(`${this.URL_API}api/directivo/eventos/`, {
                headers: this.getHeaders(),
                credentials: 'omit'
            });

            if (!res.ok) {
                if (res.status === 401) {
                    this.mostrarError('Sesión expirada. Por favor, inicie sesión nuevamente.');
                    return;
                }
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json();
            this.eventos = data.eventos || data || [];
            this.actualizarEstadisticas();
            this.renderEventos();
        } catch (err) {
            console.error('Error cargando eventos:', err);
            this.mostrarError('Error de conexión al cargar eventos');
        }
    }

    getToken() {
        return localStorage.getItem('access_token');
    }

    getHeaders() {
        const token = this.getToken();
        return {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
        };
    }

    actualizarEstadisticas() {
        const ahora = new Date();

        const totalEventos = this.eventos.length;
        const proximosEventos = this.eventos.filter(e => new Date(e.fecha) > ahora).length;
        const eventosHoy = this.eventos.filter(e => {
            const fe = new Date(e.fecha);
            return fe.toDateString() === ahora.toDateString();
        }).length;

        // Cálculo corregido de inscritos
        const totalInscritos = this.eventos.reduce((acc, e) => {
            // Usar inscritos_count si está disponible, sino calcular
            if (e.inscritos_count !== undefined) return acc + e.inscritos_count;
            if (e.cupo_maximo !== undefined && e.cupos_disponibles !== undefined) {
                return acc + (e.cupo_maximo - e.cupos_disponibles);
            }
            return acc;
        }, 0);

        this.actualizarElementoTexto('total-eventos', totalEventos);
        this.actualizarElementoTexto('proximos-eventos', proximosEventos);
        this.actualizarElementoTexto('eventos-hoy', eventosHoy);
        this.actualizarElementoTexto('total-inscritos', totalInscritos);
    }

    actualizarElementoTexto(id, valor) {
        const elemento = document.getElementById(id);
        if (elemento) elemento.textContent = valor;
    }

    renderEventos(eventos = this.eventos) {
        const container = document.getElementById('eventos-body');
        if (!container) return;

        if (!eventos || eventos.length === 0) {
            container.innerHTML = this.getHTMLSinEventos();
            return;
        }

        container.innerHTML = eventos.map(ev => this.getHTMLFilaEvento(ev)).join('');
    }

    getHTMLSinEventos() {
        return `
            <tr>
                <td colspan="6" class="text-center py-5">
                    <div class="empty-state">
                        <i class="bi bi-calendar-x" style="font-size: 2.5rem;"></i>
                        <h4 class="mt-2">No hay eventos</h4>
                        <p class="text-muted">Crea tu primer evento desde "Crear Nuevo Evento".</p>
                    </div>
                </td>
            </tr>
        `;
    }

    getHTMLFilaEvento(ev) {
        const fechaEvento = new Date(ev.fecha);
        const { estado, badgeClass } = this.obtenerEstadoEvento(fechaEvento, ev.cancelado);
        const totalInscritos = this.calcularInscritos(ev);
        const cupoInfo = this.obtenerInfoCupo(ev);

        return `
            <tr>
                <td>
                    <strong>${this.escapeHtml(ev.titulo)}</strong>
                    <br><small class="text-muted">${this.escapeHtml((ev.descripcion || '').substring(0, 80))}...</small>
                </td>
                <td>
                    ${fechaEvento.toLocaleDateString('es-ES')}
                    <br><small class="text-muted">${fechaEvento.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</small>
                </td>
                <td>${totalInscritos}</td>
                <td>${cupoInfo}</td>
                <td><span class="badge badge-estado ${badgeClass}">${estado}</span></td>
                <td>
                    <div class="btn-action-group">
                        <button class="btn-action btn-ver-inscritos" data-evento-id="${ev.id}" title="Ver inscritos">
                            <i class="bi bi-people"></i><span class="btn-text d-none d-md-inline"> Ver</span>
                        </button>
                        <button class="btn-action btn-editar-evento" data-evento-id="${ev.id}" title="Editar evento">
                            <i class="bi bi-pencil"></i><span class="btn-text d-none d-md-inline"> Editar</span>
                        </button>
                        <button class="btn-action btn-eliminar-evento" data-evento-id="${ev.id}" title="Eliminar evento">
                            <i class="bi bi-trash"></i><span class="btn-text d-none d-md-inline"> Eliminar</span>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    obtenerEstadoEvento(fechaEvento, cancelado) {
        const ahora = new Date();
        
        if (cancelado) {
            return { estado: 'Cancelado', badgeClass: 'badge-cancelado' };
        }

        if (fechaEvento < ahora) {
            return { estado: 'Pasado', badgeClass: 'badge-pasado' };
        } else if (fechaEvento.toDateString() === ahora.toDateString()) {
            return { estado: 'Hoy', badgeClass: 'badge-proximo' };
        } else {
            return { estado: 'Próximo', badgeClass: 'badge-activo' };
        }
    }

    calcularInscritos(evento) {
        if (evento.inscritos_count !== undefined) return evento.inscritos_count;
        if (evento.cupo_maximo !== undefined && evento.cupos_disponibles !== undefined) {
            return evento.cupo_maximo - evento.cupos_disponibles;
        }
        return 0;
    }

    obtenerInfoCupo(evento) {
        if (!evento.cupo_maximo || evento.cupo_maximo === 0) return 'Ilimitado';
        const inscritos = this.calcularInscritos(evento);
        return `${inscritos} / ${evento.cupo_maximo}`;
    }

    filtrarEventos() {
        const termino = (document.getElementById('buscarEvento')?.value || '').toLowerCase();
        const filtro = document.getElementById('filtroEstado')?.value || '';
        const ahora = new Date();

        const filtrados = this.eventos.filter(ev => {
            // Filtro por texto
            if (termino) {
                const titulo = (ev.titulo || '').toLowerCase();
                const desc = (ev.descripcion || '').toLowerCase();
                if (!titulo.includes(termino) && !desc.includes(termino)) return false;
            }

            // Filtro por estado
            const fe = new Date(ev.fecha);
            switch (filtro) {
                case 'activos': return fe >= ahora && !ev.cancelado;
                case 'pasados': return fe < ahora && !ev.cancelado;
                case 'proximos': return fe > ahora && fe.toDateString() !== ahora.toDateString() && !ev.cancelado;
                default: return true;
            }
        });

        this.renderEventos(filtrados);
    }

    async verInscritos(eventoId) {
        try {
            const res = await fetch(`${this.URL_API}api/directivo/eventos/${eventoId}/inscritos/`, {
                headers: this.getHeaders()
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            this.inscritosData = data.inscritos || [];
            this.eventoSeleccionado = data.evento || this.eventos.find(e => e.id == eventoId);
            
            this.mostrarInscritos(this.inscritosData);
            this.mostrarModal('verInscritosModal');
        } catch (err) {
            console.error('Error cargando inscritos:', err);
            this.mostrarError('Error al cargar los inscritos');
        }
    }

    mostrarInscritos(inscritos) {
        const container = document.getElementById('lista-inscritos');
        if (!container) return;

        if (!inscritos || inscritos.length === 0) {
            container.innerHTML = this.getHTMLSinInscritos();
            return;
        }

        container.innerHTML = inscritos.map(i => this.getHTMLFilaInscrito(i)).join('');
    }

    getHTMLSinInscritos() {
        return `
            <tr><td colspan="5" class="text-center py-4">
                <i class="bi bi-people text-muted" style="font-size:2rem"></i>
                <p class="text-muted mt-2">No hay inscritos para este evento</p>
            </td></tr>
        `;
    }

    getHTMLFilaInscrito(inscrito) {
        return `
            <tr>
                <td>${this.escapeHtml(inscrito.nombre_completo || inscrito.nombre || '')}</td>
                <td>${this.escapeHtml(inscrito.email || '')}</td>
                <td>${this.escapeHtml(inscrito.rut || '')}</td>
                <td>${inscrito.cantidad_acompanantes || 0}</td>
                <td>${new Date(inscrito.fecha_inscripcion || inscrito.created_at || Date.now()).toLocaleDateString('es-ES')}</td>
            </tr>
        `;
    }

    async crearEvento() {
        const form = document.getElementById('formCrearEvento');
        if (!form || !form.reportValidity()) return;

        const formData = new FormData(form);
        const payload = this.prepararDatosEvento(formData);

        try {
            const res = await fetch(`${this.URL_API}api/directivo/eventos/crear/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                this.mostrarMensaje('Evento creado exitosamente', 'success');
                this.cerrarModal('crearEventoModal');
                form.reset();
                await this.cargarEventos();
            } else {
                const error = await res.json().catch(() => ({}));
                throw new Error(error.detail || error.message || 'Error al crear evento');
            }
        } catch (err) {
            console.error('Error creando evento:', err);
            this.mostrarError(err.message);
        }
    }

    async editarEvento(eventoId) {
        try {
            // Buscar el evento en la lista local primero
            const evento = this.eventos.find(e => e.id == eventoId);
            if (!evento) {
                this.mostrarError('Evento no encontrado');
                return;
            }

            // Poblar el formulario de edición
            this.poblarFormularioEdicion(evento);
            this.mostrarModal('editarEventoModal');

        } catch (err) {
            console.error('Error preparando edición:', err);
            this.mostrarError('Error al cargar datos del evento');
        }
    }

    poblarFormularioEdicion(evento) {
        const form = document.getElementById('formEditarEvento');
        if (!form) return;

        // Convertir fecha al formato correcto para datetime-local
        const fecha = new Date(evento.fecha);
        const fechaFormateada = fecha.toISOString().slice(0, 16);

        form.querySelector('[name="evento_id"]').value = evento.id;
        form.querySelector('[name="titulo"]').value = evento.titulo || '';
        form.querySelector('[name="descripcion"]').value = evento.descripcion || '';
        form.querySelector('[name="fecha"]').value = fechaFormateada;
        form.querySelector('[name="cupo_maximo"]').value = evento.cupo_maximo || 0;
        form.querySelector('[name="cupo_por_vecino"]').value = evento.cupo_por_vecino || 1;
        form.querySelector('[name="permite_acompanantes"]').value = evento.permite_acompanantes ? 'true' : 'false';
    }

    async guardarEdicionEvento() {
        const form = document.getElementById('formEditarEvento');
        if (!form || !form.reportValidity()) return;

        const formData = new FormData(form);
        const eventoId = formData.get('evento_id');
        const payload = this.prepararDatosEvento(formData);

        try {
            const res = await fetch(`${this.URL_API}api/directivo/eventos/${eventoId}/editar/`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                this.mostrarMensaje('Evento actualizado exitosamente', 'success');
                this.cerrarModal('editarEventoModal');
                await this.cargarEventos();
            } else {
                const error = await res.json().catch(() => ({}));
                throw new Error(error.detail || error.message || 'Error al actualizar evento');
            }
        } catch (err) {
            console.error('Error actualizando evento:', err);
            this.mostrarError(err.message);
        }
    }

    prepararDatosEvento(formData) {
        return {
            titulo: (formData.get('titulo') || '').trim(),
            descripcion: (formData.get('descripcion') || '').trim(),
            fecha: formData.get('fecha'),
            cupo_maximo: parseInt(formData.get('cupo_maximo') || 0, 10),
            cupo_por_vecino: parseInt(formData.get('cupo_por_vecino') || 1, 10),
            permite_acompanantes: formData.get('permite_acompanantes') === 'true'
        };
    }

    limpiarFormularioEdicion() {
        const form = document.getElementById('formEditarEvento');
        if (form) form.reset();
    }

    async eliminarEvento(eventoId) {
        if (!confirm('¿Está seguro de que desea eliminar este evento? Esta acción no se puede deshacer.')) return;

        try {
            const res = await fetch(`${this.URL_API}api/directivo/eventos/${eventoId}/eliminar/`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });

            if (res.ok) {
                this.mostrarMensaje('Evento eliminado exitosamente', 'success');
                await this.cargarEventos();
            } else {
                throw new Error(`HTTP ${res.status}`);
            }
        } catch (err) {
            console.error('Error eliminando evento:', err);
            this.mostrarError('Error al eliminar el evento');
        }
    }

    exportarInscritos() {
        if (!this.eventoSeleccionado || !this.inscritosData || this.inscritosData.length === 0) {
            this.mostrarMensaje('No hay datos para exportar', 'info');
            return;
        }

        try {
            const csv = this.convertToCSV(this.inscritosData);
            const safeTitle = (this.eventoSeleccionado.titulo || 'evento').replace(/[^\w\-]/g, '_').slice(0, 50);
            const filename = `inscritos_${safeTitle}_${new Date().toISOString().split('T')[0]}.csv`;
            this.downloadCSV(csv, filename);
            this.mostrarMensaje('Datos exportados correctamente', 'success');
        } catch (err) {
            console.error('Error exportando inscritos:', err);
            this.mostrarError('Error al exportar los datos');
        }
    }

    convertToCSV(data) {
        const headers = ['Nombre', 'Email', 'RUT', 'Teléfono', 'Acompañantes', 'Nombres Acompañantes', 'Fecha Inscripción'];
        const rows = data.map(item => {
            const escapeValue = v => {
                if (v === null || v === undefined) return '';
                const s = Array.isArray(v) ? v.join(', ') : String(v);
                return `"${s.replace(/"/g, '""')}"`;
            };

            return [
                escapeValue(item.nombre_completo || item.nombre || ''),
                escapeValue(item.email || ''),
                escapeValue(item.rut || ''),
                escapeValue(item.telefono || ''),
                escapeValue(item.cantidad_acompanantes || 0),
                escapeValue(Array.isArray(item.nombres_acompanantes) ? item.nombres_acompanantes.join(', ') : item.nombres_acompanantes || ''),
                escapeValue(item.fecha_inscripcion || item.created_at || '')
            ].join(',');
        });

        return [headers.join(','), ...rows].join('\n');
    }

    downloadCSV(content, filename) {
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    mostrarModal(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    }

    cerrarModal(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }
    }

    mostrarMensaje(mensaje, tipo = 'info') {
        // Implementar según tu sistema de notificaciones
        alert(`${tipo.toUpperCase()}: ${mensaje}`);
    }

    mostrarError(mensaje) {
        this.mostrarMensaje(mensaje, 'error');
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe.replace(/[&<"'>]/g, m => 
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]
        );
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.gestionEventos = new GestionEventos();
});