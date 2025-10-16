document.addEventListener('DOMContentLoaded', () => {
    const noticiasContainer = document.getElementById('home-noticias-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');

    if (noticiasContainer) {
        fetchNoticias();
    }

    async function fetchNoticias() {
        try {
            // Fetch the list of public news articles
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}noticias/`);

            if (!response.ok) {
                throw new Error('Error al cargar las noticias');
            }

            const noticias = await response.json();
            renderNoticias(noticias);

        } catch (error) {
            console.error('Error fetching noticias:', error);
            mostrarError();
        } finally {
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
        }
    }

    function renderNoticias(noticias) {
        // We only need the first 6 news items for the home page
        const noticiasRecientes = noticias.slice(0, 6);

        if (noticiasRecientes.length === 0) {
            mostrarEstadoVacio();
            return;
        }

        const noticiasHTML = `
            <div class="row g-4">
                ${noticiasRecientes.map(noticia => {
                    // Function to get the full image URL from the relative path
                    const getFullImageUrl = (path) => {
                        if (!path) return '';
                        const base = window.URL_API ? 
                            (window.URL_API.endsWith('/') ? window.URL_API.slice(0, -1) : window.URL_API) 
                            : 'http://127.0.0.1:8000';
                        return `${base}${path}`;
                    };
                    
                    const imageUrl = noticia.imagen_principal ? 
                        getFullImageUrl(noticia.imagen_principal) : 
                        (noticia.obtener_imagen_principal_url ? getFullImageUrl(noticia.obtener_imagen_principal_url) : '');
                    
                    const fechaFormateada = new Date(noticia.fecha_creacion).toLocaleDateString('es-ES', { 
                        day: 'numeric', 
                        month: 'long', 
                        year: 'numeric' 
                    });

                    // Limitar contenido a 150 caracteres
                    const contenidoCorto = noticia.contenido ? 
                        (noticia.contenido.length > 150 ? noticia.contenido.substring(0, 150) + '...' : noticia.contenido) 
                        : '';

                    return `
                        <div class="col-lg-4 col-md-6">
                            <div class="card news-card h-100">
                                ${imageUrl ? 
                                    `<img src="${imageUrl}" class="card-img-top news-image" alt="${noticia.titulo || 'Noticia'}">` : 
                                    `<div class="card-img-top news-image bg-light d-flex align-items-center justify-content-center">
                                        <i class="bi bi-newspaper text-muted" style="font-size: 3rem;"></i>
                                    </div>`
                                }
                                <div class="card-body">
                                    <span class="news-date">
                                        <i class="bi bi-calendar me-1"></i>
                                        ${fechaFormateada}
                                    </span>
                                    <h5 class="card-title mt-2">${noticia.titulo || 'Sin título'}</h5>
                                    <p class="card-text news-excerpt text-muted">
                                        ${contenidoCorto}
                                    </p>
                                </div>
                                <div class="card-footer bg-transparent border-0">
                                    <small class="text-muted">
                                        <i class="bi bi-person me-1"></i>
                                        ${noticia.autor ? (noticia.autor.nombre || 'Administración') : 'Administración'}
                                    </small>
                                    <a href="/noticias/${noticia.id}/" class="btn btn-primary btn-sm float-end">Leer más</a>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        noticiasContainer.innerHTML = noticiasHTML;
    }

    function mostrarEstadoVacio() {
        if (emptyState) {
            emptyState.classList.remove('d-none');
        } else {
            noticiasContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-newspaper text-muted" style="font-size: 4rem;"></i>
                    <h4 class="text-muted mt-3">Aún no hay noticias públicas</h4>
                    <p class="text-muted">Las noticias de la comunidad aparecerán aquí próximamente.</p>
                </div>
            `;
        }
    }

    function mostrarError() {
        noticiasContainer.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    No se pudieron cargar las noticias. Por favor, intente de nuevo más tarde.
                </div>
                <button class="btn btn-primary mt-3" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise me-2"></i>Reintentar
                </button>
            </div>
        `;
    }
});