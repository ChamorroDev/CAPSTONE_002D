class PasswordRecoveryUnified {
    constructor() {
        this.currentStep = 1;
        this.userEmail = '';
        this.verificationToken = '';
        this.resendTimeout = null;
        this.countdownInterval = null;
        this.init();
    }

    init() {
        this.cacheDOMElements();
        this.setupEventListeners();
        this.showStep(1);
    }

    cacheDOMElements() {
        this.elements = {
            stepEmail: document.getElementById('step-email'),
            stepCode: document.getElementById('step-code'),
            stepPassword: document.getElementById('step-password'),
            
            email: document.getElementById('email'),
            verificationCode: document.getElementById('verification-code'),
            newPassword: document.getElementById('new-password'),
            confirmPassword: document.getElementById('confirm-password'),
            
            btnSendCode: document.getElementById('btn-send-code'),
            btnResendCode: document.getElementById('btn-resend-code'),
            btnVerifyCode: document.getElementById('btn-verify-code'),
            btnResetPassword: document.getElementById('btn-reset-password'),
            
            emailDisplay: document.getElementById('email-display'),
            countdown: document.getElementById('countdown'),
            passwordStrengthBar: document.getElementById('password-strength-bar'),
            passwordStrengthText: document.getElementById('password-strength-text'),
            passwordMatchText: document.getElementById('password-match-text')
        };
    }

    setupEventListeners() {
        this.elements.btnSendCode.addEventListener('click', () => this.sendVerificationCode());
        this.elements.email.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendVerificationCode();
        });

        this.elements.btnVerifyCode.addEventListener('click', () => this.verifyCode());
        this.elements.verificationCode.addEventListener('input', (e) => {
            if (e.target.value.length === 6) this.verifyCode();
        });
        this.elements.btnResendCode.addEventListener('click', () => this.resendCode());

        this.elements.newPassword.addEventListener('input', () => this.checkPasswordStrength());
        this.elements.confirmPassword.addEventListener('input', () => this.checkPasswordMatch());
        this.elements.btnResetPassword.addEventListener('click', (e) => {
            e.preventDefault();
            this.resetPassword();
        });

        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', (e) => this.togglePasswordVisibility(e));
        });
    }

    async sendVerificationCode() {
        const email = this.elements.email.value.trim();
        
        if (!this.validateEmail(email)) {
            this.showError('Por favor ingresa un email válido');
            return;
        }

        this.setButtonLoading(this.elements.btnSendCode, true);

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/auth/send-verification-code/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.userEmail = email;
                this.elements.emailDisplay.textContent = email;
                this.showStep(2);
                this.showSuccess('Código enviado correctamente');
            } else {
                this.showError(data.message || 'Error al enviar el código');
            }
        } catch (error) {
            this.showError('Error de conexión. Intenta nuevamente.');
        } finally {
            this.setButtonLoading(this.elements.btnSendCode, false);
        }
    }

    async verifyCode() {
        const code = this.elements.verificationCode.value.trim();
        
        if (code.length !== 6) {
            this.showError('El código debe tener 6 dígitos');
            return;
        }

        this.setButtonLoading(this.elements.btnVerifyCode, true);

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/auth/verify-code/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: this.userEmail, 
                    code: code 
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.verificationToken = data.token;
                this.showStep(3);
                this.clearCountdown();
            } else {
                this.showError(data.message || 'Código inválido');
                this.elements.verificationCode.classList.add('shake');
                setTimeout(() => this.elements.verificationCode.classList.remove('shake'), 500);
            }
        } catch (error) {
            this.showError('Error de conexión');
        } finally {
            this.setButtonLoading(this.elements.btnVerifyCode, false);
        }
    }

    async resetPassword() {
        const password = this.elements.newPassword.value;
        const confirmPassword = this.elements.confirmPassword.value;

        if (!this.validatePassword(password, confirmPassword)) {
            return;
        }

        this.setButtonLoading(this.elements.btnResetPassword, true);

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/auth/reset-password/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: this.userEmail,
                    token: this.verificationToken,
                    new_password: password,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showSuccess('Contraseña restablecida correctamente');
                setTimeout(() => {
                    window.location.href = "/login/";
                }, 2000);
            } else {
                this.showError(data.message || 'Error al restablecer la contraseña');
            }
        } catch (error) {
            this.showError('Error de conexión');
        } finally {
            this.setButtonLoading(this.elements.btnResetPassword, false);
        }
    }

    async resendCode() {
        if (this.resendTimeout) return;

        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/auth/resend-code/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: this.userEmail })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showSuccess('Código reenviado correctamente');
                this.startResendTimeout(60); 
                this.startCountdown(300); 
            } else {
                this.showError(data.message || 'Error al reenviar el código');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    showStep(stepNumber) {
        this.elements.stepEmail.classList.remove('active');
        this.elements.stepCode.classList.remove('active');
        this.elements.stepPassword.classList.remove('active');
        
        if (stepNumber === 1) {
            this.elements.stepEmail.classList.add('active');
            this.elements.email.focus();
        } else if (stepNumber === 2) {
            this.elements.stepCode.classList.add('active');
            this.elements.verificationCode.focus();
        } else if (stepNumber === 3) {
            this.elements.stepPassword.classList.add('active');
            this.elements.newPassword.focus();
        }
        
        this.currentStep = stepNumber;
    }

    startCountdown(seconds) {
        this.clearCountdown();
        
        let timeLeft = seconds;
        this.updateCountdownDisplay(timeLeft);
        
        this.countdownInterval = setInterval(() => {
            timeLeft--;
            this.updateCountdownDisplay(timeLeft);
            
            if (timeLeft <= 0) {
                this.clearCountdown();
                this.showError('El código ha expirado. Solicita uno nuevo.');
                this.elements.btnResendCode.disabled = false;
            }
        }, 1000);
    }

    updateCountdownDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        this.elements.countdown.textContent = ` (Expira en: ${minutes}:${secs.toString().padStart(2, '0')})`;
        this.elements.countdown.className = seconds < 60 ? 'countdown-warning' : 'countdown-normal';
    }

    clearCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
    }

    startResendTimeout(seconds) {
        this.elements.btnResendCode.disabled = true;
        let timeLeft = seconds;
        
        this.resendTimeout = setInterval(() => {
            timeLeft--;
            this.elements.btnResendCode.textContent = `Reenviar (${timeLeft}s)`;
            
            if (timeLeft <= 0) {
                clearInterval(this.resendTimeout);
                this.resendTimeout = null;
                this.elements.btnResendCode.disabled = false;
                this.elements.btnResendCode.textContent = 'Reenviar';
            }
        }, 1000);
    }

    checkPasswordStrength() {
        const password = this.elements.newPassword.value;
        const strength = this.calculatePasswordStrength(password);
        
        this.elements.passwordStrengthBar.style.width = strength.percentage + '%';
        this.elements.passwordStrengthBar.className = `progress-bar ${strength.class}`;
        this.elements.passwordStrengthText.textContent = strength.text;
    }

    calculatePasswordStrength(password) {
        let score = 0;
        
        if (password.length >= 8) score += 25;
        if (/[A-Z]/.test(password)) score += 25;
        if (/[0-9]/.test(password)) score += 25;
        if (/[^A-Za-z0-9]/.test(password)) score += 25;
        
        if (score >= 75) return { percentage: 100, class: 'password-very-strong', text: 'Muy segura' };
        if (score >= 50) return { percentage: 75, class: 'password-strong', text: 'Segura' };
        if (score >= 25) return { percentage: 50, class: 'password-medium', text: 'Media' };
        return { percentage: 25, class: 'password-weak', text: 'Débil' };
    }

    checkPasswordMatch() {
        const password = this.elements.newPassword.value;
        const confirm = this.elements.confirmPassword.value;
        
        if (confirm === '') {
            this.elements.passwordMatchText.textContent = '';
            return;
        }
        
        if (password === confirm) {
            this.elements.passwordMatchText.textContent = '✓ Las contraseñas coinciden';
            this.elements.passwordMatchText.className = 'form-text password-match';
        } else {
            this.elements.passwordMatchText.textContent = '✗ Las contraseñas no coinciden';
            this.elements.passwordMatchText.className = 'form-text password-mismatch';
        }
    }

    validatePassword(password, confirmPassword) {
        if (password.length < 8) {
            this.showError('La contraseña debe tener al menos 8 caracteres');
            return false;
        }
        
        if (password !== confirmPassword) {
            this.showError('Las contraseñas no coinciden');
            return false;
        }
        
        return true;
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    togglePasswordVisibility(e) {
        const button = e.target.closest('.toggle-password');
        const targetId = button.dataset.target;
        const input = document.getElementById(targetId);
        const icon = button.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    }

    setButtonLoading(button, isLoading) {
        const originalText = button.innerHTML;
        
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Procesando...';
        } else {
            button.disabled = false;
            if (button.id === 'btn-send-code') {
                button.innerHTML = '<i class="bi bi-send me-2"></i>Enviar código de verificación';
            } else if (button.id === 'btn-verify-code') {
                button.innerHTML = '<i class="bi bi-check-circle me-2"></i>Verificar código';
            } else if (button.id === 'btn-reset-password') {
                button.innerHTML = '<i class="bi bi-check-lg me-2"></i>Restablecer contraseña';
            }
        }
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showToast(message, type) {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        const toastId = 'toast-' + Date.now();
        const bgColor = type === 'error' ? 'danger' : 'success';
        const icon = type === 'error' ? 'bi-exclamation-triangle' : 'bi-check-circle';
        
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${bgColor} border-0" id="${toastId}">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${icon} me-2"></i>${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.innerHTML += toastHTML;
        const toast = new bootstrap.Toast(document.getElementById(toastId));
        toast.show();
        
        document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    }

    async checkResetStatus() {
        try {
            const response = await fetch(`${window.URL_API || 'http://127.0.0.1:8000/'}api/auth/check-reset-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: this.userEmail })
            });

            const data = await response.json();
            
            if (data.success && data.status === 'active') {
                if (data.verified) {
                    this.showStep(3);
                } else {
                    this.showStep(2);
                    this.startCountdown(300 - data.attempts * 60); // Ajustar countdown
                }
            }
        } catch (error) {
            console.log('No se pudo verificar el estado');
        }
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
        return container;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('recoveryForm')) {
        new PasswordRecoveryUnified();
    }
});