// работа с cookies
function setCookie(name, value, days = 7) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name) {
    const matches = document.cookie.match(new RegExp(
        `(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1')}=([^;]*)`
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function delCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

// проверка авторизации
function isAuthenticated() {
    return !!getCookie('access_token');
}

function updateAuthUI() {
    const authBtn = document.getElementById('authBtn');
    const userStatus = document.getElementById('userStatus');
    
    if (isAuthenticated()) {
        authBtn.textContent = 'Выход';
        authBtn.href = '#';
        authBtn.onclick = (e) => { e.preventDefault(); logout(); };
        userStatus.textContent = 'Вы вошли как администратор';
    } else {
        authBtn.textContent = 'Вход';
        authBtn.href = '/login';
        authBtn.onclick = null;
        userStatus.textContent = '';
    }
}

// вход/выход
async function login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }
        
        const data = await response.json();
        setCookie('access_token', data.access_token);
        updateAuthUI();
        return { success: true };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

function logout() {
    delCookie('access_token');
    updateAuthUI();
    window.location.href = '/';
}

// функция для запросов к API 
async function apiRequest(url, options = {}) {
    const token = getCookie('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401 && token) {
        // Токен истёк — выходим
        logout();
        throw new Error('Сессия истекла, выполните вход повторно');
    }
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Ошибка ${response.status}`);
    }
    
    return response.json();
}

// инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
});