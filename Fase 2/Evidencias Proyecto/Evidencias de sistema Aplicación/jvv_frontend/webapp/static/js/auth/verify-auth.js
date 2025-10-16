const requiredFunctions = ['checkAuthentication', 'checkAuthSafe', 'redirectByRole', 'authFetch'];

requiredFunctions.forEach(funcName => {
});

// Función de autenticación universal
window.ensureAuth = function() {
    // Intentar todas las formas posibles
    if (typeof checkAuthentication === 'function') {
        return checkAuthentication();
    }
    
    if (typeof checkAuthSafe === 'function') {
        return checkAuthSafe();
    }
    
    // Fallback básico
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    return {
        isAuthenticated: !!token,
        user: userData ? JSON.parse(userData) : null,
        role: localStorage.getItem('user_role')
    };
};
