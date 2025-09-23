document.addEventListener('DOMContentLoaded', async () => {
    // URL base de la API
    const URL_API = 'http://127.0.0.1:8000/';
    const token = localStorage.getItem('access_token');
    
    // Elementos del DOM
    const form = document.getElementById('noticiaForm');
    const tituloInput = document.getElementById('titulo');
    const contenidoInput = document.getElementById('contenido');
    const esPublicaInput = document.getElementById('esPublica');
    const newImagesInput = document.getElementById('newImages');
    const imageGallery = document.getElementById('imageGallery');
    const alertsContainer = document.getElementById('alertsContainer');
    const formSpinner = document.getElementById('formSpinner');

    // Obtener el ID de la noticia desde la URL
    const pathParts = window.location.pathname.split('/').filter(part => part.trim() !== '');
    const noticiaId = pathParts[pathParts.length - 2] === 'editar' ? pathParts[pathParts.length - 1] : null;

    // Verificar si el ID existe y es válido
    if (!noticiaId || isNaN(parseInt(noticiaId))) {
        showAlert('No se ha especificado una noticia válida para editar. Serás redirigido.', 'danger');
        setTimeout(() => {
            window.location.href = '/gestion_noticias/';
        }, 3000);
        return;
    }

    // Cargar los datos de la noticia
    await fetchNoticiaData(noticiaId);

    // --- Funciones de utilidad ---
    function showAlert(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertsContainer.appendChild(alert);
        
        if (duration) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
    }

    function showLoading(button, show = true) {
        const spinner = button.querySelector('.loading-spinner') || formSpinner;
        if (spinner) {
            spinner.style.display = show ? 'inline-block' : 'none';
        }
        button.disabled = show;
    }

    // --- Cargar datos de la noticia ---
    async function fetchNoticiaData(id) {
        try {
            const response = await fetch(`${URL_API}api/directivo/noticias/${id}/`, {
                method: 'GET',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Noticia no encontrada.');
                }
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const noticia = await response.json();
            
            // Rellenar el formulario con los datos de la noticia
            tituloInput.value = noticia.titulo || '';
            contenidoInput.value = noticia.contenido || '';
            esPublicaInput.checked = noticia.es_publica || false;

            // Renderizar la galería de imágenes
            await renderGallery(noticia.imagenes, noticia.imagen_principal);

        } catch (error) {
            console.error('Error al cargar la noticia:', error);
            showAlert(`Error al cargar la noticia: ${error.message}`, 'danger');
            setTimeout(() => {
                window.location.href = '/gestion_noticias/';
            }, 3000);
        }
    }

    // --- Renderizar galería de imágenes ---
    async function renderGallery(imagenes, imagenPrincipal) {
        if (!imagenes || imagenes.length === 0) {
            imageGallery.innerHTML = `
                <div class="placeholder-gallery">
                    <i class="bi bi-image text-muted fs-1 mb-2"></i>
                    <p class="text-muted">No hay imágenes en esta noticia</p>
                    <small class="text-muted">Agrega imágenes usando el botón de arriba</small>
                </div>
            `;
            return;
        }

        const principalImageId = imagenPrincipal ? imagenPrincipal.id : null;
        
        imageGallery.innerHTML = imagenes.map(imagen => {
            const isPrincipal = imagen.id === principalImageId;
            const imageUrl = `${URL_API.replace(/\/$/, '')}${imagen.imagen}`;
            
            return `
                <div class="image-card ${isPrincipal ? 'principal' : ''}" data-image-id="${imagen.id}">
                    <img src="${imageUrl}" alt="Imagen de la noticia" loading="lazy">
                    ${isPrincipal ? '<span class="principal-badge"><i class="bi bi-star-fill"></i> Principal</span>' : ''}
                    <div class="image-overlay">
                        <div class="image-actions">
                            <button class="btn btn-danger btn-icon" data-action="delete" data-id="${imagen.id}" 
                                    title="Eliminar imagen">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="image-actions">
                            <button class="btn btn-${isPrincipal ? 'success' : 'primary'} btn-sm" 
                                    data-action="set-principal" data-id="${imagen.id}"
                                    ${isPrincipal ? 'disabled' : ''}>
                                <i class="bi bi-star${isPrincipal ? '-fill' : ''}"></i>
                                ${isPrincipal ? 'Principal' : 'Hacer Principal'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // --- Manejar el envío del formulario principal ---
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const submitButton = event.target.querySelector('button[type="submit"]');
        showLoading(submitButton, true);

        try {
            const formData = new FormData();
            formData.append('titulo', tituloInput.value);
            formData.append('contenido', contenidoInput.value);
            formData.append('es_publica', esPublicaInput.checked);
            
            const response = await fetch(`${URL_API}api/directivo/noticias/${noticiaId}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                showAlert('Noticia actualizada con éxito.', 'success');
                setTimeout(() => {
                    window.location.href = '/gestion_noticias/';
                }, 1500);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || JSON.stringify(errorData));
            }
        } catch (error) {
            console.error('Error al guardar la noticia:', error);
            showAlert(`Error al guardar: ${error.message}`, 'danger');
        } finally {
            showLoading(submitButton, false);
        }
    });

    // --- Manejar eventos de la galería ---
    imageGallery.addEventListener('click', async (event) => {
        const button = event.target.closest('button');
        if (!button) return;

        const action = button.getAttribute('data-action');
        const imageId = button.getAttribute('data-id');

        if (action === 'delete') {
            if (!confirm('¿Estás seguro de que quieres eliminar esta imagen? Esta acción no se puede deshacer.')) {
                return;
            }

            try {
                showLoading(button, true);
                const response = await fetch(`${URL_API}api/directivo/noticias_imagenes/${imageId}/`, {
                    method: 'DELETE',
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    showAlert('Imagen eliminada con éxito.', 'success');
                    await fetchNoticiaData(noticiaId);
                } else {
                    throw new Error('Error al eliminar la imagen');
                }
            } catch (error) {
                console.error('Error al eliminar imagen:', error);
                showAlert('Error al eliminar la imagen.', 'danger');
            } finally {
                showLoading(button, false);
            }
        } else if (action === 'set-principal') {
            try {
                showLoading(button, true);
                const response = await fetch(`${URL_API}api/directivo/noticias/${noticiaId}/set_imagen_principal/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ imagen_principal: imageId })
                });

                if (response.ok) {
                    showAlert('Imagen principal actualizada con éxito.', 'success');
                    await fetchNoticiaData(noticiaId);
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || JSON.stringify(errorData));
                }
            } catch (error) {
                console.error('Error al establecer imagen principal:', error);
                showAlert(`Error: ${error.message}`, 'danger');
            } finally {
                showLoading(button, false);
            }
        }
    });

    // --- Manejar subida de nuevas imágenes ---
    newImagesInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        // Validar archivos
        const validFiles = Array.from(files).filter(file => {
            const isValidType = file.type.startsWith('image/');
            const isValidSize = file.size <= 5 * 1024 * 1024; // 5MB
            return isValidType && isValidSize;
        });

        if (validFiles.length === 0) {
            showAlert('Por favor, selecciona imágenes válidas (JPG, PNG, WEBP) de máximo 5MB.', 'warning');
            return;
        }

        if (validFiles.length !== files.length) {
            showAlert('Algunos archivos fueron omitidos por no ser imágenes o exceder el tamaño máximo.', 'warning');
        }

        const formData = new FormData();
        formData.append('noticia', noticiaId);
        validFiles.forEach(file => {
            formData.append('imagen', file);
        });

        try {
            showAlert('Subiendo imágenes...', 'info', 0);
            const response = await fetch(`${URL_API}api/directivo/noticias_imagenes/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                showAlert('Imágenes subidas con éxito.', 'success');
                await fetchNoticiaData(noticiaId);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || JSON.stringify(errorData));
            }
        } catch (error) {
            console.error('Error al subir imágenes:', error);
            showAlert(`Error al subir imágenes: ${error.message}`, 'danger');
        } finally {
            // Limpiar input
            newImagesInput.value = '';
            // Eliminar alerta de carga
            const loadingAlert = alertsContainer.querySelector('.alert-info');
            if (loadingAlert) loadingAlert.remove();
        }
    });

    // --- Drag and drop para imágenes ---
    const uploadSection = document.querySelector('.upload-section');
    if (uploadSection) {
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.style.borderColor = '#0d6efd';
            uploadSection.style.background = '#e9f2ff';
        });

        uploadSection.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadSection.style.borderColor = '#dee2e6';
            uploadSection.style.background = '#f8f9fa';
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.style.borderColor = '#dee2e6';
            uploadSection.style.background = '#f8f9fa';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                newImagesInput.files = files;
                newImagesInput.dispatchEvent(new Event('change'));
            }
        });
    }

    // --- Prevenir envío con Enter en inputs ---
    form.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
        }
    });
});