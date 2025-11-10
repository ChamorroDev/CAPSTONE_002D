class LoginManager {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.loginBtn = document.getElementById('loginBtn');
        this.loginText = document.getElementById('loginText');
        this.loginSpinner = document.getElementById('loginSpinner');
        this.alert = document.getElementById('loginAlert');
        
        this.isSubmitting = false;
        this.init();
    }

    init() {
        this.checkExistingAuth();
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleLogin(e));
        }
    }

    checkExistingAuth() {
        try {
            const token = localStorage.getItem('access_token');
            const userRole = localStorage.getItem('user_role');
            
            if (token && userRole) {
                redirectByRole(userRole);
            }
        } catch (error) {
            console.error('Error verificando autenticación:', error);
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        this.isSubmitting = true;

        const email = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value;
        const csrfToken = this.getCSRFToken();

        if (!email || !password) {
            this.showAlert('Por favor, complete todos los campos');
            this.isSubmitting = false;
            return;
        }

        if (!this.isValidEmail(email)) {
            this.showAlert('Por favor, ingrese un correo electrónico válido');
            this.isSubmitting = false;
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch(`${URL_API}api/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                await this.handleLoginSuccess(data);
            } else {
                this.handleLoginError(response.status, data);
            }
        } catch (error) {
            this.showAlert('Error de conexión. Por favor, intente nuevamente.');
        } finally {
            this.setLoading(false);
            this.isSubmitting = false;
        }
    }

    handleLoginError(statusCode, data) {
        const errorMessage = data.error || 'Error en el inicio de sesión';
        this.showAlert(errorMessage);
        
        // Limpiar campo de contraseña en caso de error
        document.getElementById('password').value = '';
        document.getElementById('password').focus();
    }

    async handleLoginSuccess(loginData) {
        localStorage.setItem('access_token', loginData.access);
        localStorage.setItem('refresh_token', loginData.refresh);
        localStorage.setItem('user_data', JSON.stringify(loginData.user));
        localStorage.setItem('user_role', loginData.user.rol);
        
        // Actualizar navbar si existe la función
        if (typeof safeNavbarUpdate === 'function') {
            safeNavbarUpdate();
        }
        
        this.showAlert('¡Login exitoso! Redirigiendo...', 'success');
        
        setTimeout(() => {
            redirectByRole(loginData.user.rol);
        }, 1000);
    }

    setLoading(loading) {
        if (loading) {
            this.loginText.classList.add('d-none');
            this.loginSpinner.classList.remove('d-none');
            this.loginBtn.disabled = true;
        } else {
            this.loginText.classList.remove('d-none');
            this.loginSpinner.classList.add('d-none');
            this.loginBtn.disabled = false;
        }
    }

    showAlert(message, type = 'danger') {
        if (this.alert) {
            this.alert.textContent = message;
            this.alert.className = `alert alert-${type} mt-3`;
            this.alert.classList.remove('d-none');
            
            this.alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            setTimeout(() => {
                this.alert.classList.add('d-none');
            }, 5000);
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieValue) {
            return cookieValue;
        }
        
        const metaToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (metaToken) {
            return metaToken.value;
        }
        
        return '';
    }
}

// Funciones globales
function redirectByRole(role) {
    const userRole = (role || '').toString().toLowerCase().trim();
    
    switch(userRole) {
        case 'administrador':
        case 'admin':
        case 'administrator':
            window.location.href = '/admin-dashboard/';
            break;
        case 'directivo':
        case 'director':
        case 'moderator':
            window.location.href = '/directivo-dashboard/';
            break;
        case 'vecino':
        case 'user':
        case 'usuario':
            window.location.href = '/vecino-dashboard/';
            break;
        default:
            window.location.href = '/';
    }
}

function globalLogout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        localStorage.clear();
        window.location.href = '/login/';
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('loginForm')) {
        window.loginManager = new LoginManager();
    }
});

window.redirectByRole = redirectByRole;
window.globalLogout = globalLogout;