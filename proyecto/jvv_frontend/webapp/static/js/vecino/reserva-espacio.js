
class ReservaEspacio {
    constructor() {
        // Estado de la aplicación
        this.espacios = [];
        this.todasReservas = []; // Mantenemos esta lista para el estado del calendario
        this.fechaSeleccionada = new Date();
        this.espacioSeleccionadoId = '';
        this.detallesReservaModal = null;

        // Inicialización
        this.init();
    }

    async init() {
        this.mostrarMensaje('Cargando datos...', 'info');
        await this.cargarDatosIniciales();
        this.setupEventListeners();
        this.renderizarCalendario();
        this.mostrarMensaje('¡Listo para reservar!', 'success', 2000);
        // Inicializa el modal al cargar la página
        this.detallesReservaModal = new bootstrap.Modal(document.getElementById('detallesReservaModal'));
    }

    // --- Carga de datos del backend ---
    async cargarDatosIniciales() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            this.mostrarError('Debe iniciar sesión para usar este servicio.');
            return;
        }

        try {
            await Promise.all([
                this.fetchEspacios(token),
                this.fetchReservas(token), // Mantenemos esta llamada para pintar el calendario
                this.fetchMisReservas(token)
            ]);
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.mostrarError('Error al cargar datos. Intente recargar la página.');
        }
    }

    async fetchEspacios(token) {
        const response = await fetch(`${URL_API}api/espacios/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al cargar espacios.');
        this.espacios = await response.json();
        this.llenarSelectsEspacios();
    }

    async fetchReservas(token) {
        const response = await fetch(`${URL_API}api/reservas/`, { // Endpoint para TODAS las reservas (para el calendario)
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al cargar reservas del calendario.');
        this.todasReservas = await response.json();
    }
    
    async fetchMisReservas(token) {
        const response = await fetch(`${URL_API}api/espacios/mis_reservas/`, { 
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al cargar mis reservas.');
        const misReservas = await response.json();
        this.actualizarTablaReservas(misReservas);
    }
    
    // --- Event Listeners y Lógica de UI ---
    setupEventListeners() {
        const form = document.getElementById('reservaForm');
        if (form) {
            form.addEventListener('submit', (e) => this.validarYEnviarFormulario(e));
        }

        const selectorCalendario = document.getElementById('selectorEspacioCalendario');
        if (selectorCalendario) {
            selectorCalendario.addEventListener('change', (e) => {
                this.espacioSeleccionadoId = e.target.value;
                this.renderizarCalendario();
            });
        }
        
        const calendarioMini = document.getElementById('calendario-mini');
        if (calendarioMini) {
            calendarioMini.addEventListener('click', (e) => {
                const diaElement = e.target.closest('.calendar-day');
                if (diaElement && diaElement.dataset.fecha && !diaElement.classList.contains('pasado')) {
                    this.seleccionarDia(diaElement.dataset.fecha);
                }
            });
        }

        const fechaInput = document.getElementById('id_fecha_evento');
        const espacioSelect = document.getElementById('id_espacio');
        if (fechaInput && espacioSelect) {
            fechaInput.addEventListener('change', () => this.actualizarHorasDisponibles());
            espacioSelect.addEventListener('change', () => this.actualizarHorasDisponibles());
        }
    }

    // --- Lógica de validación y envío del formulario ---
    validarYEnviarFormulario(e) {
        e.preventDefault();
        
        const horaInicio = document.getElementById('id_hora_inicio').value;
        const horaFin = document.getElementById('id_hora_fin').value;

        if (horaInicio >= horaFin) {
            this.mostrarError('La hora de inicio debe ser anterior a la hora de fin.');
            return;
        }

        this.enviarSolicitud(e);
    }

    async enviarSolicitud(e) {
        this.mostrarLoading(true);

        const token = localStorage.getItem('access_token');
        if (!token) {
            this.mostrarError('Debe iniciar sesión para reservar');
            this.mostrarLoading(false);
            return;
        }

        const formData = {
            espacio: parseInt(document.getElementById('id_espacio').value),
            fecha_evento: document.getElementById('id_fecha_evento').value,
            hora_inicio: document.getElementById('id_hora_inicio').value,
            hora_fin: document.getElementById('id_hora_fin').value,
            motivo: document.getElementById('id_motivo').value
        };

        try {
            const response = await fetch(`${URL_API}api/espacios/solicitar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.mostrarExito('Solicitud de reserva enviada correctamente.');
                this.limpiarFormulario();
                await this.cargarDatosIniciales();
            } else {
                this.mostrarError(data.error || 'Error al enviar la solicitud.');
            }
        } catch (error) {
            this.mostrarError('Error de conexión: ' + error.message);
        } finally {
            this.mostrarLoading(false);
        }
    }

    // --- Lógica del calendario ---
    renderizarCalendario() {
        const calendarioDiv = document.getElementById('calendario-mini');
        if (!calendarioDiv) return;

        const mes = this.fechaSeleccionada.getMonth();
        const año = this.fechaSeleccionada.getFullYear();
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        const diasSemana = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'];

        let html = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <button class="btn btn-sm btn-outline-primary" id="btnMesAnterior"><i class="bi bi-chevron-left"></i></button>
                <h6 class="mb-0 fw-bold">${meses[mes]} ${año}</h6>
                <button class="btn btn-sm btn-outline-primary" id="btnMesSiguiente"><i class="bi bi-chevron-right"></i></button>
            </div>
            <div class="calendar-grid mb-2">
                ${diasSemana.map(dia => `<div class="calendar-weekday">${dia}</div>`).join('')}
        `;
        
        const primerDia = new Date(año, mes, 1);
        const ultimoDia = new Date(año, mes + 1, 0);
        const primerDiaSemana = primerDia.getDay();

        for (let i = 0; i < primerDiaSemana; i++) {
            html += '<div class="calendar-day empty"></div>';
        }

        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);

        for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
            const fecha = new Date(año, mes, dia);
            const fechaISO = fecha.toISOString().split('T')[0];
            const estado = this.obtenerEstadoDia(fecha);
            const esHoy = fecha.getTime() === hoy.getTime();

            html += `
                <div class="calendar-day ${estado} ${esHoy ? 'hoy' : ''}" data-fecha="${fechaISO}">
                    ${dia}
                </div>
            `;
        }

        html += '</div>';
        calendarioDiv.innerHTML = html;

        document.getElementById('btnMesAnterior').addEventListener('click', () => this.mesAnterior());
        document.getElementById('btnMesSiguiente').addEventListener('click', () => this.mesSiguiente());
    }

    obtenerEstadoDia(fecha) {
        const fechaStr = fecha.toISOString().split('T')[0];
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);

        if (fecha < hoy) {
            return 'pasado';
        }
        
        if (this.todasReservas.length === 0) {
            return 'disponible';
        }

        const reservasDia = this.todasReservas.filter(reserva => {
            const coincideFecha = reserva.fecha_evento === fechaStr;
            const coincideEspacio = !this.espacioSeleccionadoId || reserva.espacio == this.espacioSeleccionadoId;
            return coincideFecha && coincideEspacio;
        });

        if (reservasDia.length === 0) {
            return 'disponible';
        }
        
        const tieneAprobadas = reservasDia.some(r => r.estado === 'aprobado');
        const tienePendientes = reservasDia.some(r => r.estado === 'pendiente');
        
        if (tieneAprobadas) return 'occupied';
        if (tienePendientes) return 'pending';
        return 'available';
    }

    mesAnterior() {
        this.fechaSeleccionada.setMonth(this.fechaSeleccionada.getMonth() - 1);
        this.renderizarCalendario();
    }

    mesSiguiente() {
        this.fechaSeleccionada.setMonth(this.fechaSeleccionada.getMonth() + 1);
        this.renderizarCalendario();
    }

    seleccionarDia(fechaStr) {
        // Se valida que el usuario haya seleccionado un espacio antes de solicitar los detalles.
        const espacioId = document.getElementById('selectorEspacioCalendario').value;
        
        if (!espacioId) {
            this.mostrarMensaje('Por favor, selecciona un espacio primero para ver los detalles del día.', 'warning');
            return;
        }

        document.getElementById('id_fecha_evento').value = fechaStr;
        
        this.mostrarDetallesDia(fechaStr, espacioId);
    }

    async actualizarHorasDisponibles() {
        const espacioId = document.getElementById('id_espacio').value;
        const fecha = document.getElementById('id_fecha_evento').value;
        
        const selectInicio = document.getElementById('id_hora_inicio');
        const selectFin = document.getElementById('id_hora_fin');

        if (!espacioId || !fecha) {
            selectInicio.innerHTML = '<option value="">Selecciona fecha y espacio</option>';
            selectFin.innerHTML = '<option value="">Selecciona fecha y espacio</option>';
            return;
        }

        selectInicio.innerHTML = '<option value="">Cargando horas...</option>';
        selectFin.innerHTML = '<option value="">Cargando horas...</option>';

        const token = localStorage.getItem('access_token');
        try {
            const response = await fetch(`${URL_API}api/espacios/disponibilidad/?espacio_id=${espacioId}&fecha=${fecha}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const disponibilidad = await response.json();

            this.llenarSelectsHoras(disponibilidad);
        } catch (error) {
            console.error('Error al obtener disponibilidad:', error);
            this.mostrarError('No se pudo cargar la disponibilidad de horarios.');
            selectInicio.innerHTML = '<option value="">Error al cargar</option>';
            selectFin.innerHTML = '<option value="">Error al cargar</option>';
        }
    }

    llenarSelectsHoras(disponibilidad) {
        const selectInicio = document.getElementById('id_hora_inicio');
        const selectFin = document.getElementById('id_hora_fin');
        const horas = Array.from({length: 13}, (_, i) => `${(8 + i).toString().padStart(2, '0')}:00`); // 08:00 a 20:00

        selectInicio.innerHTML = '<option value="">Selecciona hora</option>';
        selectFin.innerHTML = '<option value="">Selecciona hora</option>';

        horas.forEach(hora => {
            const isAvailable = disponibilidad.available_hours.includes(hora);
            if (isAvailable) {
                const optionInicio = new Option(hora, hora);
                const optionFin = new Option(hora, hora);
                selectInicio.add(optionInicio);
                selectFin.add(optionFin);
            }
        });

        // Habilita o deshabilita los selects si no hay opciones
        selectInicio.disabled = selectInicio.length <= 1;
        selectFin.disabled = selectFin.length <= 1;
    }

    // --- Helpers de UI y utilidades ---
    llenarSelectsEspacios() {
        const selectForm = document.getElementById('id_espacio');
        const selectCalendario = document.getElementById('selectorEspacioCalendario');

        if (selectForm) {
            selectForm.innerHTML = '<option value="">Selecciona un espacio</option>';
            this.espacios.forEach(espacio => {
                selectForm.innerHTML += `<option value="${espacio.id}">${espacio.nombre} (${espacio.tipo})</option>`;
            });
        }
        
        if (selectCalendario) {
            selectCalendario.innerHTML = '<option value="">Todos los espacios</option>';
            this.espacios.forEach(espacio => {
                selectCalendario.innerHTML += `<option value="${espacio.id}">${espacio.nombre}</option>`;
            });
        }
    }

    actualizarTablaReservas(reservas) {
        const tbody = document.querySelector('#tabla-reservas tbody');
        if (!tbody) return;

        if (reservas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No tienes reservas previas</td></tr>';
            return;
        }

        tbody.innerHTML = reservas.map(reserva => `
            <tr>
                <td>${reserva.espacio_nombre || 'N/A'}</td>
                <td>${new Date(reserva.fecha_evento).toLocaleDateString()}</td>
                <td>${reserva.hora_inicio} - ${reserva.hora_fin}</td>
                <td><span class="badge ${this.getBadgeClass(reserva.estado)}">${reserva.estado}</span></td>
                <td>${(reserva.motivo || '').substring(0, 30)}${reserva.motivo && reserva.motivo.length > 30 ? '...' : ''}</td>
            </tr>
        `).join('');
    }

    getBadgeClass(estado) {
        switch(estado) {
            case 'aprobado': return 'bg-success';
            case 'rechazado': return 'bg-danger';
            default: return 'bg-warning text-dark';
        }
    }

    mostrarLoading(mostrar) {
        const btnSubmit = document.querySelector('#reservaForm button[type="submit"]');
        if (!btnSubmit) return;
        btnSubmit.disabled = mostrar;
        btnSubmit.innerHTML = mostrar ? '<span class="spinner-border spinner-border-sm"></span> Enviando...' : 'Enviar Solicitud de Reserva';
    }

    mostrarExito(mensaje, duracion = 3000) { this.mostrarMensaje(mensaje, 'success', duracion); }
    mostrarError(mensaje, duracion = 5000) { this.mostrarMensaje(mensaje, 'danger', duracion); }
    
    mostrarMensaje(mensaje, tipo, duracion) {
        const messageDiv = document.getElementById('reserva-message');
        if (!messageDiv) return;
        messageDiv.innerHTML = `<div class="alert alert-${tipo} alert-dismissible fade show">
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
        if (duracion) {
            setTimeout(() => {
                const alert = messageDiv.querySelector('.alert');
                if (alert) alert.classList.remove('show');
                messageDiv.innerHTML = '';
            }, duracion);
        }
    }

    limpiarFormulario() {
        const form = document.getElementById('reservaForm');
        if (form) form.reset();
        this.actualizarHorasDisponibles(); // Resetea las horas
    }
    
    async mostrarDetallesDia(fecha, espacioId) {
        const modalBody = document.getElementById('modalReservaBody');
        if (!modalBody) return;
        
        modalBody.innerHTML = `
            <div class="text-center p-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>`;
        this.detallesReservaModal.show();
        
        try {
            // ** EL CAMBIO IMPORTANTE ESTÁ AQUÍ **
            // Hacemos una llamada al nuevo endpoint de Django para obtener los datos
            // específicos del día y espacio seleccionados.
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${URL_API}api/espacios/detalles_dia/?espacio_id=${espacioId}&fecha=${fecha}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (!response.ok) {
                throw new Error('Error al cargar los detalles de las reservas.');
            }
            
            const reservasOcupadas = await response.json();
            
            if (reservasOcupadas.length === 0) {
                modalBody.innerHTML = '<p class="text-success fw-bold">No hay reservas para este día.</p>';
                return;
            }

            let html = `<h6>Reservas para el ${new Date(fecha).toLocaleDateString()}:</h6>`;
            html += '<ul class="list-group list-group-flush">';
            
            reservasOcupadas.forEach(reserva => {
                const estadoBadge = this.getBadgeClass(reserva.estado);
                html += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${reserva.hora_inicio} - ${reserva.hora_fin}</strong>
                            <small class="d-block text-muted">Motivo: ${reserva.motivo}</small>
                        </div>
                        <span class="badge ${estadoBadge}">${reserva.estado}</span>
                    </li>
                `;
            });

            html += '</ul>';
            modalBody.innerHTML = html;
        } catch (error) {
            console.error('Error al obtener detalles del día:', error);
            modalBody.innerHTML = '<p class="text-danger">Error al cargar los detalles. Intente de nuevo.</p>';
        }
    }
}

// Inicia la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ReservaEspacio();
});
