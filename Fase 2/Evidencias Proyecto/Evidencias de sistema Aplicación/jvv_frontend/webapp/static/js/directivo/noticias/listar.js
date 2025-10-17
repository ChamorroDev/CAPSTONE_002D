document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    let allNoticias = [];
    let currentPage = 1;
    const pageSize = 10;
    let filteredNoticias = [];
    
    const noticiasList = document.getElementById('noticiasList');
    const searchInput = document.getElementById('searchInput');
    const filterStatus = document.getElementById('filterStatus');

    // Función para obtener todas las noticias
    async function fetchAllNoticias() {
        try {
            const response = await fetch(`${URL_API}api/directivo/noticias/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${await response.text()}`);
            }

            allNoticias = await response.json();
            console.log('Noticias cargadas:', allNoticias.length);
            
            // Aplicar filtros iniciales
            applyFilters();
            
        } catch (error) {
            console.error('Error al cargar las noticias:', error);
            noticiasList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger py-4">
                        Error al cargar las noticias: ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    // Función para aplicar filtros
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const status = filterStatus.value;

        filteredNoticias = allNoticias.filter(noticia => {
            const matchesSearch = noticia.titulo.toLowerCase().includes(searchTerm);
            
            let matchesStatus = false;
            if (status === 'all') {
                matchesStatus = true;
            } else if (status === 'publicado' && noticia.es_publica) {
                matchesStatus = true;
            } else if (status === 'borrador' && !noticia.es_publica) {
                matchesStatus = true;
            }

            return matchesSearch && matchesStatus;
        });

        // Resetear a página 1 cuando se aplican filtros
        currentPage = 1;
        renderTable();
        renderPagination();
    }

    // Obtener noticias para la página actual
    function getNoticiasForCurrentPage() {
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return filteredNoticias.slice(startIndex, endIndex);
    }

    // Función para llenar la tabla
    function renderTable() {
        const noticiasParaMostrar = getNoticiasForCurrentPage();
        
        if (filteredNoticias.length === 0) {
            noticiasList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">
                        <i class="bi bi-inbox fs-1 text-muted"></i>
                        <p class="text-muted mt-2">No se encontraron noticias con esos criterios.</p>
                    </td>
                </tr>
            `;
            return;
        }

        if (noticiasParaMostrar.length === 0) {
            noticiasList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">
                        <i class="bi bi-exclamation-circle fs-1 text-muted"></i>
                        <p class="text-muted mt-2">No hay noticias en esta página.</p>
                    </td>
                </tr>
            `;
            return;
        }

        const html = noticiasParaMostrar.map(noticia => {
            const fecha = new Date(noticia.fecha_creacion).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
            const estadoTexto = noticia.es_publica ? 'Publicada' : 'Borrador';
            const estadoClase = noticia.es_publica ? 'bg-success' : 'bg-secondary';

            return `
                <tr>
                    <td class="align-middle">
                        <strong>${noticia.titulo}</strong>
                        ${noticia.imagen_principal_url ? '<i class="bi bi-image text-primary ms-2" title="Tiene imagen"></i>' : ''}
                    </td>
                    <td class="align-middle">
                        <span class="badge ${estadoClase}">${estadoTexto}</span>
                    </td>
                    <td class="align-middle">
                        <small class="text-muted">${fecha}</small>
                    </td>
                    <td class="align-middle">
                        <button class="btn btn-primary btn-sm me-2 editar-btn" data-id="${noticia.id}" title="Editar noticia">
                            <i class="bi bi-pencil"></i> Editar
                        </button>
                        <button class="btn btn-danger btn-sm eliminar-btn" data-id="${noticia.id}" title="Eliminar noticia">
                            <i class="bi bi-trash"></i> Eliminar
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
        noticiasList.innerHTML = html;
        
        updateCounter();
    }

    
    function renderPagination() {
        const totalPages = Math.ceil(filteredNoticias.length / pageSize);
        
        // Eliminar paginación existente
        const existingPagination = document.getElementById('paginationContainer');
        if (existingPagination) {
            existingPagination.remove();
        }

        if (totalPages <= 1) return;

        // Crear contenedor de paginación
        const paginationContainer = document.createElement('div');
        paginationContainer.id = 'paginationContainer';
        paginationContainer.className = 'd-flex flex-column flex-md-row justify-content-between align-items-center gap-3 mt-4';

        // Información de página - siempre visible
        const startItem = ((currentPage - 1) * pageSize) + 1;
        const endItem = Math.min(currentPage * pageSize, filteredNoticias.length);
        
        const pageInfo = document.createElement('div');
        pageInfo.className = 'text-muted small text-center text-md-start';
        pageInfo.innerHTML = `Mostrando <strong>${startItem}-${endItem}</strong> de <strong>${filteredNoticias.length}</strong>`;

        // Controles de paginación
        const paginationControls = document.createElement('div');
        paginationControls.className = 'd-flex align-items-center gap-2';

        // Botón anterior
        const prevButton = document.createElement('button');
        prevButton.className = `btn btn-outline-primary btn-sm ${currentPage === 1 ? 'disabled' : ''}`;
        prevButton.innerHTML = '<i class="bi bi-chevron-left"></i>';
        prevButton.disabled = currentPage === 1;
        prevButton.title = 'Página anterior';
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
                renderPagination();
            }
        });

        // Contador de página compacto
        const pageIndicator = document.createElement('span');
        pageIndicator.className = 'mx-1 text-muted small';
        pageIndicator.innerHTML = `<strong>${currentPage}</strong> / <strong>${totalPages}</strong>`;

        // Botón siguiente
        const nextButton = document.createElement('button');
        nextButton.className = `btn btn-outline-primary btn-sm ${currentPage === totalPages ? 'disabled' : ''}`;
        nextButton.innerHTML = '<i class="bi bi-chevron-right"></i>';
        nextButton.disabled = currentPage === totalPages;
        nextButton.title = 'Página siguiente';
        nextButton.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
                renderPagination();
            }
        });

        // Selector de página rápida - solo en desktop
        const pageSelectContainer = document.createElement('div');
        pageSelectContainer.className = 'd-none d-md-block ms-2';
        
        const pageSelect = document.createElement('select');
        pageSelect.className = 'form-select form-select-sm';
        pageSelect.style.width = '80px';
        pageSelect.title = 'Ir a página';
        
        for (let i = 1; i <= totalPages; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i;
            option.selected = i === currentPage;
            pageSelect.appendChild(option);
        }
        
        pageSelect.addEventListener('change', (e) => {
            currentPage = parseInt(e.target.value);
            renderTable();
            renderPagination();
        });

        pageSelectContainer.appendChild(pageSelect);

        // Ensamblar controles
        paginationControls.appendChild(prevButton);
        paginationControls.appendChild(pageIndicator);
        paginationControls.appendChild(nextButton);
        paginationControls.appendChild(pageSelectContainer);

        // Ensamblar contenedor
        paginationContainer.appendChild(pageInfo);
        paginationContainer.appendChild(paginationControls);

        // Insertar después de la tabla
        const tableContainer = noticiasList.closest('.table-responsive');
        tableContainer.parentNode.insertBefore(paginationContainer, tableContainer.nextSibling);
    }

    function updateCounter() {
        const counterElement = document.getElementById('noticiasCounter');
        if (!counterElement) return;
        
        const totalFiltradas = filteredNoticias.length;
        const totalGeneral = allNoticias.length;
        
        let counterText = `${totalFiltradas} noticias`;
        if (totalFiltradas !== totalGeneral) {
            counterText += ` (filtradas de ${totalGeneral} totales)`;
        }
        
        counterElement.textContent = counterText;
    }

    
    async function handleDelete(id) {
        if (confirm('¿Estás seguro de que deseas eliminar esta noticia?')) {
            try {
                const response = await fetch(`${URL_API}api/directivo/noticias/${id}/`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.status === 204) {
                    console.log(`Noticia con ID ${id} eliminada con éxito.`);
                    await fetchAllNoticias(); 
                } else {
                    console.error('Error al eliminar la noticia:', response.statusText);
                    alert('Hubo un error al intentar eliminar la noticia.');
                }
            } catch (error) {
                console.error('Error de red al eliminar la noticia:', error);
                alert('Hubo un error de conexión. Inténtelo de nuevo.');
            }
        }
    }

    function handleEdit(id) {
        window.location.href = `/gestion_noticias/editar/${id}`;
    }

    noticiasList.addEventListener('click', (event) => {
        if (event.target.classList.contains('eliminar-btn')) {
            const noticiaId = event.target.getAttribute('data-id');
            handleDelete(noticiaId);
        }
        if (event.target.classList.contains('editar-btn')) {
            const noticiaId = event.target.getAttribute('data-id');
            handleEdit(noticiaId);
        }
    });

    searchInput.addEventListener('input', () => {
        applyFilters();
    });
    
    filterStatus.addEventListener('change', () => {
        applyFilters();
    });

    await fetchAllNoticias();
});