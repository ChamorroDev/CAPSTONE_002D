async function login(email, password) {
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

        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            localStorage.setItem('user_role', data.user.rol);

            if (typeof safeNavbarUpdate === 'function') {
                safeNavbarUpdate();
            }

            return { success: true, data };
        } else {
            return { success: false, error: data.detail || 'Error en el login' };
        }
    } catch (error) {
        return { success: false, error: 'Error de conexión' };
    }
}

function logout() {
    if (typeof safeLogout === 'function') {
        safeLogout();
    } else {
        if (confirm('¿Está seguro que desea cerrar sesión?')) {
            localStorage.clear();
            window.location.href = "/login/";
        }
    }
}

function safeNavbarUpdate() {
    const authSection = document.getElementById('navbar-auth-section');
    const userData = localStorage.getItem('user_data');
    const userRole = localStorage.getItem('user_role');
    
    const navEventos = document.getElementById('nav-eventos-link');
    const navMiBarrio = document.getElementById('nav-mibarrio-link');
    const navPanelControl = document.getElementById('nav-panel-control-link');

    if (navEventos) navEventos.style.display = 'none';
    if (navMiBarrio) navMiBarrio.style.display = 'none';
    if (navPanelControl) navPanelControl.style.display = 'none';

    if (authSection) {
        authSection.className = 'navbar-auth-section';
        
        if (userData) {
            const user = JSON.parse(userData);
            authSection.innerHTML = `
                <span class="auth-welcome-text">
                    <a href="${miPerfilUrl}" class="auth-profile-link">
                        <i class="bi bi-person-circle me-1"></i> 
                        ${user.nombre || user.username || 'Mi Perfil'}
                    </a>
                </span>
                <button class="btn btn-outline-light btn-sm auth-logout-btn" onclick="logout()">
                    <i class="bi bi-box-arrow-right"></i> 
                    <span class="auth-btn-text">Salir</span>
                </button>
            `;
            
            if (navEventos) navEventos.style.display = 'block';
            if (navMiBarrio) navMiBarrio.style.display = 'block';
            
            if (navPanelControl && userRole === 'directivo') {
                navPanelControl.style.display = 'block';
            }
            
        } else {
            authSection.innerHTML = `
                <a class="btn btn-outline-light btn-sm auth-btn" href="/registro/">
                    <i class="bi bi-person-plus"></i> 
                    <span class="auth-btn-text">Registrarse</span>
                </a>
                <a class="btn btn-light btn-sm auth-btn" href="/login/">
                    <i class="bi bi-box-arrow-in-right"></i> 
                    <span class="auth-btn-text">Ingresar</span>
                </a>
            `;
        }
    }
}
window.safeNavbarUpdate = safeNavbarUpdate;

function safeLogout() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        localStorage.clear();
        safeNavbarUpdate();
        window.location.href = '/login/';

    }
}
window.safeLogout = safeLogout;

document.addEventListener('DOMContentLoaded', function() {
    var navbarCollapse = document.getElementById('navbarNav');
    if (navbarCollapse) {
        navbarCollapse.querySelectorAll('.nav-link').forEach(function(link) {
            link.addEventListener('click', function() {
                if (navbarCollapse.classList.contains('show')) {
                    var collapseInstance = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
                    collapseInstance.hide();
                }
            });
        });
    }
    
    safeNavbarUpdate();
});

window.addEventListener('load', function() {
    setTimeout(safeNavbarUpdate, 100);
});