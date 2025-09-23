class VecinoDashboard {
    constructor() {
        this.init();
    }

    async init() {
        console.log('Inicializando VecinoDashboard...');
        
        if (!this.isAuthenticated()) {
            this.showError('Debe iniciar sesión para acceder al dashboard');
            setTimeout(() => window.location.href = '/login/', 2000);
            return;
        }

        try {
            await this.loadDashboardData();
        } catch (error) {
            console.error('Error en dashboard:', error);
            this.showError('Error al cargar el dashboard: ' + error.message);
        }
    }

    isAuthenticated() {
        if (typeof checkAuthentication === 'function') {
            const auth = checkAuthentication();
            return auth.isAuthenticated;
        }
        
        if (typeof checkAuthSafe === 'function') {
            const auth = checkAuthSafe();
            return auth.isAuthenticated;
        }
        
        const token = localStorage.getItem('access_token');
        return !!token;
    }

    async loadDashboardData() {
        console.log('Cargando datos del dashboard...');
        
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('No hay token de acceso');
        }

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/vecino/dashboard/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('Response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Datos recibidos:', data);
                this.renderDashboard(data);
            } else if (response.status === 401) {
                throw new Error('Token inválido o expirado. Por favor inicie sesión nuevamente.');
            } else if (response.status === 403) {
                throw new Error('No tiene permisos para acceder al dashboard de vecino.');
            } else {
                throw new Error('Error del servidor: ' + response.status);
            }
        } catch (error) {
            console.error('Error en loadDashboardData:', error);
            throw error;
        }
    }

    renderDashboard(data) {
        document.getElementById('loading-spinner').classList.add('d-none');
        document.getElementById('dashboard-data').classList.remove('d-none');

        this.updateUserInfo(data.usuario);
        this.updateStats(data.estadisticas);
        this.renderNoticias(data.noticias_recientes);
        this.renderActividades(data.proximas_actividades);
    }

    updateUserInfo(usuario) {
        if (!usuario) return;
        
        document.getElementById('user-name').textContent = usuario.nombre || 'Vecino';
        document.getElementById('junta-nombre').textContent = usuario.junta_vecinos || 'Junta de Vecinos';
        
        document.getElementById('info-nombre').textContent = `${usuario.nombre || ''} ${usuario.apellido || ''}`.trim() || 'No especificado';
        document.getElementById('info-email').textContent = usuario.email || 'No especificado';
        document.getElementById('info-telefono').textContent = usuario.telefono || 'No especificado';
        document.getElementById('info-direccion').textContent = usuario.direccion || 'No especificado';
    }

    updateStats(estadisticas) {
        if (!estadisticas) return;
        
        // Estadísticas generales
        document.getElementById('stats-totales').textContent = estadisticas.solicitudes_totales || 0;
        document.getElementById('stats-pendientes').textContent = estadisticas.solicitudes_pendientes_totales || 0;
        
        // Total de aprobados
        const totalAprobados = (estadisticas.certificados_aprobados || 0) + 
                              (estadisticas.espacios_aprobados || 0) + 
                              (estadisticas.proyectos_aprobados || 0);
        document.getElementById('stats-aprobadas').textContent = totalAprobados;
    }

    renderNoticias(noticias) {
        const container = document.getElementById('noticias-container');
        if (!container) return;
        
        // Limitar a solo 5 noticias
        const noticiasLimitadas = noticias ? noticias.slice(0, 5) : [];
        
        if (noticiasLimitadas.length === 0) {
            container.innerHTML = `
                <div class="content-container">
                    <div class="empty-state">
                        <i class="bi bi-newspaper"></i>
                        <p>No hay noticias recientes</p>
                    </div>
                </div>
            `;
            return;
        }

        const noticiasHTML = noticiasLimitadas.map(noticia => {
            // Validar y sanitizar los datos
            const titulo = this.safeString(noticia.titulo, 'Sin título');
            const fecha = noticia.fecha_publicacion ? new Date(noticia.fecha_publicacion).toLocaleDateString('es-ES') : 'Fecha no disponible';
            const contenido = this.safeString(noticia.contenido, '').substring(0, 100);
            const autor = this.safeString(noticia.autor, 'Administración');
            
            return `
                <div class="news-item">
                    <div class="news-title">${titulo}</div>
                    <div class="news-date">
                        <i class="bi bi-calendar"></i> ${fecha}
                    </div>
                    <div class="news-excerpt">
                        ${contenido}${noticia.contenido && noticia.contenido.length > 100 ? '...' : ''}
                    </div>
                    <div class="news-meta">
                        <span><i class="bi bi-person"></i> ${autor}</span>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="content-container">
                ${noticiasHTML}
            </div>
        `;
    }

    renderActividades(actividades) {
        const container = document.getElementById('actividades-container');
        if (!container) return;
        
        // Limitar a solo 5 actividades
        const actividadesLimitadas = actividades ? actividades.slice(0, 5) : [];
        
        if (actividadesLimitadas.length === 0) {
            container.innerHTML = `
                <div class="content-container">
                    <div class="empty-state">
                        <i class="bi bi-calendar-x"></i>
                        <p>No hay actividades próximas</p>
                    </div>
                </div>
            `;
            return;
        }

        const actividadesHTML = actividadesLimitadas.map(actividad => {
            // Validar y sanitizar los datos
            const titulo = this.safeString(actividad.titulo, 'Actividad');
            const fechaEvento = actividad.fecha ? new Date(actividad.fecha) : null;
            const esHoy = fechaEvento && new Date().toDateString() === fechaEvento.toDateString();
            const fechaTexto = fechaEvento ? 
                `${fechaEvento.toLocaleDateString('es-ES')} a las ${fechaEvento.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                })}` : 
                'Fecha no disponible';
            const descripcion = this.safeString(actividad.descripcion, '').substring(0, 80);
            const lugar = this.safeString(actividad.lugar, 'Por confirmar');
            const inscritos = actividad.inscritos || 0;
            
            return `
                <div class="activity-item">
                    <div class="activity-title">
                        ${titulo}
                        ${esHoy ? '<span class="badge bg-warning ms-2">Hoy</span>' : ''}
                    </div>
                    <div class="activity-date">
                        <i class="bi bi-clock"></i> ${fechaTexto}
                    </div>
                    <div class="activity-description">
                        ${descripcion}${actividad.descripcion && actividad.descripcion.length > 80 ? '...' : ''}
                    </div>
                    <div class="activity-meta">
                        <span><i class="bi bi-geo-alt"></i> ${lugar}</span>
                        <span><i class="bi bi-people"></i> ${inscritos} inscritos</span>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="content-container">
                ${actividadesHTML}
            </div>
        `;
    }

    // Función segura para manejar strings
    safeString(value, defaultValue = '') {
        if (value === null || value === undefined || typeof value !== 'string') {
            return defaultValue;
        }
        return this.escapeHtml(value);
    }

    // Función escapeHtml mejorada
    escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) {
            return '';
        }
        
        // Convertir a string si no lo es
        const safeString = String(unsafe);
        
        return safeString.replace(/[&<"'>]/g, m => 
            ({ 
                '&': '&amp;', 
                '<': '&lt;', 
                '>': '&gt;', 
                '"': '&quot;', 
                "'": '&#039;' 
            })[m]
        );
    }

    showError(message) {
        console.error('Mostrando error:', message);
        
        document.getElementById('loading-spinner').classList.add('d-none');
        const errorDiv = document.getElementById('auth-error');
        
        if (errorDiv) {
            errorDiv.classList.remove('d-none');
            const messageElement = errorDiv.querySelector('#error-message');
            if (messageElement) {
                messageElement.textContent = message;
            }
        }
    }
}

// Función de verificación de autenticación
function verifyAuth() {
    if (typeof checkAuthentication === 'function') {
        return checkAuthentication();
    }
    
    if (typeof checkAuthSafe === 'function') {
        return checkAuthSafe();
    }
    
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    const userRole = localStorage.getItem('user_role');
    
    return {
        isAuthenticated: !!token,
        user: userData ? JSON.parse(userData) : null,
        role: userRole
    };
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado - Verificando autenticación...');
    
    const auth = verifyAuth();
    if (!auth.isAuthenticated) {
        console.log('Usuario no autenticado, redirigiendo...');
        window.location.href = '/login/';
        return;
    }
    
    if (auth.role && auth.role !== 'vecino' && auth.role !== 'directivo') {
        console.log('Usuario no es válido, redirigiendo...');
        if (typeof redirectByRole === 'function') {
            redirectByRole(auth.role);
        } else {
            window.location.href = '/';
        }
        return;
    }
    
    if (document.getElementById('dashboard-content')) {
        console.log('Inicializando dashboard...');
        new VecinoDashboard();
    }
});