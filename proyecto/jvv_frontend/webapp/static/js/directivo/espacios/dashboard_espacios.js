class DirectivoDashboard {
    constructor() {
        this.BASE_URL = 'http://127.0.0.1:8000';
        this.solicitudes = [];
        this.espacios = [];
        this.filtros = {
            estado: '',
            espacio: '',
            fecha_desde: '',
            fecha_hasta: ''
        };
        this.paginaActual = 1;
        this.porPagina = 10;
        // Variables para almacenar instancias de gráficos
        this.solicitudesChartInstance = null;
        this.estadosChartInstance = null;
        this.init();
    }

    async init() {
        await this.cargarDatosIniciales();
        this.setupEventListeners();
        this.setupFiltros();
    }

    async cargarDatosIniciales() {
        try {
            await Promise.all([
                this.cargarSolicitudes(),
                this.cargarEspacios(),
                this.cargarEstadisticas()
            ]);
        } catch (error) {
            console.error('Error cargando datos:', error);
            this.mostrarMensaje('Error al cargar los datos', 'error');
        }
    }

    async cargarSolicitudes() {
        try {
            const token = localStorage.getItem('access_token');
            let url = `${this.BASE_URL}/api/directivo/espacios/todas-solicitudes/`;
            
            // Agregar filtros a la URL
            const params = new URLSearchParams();
            if (this.filtros.estado) params.append('estado', this.filtros.estado);
            if (this.filtros.espacio) params.append('espacio', this.filtros.espacio);
            if (this.filtros.fecha_desde) params.append('fecha_desde', this.filtros.fecha_desde);
            if (this.filtros.fecha_hasta) params.append('fecha_hasta', this.filtros.fecha_hasta);
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.solicitudes = await response.json();
                this.renderSolicitudes();
                this.actualizarContadores();
            }
        } catch (error) {
            console.error('Error cargando solicitudes:', error);
        }
    }

    async cargarEspacios() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${this.BASE_URL}/api/directivo/espacios/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.espacios = await response.json();
                this.llenarSelectorEspacios();
            }
        } catch (error) {
            console.error('Error cargando espacios:', error);
        }
    }

    async cargarEstadisticas() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${this.BASE_URL}/api/directivo/espacios/estadisticas/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.actualizarEstadisticas(data);
                this.initCharts(data);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    renderSolicitudes() {
        const container = document.getElementById('solicitudes-list');
        const inicio = (this.paginaActual - 1) * this.porPagina;
        const fin = inicio + this.porPagina;
        const solicitudesPagina = this.solicitudes.slice(inicio, fin);

        if (solicitudesPagina.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">
                        <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                        <p class="text-muted mt-2">No hay solicitudes que coincidan con los filtros</p>
                    </td>
                </tr>
            `;
            return;
        }

        container.innerHTML = solicitudesPagina.map(solicitud => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="flex-grow-1">
                            <h6 class="mb-0">${solicitud.solicitante_nombre}</h6>
                            <small class="text-muted">${solicitud.solicitante_email}</small>
                        </div>
                    </div>
                </td>
                <td>${solicitud.espacio_nombre}</td>
                <td>${new Date(solicitud.fecha_evento).toLocaleDateString('es-ES')}</td>
                <td>${solicitud.hora_inicio} - ${solicitud.hora_fin}</td>
                <td>
                    <span class="d-inline-block text-truncate" style="max-width: 150px;" 
                          title="${solicitud.motivo}">
                        ${solicitud.motivo}
                    </span>
                </td>
                <td>
                    <span class="badge ${this.getBadgeClass(solicitud.estado)}">
                        ${solicitud.estado}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-primary" onclick="directivoDashboard.verDetalles(${solicitud.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        ${solicitud.estado === 'pendiente' ? `
                        <button class="btn btn-success" onclick="directivoDashboard.aprobarSolicitud(${solicitud.id})">
                            <i class="bi bi-check"></i>
                        </button>
                        <button class="btn btn-danger" onclick="directivoDashboard.rechazarSolicitud(${solicitud.id})">
                            <i class="bi bi-x"></i>
                        </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        this.actualizarPaginacion();
    }

    getBadgeClass(estado) {
        const clases = {
            'pendiente': 'bg-warning',
            'aprobado': 'bg-success',
            'rechazado': 'bg-danger'
        };
        return clases[estado] || 'bg-secondary';
    }

    async verDetalles(solicitudId) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${this.BASE_URL}/api/directivo/espacios/solicitudes/${solicitudId}/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const solicitud = await response.json();
                this.mostrarModalDetalles(solicitud);
            }
        } catch (error) {
            console.error('Error cargando detalles:', error);
        }
    }

    mostrarModalDetalles(solicitud) {
        const modalBody = document.getElementById('modal-detalles-body');
        const modalAcciones = document.getElementById('modal-acciones');

        // Verificar que los datos existan
        console.log('Datos de solicitud:', solicitud);

        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Información de la Reserva</h6>
                    <p><strong>Espacio:</strong> ${solicitud.espacio?.nombre || 'No disponible'}</p>
                    <p><strong>Fecha:</strong> ${new Date(solicitud.fecha_evento).toLocaleDateString('es-ES')}</p>
                    <p><strong>Horario:</strong> ${solicitud.hora_inicio} - ${solicitud.hora_fin}</p>
                    <p><strong>Estado:</strong> <span class="badge ${this.getBadgeClass(solicitud.estado)}">${solicitud.estado}</span></p>
                </div>
                <div class="col-md-6">
                    <h6>Información del Solicitante</h6>
                    <p><strong>Nombre:</strong> ${solicitud.solicitante?.nombre_completo || 'No disponible'}</p>
                    <p><strong>Email:</strong> ${solicitud.solicitante?.email || 'No disponible'}</p>
                    <p><strong>Teléfono:</strong> ${solicitud.solicitante?.telefono || 'No disponible'}</p>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Motivo de la Reserva</h6>
                    <p class="border p-3 rounded">${solicitud.motivo || 'Sin motivo especificado'}</p>
                </div>
            </div>
            ${solicitud.observaciones ? `
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Observaciones</h6>
                    <p class="border p-3 rounded bg-light">${solicitud.observaciones}</p>
                </div>
            </div>
            ` : ''}
        `;

        if (solicitud.estado === 'pendiente') {
            modalAcciones.innerHTML = `
                <button class="btn btn-success" onclick="directivoDashboard.aprobarSolicitud(${solicitud.id})">
                    <i class="bi bi-check me-1"></i>Aprobar
                </button>
                <button class="btn btn-danger" onclick="directivoDashboard.rechazarSolicitud(${solicitud.id})">
                    <i class="bi bi-x me-1"></i>Rechazar
                </button>
            `;
        } else {
            modalAcciones.innerHTML = '';
        }

        new bootstrap.Modal(document.getElementById('modalDetallesSolicitud')).show();
    }

    async aprobarSolicitud(solicitudId) {
        if (confirm('¿Estás seguro de aprobar esta solicitud?')) {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`${this.BASE_URL}/api/directivo/espacios/solicitudes/${solicitudId}/aprobar/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    this.mostrarMensaje('Solicitud aprobada correctamente', 'success');
                    bootstrap.Modal.getInstance(document.getElementById('modalDetallesSolicitud')).hide();
                    await this.cargarDatosIniciales();
                } else {
                    throw new Error('Error al aprobar solicitud');
                }
            } catch (error) {
                this.mostrarMensaje('Error al aprobar solicitud', 'error');
            }
        }
    }

    async rechazarSolicitud(solicitudId) {
        const motivo = prompt('Ingrese el motivo del rechazo:');
        if (motivo === null) return;
        
        if (motivo.trim() === '') {
            alert('Debe ingresar un motivo para el rechazo');
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${this.BASE_URL}/api/directivo/espacios/solicitudes/${solicitudId}/rechazar/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ motivo: motivo.trim() })
            });

            if (response.ok) {
                this.mostrarMensaje('Solicitud rechazada correctamente', 'success');
                bootstrap.Modal.getInstance(document.getElementById('modalDetallesSolicitud')).hide();
                await this.cargarDatosIniciales();
            } else {
                throw new Error('Error al rechazar solicitud');
            }
        } catch (error) {
            this.mostrarMensaje('Error al rechazar solicitud', 'error');
        }
    }

    setupFiltros() {
        // Llenar selector de espacios
        this.llenarSelectorEspacios();

        // Event listeners para filtros
        document.getElementById('filtro-estado').addEventListener('change', (e) => {
            this.filtros.estado = e.target.value;
        });

        document.getElementById('filtro-espacio').addEventListener('change', (e) => {
            this.filtros.espacio = e.target.value;
        });

        document.getElementById('filtro-fecha-desde').addEventListener('change', (e) => {
            this.filtros.fecha_desde = e.target.value;
        });

        document.getElementById('filtro-fecha-hasta').addEventListener('change', (e) => {
            this.filtros.fecha_hasta = e.target.value;
        });
    }

    llenarSelectorEspacios() {
        const select = document.getElementById('filtro-espacio');
        select.innerHTML = '<option value="">Todos los espacios</option>';
        
        this.espacios.forEach(espacio => {
            const option = document.createElement('option');
            option.value = espacio.id;
            option.textContent = espacio.nombre;
            select.appendChild(option);
        });
    }

    aplicarFiltros() {
        this.paginaActual = 1;
        this.cargarSolicitudes();
    }

    limpiarFiltros() {
        document.getElementById('filtro-estado').value = '';
        document.getElementById('filtro-espacio').value = '';
        document.getElementById('filtro-fecha-desde').value = '';
        document.getElementById('filtro-fecha-hasta').value = '';
        
        this.filtros = {
            estado: '',
            espacio: '',
            fecha_desde: '',
            fecha_hasta: ''
        };
        
        this.aplicarFiltros();
    }

    actualizarContadores() {
        const total = this.solicitudes.length;
        const pendientes = this.solicitudes.filter(s => s.estado === 'pendiente').length;
        const aprobadas = this.solicitudes.filter(s => s.estado === 'aprobado').length;
        const rechazadas = this.solicitudes.filter(s => s.estado === 'rechazado').length;

        document.getElementById('total-solicitudes').textContent = total;
        document.getElementById('solicitudes-pendientes').textContent = pendientes;
        document.getElementById('solicitudes-aprobadas').textContent = aprobadas;
        document.getElementById('solicitudes-rechazadas').textContent = rechazadas;
        document.getElementById('total-solicitudes-badge').textContent = total;
    }

    actualizarEstadisticas(data) {
        // Actualizar contadores principales
        document.getElementById('total-solicitudes').textContent = data.totales.solicitudes || 0;
        document.getElementById('solicitudes-pendientes').textContent = data.totales.pendientes || 0;
        document.getElementById('solicitudes-aprobadas').textContent = data.totales.aprobadas || 0;
        document.getElementById('solicitudes-rechazadas').textContent = data.totales.rechazadas || 0;
        
        // Inicializar gráficos
        this.initCharts(data);
    }

    initCharts(data) {
        this.destruirGraficos();
        this.initSolicitudesChart(data.solicitudes_mes_a_mes || []);
        this.initEstadosChart(data.distribucion_estados || {});
        this.initEspaciosPopularesChart(data.espacios_populares || []);
    }
    destruirGraficos() {
        // Destruir gráficos existentes si los hay
        if (this.solicitudesChartInstance) {
            this.solicitudesChartInstance.destroy();
            this.solicitudesChartInstance = null;
        }
        
        if (this.estadosChartInstance) {
            this.estadosChartInstance.destroy();
            this.estadosChartInstance = null;
        }
    }

    recargarDatos() {
        this.cargarDatosIniciales();
        this.mostrarMensaje('Datos actualizados', 'success');
    }
    initSolicitudesChart(solicitudesData) {
        const ctx = document.getElementById('solicitudesChart');
        if (!ctx) return;

        // Destruir instancia previa si existe
        if (this.solicitudesChartInstance) {
            this.solicitudesChartInstance.destroy();
        }

        // Ordenar datos por mes
        const datosOrdenados = solicitudesData.sort((a, b) => {
            return new Date(a.mes + '-01') - new Date(b.mes + '-01');
        });

        this.solicitudesChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: datosOrdenados.map(item => {
                    const [year, month] = item.mes.split('-');
                    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                    return `${meses[parseInt(month) - 1]} ${year}`;
                }),
                datasets: [
                    {
                        label: 'Aprobadas',
                        data: datosOrdenados.map(item => item.aprobadas || 0),
                        backgroundColor: 'rgba(40, 167, 69, 0.8)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Pendientes',
                        data: datosOrdenados.map(item => item.pendientes || 0),
                        backgroundColor: 'rgba(255, 193, 7, 0.8)',
                        borderColor: 'rgba(255, 193, 7, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Rechazadas',
                        data: datosOrdenados.map(item => item.rechazadas || 0),
                        backgroundColor: 'rgba(220, 53, 69, 0.8)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad de Solicitudes'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Solicitudes por Mes'
                    },
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }

    initEstadosChart(estadosData) {
        const ctx = document.getElementById('estadosChart');
        if (!ctx) return;

        // Destruir instancia previa si existe
        if (this.estadosChartInstance) {
            this.estadosChartInstance.destroy();
        }

        const total = estadosData.aprobado + estadosData.pendiente + estadosData.rechazado;
        
        this.estadosChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    `Aprobadas (${estadosData.aprobado})`,
                    `Pendientes (${estadosData.pendiente})`,
                    `Rechazadas (${estadosData.rechazado})`
                ],
                datasets: [{
                    data: [estadosData.aprobado, estadosData.pendiente, estadosData.rechazado],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: `Distribución por Estado - Total: ${total}`
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    initEspaciosPopularesChart(espaciosData) {
        const container = document.getElementById('espacios-populares');
        if (!container) return;

        if (espaciosData.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay datos de espacios populares</p>';
            return;
        }

        container.innerHTML = espaciosData.map(espacio => `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <strong>${espacio.nombre}</strong>
                    <span class="badge bg-primary">${espacio.total_solicitudes} solicitudes</span>
                </div>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar bg-success" 
                        role="progressbar" 
                        style="width: ${espacio.tasa_aprobacion || 0}%"
                        aria-valuenow="${espacio.tasa_aprobacion || 0}" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                        ${espacio.tasa_aprobacion ? Math.round(espacio.tasa_aprobacion) : 0}% aprobación
                    </div>
                </div>
                <div class="d-flex justify-content-between small text-muted">
                    <span>${espacio.solicitudes_aprobadas || 0} aprobadas</span>
                    <span>${(espacio.total_solicitudes - espacio.solicitudes_aprobadas) || 0} otras</span>
                </div>
            </div>
        `).join('');
    }

    exportarDatos() {
        // Implementar exportación
        this.mostrarMensaje('Funcionalidad de exportación en desarrollo', 'info');
    }

    mostrarMensaje(mensaje, tipo = 'success') {
        // Implementar sistema de mensajes
        alert(`${tipo.toUpperCase()}: ${mensaje}`);
    }

    setupEventListeners() {
        this.setupPaginacionListeners();
        // Event listeners adicionales si son necesarios
    }
    actualizarPaginacion() {
        const paginacionContainer = document.getElementById('paginacion-solicitudes');
        if (!paginacionContainer) return;

        const totalPaginas = Math.ceil(this.solicitudes.length / this.porPagina);
        
        if (totalPaginas <= 1) {
            paginacionContainer.style.display = 'none';
            return;
        }

        paginacionContainer.style.display = 'flex';
        
        let html = '';
        
        // Botón Anterior
        html += `
            <li class="page-item ${this.paginaActual === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-pagina="${this.paginaActual - 1}">
                    <i class="bi bi-chevron-left"></i> Anterior
                </a>
            </li>
        `;

        // Páginas
        const paginasMostrar = this.obtenerPaginasAMostrar(this.paginaActual, totalPaginas);
        
        for (let i = 1; i <= totalPaginas; i++) {
            if (paginasMostrar.includes(i)) {
                html += `
                    <li class="page-item ${i === this.paginaActual ? 'active' : ''}">
                        <a class="page-link" href="#" data-pagina="${i}">${i}</a>
                    </li>
                `;
            } else if (i === paginasMostrar[paginasMostrar.length - 1] + 1 && i < totalPaginas) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        // Botón Siguiente
        html += `
            <li class="page-item ${this.paginaActual === totalPaginas ? 'disabled' : ''}">
                <a class="page-link" href="#" data-pagina="${this.paginaActual + 1}">
                    Siguiente <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;

        paginacionContainer.innerHTML = html;
        
        // Agregar event listeners
        this.setupPaginacionListeners();
    }

    obtenerPaginasAMostrar(paginaActual, totalPaginas) {
        const paginas = [];
        const paginasVisibles = 5; // Número máximo de páginas a mostrar
        
        if (totalPaginas <= paginasVisibles) {
            // Mostrar todas las páginas
            for (let i = 1; i <= totalPaginas; i++) {
                paginas.push(i);
            }
        } else {
            // Mostrar páginas alrededor de la actual
            let inicio = Math.max(1, paginaActual - Math.floor(paginasVisibles / 2));
            let fin = Math.min(totalPaginas, inicio + paginasVisibles - 1);
            
            // Ajustar si estamos cerca del inicio o final
            if (fin - inicio + 1 < paginasVisibles) {
                inicio = Math.max(1, fin - paginasVisibles + 1);
            }
            
            for (let i = inicio; i <= fin; i++) {
                paginas.push(i);
            }
            
            // Siempre incluir primera y última página
            if (!paginas.includes(1)) {
                paginas.unshift(1);
                if (paginas.length > paginasVisibles) {
                    paginas.splice(1, 0, '...');
                }
            }
            
            if (!paginas.includes(totalPaginas)) {
                paginas.push(totalPaginas);
                if (paginas.length > paginasVisibles) {
                    paginas.splice(paginas.length - 2, 0, '...');
                }
            }
        }
        
        return paginas.filter(pagina => pagina !== '...');
    }

    setupPaginacionListeners() {
        const paginacionContainer = document.getElementById('paginacion-solicitudes');
        if (!paginacionContainer) return;

        paginacionContainer.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pagina = parseInt(link.dataset.pagina);
                
                if (pagina && pagina !== this.paginaActual) {
                    this.paginaActual = pagina;
                    this.renderSolicitudes();
                    
                    // Scroll suave hacia la tabla
                    document.getElementById('solicitudes-list').scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    window.directivoDashboard = new DirectivoDashboard();
});