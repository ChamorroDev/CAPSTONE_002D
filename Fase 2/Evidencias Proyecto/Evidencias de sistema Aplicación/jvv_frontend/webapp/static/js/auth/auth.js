/**
 * Funciones básicas de autenticación
 */

// Función de login básica
async function simpleLogin(email, password) {
    try {
        const response = await fetch(`${URL_API}api/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        return { success: response.ok, data: data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Verificación básica de autenticación
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

// Obtener datos del usuario
function getUserData() {
    try {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    } catch (error) {
        return null;
    }
}

// Obtener rol del usuario
function getUserRole() {
    return localStorage.getItem('user_role');
}

// Hacer funciones disponibles globalmente
window.simpleLogin = simpleLogin;
window.isAuthenticated = isAuthenticated;
window.getUserData = getUserData;
window.getUserRole = getUserRole;