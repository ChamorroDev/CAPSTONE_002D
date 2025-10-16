document.addEventListener('DOMContentLoaded', async () => {
    // URL base de la API, según las URLs que definiste
    const token = localStorage.getItem('access_token');
    let allNoticias = []; // Variable para almacenar todas las noticias
    
    const noticiasList = document.getElementById('noticiasList');
    const searchInput = document.getElementById('searchInput');
    const filterStatus = document.getElementById('filterStatus');

    // Función para obtener y mostrar las noticias
    async function fetchAndRenderNoticias() {
        try {

            const response = await fetch(`${URL_API}api/directivo/noticias/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('No se pudo obtener las noticias.');
            }

            allNoticias = await response.json();
            console.log('Noticias cargadas:', allNoticias);
            filterAndRender(); // Renderiza todas las noticias al inicio
        } catch (error) {
            console.error('Error al cargar las noticias:', error);
            noticiasList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger py-4">Error al cargar las noticias. Inténtelo de nuevo más tarde.</td>
                </tr>
            `;
        }
    }

    // Función para filtrar y renderizar las noticias
    function filterAndRender() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const status = filterStatus.value;

        const filteredNoticias = allNoticias.filter(noticia => {
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

        renderTable(filteredNoticias);
    }

    // Función para llenar la tabla
    function renderTable(noticias) {
        if (noticias.length === 0) {
            noticiasList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">No se encontraron noticias con esos criterios.</td>
                </tr>
            `;
            return;
        }

        const html = noticias.map(noticia => {
            const fecha = new Date(noticia.fecha_creacion).toLocaleDateString();
            const estadoTexto = noticia.es_publica ? 'Publicada' : 'Borrador';
            const estadoClase = noticia.es_publica ? 'bg-success' : 'bg-secondary';

            return `
                <tr>
                    <td>${noticia.titulo}</td>
                    <td><span class="badge ${estadoClase}">${estadoTexto}</span></td>
                    <td>${fecha}</td>
                    <td>
                        <button class="btn btn-primary btn-sm me-2 editar-btn" data-id="${noticia.id}">Editar</button>
                        <button class="btn btn-danger btn-sm eliminar-btn" data-id="${noticia.id}">Eliminar</button>
                    </td>
                </tr>
            `;
        }).join('');
        
        noticiasList.innerHTML = html;
    }

    // --- Funcionalidad de Botones de Acción ---
    
    // Función para manejar la eliminación de una noticia
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
                    await fetchAndRenderNoticias(); // Vuelve a cargar y renderizar la tabla
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

    // Función para manejar la edición de una noticia
    function handleEdit(id) {
        // Redirige al formulario de edición con el ID en la URL
        window.location.href = `/gestion_noticias/editar/${id}`;
    }


    // Usar delegación de eventos para los botones de acción
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

    // Agregar escuchadores de eventos a los filtros
    searchInput.addEventListener('input', filterAndRender);
    filterStatus.addEventListener('change', filterAndRender);

    // Llamar a la función principal al cargar la página
    fetchAndRenderNoticias();
});