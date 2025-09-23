class GestorEventos {
    constructor() {
        this.currentDate = new Date();
        this.currentEventoId = null;
        this.currentEvento = null;
        this.cantidadAcompanantes = 0;
        this.nombresAcompanantes = [];
        this.filtroDiaActivo = null;
        this.eventos = [];
        this.isLoading = false;
        
        // Cache de elementos DOM
        this.domCache = {};
        
        this.init();
    }

    async init() {
        await this.cacheDOM();
        await this.cargarEventos();
        this.renderCalendar();
        this.setupEventListeners();
    }

    // Cachear elementos DOM para mejor performance
    cacheDOM() {
        const selectors = {
            // Navegación
            'prevMonth': '.prev-month',
            'nextMonth': '.next-month',
            'currentMonth': '#current-month',
            'calendarGrid': '#calendar-grid',
            
            // Botones principales
            'btnInscripciones': '#btn-inscripciones',
            'btnVerTodos': '#btn-ver-todos',
            'btnQuitarFiltro': '#btn-quitar-filtro',
            
            // Modales y botones
            'eventoModal': '#eventoModal',
            'eventoModalTitle': '#eventoModalTitle',
            'eventoModalBody': '#eventoModalBody',
            'btnInscribirse': '#btn-inscribirse',
            'btnCancelar': '#btn-cancelar',
            
            // Acompañantes
            'acompanantesModal': '#acompanantesModal',
            'acompanantesModalBody': '#acompanantesModalBody',
            'btnConfirmarInscripcion': '#btn-confirmar-inscripcion',
            
            // Contenedores
            'eventosContainer': '#eventos-container',
            'inscripcionesContainer': '#inscripciones-container',
            'inscripcionesModal': '#inscripcionesModal'
        };

        for (const [key, selector] of Object.entries(selectors)) {
            this.domCache[key] = document.querySelector(selector);
        }
    }

    setupEventListeners() {
        // Navegación del calendario - delegación mejorada
        this.domCache.calendarGrid?.addEventListener('click', (e) => {
            const dayItem = e.target.closest('.day-item');
            if (dayItem) {
                const dia = parseInt(dayItem.textContent);
                if (!isNaN(dia)) {
                    this.filtrarPorDia(dia);
                }
            }
        });

        // Botones de navegación del mes
        this.domCache.prevMonth?.addEventListener('click', () => this.navegarMes(-1));
        this.domCache.nextMonth?.addEventListener('click', () => this.navegarMes(1));

        // Botones principales con debounce
        this.debouncedClick(this.domCache.btnInscripciones, () => this.mostrarMisInscripciones());
        this.debouncedClick(this.domCache.btnVerTodos, () => this.quitarFiltroDia());
        this.debouncedClick(this.domCache.btnQuitarFiltro, () => this.quitarFiltroDia());

        // Botones de modales
        this.debouncedClick(this.domCache.btnInscribirse, () => this.prepararInscripcion());
        this.debouncedClick(this.domCache.btnCancelar, () => this.cancelarInscripcion());
        this.debouncedClick(this.domCache.btnConfirmarInscripcion, () => this.confirmarInscripcionConAcompanantes());

        // Delegación para botones dinámicos
        document.addEventListener('click', (e) => {
            // Botones de ver detalles
            if (e.target.closest('.btn-ver-detalles')) {
                const btn = e.target.closest('.btn-ver-detalles');
                const eventoId = btn.dataset.eventoId;
                this.mostrarDetallesEvento(eventoId);
                return;
            }

            // Botones de cancelar inscripción
            if (e.target.closest('.btn-cancelar-inscripcion')) {
                const btn = e.target.closest('.btn-cancelar-inscripcion');
                const eventoId = btn.dataset.eventoId;
                this.cancelarInscripcionDesdeModal(eventoId);
                return;
            }
        });

        // Input de acompañantes con debounce
        document.addEventListener('input', this.debounce((e) => {
            if (e.target.id === 'cantidadAcompanantes') {
                this.actualizarFormularioAcompanantes(e.target.value);
            }
        }, 300));

        // Responsive
        window.addEventListener('resize', this.debounce(() => {
            this.actualizarBotonesResponsive();
        }, 250));
    }

    // Debounce para mejorar performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    debouncedClick(element, callback) {
        if (!element) return;
        element.addEventListener('click', this.debounce(callback, 200));
    }

    navegarMes(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        this.renderCalendar();
        // Si hay filtro activo, mantenerlo aplicado al nuevo mes
        if (this.filtroDiaActivo) {
            this.mostrarEventosFiltrados();
        }
    }

    async cargarEventos() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.mostrarLoading(true);

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/eventos/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                this.eventos = await response.json();
                this.renderEventos();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Error cargando eventos:', error);
            this.mostrarError('Error al cargar eventos');
        } finally {
            this.isLoading = false;
            this.mostrarLoading(false);
        }
    }

    mostrarLoading(mostrar) {
        if (!this.domCache.eventosContainer) return;

        if (mostrar) {
            this.domCache.eventosContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="text-muted mt-2">Cargando eventos...</p>
                </div>
            `;
        }
    }

    renderEventos(eventos = this.eventos) {
        if (!this.domCache.eventosContainer) return;

        const eventosParaMostrar = eventos || this.eventos;
        
        if (!eventosParaMostrar.length) {
            const mensaje = this.filtroDiaActivo ? 
                `No hay eventos programados para el día ${this.filtroDiaActivo}` :
                'No hay eventos programados';
                
            this.domCache.eventosContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-calendar-x" style="font-size: 3rem; opacity: 0.5;"></i>
                    <p class="text-muted mt-2">${mensaje}</p>
                </div>
            `;
            return;
        }

        // Actualizar título según filtro
        const tituloElement = document.querySelector('h2.mb-4');
        if (tituloElement) {
            tituloElement.innerHTML = this.filtroDiaActivo ? 
                `Eventos del ${this.filtroDiaActivo} 
                 <span class="badge bg-warning text-dark">
                     ${this.currentDate.toLocaleString('es-ES', { month: 'long' })}
                 </span>` :
                'Próximos Eventos';
        }

        // Usar DocumentFragment para mejor performance
        const fragment = document.createDocumentFragment();
        
        eventosParaMostrar.forEach(evento => {
            const eventoElement = this.crearElementoEvento(evento);
            fragment.appendChild(eventoElement);
        });

        this.domCache.eventosContainer.innerHTML = '';
        this.domCache.eventosContainer.appendChild(fragment);
    }

    crearElementoEvento(evento) {
        const fechaEvento = new Date(evento.fecha);
        const cupoInfo = evento.cupo_maximo > 0 ? 
            `<span class="badge bg-${evento.cupos_disponibles > 0 ? 'success' : 'danger'} badge-cupo">
                ${evento.cupos_disponibles} cupos disponibles
            </span>` : 
            '<span class="badge bg-info badge-cupo">Cupo ilimitado</span>';
        
        const badgeInscrito = evento.esta_inscrito ? 
            '<span class="badge bg-success ms-2">Inscrito</span>' : '';

        const div = document.createElement('div');
        div.className = 'card mb-3 shadow-sm event-card';
        div.innerHTML = `
            <div class="card-body d-flex align-items-center justify-content-between p-4">
                <div class="d-flex align-items-center">
                    <div class="me-4 text-center">
                        <h3 class="fw-bold mb-0 text-primary">${fechaEvento.getDate()}</h3>
                        <small class="text-muted">${fechaEvento.toLocaleString('es-ES', { month: 'short' }).toUpperCase()}</small>
                    </div>
                    <div>
                        <h5 class="card-title mb-1">${this.escapeHtml(evento.titulo)} ${badgeInscrito}</h5>
                        <p class="card-text text-muted mb-0">
                            ${fechaEvento.toLocaleTimeString('es-ES', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                            })}
                        </p>
                        ${cupoInfo}
                        ${evento.permite_acompanantes ? 
                            `<small class="text-muted d-block mt-1">
                                <i class="bi bi-people"></i> Máximo ${evento.cupo_por_vecino} personas
                            </small>` : ''}
                    </div>
                </div>
                <button class="btn btn-outline-primary btn-ver-detalles" 
                        data-evento-id="${evento.id}">
                    <span class="d-none d-md-inline">Ver Detalles</span>
                    <span class="d-md-none">Ver</span>
                </button>
            </div>
        `;

        return div;
    }

    async mostrarDetallesEvento(eventoId) {
        // Buscar en eventos ya cargados primero (más rápido)
        const evento = this.eventos.find(e => e.id == eventoId);
        if (evento) {
            this.currentEventoId = eventoId;
            this.currentEvento = evento;
            this.mostrarModalEvento(evento);
            return;
        }

        // Si no está en cache, cargar desde API
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/eventos/${eventoId}/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const evento = await response.json();
                this.currentEventoId = eventoId;
                this.currentEvento = evento;
                this.mostrarModalEvento(evento);
            }
        } catch (error) {
            this.mostrarError('Error al cargar detalles');
        }
    }

    mostrarModalEvento(evento) {
        if (!this.domCache.eventoModalTitle || !this.domCache.eventoModalBody) return;

        this.domCache.eventoModalTitle.textContent = evento.titulo;
        
        const fechaEvento = new Date(evento.fecha);
        const cupoInfo = evento.cupo_maximo > 0 ? 
            `<p><strong>Cupos disponibles:</strong> ${evento.cupos_disponibles} / ${evento.cupo_maximo}</p>
            <small class="text-muted">* Incluye vecino + acompañantes</small>` : 
            '<p><strong>Cupo ilimitado</strong></p>';
        
        const acompanantesInfo = evento.permite_acompanantes ? 
            `<p><strong>Máximo por inscripción:</strong> ${evento.cupo_por_vecino} personas</p>` : '';

        this.domCache.eventoModalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Fecha:</strong> ${fechaEvento.toLocaleString('es-ES')}</p>
                    <p><strong>Descripción:</strong></p>
                    <p>${this.escapeHtml(evento.descripcion)}</p>
                </div>
                <div class="col-md-6">
                    ${cupoInfo}
                    ${acompanantesInfo}
                    <p><strong>Organizado por:</strong> ${evento.creada_por?.nombre || 'Junta de Vecinos'}</p>
                </div>
            </div>
        `;

        // Configurar botones
        if (this.domCache.btnInscribirse && this.domCache.btnCancelar) {
            if (evento.esta_inscrito) {
                this.domCache.btnInscribirse.classList.add('d-none');
                this.domCache.btnCancelar.classList.remove('d-none');
            } else {
                this.domCache.btnInscribirse.classList.remove('d-none');
                this.domCache.btnCancelar.classList.add('d-none');
                
                const sinCupos = evento.cupo_maximo > 0 && evento.cupos_disponibles <= 0;
                this.domCache.btnInscribirse.disabled = sinCupos;
                this.domCache.btnInscribirse.textContent = sinCupos ? 'Sin cupos' : 'Inscribirse';
            }
        }

        this.mostrarModal('eventoModal');
    }

    prepararInscripcion() {
        if (!this.currentEvento) return;

        if (this.currentEvento.permite_acompanantes) {
            this.mostrarModalAcompanantes();
        } else {
            this.inscribirEvento(0, []);
        }
    }

    mostrarModalAcompanantes() {
        if (!this.domCache.acompanantesModalBody) return;

        const maxAcompanantes = this.currentEvento.cupo_por_vecino - 1;

        this.domCache.acompanantesModalBody.innerHTML = `
            <div class="mb-3">
                <label for="cantidadAcompanantes" class="form-label">¿Cuántos acompañantes llevará?</label>
                <input type="number" class="form-control" id="cantidadAcompanantes" 
                       min="0" max="${maxAcompanantes}" value="0">
                <div class="form-text">Máximo ${maxAcompanantes} acompañantes permitidos</div>
            </div>
            <div id="formularioAcompanantes"></div>
        `;

        this.mostrarModal('acompanantesModal');
    }

    actualizarFormularioAcompanantes(cantidad) {
        const container = document.getElementById('formularioAcompanantes');
        if (!container) return;
        
        cantidad = parseInt(cantidad) || 0;
        
        if (cantidad > 0) {
            let html = `
                <div class="mb-3">
                    <label class="form-label fw-bold">Nombres de los acompañantes:</label>
                    <small class="text-muted d-block mb-2">Complete el nombre completo de cada acompañante</small>
            `;
            
            for (let i = 1; i <= cantidad; i++) {
                html += `
                    <input type="text" class="form-control mb-2 acompanante-input" 
                        placeholder="Nombre y apellido del acompañante ${i}" 
                        data-index="${i}">
                `;
            }
            
            html += `</div>`;
            container.innerHTML = html;
        } else {
            container.innerHTML = '';
        }
    }

    confirmarInscripcionConAcompanantes() {
        const cantidadInput = document.getElementById('cantidadAcompanantes');
        if (!cantidadInput) return;
        
        const cantidad = parseInt(cantidadInput.value) || 0;
        
        let nombres = [];
        let todosCompletos = true;
        
        if (cantidad > 0) {
            const inputsAcompanantes = document.querySelectorAll('.acompanante-input');
            
            if (inputsAcompanantes.length !== cantidad) {
                this.mostrarMensaje('error', 'Error en el formulario. Por favor recargue la página.');
                return;
            }
            
            inputsAcompanantes.forEach((input) => {
                const valor = input.value.trim();
                
                if (valor) {
                    nombres.push(valor);
                    input.classList.remove('is-invalid');
                } else {
                    todosCompletos = false;
                    input.classList.add('is-invalid');
                }
            });
            
            if (!todosCompletos) {
                this.mostrarMensaje('error', 'Por favor complete todos los nombres de acompañantes');
                return;
            }
        }

        this.cerrarModalPorId('acompanantesModal');
        this.cerrarModalPorId('eventoModal');
        this.inscribirEvento(cantidad, nombres);
    }

    async inscribirEvento(cantidadAcompanantes, nombresAcompanantes) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/eventos/${this.currentEventoId}/inscribir/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cantidad_acompanantes: cantidadAcompanantes,
                    nombres_acompanantes: nombresAcompanantes
                })
            });

            const data = await response.json();

            if (response.ok) {
                const totalPersonas = 1 + cantidadAcompanantes;
                this.mostrarMensaje('success', 
                    `¡Inscripción exitosa! Se registraron ${totalPersonas} personas.`);
                await this.cargarEventos();
            } else {
                this.mostrarMensaje('error', data.error || 'Error al inscribirse');
            }
        } catch (error) {
            this.mostrarMensaje('error', 'Error de conexión');
        }
    }

    async cancelarInscripcion() {
        if (!confirm('¿Estás seguro de que quieres cancelar tu inscripción?')) {
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/actividades/${this.currentEventoId}/cancelar/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.mostrarMensaje('success', 'Inscripción cancelada');
                this.cerrarModalPorId('eventoModal');
                await this.cargarEventos();
            } else {
                this.mostrarMensaje('error', data.error || 'Error al cancelar');
            }
        } catch (error) {
            this.mostrarMensaje('error', 'Error de conexión');
        }
    }

    renderCalendar() {
        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        
        if (this.domCache.currentMonth) {
            this.domCache.currentMonth.textContent = 
                `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
        }

        if (!this.domCache.calendarGrid) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // Limpiar solo los días, mantener los headers
        const existingChildren = Array.from(this.domCache.calendarGrid.children);
        for (let i = 7; i < existingChildren.length; i++) {
            this.domCache.calendarGrid.removeChild(existingChildren[i]);
        }

        // Usar fragment para mejor performance
        const fragment = document.createDocumentFragment();

        // Agregar días vacíos al inicio
        for (let i = 0; i < firstDay.getDay(); i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'p-1 p-md-2 border-0 bg-light';
            emptyDay.innerHTML = '&nbsp;';
            fragment.appendChild(emptyDay);
        }

        // Agregar días del mes
        const hoy = new Date();
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'day-item';
            dayElement.textContent = day;
            
            // Marcar si es el día actual
            if (day === hoy.getDate() && month === hoy.getMonth() && year === hoy.getFullYear()) {
                dayElement.classList.add('bg-info', 'text-white');
            }
            
            // Marcar días con eventos
            if (this.tieneEventosEsteDia(day, month, year)) {
                dayElement.classList.add('has-events');
            }
            
            // Marcar si está filtrado
            if (this.filtroDiaActivo === day) {
                dayElement.classList.add('border-warning', 'border-3');
            }
            
            fragment.appendChild(dayElement);
        }

        this.domCache.calendarGrid.appendChild(fragment);
    }

    tieneEventosEsteDia(dia, mes, año) {
        return this.eventos.some(evento => {
            const eventDate = new Date(evento.fecha);
            return eventDate.getDate() === dia && 
                   eventDate.getMonth() === mes && 
                   eventDate.getFullYear() === año;
        });
    }

    filtrarPorDia(dia) {
        this.filtroDiaActivo = dia;
        
        if (this.domCache.btnQuitarFiltro) {
            this.domCache.btnQuitarFiltro.classList.remove('d-none');
            const isMobile = window.innerWidth < 768;
            this.domCache.btnQuitarFiltro.innerHTML = isMobile ? 
                `<i class="bi bi-x-circle me-1"></i> Quitar` :
                `<i class="bi bi-x-circle me-1"></i> Quitar Filtro (Día ${dia})`;
        }
        
        this.resaltarDiaSeleccionado(dia);
        this.mostrarEventosFiltrados();
    }

    resaltarDiaSeleccionado(dia) {
        const days = this.domCache.calendarGrid?.querySelectorAll('.day-item');
        days?.forEach(dayElement => {
            dayElement.classList.remove('border-warning', 'border-3');
            if (parseInt(dayElement.textContent) === dia) {
                dayElement.classList.add('border-warning', 'border-3');
            }
        });
    }

    mostrarEventosFiltrados() {
        if (this.filtroDiaActivo === null) {
            this.renderEventos();
            return;
        }

        const eventosFiltrados = this.eventos.filter(evento => {
            const eventDate = new Date(evento.fecha);
            const currentYear = this.currentDate.getFullYear();
            const currentMonth = this.currentDate.getMonth();
            
            return eventDate.getDate() === this.filtroDiaActivo &&
                   eventDate.getMonth() === currentMonth &&
                   eventDate.getFullYear() === currentYear;
        });

        this.renderEventos(eventosFiltrados);
    }

    quitarFiltroDia() {
        this.filtroDiaActivo = null;
        
        if (this.domCache.btnQuitarFiltro) {
            this.domCache.btnQuitarFiltro.classList.add('d-none');
        }
        
        this.resaltarDiaSeleccionado(null);
        this.renderEventos();
    }

    actualizarBotonesResponsive() {
        if (this.domCache.btnQuitarFiltro && !this.domCache.btnQuitarFiltro.classList.contains('d-none') && this.filtroDiaActivo) {
            const isMobile = window.innerWidth < 768;
            this.domCache.btnQuitarFiltro.innerHTML = isMobile ? 
                `<i class="bi bi-x-circle me-1"></i> Quitar` :
                `<i class="bi bi-x-circle me-1"></i> Quitar Filtro (Día ${this.filtroDiaActivo})`;
        }
    }

    mostrarModal(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    cerrarModalPorId(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            } else {
                new bootstrap.Modal(modalElement).hide();
            }
        }
    }

    async mostrarMisInscripciones() {
        try {
            const inscripciones = await this.cargarMisInscripciones();
            this.mostrarModalInscripciones(inscripciones);
        } catch (error) {
            this.mostrarMensaje('error', 'Error al cargar inscripciones: ' + error.message);
        }
    }

    async cargarMisInscripciones() {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            throw new Error('Debe iniciar sesión');
        }

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/mis-inscripciones/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    mostrarModalInscripciones(inscripciones) {
        if (!this.domCache.inscripcionesContainer) return;

        if (!inscripciones || inscripciones.length === 0) {
            this.domCache.inscripcionesContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-calendar-x" style="font-size: 3rem; opacity: 0.5;"></i>
                    <p class="text-muted mt-3">No tienes inscripciones activas</p>
                </div>
            `;
        } else {
            this.domCache.inscripcionesContainer.innerHTML = this.generarHTMLInscripciones(inscripciones);
        }

        this.mostrarModal('inscripcionesModal');
    }

    generarHTMLInscripciones(inscripciones) {
        return `
            <div class="table-responsive">
                <table class="table table-hover table-sm">
                    <thead class="table-light">
                        <tr>
                            <th>Evento</th>
                            <th>Fecha</th>
                            <th>Hora</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${inscripciones.map(insc => {
                            try {
                                const fechaEvento = new Date(insc.fecha);
                                const fechaInscripcion = new Date(insc.fecha_inscripcion);
                                const ahora = new Date();
                                const puedeCancelar = fechaEvento > ahora;
                                const esHoy = fechaEvento.toDateString() === ahora.toDateString();
                                
                                return `
                                    <tr>
                                        <td>
                                            <strong>${insc.titulo || 'Evento'}</strong>
                                            <br>
                                            <small class="text-muted">
                                                Inscrito: ${fechaInscripcion.toLocaleDateString('es-ES')}
                                            </small>
                                        </td>
                                        <td>
                                            ${fechaEvento.toLocaleDateString('es-ES')}
                                            ${esHoy ? '<span class="badge bg-info ms-1">Hoy</span>' : ''}
                                        </td>
                                        <td>${fechaEvento.toLocaleTimeString('es-ES', { 
                                            hour: '2-digit', 
                                            minute: '2-digit' 
                                        })}</td>
                                        <td>
                                            <span class="badge bg-${puedeCancelar ? 'success' : 'secondary'}">
                                                ${puedeCancelar ? 'Activa' : 'Finalizada'}
                                            </span>
                                        </td>
                                        <td>
                                            ${puedeCancelar ? `
                                                <button class="btn btn-sm btn-outline-danger btn-cancelar-inscripcion" 
                                                        data-evento-id="${insc.id}">
                                                    <i class="bi bi-x-circle"></i> Cancelar
                                                </button>
                                            ` : `
                                                <span class="text-muted small">No cancelable</span>
                                            `}
                                        </td>
                                    </tr>
                                `;
                            } catch (error) {
                                return `
                                    <tr class="table-warning">
                                        <td colspan="5" class="text-center">
                                            <i class="bi bi-exclamation-triangle"></i>
                                            Error mostrando inscripción
                                        </td>
                                    </tr>
                                `;
                            }
                        }).join('')}
                    </tbody>
                </table>
            </div>
            <div class="alert alert-info mt-3">
                <i class="bi bi-info-circle"></i>
                <strong>Total:</strong> ${inscripciones.length} inscripciones
            </div>
        `;
    }

    async cancelarInscripcionDesdeModal(eventoId) {
        if (!confirm('¿Estás seguro de que quieres cancelar esta inscripción?')) {
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/actividades/${eventoId}/cancelar/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.mostrarMensaje('success', 'Inscripción cancelada correctamente');
                const inscripciones = await this.cargarMisInscripciones();
                this.actualizarModalInscripciones(inscripciones);
                await this.cargarEventos();
            } else {
                const data = await response.json();
                this.mostrarMensaje('error', data.error || 'Error al cancelar');
            }
        } catch (error) {
            this.mostrarMensaje('error', 'Error de conexión');
        }
    }

    actualizarModalInscripciones(inscripciones) {
        if (!this.domCache.inscripcionesContainer) return;

        if (!inscripciones || inscripciones.length === 0) {
            this.domCache.inscripcionesContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-calendar-x" style="font-size: 3rem; opacity: 0.5;"></i>
                    <p class="text-muted mt-3">No tienes inscripciones activas</p>
                </div>
            `;
        } else {
            this.domCache.inscripcionesContainer.innerHTML = this.generarHTMLInscripciones(inscripciones);
        }
    }

    mostrarMensaje(tipo, mensaje) {
        // Usar toast de Bootstrap si está disponible
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            this.mostrarToast(mensaje, tipo);
        } else {
            alert(`${tipo.toUpperCase()}: ${mensaje}`);
        }
    }

    mostrarToast(mensaje, tipo = 'success') {
        const toastContainer = document.getElementById('toast-container') || this.crearToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${tipo} border-0" id="${toastId}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${mensaje}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.innerHTML += toastHTML;
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover el toast después de que se oculta
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    crearToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
        return container;
    }

    mostrarError(mensaje) {
        if (this.domCache.eventosContainer) {
            this.domCache.eventosContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> ${mensaje}
                </div>
            `;
        }
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe.replace(/[&<"'>]/g, m => 
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]
        );
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    // Pequeño delay para que el DOM esté completamente listo
    setTimeout(() => {
        window.gestorEventos = new GestorEventos();
    }, 100);
});