// En gestion_usuarios.js

let allUsuarios = [];

// --- Funciones de Utilidad ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Lógica Principal ---
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Inicializando gestión de usuarios...');
    await fetchUsuarios();

    document.getElementById('search-input').addEventListener('input', () => {
        filterAndRender();
    });
    document.getElementById('role-filter').addEventListener('change', async () => {
        await fetchUsuarios();
    });
});

async function fetchUsuarios() {
    const tableBody = document.getElementById('usuarios-list');
    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center py-4">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="text-muted mt-2">Cargando usuarios...</p>
            </td>
        </tr>
    `;

    try {
        const token = localStorage.getItem('access_token');
        const role = document.getElementById('role-filter').value;
        
        let url = `${URL_API}api/directivo/usuarios/`;
        if (role) {
            url += `?rol=${role}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Error al obtener los usuarios.');
        }

        allUsuarios = await response.json();
        filterAndRender();
    } catch (error) {
        console.error('Error:', error);
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al cargar los usuarios.</td></tr>`;
    }
}

function filterAndRender() {
    const searchInput = document.getElementById('search-input').value.toLowerCase();
    
    const filteredUsuarios = allUsuarios.filter(usuario => {
        const matchesSearch = usuario.nombre.toLowerCase().includes(searchInput) ||
                              usuario.apellido.toLowerCase().includes(searchInput) ||
                              (usuario.rut && usuario.rut.toLowerCase().includes(searchInput));
        
        return matchesSearch;
    });

    renderUsuarios(filteredUsuarios);
}

function renderUsuarios(usuarios) {
    const tableBody = document.getElementById('usuarios-list');
    tableBody.innerHTML = ''; // Limpiar tabla

    if (usuarios.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center">No se encontraron usuarios.</td></tr>`;
        return;
    }

    usuarios.forEach(usuario => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${usuario.nombre} ${usuario.apellido}</td>
            <td>${usuario.rut}</td>
            <td>${usuario.email}</td>
            <td>${usuario.direccion || 'N/A'}</td>
            <td>
                <a href="/usuarios/${usuario.id}/editar/" class="btn btn-sm btn-primary">
                    <i class="bi bi-pencil-square"></i> Editar
                </a>
            </td>
        `;
        tableBody.appendChild(row);
    });
}