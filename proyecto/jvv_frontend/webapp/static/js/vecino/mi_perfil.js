class MiPerfil {
    constructor() {
        this.usuario = null;
        this.domElements = {};
        this.init();
    }

    async init() {
        console.log('Inicializando MiPerfil...');
        
        // Primero cachear los elementos del DOM
        this.cacheDOMElements();
        
        if (!this.isAuthenticated()) {
            this.showError('Debe iniciar sesión para acceder al perfil');
            setTimeout(() => window.location.href = '/login/', 2000);
            return;
        }

        try {
            await this.loadPerfilData();
            this.setupEventListeners();
        } catch (error) {
            console.error('Error en perfil:', error);
            this.showError('Error al cargar el perfil: ' + error.message);
        }
    }

    cacheDOMElements() {
        // Cachear todos los elementos del DOM que vamos a usar
        this.domElements = {
            // Estados
            loadingSpinner: document.getElementById('loading-spinner'),
            authError: document.getElementById('auth-error'),
            perfilData: document.getElementById('perfil-data'),
            errorMessage: document.getElementById('error-message'),
            
            // Información básica
            profileName: document.getElementById('profile-name'),
            profileEmail: document.getElementById('profile-email'),
            memberSince: document.getElementById('member-since'),
            
            // Información de contacto
            infoNombreCompleto: document.getElementById('info-nombre-completo'),
            infoEmailDetalle: document.getElementById('info-email-detalle'),
            infoTelefono: document.getElementById('info-telefono'),
            infoDireccion: document.getElementById('info-direccion'),
            
            // Información de cuenta
            infoUsername: document.getElementById('info-username'),
            infoFechaRegistro: document.getElementById('info-fecha-registro'),
            infoUltimoAcceso: document.getElementById('info-ultimo-acceso'),
            
            // Botones
            btnEditarPerfil: document.getElementById('btn-editar-perfil'),
            btnEditarContacto: document.getElementById('btn-editar-contacto'),
            btnCambiarPassword: document.getElementById('btn-cambiar-password'),
            btnGuardarPerfil: document.getElementById('btn-guardar-perfil'),
            btnGuardarPassword: document.getElementById('btn-guardar-password'),
            
            // Formularios
            formEditarPerfil: document.getElementById('formEditarPerfil'),
            formCambiarPassword: document.getElementById('formCambiarPassword')
        };
        
        console.log('Elementos cacheados:', this.domElements);
    }

    isAuthenticated() {
        const token = localStorage.getItem('access_token');
        return !!token;
    }

    async loadPerfilData() {
        console.log('Cargando datos del perfil...');
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('No hay token de acceso');
        }

        try {
            // Primero intentar cargar del endpoint específico de perfil
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/vecino/obtener-perfil/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.usuario = data.perfil;
                    this.renderPerfil(this.usuario);
                } else {
                    throw new Error(data.message || 'Error al cargar el perfil');
                }
            } else {
                throw new Error(`Error del servidor: ${response.status}`);
            }
        } catch (error) {
            console.error('Error cargando perfil específico:', error);
            // Fallback: intentar cargar del dashboard
            await this.loadPerfilFromDashboard();
        }
    }

    async loadPerfilFromDashboard() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/vecino/dashboard/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.usuario = data.usuario;
                this.renderPerfil(this.usuario);
            } else {
                await this.loadBasicUserData();
            }
        } catch (error) {
            console.error('Error cargando del dashboard:', error);
            await this.loadBasicUserData();
        }
    }

    async loadBasicUserData() {
        const token = localStorage.getItem('access_token');
        const userData = localStorage.getItem('user_data');
        
        if (userData) {
            try {
                this.usuario = JSON.parse(userData);
                this.renderPerfil(this.usuario);
            } catch (e) {
                this.usuario = this.createDefaultUserData();
                this.renderPerfil(this.usuario);
            }
        } else {
            this.usuario = this.createDefaultUserData();
            this.renderPerfil(this.usuario);
        }
    }

    createDefaultUserData() {
        return {
            nombre: 'Usuario',
            apellido: '',
            email: 'usuario@ejemplo.com',
            telefono: '',
            direccion: '',
            date_joined: new Date().toISOString(),
            nombre_completo: 'Usuario'
        };
    }

    renderPerfil(usuario) {
        // Ocultar loading y mostrar datos
        if (this.domElements.loadingSpinner) {
            this.domElements.loadingSpinner.classList.add('d-none');
        }
        if (this.domElements.perfilData) {
            this.domElements.perfilData.classList.remove('d-none');
        }

        // Función segura para actualizar elementos
        const safeUpdate = (element, value, defaultValue = 'No especificado') => {
            if (element) {
                element.textContent = value || defaultValue;
            }
        };

        // Actualizar información básica
        const nombreCompleto = usuario.nombre_completo || 
                              `${usuario.nombre || ''} ${usuario.apellido || ''}`.trim() || 
                              'Usuario';
        
        safeUpdate(this.domElements.profileName, nombreCompleto);
        safeUpdate(this.domElements.profileEmail, usuario.email);
        
        // Fecha de miembro
        const fechaRegistro = usuario.fecha_registro || usuario.date_joined;
        const fechaRegistroObj = fechaRegistro ? new Date(fechaRegistro) : new Date();
        safeUpdate(this.domElements.memberSince, fechaRegistroObj.toLocaleDateString('es-ES'));

        // Información de contacto
        safeUpdate(this.domElements.infoNombreCompleto, nombreCompleto);
        safeUpdate(this.domElements.infoEmailDetalle, usuario.email);
        safeUpdate(this.domElements.infoTelefono, usuario.telefono);
        safeUpdate(this.domElements.infoDireccion, usuario.direccion);

        // Información de cuenta
        safeUpdate(this.domElements.infoUsername, usuario.email || usuario.username);
        safeUpdate(this.domElements.infoFechaRegistro, fechaRegistroObj.toLocaleDateString('es-ES'));
        
        const ultimoAcceso = usuario.last_login ? 
            new Date(usuario.last_login).toLocaleString('es-ES') : 'Nunca';
        safeUpdate(this.domElements.infoUltimoAcceso, ultimoAcceso);
    }

    setupEventListeners() {
        // Botón editar perfil
        this.setupPasswordToggle();
        if (this.domElements.btnEditarPerfil) {
            this.domElements.btnEditarPerfil.addEventListener('click', () => {
                this.mostrarModalEditarPerfil();
            });
        }

        // Botón editar contacto
        if (this.domElements.btnEditarContacto) {
            this.domElements.btnEditarContacto.addEventListener('click', () => {
                this.mostrarModalEditarPerfil();
            });
        }

        // Botón cambiar contraseña
        if (this.domElements.btnCambiarPassword) {
            this.domElements.btnCambiarPassword.addEventListener('click', () => {
                this.mostrarModalCambiarPassword();
            });
        }

        // Guardar perfil
        if (this.domElements.btnGuardarPerfil) {
            this.domElements.btnGuardarPerfil.addEventListener('click', () => {
                this.guardarPerfil();
            });
        }

        // Guardar contraseña
        if (this.domElements.btnGuardarPassword) {
            this.domElements.btnGuardarPassword.addEventListener('click', () => {
                this.cambiarPassword();
            });
        }
    }

    setupPasswordToggle() {
        // Agregar event listeners para los botones de mostrar/ocultar contraseña
        document.querySelectorAll('.toggle-password').forEach(button => {
            button.addEventListener('click', (e) => {
                const targetId = e.target.closest('.toggle-password').dataset.target;
                const passwordInput = document.getElementById(targetId);
                const icon = e.target.closest('.toggle-password').querySelector('i');
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.remove('bi-eye');
                    icon.classList.add('bi-eye-slash');
                    e.target.closest('.toggle-password').classList.add('active');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.remove('bi-eye-slash');
                    icon.classList.add('bi-eye');
                    e.target.closest('.toggle-password').classList.remove('active');
                }
            });
        });
    }


    mostrarModalEditarPerfil() {
        if (!this.usuario) return;

        // Llenar el formulario con datos actuales
        if (this.domElements.formEditarPerfil) {
            const form = this.domElements.formEditarPerfil;
            const nombreInput = form.querySelector('[name="first_name"]');
            const apellidoInput = form.querySelector('[name="last_name"]');
            const emailInput = form.querySelector('[name="email"]');
            const telefonoInput = form.querySelector('[name="telefono"]');
            const direccionInput = form.querySelector('[name="direccion"]');
            
            if (nombreInput) nombreInput.value = this.usuario.nombre || '';
            if (apellidoInput) apellidoInput.value = this.usuario.apellido || '';
            if (emailInput) emailInput.value = this.usuario.email || '';
            if (telefonoInput) telefonoInput.value = this.usuario.telefono || '';
            if (direccionInput) direccionInput.value = this.usuario.direccion || '';
        }

        const modalElement = document.getElementById('modalEditarPerfil');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    mostrarModalCambiarPassword() {
        const modalElement = document.getElementById('modalCambiarPassword');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    async guardarPerfil() {
        if (!this.domElements.formEditarPerfil) return;
        
        const form = this.domElements.formEditarPerfil;
        const formData = new FormData(form);
        
        const datos = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email'),
            telefono: formData.get('telefono'),
            direccion: formData.get('direccion')
        };

        // Validaciones básicas
        if (!datos.first_name || !datos.last_name || !datos.email) {
            this.mostrarMensaje('error', 'Por favor complete todos los campos obligatorios');
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/vecino/actualizar-perfil/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datos)
            });

            const responseData = await response.json();

            if (response.ok && responseData.success) {
                this.mostrarMensaje('success', 'Perfil actualizado correctamente');
                
                // Actualizar datos locales
                this.usuario = { ...this.usuario, ...responseData.usuario };
                this.renderPerfil(this.usuario);
                
                // Cerrar modal
                const modalElement = document.getElementById('modalEditarPerfil');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();
                }
            } else {
                this.mostrarMensaje('error', responseData.message || 'Error al actualizar el perfil');
            }
        } catch (error) {
            this.mostrarMensaje('error', 'Error de conexión al actualizar el perfil');
        }
    }

    async cambiarPassword() {
        if (!this.domElements.formCambiarPassword) return;
        
        const form = this.domElements.formCambiarPassword;
        const formData = new FormData(form);
        
        const datos = {
            old_password: formData.get('old_password'),
            new_password1: formData.get('new_password1'),
            new_password2: formData.get('new_password2')
        };

        if (!datos.old_password || !datos.new_password1 || !datos.new_password2) {
            this.mostrarMensaje('error', 'Por favor complete todos los campos');
            return;
        }

        if (datos.new_password1 !== datos.new_password2) {
            this.mostrarMensaje('error', 'Las contraseñas nuevas no coinciden');
            return;
        }

        if (datos.new_password1.length < 8) {
            this.mostrarMensaje('error', 'La contraseña debe tener al menos 8 caracteres');
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/vecino/cambiar-password/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datos)
            });

            const responseData = await response.json();

            if (response.ok && responseData.success) {
                this.mostrarMensaje('success', 'Contraseña cambiada correctamente');
                
                // Limpiar formulario y cerrar modal
                form.reset();
                const modalElement = document.getElementById('modalCambiarPassword');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();
                }
            } else {
                this.mostrarMensaje('error', responseData.message || 'Error al cambiar la contraseña');
            }
        } catch (error) {
            this.mostrarMensaje('error', 'Error de conexión al cambiar la contraseña');
        }
    }

    mostrarMensaje(tipo, mensaje) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            this.mostrarToast(mensaje, tipo);
        } else {
            alert(`${tipo.toUpperCase()}: ${mensaje}`);
        }
    }

    mostrarToast(mensaje, tipo = 'success') {
        const toastContainer = document.getElementById('toast-container') || this.crearToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${tipo} border-0" id="${toastId}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${mensaje}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.innerHTML += toastHTML;
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    crearToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
        return container;
    }

    showError(mensaje) {
        if (this.domElements.loadingSpinner) {
            this.domElements.loadingSpinner.classList.add('d-none');
        }
        if (this.domElements.authError) {
            this.domElements.authError.classList.remove('d-none');
        }
        if (this.domElements.errorMessage) {
            this.domElements.errorMessage.textContent = mensaje;
        }
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('perfil-content')) {
        new MiPerfil();
    }
});