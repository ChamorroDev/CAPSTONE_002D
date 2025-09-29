
function globalLogout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        try {
            clearAuthData();
        } catch (e) {
            console.log('Error limpiando datos de sesión:', e);
        } finally {
            window.location.href = '/login/';
        }
    }
}

function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('user_role');
    localStorage.removeItem('junta_id');
    localStorage.removeItem('junta_nombre');
    console.log('Datos de autenticación limpiados');
}

function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    return {
        isAuthenticated: !!token,
        user: userData ? JSON.parse(userData) : null,
        role: localStorage.getItem('user_role')
    };
}

function updateUIBasedOnAuth() {
    const auth = checkAuthStatus();
    const authElements = document.querySelectorAll('[data-auth]');
    const noAuthElements = document.querySelectorAll('[data-no-auth]');
    const roleElements = document.querySelectorAll('[data-role]');

    authElements.forEach(el => {
        el.style.display = auth.isAuthenticated ? '' : 'none';
    });

    noAuthElements.forEach(el => {
        el.style.display = auth.isAuthenticated ? 'none' : '';
    });

    roleElements.forEach(el => {
        const requiredRole = el.getAttribute('data-role');
        el.style.display = (auth.role === requiredRole) ? '' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateUIBasedOnAuth();
    
    const auth = checkAuthStatus();
    if (auth.isAuthenticated && auth.user) {
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => {
            el.textContent = auth.user.nombre || auth.user.email;
        });
    }
});