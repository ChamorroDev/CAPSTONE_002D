const Notifications = (function() {
    let modalEl, modalInstance, toastEl, toastInstance;

    function init() {
        modalEl = document.getElementById('appModal');
        toastEl = document.getElementById('appToast');

        if (modalEl && window.bootstrap) {
            modalInstance = new bootstrap.Modal(modalEl, { backdrop: 'static' });
        }
        if (toastEl && window.bootstrap) {
            toastInstance = new bootstrap.Toast(toastEl, { delay: 4000 });
        }
    }

    function showModal(title, htmlMessage, options = {}) {
        if (!modalEl) return;
        document.getElementById('appModalTitle').textContent = title || 'Aviso';
        document.getElementById('appModalBody').innerHTML = htmlMessage || '';
        const oldBtn = document.getElementById('appModalConfirmBtn');
        const newBtn = oldBtn.cloneNode(true);
        oldBtn.replaceWith(newBtn);

        if (typeof options.onConfirm === 'function') {
            newBtn.style.display = '';
            newBtn.addEventListener('click', () => {
                options.onConfirm();
                if (!options.keepOpen) modalInstance.hide();
            });
        } else {
            newBtn.style.display = 'none';
        }

        modalInstance.show();
    }

    function showToast(title, message, type = 'info') {
        if (!toastEl) return;
        const titleEl = document.getElementById('appToastTitle');
        const bodyEl = document.getElementById('appToastBody');
        const timeEl = document.getElementById('appToastTime');

        titleEl.textContent = title || (type === 'success' ? 'Éxito' : 'Aviso');
        bodyEl.innerHTML = message || '';
        timeEl.textContent = new Date().toLocaleTimeString();

        toastEl.classList.remove('border-success','border-danger','border-warning','border-info');
        if (type === 'success') toastEl.classList.add('border-success');
        if (type === 'danger') toastEl.classList.add('border-danger');
        if (type === 'warning') toastEl.classList.add('border-warning');
        if (type === 'info') toastEl.classList.add('border-info');

        toastInstance.show();
    }

    function showErrors(title, errors) {
        let html = '<ul class="mb-0">';
        if (typeof errors === 'string') {
            html += `<li>${escapeHtml(errors)}</li>`;
        } else if (Array.isArray(errors)) {
            errors.forEach(e => html += `<li>${escapeHtml(e)}</li>`);
        } else if (typeof errors === 'object') {
            for (const k in errors) {
                const v = errors[k];
                if (Array.isArray(v)) {
                    v.forEach(msg => html += `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(msg)}</li>`);
                } else {
                    html += `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(v)}</li>`;
                }
            }
        }
        html += '</ul>';
        showModal(title || 'Errores', html);
    }

    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return String(unsafe).replace(/[&<"'>]/g, m =>
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]
        );
    }

    return {
        init,
        showModal,
        showToast,
        showErrors
    };
})();

document.addEventListener('DOMContentLoaded', Notifications.init);