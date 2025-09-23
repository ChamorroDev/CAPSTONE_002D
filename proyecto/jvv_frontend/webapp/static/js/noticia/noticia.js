class NoticiasLista {
    constructor() {
        this.noticias = [];
        this.filtradas = [];
        this.paginaActual = 1;
        this.porPagina = 5;
        this.filtros = {
            fecha: 'all',
            busqueda: ''
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.cargarNoticias();
        this.aplicarFiltros();
    }

    setupEventListeners() {
        document.getElementById('btnRecargar').addEventListener('click', () => {
            this.recargarNoticias();
        });

        document.getElementById('btnAplicarFiltros').addEventListener('click', () => {
            this.aplicarFiltros();
        });

        document.getElementById('btnLimpiarBusqueda').addEventListener('click', () => {
            document.getElementById('filtroBusqueda').value = '';
            this.filtros.busqueda = '';
            this.aplicarFiltros();
        });

        // Eventos de filtros de búsqueda
        document.getElementById('filtroBusqueda').addEventListener('input', (e) => {
            this.filtros.busqueda = e.target.value.toLowerCase();
        });

        document.getElementById('filtroBusqueda').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.aplicarFiltros();
            }
        });

        // Evento de filtro de fecha
        document.getElementById('filtroFecha').addEventListener('change', (e) => {
            this.filtros.fecha = e.target.value;
            this.toggleFechasPersonalizadas();
        });

        // Eventos de campos de fecha personalizados
        document.getElementById('filtroFechaInicio').addEventListener('change', (e) => {
            this.filtros.fechaInicio = e.target.value;
        });

        document.getElementById('filtroFechaFin').addEventListener('change', (e) => {
            this.filtros.fechaFin = e.target.value;
        });
    }

    toggleFechasPersonalizadas() {
        const divFechas = document.getElementById('divFechasPersonalizadas');
        if (this.filtros.fecha === 'custom') {
            divFechas.style.display = 'block';
        } else {
            divFechas.style.display = 'none';
        }
    }

    async cargarNoticias() {
        try {
            const response = await fetch(`${URL_API}noticias/`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.noticias = await response.json();
                this.actualizarEstadisticas();
            } else {
                throw new Error('Error al cargar noticias');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al cargar las noticias');
        }
    }

    aplicarFiltros() {
        this.filtradas = this.noticias.filter(noticia => {
            let fechaMatch = true;
            const fechaNoticia = new Date(noticia.fecha_creacion);
            const ahora = new Date();
            
            switch (this.filtros.fecha) {
                case 'today':
                    fechaMatch = fechaNoticia.toDateString() === ahora.toDateString();
                    break;
                case 'week':
                    const inicioSemana = new Date(ahora);
                    inicioSemana.setDate(ahora.getDate() - ahora.getDay());
                    fechaMatch = fechaNoticia >= inicioSemana;
                    break;
                case 'month':
                    fechaMatch = fechaNoticia.getMonth() === ahora.getMonth() && 
                                 fechaNoticia.getFullYear() === ahora.getFullYear();
                    break;
                case 'last30days':
                    const hace30dias = new Date();
                    hace30dias.setDate(hace30dias.getDate() - 30);
                    fechaMatch = fechaNoticia >= hace30dias;
                    break;
                case 'year':
                    fechaMatch = fechaNoticia.getFullYear() === ahora.getFullYear();
                    break;
                case 'custom':
                    const inicio = document.getElementById('filtroFechaInicio').value;
                    const fin = document.getElementById('filtroFechaFin').value;
                    if (inicio) {
                        fechaMatch = fechaNoticia >= new Date(inicio);
                    }
                    if (fin && fechaMatch) {
                        const fechaFin = new Date(fin);
                        fechaFin.setHours(23, 59, 59, 999);
                        fechaMatch = fechaNoticia <= fechaFin;
                    }
                    break;
            }
            
            const busquedaMatch = !this.filtros.busqueda || 
                                 noticia.titulo.toLowerCase().includes(this.filtros.busqueda) ||
                                 (noticia.contenido && noticia.contenido.toLowerCase().includes(this.filtros.busqueda));
            
            return fechaMatch && busquedaMatch;
        });

        this.paginaActual = 1;
        this.mostrarNoticias();
        this.actualizarEstadisticas();
    }

    mostrarNoticias() {
        const contenedor = document.getElementById('contenedor-noticias');
        const inicio = (this.paginaActual - 1) * this.porPagina;
        const fin = inicio + this.porPagina;
        const noticiasPagina = this.filtradas.slice(inicio, fin);

        if (noticiasPagina.length === 0) {
            contenedor.innerHTML = this.getHTMLNoResultados();
            this.ocultarPaginacion();
            return;
        }

        contenedor.innerHTML = `
            <div class="row vista-lista g-4">
                ${noticiasPagina.map(noticia => this.getHTMLNoticia(noticia)).join('')}
            </div>
        `;

        this.mostrarPaginacion();
        this.addEventListenersNoticias();
    }

    getHTMLNoticia(noticia) {
        const getFullImageUrl = (path) => {
            if (!path) return '';
            if (path.startsWith('http')) return path;
            const base = URL_API.endsWith('/') ? URL_API.slice(0, -1) : URL_API;
            return `${base}${path}`;
        };

        const imagenUrl = noticia.obtener_imagen_principal_url ? 
            getFullImageUrl(noticia.obtener_imagen_principal_url) : 
             'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjhmOGY4Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9IjAuMzVlbSI+Tm8gaW1hZ2VuPC90ZXh0Pjwvc3ZnPg==';

        const fecha = new Date(noticia.fecha_creacion).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const contenidoCorto = noticia.contenido ? 
            noticia.contenido.substring(0, 150) + (noticia.contenido.length > 150 ? '...' : '') : 
            'Sin contenido';

        return `
            <div class="col-md-12">
                <div class="card card-noticia shadow-sm h-100 noticia-cargada">
                    <img src="${imagenUrl}" 
                         class="card-img-top" 
                         alt="${noticia.titulo}"
                         loading="lazy"
                         onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjhmOGY4Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9IjAuMzVlbSI+RXJyb3IgY2FyZ2FuZG8gaW1hZ2VuPC90ZXh0Pjwvc3ZnPg=='">

                    <div class="card-body">
                        <h5 class="card-title fw-semibold">${noticia.titulo}</h5>
                        
                        <div class="text-muted small mb-2">
                            <i class="bi bi-calendar me-1"></i>${fecha}
                        </div>

                        <p class="card-text text-muted">${contenidoCorto}</p>
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <a href="/noticias/${noticia.id}/" class="btn btn-primary btn-sm">
                                <i class="bi bi-eye me-1"></i>Ver más
                            </a>
                            <button class="btn btn-outline-secondary btn-sm btn-vista-rapida" 
                                    data-noticia-id="${noticia.id}">
                                <i class="bi bi-search"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getHTMLNoResultados() {
        return `
            <div class="text-center py-5">
                <i class="bi bi-search display-1 text-muted"></i>
                <h3 class="text-muted mt-3">No se encontraron noticias</h3>
                <p class="text-muted">Intenta ajustar los filtros o busca con otros términos</p>
                <button class="btn btn-primary mt-2" onclick="noticiasLista.limpiarFiltros()">
                    <i class="bi bi-arrow-clockwise me-2"></i>Limpiar filtros
                </button>
            </div>
        `;
    }

    addEventListenersNoticias() {
        document.querySelectorAll('.btn-vista-rapida').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const noticiaId = e.target.closest('.btn-vista-rapida').dataset.noticiaId;
                this.mostrarVistaRapida(noticiaId);
            });
        });
    }

    async mostrarVistaRapida(noticiaId) {
        try {
            const response = await fetch(`${URL_API}api/noticias/${noticiaId}/`);
            if (response.ok) {
                const noticia = await response.json();
                
                document.getElementById('modalTitulo').textContent = noticia.titulo;
                document.getElementById('modalContenido').innerHTML = `
                    <div class="mb-3">
                        <strong>Fecha:</strong> ${new Date(noticia.fecha_creacion).toLocaleDateString('es-ES')}
                    </div>
                    <div class="mb-3">
                        <strong>Contenido:</strong>
                        <p>${noticia.contenido || 'Sin contenido'}</p>
                    </div>
                    <div class="text-center">
                        <a href="/noticias/${noticia.id}/" class="btn btn-primary">
                            <i class="bi bi-eye me-2"></i>Ver noticia completa
                        </a>
                    </div>
                `;

                new bootstrap.Modal(document.getElementById('modalNoticiaRapida')).show();
            }
        } catch (error) {
            console.error('Error en vista rápida:', error);
        }
    }

    mostrarPaginacion() {
        const totalPaginas = Math.ceil(this.filtradas.length / this.porPagina);
        const paginacion = document.getElementById('paginacion');
        
        if (totalPaginas <= 1) {
            this.ocultarPaginacion();
            return;
        }

        let html = '';
        
        html += `
            <li class="page-item ${this.paginaActual === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-pagina="${this.paginaActual - 1}">
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
        `;

        for (let i = 1; i <= totalPaginas; i++) {
            if (i === 1 || i === totalPaginas || (i >= this.paginaActual - 2 && i <= this.paginaActual + 2)) {
                html += `
                    <li class="page-item ${i === this.paginaActual ? 'active' : ''}">
                        <a class="page-link" href="#" data-pagina="${i}">${i}</a>
                    </li>
                `;
            } else if (i === this.paginaActual - 3 || i === this.paginaActual + 3) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        html += `
            <li class="page-item ${this.paginaActual === totalPaginas ? 'disabled' : ''}">
                <a class="page-link" href="#" data-pagina="${this.paginaActual + 1}">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;

        paginacion.innerHTML = html;
        paginacion.style.display = 'flex';

        paginacion.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pagina = parseInt(link.dataset.pagina);
                if (pagina && pagina !== this.paginaActual) {
                    this.paginaActual = pagina;
                    this.mostrarNoticias();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }

    ocultarPaginacion() {
        document.getElementById('paginacion').style.display = 'none';
    }

    actualizarEstadisticas() {
        document.getElementById('totalNoticias').textContent = this.noticias.length;
        
        const ahora = new Date();
        const noticiasEsteMes = this.noticias.filter(noticia => {
            const fechaNoticia = new Date(noticia.fecha_creacion);
            return fechaNoticia.getMonth() === ahora.getMonth() && 
                   fechaNoticia.getFullYear() === ahora.getFullYear();
        });
        document.getElementById('noticiasRecientes').textContent = noticiasEsteMes.length;
    }

    async recargarNoticias() {
        document.getElementById('contenedor-noticias').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="text-muted mt-3">Actualizando noticias...</p>
            </div>
        `;
        
        await this.cargarNoticias();
        this.aplicarFiltros();
    }

    limpiarFiltros() {
        document.getElementById('filtroFecha').value = 'all';
        document.getElementById('filtroBusqueda').value = '';
        document.getElementById('filtroFechaInicio').value = '';
        document.getElementById('filtroFechaFin').value = '';
        
        this.filtros = {
            fecha: 'all',
            busqueda: ''
        };
        
        this.toggleFechasPersonalizadas();
        this.aplicarFiltros();
    }

    mostrarError(mensaje) {
        document.getElementById('contenedor-noticias').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Error:</strong> ${mensaje}
                <button class="btn btn-outline-danger btn-sm ms-2" onclick="noticiasLista.recargarNoticias()">
                    Reintentar
                </button>
            </div>
        `;
    }
}

let noticiasLista;
document.addEventListener('DOMContentLoaded', function() {
    noticiasLista = new NoticiasLista();
});