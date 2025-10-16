
if (typeof redirectByRole === 'undefined') {
    console.warn('redirectByRole no definida, creando función de emergencia');
    window.redirectByRole = function(role) {
        console.log('Redirección de emergencia con rol:', role);
        window.location.href = '/';
    };
}

function redirectByRole(role) {
    const userRole = (role || '').toString().toLowerCase().trim();
    console.log('Redirigiendo con rol:', userRole);
    
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
            console.warn('Rol no reconocido, redirigiendo a home:', userRole);
            window.location.href = '/';
    }
}

function globalLogout() {
    if (typeof safeLogout === 'function') {
        safeLogout();
    } else {
        if (confirm('¿Está seguro que desea cerrar sesión?')) {
            localStorage.clear();
            window.location.href = '/login/';
        }
    }
}



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
            const newForm = this.form.cloneNode(true);
            this.form.parentNode.replaceChild(newForm, this.form);
            this.form = newForm;
            this.form.addEventListener('submit', (e) => this.handleLogin(e));
        }
    }

    checkExistingAuth() {
        try {
            let auth;
            if (typeof checkAuthSafe === 'function') {
                auth = checkAuthSafe();
            } else if (typeof checkAuthentication === 'function') {
                auth = checkAuthentication();
            } else {
                auth = {
                    isAuthenticated: localStorage.getItem('access_token') !== null,
                    user: null,
                    role: localStorage.getItem('user_role')
                };
            }
            
            if (auth.isAuthenticated) {
                console.log('Usuario ya autenticado, redirigiendo...');
                redirectByRole(auth.role);
            }
        } catch (error) {
            console.error('Error verificando autenticación:', error);
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        this.isSubmitting = true;

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const csrfToken = this.getCSRFToken();

        if (!email || !password) {
            this.showAlert('Por favor, complete todos los campos');
            this.isSubmitting = false;
            return;
        }

        this.setLoading(true);

        try {
            console.log('Intentando login...');
            
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
            console.log('Respuesta del servidor:', response.status, data);

            if (response.ok) {
                await this.handleLoginSuccess(data);
            } else {
                const errorMsg = data.detail || data.error || 'Error en el login';
                throw new Error(errorMsg);
            }
        } catch (error) {
            console.error('Error en login:', error);
            this.showAlert(error.message || 'Error de conexión');
        } finally {
            this.setLoading(false);
            this.isSubmitting = false;
        }
    }

    async handleLoginSuccess(loginData) {
        localStorage.setItem('access_token', loginData.access);
        localStorage.setItem('refresh_token', loginData.refresh);
        
        const userResponse = await fetch(`${URL_API}api/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${loginData.access}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (userResponse.ok) {
            const userData = await userResponse.json();
            localStorage.setItem('user_data', JSON.stringify(userData));
            localStorage.setItem('user_role', userData.rol);
            
            if (typeof safeNavbarUpdate === 'function') {
                safeNavbarUpdate();
            }
            
            this.showAlert('¡Login exitoso! Redirigiendo...', 'success');
            
            setTimeout(() => {
                redirectByRole(userData.rol);
            }, 1000);
        } else {
            throw new Error('Error obteniendo datos de usuario');
        }
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
            
            setTimeout(() => {
                if (this.alert) {
                    this.alert.classList.add('d-none');
                }
            }, 5000);
        } else {
            alert(message);
        }
    }

    getCSRFToken() {
        let csrfToken = '';
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieValue) {
            csrfToken = cookieValue;
        } else {
            const metaToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (metaToken) {
                csrfToken = metaToken.value;
            }
        }
        return csrfToken;
    }
}


document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('loginForm')) {
        console.log('Inicializando LoginManager...');
        window.loginManager = new LoginManager();
    }
});

window.redirectByRole = redirectByRole;
window.globalLogout = globalLogout;