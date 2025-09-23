/**
 * Funciones globales para manejo de autenticación y logout
 */

// Función global para logout
function globalLogout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        // Opcional: Hacer logout también en el backend
        fetch(`${URL_API}auth/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        }).catch(error => {
            console.log('Error en logout backend:', error);
        }).finally(() => {
            // Siempre limpiar el frontend
            clearAuthData();
            console.log('asdasdasdasdas en logout backend:', error);

            window.location.href = '';
        });
    }
}

// Limpiar todos los datos de autenticación
function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('user_role');
    localStorage.removeItem('junta_id');
    localStorage.removeItem('junta_nombre');
    console.log('Datos de autenticación limpiados');
}

// Verificar estado de autenticación
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    return {
        isAuthenticated: !!token,
        user: userData ? JSON.parse(userData) : null,
        role: localStorage.getItem('user_role')
    };
}

// Mostrar/ocultar elementos basado en autenticación
function updateUIBasedOnAuth() {
    const auth = checkAuthStatus();
    const authElements = document.querySelectorAll('[data-auth]');
    const noAuthElements = document.querySelectorAll('[data-no-auth]');
    const roleElements = document.querySelectorAll('[data-role]');

    // Elementos que requieren autenticación
    authElements.forEach(el => {
        el.style.display = auth.isAuthenticated ? '' : 'none';
    });

    // Elementos que requieren NO autenticación
    noAuthElements.forEach(el => {
        el.style.display = auth.isAuthenticated ? 'none' : '';
    });

    // Elementos basados en rol
    roleElements.forEach(el => {
        const requiredRole = el.getAttribute('data-role');
        el.style.display = (auth.role === requiredRole) ? '' : 'none';
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    updateUIBasedOnAuth();
    
    // Actualizar nombre de usuario en el navbar si existe
    const auth = checkAuthStatus();
    if (auth.isAuthenticated && auth.user) {
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => {
            el.textContent = auth.user.nombre || auth.user.email;
        });
    }
});