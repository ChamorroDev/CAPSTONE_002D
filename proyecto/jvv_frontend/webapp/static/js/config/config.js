// Configuración global de la aplicación
const URL_API = 'http://127.0.0.1:8000/';

// Estado de la aplicación
let appState = {
    user: null,
    isAuthenticated: false,
    userRole: null
};

// Cargar estado inicial
function loadAppState() {
    try {
        const userData = localStorage.getItem('user_data');
        if (userData) {
            appState.user = JSON.parse(userData);
            appState.userRole = localStorage.getItem('user_role');
            appState.isAuthenticated = true;
        }
    } catch (error) {
        console.error('Error loading app state:', error);
        clearAppState();
    }
}

// Limpiar estado de la aplicación
function clearAppState() {
    appState = {
        user: null,
        isAuthenticated: false,
        userRole: null
    };
    localStorage.clear();
}

// Cargar estado al iniciar
loadAppState();