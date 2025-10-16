// static/js/directivo/usuarios/editar.js

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Obtener el ID del usuario de la URL
    const path = window.location.pathname;
    const userId = path.split('/')[2]; 
    
    if (userId) {
        await fetchAndFillUser(userId);
    } else {
        alert('ID de usuario no encontrado en la URL.');
        window.location.href = '/usuarios-lista/';
    }

    // 2. Manejar el envío del formulario de edición
    const editUserForm = document.getElementById('editUserForm');
    editUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleUpdateUser(userId);
    });

    // 3. Manejar el botón de estado de cuenta
    const statusBtn = document.getElementById('deactivateUserBtn');
    statusBtn.addEventListener('click', async () => {
        // Obtenemos el estado actual del usuario desde el texto del botón
        const isActive = statusBtn.textContent.includes('Desactivar');
        const action = isActive ? 'desactivar' : 'activar';
        const newStatus = !isActive;

        if (confirm(`¿Estás seguro de que deseas ${action} esta cuenta?`)) {
            await handleAccountStatus(userId, newStatus);
        }
    });

    // 4. Lógica para el botón de ver documento
    const viewDocumentBtn = document.getElementById('viewDocumentBtn');
    viewDocumentBtn.addEventListener('click', () => {
        const documentoUrl = viewDocumentBtn.dataset.documentoUrl;
        if (documentoUrl) {
            window.open(documentoUrl, '_blank');
        } else {
            alert('No se encontró documentación para este usuario.');
        }
    });
});

// --- Funciones de Lógica ---
async function fetchAndFillUser(userId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/usuarios/editar/${userId}/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Usuario no encontrado o no autorizado.');
        }

        const usuario = await response.json();
        
        // Llenar el formulario con los datos del usuario
        document.getElementById('userId').value = usuario.id;
        document.getElementById('nombre').value = usuario.nombre;
        document.getElementById('apellido').value = usuario.apellido;
        document.getElementById('rut').value = usuario.rut;
        document.getElementById('email').value = usuario.email;
        document.getElementById('rol').value = usuario.rol;

        // Manejar el botón de ver documento
        const viewDocumentBtn = document.getElementById('viewDocumentBtn');
        if (usuario.documento_verificacion) {
            const documentoUrl = `${URL_API}${usuario.documento_verificacion}`;
            viewDocumentBtn.dataset.documentoUrl = documentoUrl;
            viewDocumentBtn.disabled = false;
        } else {
            viewDocumentBtn.textContent = 'Sin Documentación';
            viewDocumentBtn.classList.remove('btn-info');
            viewDocumentBtn.classList.add('btn-secondary');
        }

        // Si la cuenta está inactiva, cambiar el texto del botón
        const statusBtn = document.getElementById('deactivateUserBtn');
        if (!usuario.is_active) {
            statusBtn.textContent = 'Activar Cuenta';
            statusBtn.classList.remove('btn-danger');
            statusBtn.classList.add('btn-success');
        } else {
            statusBtn.textContent = 'Desactivar Cuenta';
            statusBtn.classList.remove('btn-success');
            statusBtn.classList.add('btn-danger');
        }

    } catch (error) {
        console.error('Error al obtener los datos del usuario:', error);
        alert(`Error: ${error.message}`);
        window.location.href = '/usuarios-lista/';
    }
}

async function handleUpdateUser(userId) {
    try {
        const token = localStorage.getItem('access_token');
        
        // 1. Recoger los datos del formulario que se pueden editar
        const nombre = document.getElementById('nombre').value;
        const apellido = document.getElementById('apellido').value;
        const rol = document.getElementById('rol').value;

        const data = {
            nombre: nombre,
            apellido: apellido,
            rol: rol
        };
        
        // 2. Enviar la petición PATCH
        const response = await fetch(`${URL_API}api/directivo/usuarios/editar/${userId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al actualizar el usuario.');
        }

        alert('Usuario actualizado correctamente.');
        window.location.href = '/usuarios-lista/';
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
}

async function handleAccountStatus(userId, newStatus) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${URL_API}api/directivo/usuarios/editar/${userId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ is_active: newStatus })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al cambiar el estado del usuario.');
        }

        const action = newStatus ? 'activada' : 'desactivada';
        alert(`Cuenta ${action} correctamente.`);
        window.location.href = '/usuarios-lista/';
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
}
