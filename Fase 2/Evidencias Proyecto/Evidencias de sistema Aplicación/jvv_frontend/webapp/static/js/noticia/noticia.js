
class NoticiasLista {
    constructor() {
        this.noticias = [];
        this.filtradas = [];
        this.paginaActual = 1;
        this.porPagina = 6;
        this.filtros = { fecha: 'all', busqueda: '' };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.cargarNoticias();
        this.aplicarFiltros();
    }

    setupEventListeners() {
        document.getElementById('btnRecargar')?.addEventListener('click', () => this.recargarNoticias());
        document.getElementById('btnLimpiarBusqueda')?.addEventListener('click', () => {
            document.getElementById('filtroBusqueda').value = '';
            this.filtros.busqueda = '';
            this.aplicarFiltros();
        });

        document.getElementById('filtroBusqueda')?.addEventListener('input', (e) => {
            this.filtros.busqueda = e.target.value.toLowerCase();
            this.aplicarFiltros();
        });

        document.getElementById('filtroFecha')?.addEventListener('change', (e) => {
            this.filtros.fecha = e.target.value;
            this.toggleFechasPersonalizadas();
            this.aplicarFiltros();
        });

        document.getElementById('filtroFechaInicio')?.addEventListener('change', (e) => {
            this.filtros.fechaInicio = e.target.value;
            this.aplicarFiltros();
        });

        document.getElementById('filtroFechaFin')?.addEventListener('change', (e) => {
            this.filtros.fechaFin = e.target.value;
            this.aplicarFiltros();
        });

        document.getElementById('orden')?.addEventListener('change', (e) => {
            this.orden = e.target.value;
            this.aplicarFiltros();
        });
    }

    toggleFechasPersonalizadas() {
        const divFechas = document.getElementById('divFechasPersonalizadas');
        divFechas.style.display = (this.filtros.fecha === 'custom') ? 'block' : 'none';
    }

    async cargarNoticias() {
        try {
            const res = await fetch(`${URL_API}noticias/`);
            if (!res.ok) throw new Error('Error al cargar noticias');
            this.noticias = await res.json();
            this.actualizarEstadisticas();
        } catch (err) {
            console.error(err);
            this.mostrarError('Error al cargar las noticias');
        }
    }

    aplicarFiltros() {
        this.filtradas = this.noticias.filter(n => {
            let fechaMatch = true;
            const fechaNoticia = new Date(n.fecha_creacion || n.fechaPublicacion);
            const ahora = new Date();

            switch (this.filtros.fecha) {
                case 'today': fechaMatch = fechaNoticia.toDateString() === ahora.toDateString(); break;
                case 'week':
                    const inicioSemana = new Date(ahora);
                    inicioSemana.setDate(ahora.getDate() - ahora.getDay());
                    fechaMatch = fechaNoticia >= inicioSemana; break;
                case 'month': fechaMatch = fechaNoticia.getMonth() === ahora.getMonth() && fechaNoticia.getFullYear() === ahora.getFullYear(); break;
                case 'last30days':
                    const hace30dias = new Date(); hace30dias.setDate(hace30dias.getDate() - 30);
                    fechaMatch = fechaNoticia >= hace30dias; break;
                case 'year': fechaMatch = fechaNoticia.getFullYear() === ahora.getFullYear(); break;
                case 'custom':
                    if (this.filtros.fechaInicio) fechaMatch = fechaNoticia >= new Date(this.filtros.fechaInicio);
                    if (this.filtros.fechaFin && fechaMatch) {
                        const fin = new Date(this.filtros.fechaFin); fin.setHours(23,59,59,999);
                        fechaMatch = fechaNoticia <= fin;
                    } break;
            }

            const busquedaMatch = !this.filtros.busqueda ||
                n.titulo.toLowerCase().includes(this.filtros.busqueda) ||
                (n.contenido && n.contenido.toLowerCase().includes(this.filtros.busqueda));

            return fechaMatch && busquedaMatch;
        });

        this.paginaActual = 1;
        this.mostrarNoticias();
        this.actualizarEstadisticas();
    }

    mostrarNoticias() {
        const contenedor = document.getElementById('contenedor-noticias');
        if (!contenedor) return;

        const inicio = (this.paginaActual - 1) * this.porPagina;
        const fin = inicio + this.porPagina;
        const noticiasPagina = this.filtradas.slice(inicio, fin);

        if (noticiasPagina.length === 0) {
            contenedor.innerHTML = '<p class="text-center py-5">No se encontraron noticias</p>';
            this.ocultarPaginacion();
            return;
        }

        contenedor.innerHTML = `
            <div class="row g-4">
                ${noticiasPagina.map(n => this.getHTMLNoticia(n)).join('')}
            </div>
        `;

        this.mostrarPaginacion();
        this.addEventListenersNoticias();
    }

    getHTMLNoticia(n) {
        const getFullImageUrl = (path) => {
            if (!path) return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2U1ZTVlNSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE0IiBmaWxsPSIjY2NjIj5JbWFnZW4gTm8gRm91bmQ8L3RleHQ+PC9zdmc+';
            if (path.startsWith('http')) return path;
            const base = URL_API.endsWith('/') ? URL_API.slice(0, -1) : URL_API;
            return `${base}${path}`;
        };

        const imagenUrl = getFullImageUrl(n.obtener_imagen_principal_url);
        const fecha = new Date(n.fecha_creacion || n.fechaPublicacion).toLocaleDateString('es-ES', {
            year:'numeric', month:'long', day:'numeric'
        });
        let autorCompleto = n.autor || 'Desconocido';
        const autorSolonombre = autorCompleto.split('-')[0].trim();
        const categoria = n.categoria || 'General';
        const contenidoCorto = n.contenido 
            ? n.contenido.substring(0, 120) + (n.contenido.length > 120 ? '...' : '') 
            : '';
        const destacada = n.importante ? 'Destacada' : '';

        return `
            <div class="col-xl-4 col-lg-6 col-md-6 mb-4">
                <div class="card news-card h-100 shadow-sm d-flex flex-column">
                    <div class="card-img-top-container position-relative">
                        <img src="${imagenUrl}" class="card-img-top news-image" alt="${n.titulo}">
                        <div class="card-badge position-absolute top-0 end-0 m-3">
                            <span class="badge bg-primary">${categoria}</span>
                        </div>
                    </div>
                    <div class="card-body d-flex flex-column flex-grow-1">
                        <div class="news-meta mb-2">
                            <small class="text-muted">
                                <i class="bi bi-calendar me-1"></i> ${fecha}
                            </small>
                            ${destacada ? `<small class="text-muted ms-3">
                                <i class="bi bi-star-fill text-warning me-1"></i>${destacada}
                            </small>` : ''}
                        </div>
                        <h5 class="card-title text-dark">${n.titulo}</h5>
                        <p class="card-text news-excerpt text-muted flex-grow-1">${contenidoCorto}</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <a href="/noticias/${n.id}/" class="btn btn-outline-primary btn-sm">
                                Leer más
                            </a>
                            <small class="text-muted">${autorSolonombre}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }




    addEventListenersNoticias() {
        document.querySelectorAll('.btn-vista-rapida').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                this.mostrarVistaRapida(id);
            });
        });
    }

    async mostrarVistaRapida(id) {
        try {
            const res = await fetch(`${URL_API}api/noticias/${id}/`);
            if (!res.ok) throw new Error('Error al obtener noticia');
            const n = await res.json();
            document.getElementById('modalTitulo').textContent = n.titulo;
            document.getElementById('modalContenido').innerHTML = `
                <p><strong>Fecha:</strong> ${new Date(n.fecha_creacion || n.fechaPublicacion).toLocaleDateString('es-ES')}</p>
                <p><strong>Autor:</strong> ${n.autor || 'Desconocido'}</p>
                <p>${n.contenido || ''}</p>
            `;
            new bootstrap.Modal(document.getElementById('modalNoticiaRapida')).show();
        } catch (err) {
            console.error(err);
        }
    }

    mostrarPaginacion() {
        const totalPaginas = Math.ceil(this.filtradas.length / this.porPagina);
        const paginacion = document.getElementById('paginacion');
        if (!paginacion || totalPaginas <= 1) return this.ocultarPaginacion();

        let html = `<li class="page-item ${this.paginaActual === 1 ? 'disabled' : ''}">
                        <a class="page-link" href="#" data-pagina="${this.paginaActual -1}">&laquo;</a>
                    </li>`;

        for(let i=1; i<=totalPaginas; i++){
            html += `<li class="page-item ${i===this.paginaActual?'active':''}">
                        <a class="page-link" href="#" data-pagina="${i}">${i}</a>
                    </li>`;
        }

        html += `<li class="page-item ${this.paginaActual===totalPaginas?'disabled':''}">
                    <a class="page-link" href="#" data-pagina="${this.paginaActual+1}">&raquo;</a>
                 </li>`;

        paginacion.innerHTML = html;

        paginacion.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const p = parseInt(link.dataset.pagina);
                if (p>=1 && p<=totalPaginas && p!==this.paginaActual){
                    this.paginaActual = p;
                    this.mostrarNoticias();
                    window.scrollTo({top:0,behavior:'smooth'});
                }
            });
        });
    }

    ocultarPaginacion() {
        const p = document.getElementById('paginacion');
        if(p) p.style.display='none';
    }

    actualizarEstadisticas() {
        const totalElem = document.getElementById('totalNoticias');
        if (totalElem) totalElem.textContent = this.noticias.length;

        const ahora = new Date();
        const noticiasMes = this.noticias.filter(n => {
            const f = new Date(n.fecha_creacion || n.fechaPublicacion);
            return f.getMonth() === ahora.getMonth() && f.getFullYear() === ahora.getFullYear();
        });
        const mesElem = document.getElementById('noticiasEsteMes');
        if (mesElem) mesElem.textContent = noticiasMes.length;

        const hace7Dias = new Date();
        hace7Dias.setDate(hace7Dias.getDate() - 7);
        const recientes = this.noticias.filter(n => new Date(n.fecha_creacion || n.fechaPublicacion) >= hace7Dias);
        const recientesElem = document.getElementById('noticiasRecientes');
        if (recientesElem) recientesElem.textContent = recientes.length;
    }

    async recargarNoticias() {
        await this.cargarNoticias();
        this.aplicarFiltros();
    }

    mostrarError(msg) {
        const contenedor = document.getElementById('contenedor-noticias');
        if(contenedor) contenedor.innerHTML = `<p class="text-center text-danger py-5">${msg}</p>`;
    }
}

let noticiasLista;
document.addEventListener('DOMContentLoaded', () => { noticiasLista = new NoticiasLista(); });
