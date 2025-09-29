const URL_API = 'http://192.168.2.100:8000/';

let userData = null;
let userRole = null;

document.addEventListener('DOMContentLoaded', function() {
    const savedUserData = localStorage.getItem('user_data');
    if (savedUserData) {
        userData = JSON.parse(savedUserData);
        userRole = localStorage.getItem('user_role');
    }
});

function globalLogout() { 
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        fetch(`${URL_API}auth/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        }).catch(error => {
            console.log('Error en logout backend:', error);
        }).finally(() => {
            clearAuthData();
            window.location.href = '/login/';
        });
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