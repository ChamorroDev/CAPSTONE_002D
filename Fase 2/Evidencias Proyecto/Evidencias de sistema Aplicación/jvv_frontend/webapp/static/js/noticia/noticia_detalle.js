const token = localStorage.getItem('access_token');

class NoticiaDetalle {
    constructor() {
        this.noticiaId = this.obtenerIdDeUrl();
        this.init();
    }

    obtenerIdDeUrl() {
        const path = window.location.pathname;
        const partes = path.split('/').filter(part => part.trim() !== '');
        
        // Diferentes patrones de URL
        if (partes.includes('noticias') && partes.length > 1) {
            const index = partes.indexOf('noticias');
            return partes[index + 1];
        }
        
        // Último segmento numérico
        for (let i = partes.length - 1; i >= 0; i--) {
            if (!isNaN(parseInt(partes[i]))) {
                return partes[i];
            }
        }
        
        return null;
    }

    async init() {
        if (this.noticiaId) {
            await this.cargarNoticia(this.noticiaId);
        } else {
            this.mostrarError('ID de noticia no válido');
        }
    }



    async cargarNoticia(noticiaId) {
        try {
            const response = await fetch(`${URL_API}api/noticias/${noticiaId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const noticia = await response.json();
                this.mostrarNoticia(noticia);
            } else if (response.status === 404) {
                this.mostrarError('Noticia no encontrada');
            } else if (response.status === 403) {
                this.mostrarError('No tienes permisos para ver esta noticia');
            } else {
                this.mostrarError('Error al cargar la noticia');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error de conexión. Intenta recargar la página.');
        }
    }

    mostrarNoticia(noticia) {
        const container = document.getElementById('noticia-detalle-container');
        
        const getFullImageUrl = (path) => {
            if (!path) return '';
            const base = URL_API.endsWith('/') ? URL_API.slice(0, -1) : URL_API;
            return `${base}${path}`;
        };

        const formatDate = (dateString) => {
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        };

        // CORREGIDO: El problema estaba aquí en el template string
        const noticiaHTML = `
            <div class="noticia-cargada">
                <!-- Header con gradiente -->
                <div class="noticia-header text-center position-relative">
                    <div class="position-relative z-1">
                        <span class="badge-publicada mb-3">
                            <i class="bi bi-check-circle-fill me-2"></i>
                            Noticia ${noticia.es_publica ? 'Publicada' : 'No Publicada'}
                        </span>
                        
                        <h1 class="display-5 fw-bold mb-3">${noticia.titulo || 'Sin título'}</h1>
                        
                        <div class="d-flex justify-content-center align-items-center flex-wrap gap-3">
                            <span class="fecha-estilo">
                                <i class="bi bi-calendar-event me-2"></i>
                                ${formatDate(noticia.fecha_creacion)}
                            </span>
                            
                            ${noticia.autor ? `
                                <span class="fecha-estilo">
                                    <i class="bi bi-person-circle me-2"></i>
                                    ${noticia.autor}
                                </span>
                            ` : ''}
                        </div>
                    </div>
                </div>

                <!-- Imagen Principal -->
                ${noticia.imagen_principal && noticia.imagen_principal.imagen ? `
                    <div class="mb-4 text-center">
                        <img src="${getFullImageUrl(noticia.imagen_principal.imagen)}" 
                             class="noticia-imagen-principal" 
                             alt="${noticia.titulo || 'Imagen principal de la noticia'}"
                             loading="lazy">
                        <div class="text-center mt-2">
                            <small class="text-muted">
                                <i class="bi bi-star-fill text-warning me-1"></i>
                                Imagen principal
                            </small>
                        </div>
                    </div>
                ` : ''}

                <!-- Contenido -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-body">
                        <div class="noticia-contenido">
                            ${noticia.contenido ? this.formatContent(noticia.contenido) : `
                                <div class="text-center text-muted py-4">
                                    <i class="bi bi-newspaper display-4 d-block mb-3"></i>
                                    <p class="fs-5">No hay contenido disponible para esta noticia.</p>
                                </div>
                            `}
                        </div>
                    </div>
                </div>

                <!-- Galería de Imágenes -->
                ${noticia.imagenes && noticia.imagenes.length > 0 ? `
                    <div class="card border-0 shadow-sm mb-4">
                        <div class="card-header bg-transparent border-0">
                            <h3 class="h4 mb-0">
                                <i class="bi bi-images text-primary me-2"></i>
                                Galería de Imágenes
                                <span class="badge bg-primary ms-2">${noticia.imagenes.length}</span>
                            </h3>
                        </div>
                        <div class="card-body">
                            <div class="galeria-grid">
                                ${noticia.imagenes.map((imagen, index) => `
                                    <div class="galeria-item">
                                        <img src="${getFullImageUrl(imagen.imagen)}" 
                                             alt="Imagen ${index + 1} de la noticia: ${noticia.titulo || ''}"
                                             loading="lazy">
                                        <div class="sr-only">Imagen ${index + 1} de la galería</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                ` : ''}

                <!-- Navegación -->
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mt-5 pt-4 border-top">
                    <a href="/noticias/" class="btn btn-outline-primary btn-lg">
                        <i class="bi bi-arrow-left me-2"></i>
                        Volver a Noticias
                    </a>
                    
                    <div class="d-flex gap-2">
                        <button onclick="window.print()" class="btn btn-outline-secondary">
                            <i class="bi bi-printer me-2"></i>
                            Imprimir
                        </button>
                        <button onclick="window.location.reload()" class="btn btn-outline-primary">
                            <i class="bi bi-arrow-clockwise me-2"></i>
                            Recargar
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = noticiaHTML;
        
        // Añadir interactividad a las imágenes de la galería
        this.addGalleryInteractivity();
    }

    formatContent(content) {
        // Convertir saltos de línea en párrafos
        return content.split('\n').filter(paragraph => paragraph.trim()).map(paragraph => `
            <p>${paragraph.trim()}</p>
        `).join('');
    }

    addGalleryInteractivity() {
        // Lightbox simple para la galería
        const galleryItems = document.querySelectorAll('.galeria-item');
        galleryItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                const img = item.querySelector('img');
                if (img) {
                    // Crear modal simple
                    const modalHTML = `
                        <div class="modal fade" id="imageModal" tabindex="-1">
                            <div class="modal-dialog modal-dialog-centered modal-lg">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Imagen ${index + 1}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body text-center">
                                        <img src="${img.src}" class="img-fluid" alt="${img.alt}">
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.body.insertAdjacentHTML('beforeend', modalHTML);
                    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
                    modal.show();
                    
                    // Limpiar modal al cerrar
                    document.getElementById('imageModal').addEventListener('hidden.bs.modal', function () {
                        this.remove();
                    });
                }
            });
        });
    }

    mostrarError(mensaje) {
        const container = document.getElementById('noticia-detalle-container');
        container.innerHTML = `
            <div class="alert alert-danger shadow-sm">
                <div class="d-flex align-items-center">
                    <i class="bi bi-exclamation-triangle-fill text-danger fs-2 me-3"></i>
                    <div>
                        <h4 class="alert-heading mb-2">¡Ups! Algo salió mal</h4>
                        <p class="mb-3">${mensaje}</p>
                        <div class="d-flex gap-2 flex-wrap">
                            <a href="/noticias/" class="btn btn-primary">
                                <i class="bi bi-newspaper me-2"></i>Ver todas las noticias
                            </a>
                            <a href="/" class="btn btn-outline-primary">
                                <i class="bi bi-house me-2"></i>Ir al inicio
                            </a>
                            <button onclick="window.location.reload()" class="btn btn-outline-secondary">
                                <i class="bi bi-arrow-clockwise me-2"></i>Reintentar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('noticia-detalle-container')) {
        new NoticiaDetalle();
    }
});