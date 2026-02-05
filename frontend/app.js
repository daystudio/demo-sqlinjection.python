const API_BASE_URL = 'http://localhost:5001/api';
const SESSION_STORAGE_KEY = 'sqlinjection_session';

let currentUser = null;

// Check for existing session on page load
window.addEventListener('DOMContentLoaded', async () => {
    await checkSession();
});

async function checkSession() {
    // First check localStorage as fallback (works even if cookies don't)
    const storedSession = localStorage.getItem(SESSION_STORAGE_KEY);
    if (storedSession) {
        try {
            const sessionData = JSON.parse(storedSession);
            currentUser = {
                id: sessionData.user_id || 0,
                username: sessionData.username,
                original_username: sessionData.original_username,
                is_admin_user: sessionData.is_admin
            };
            
            // Try to verify with server, but don't fail if it doesn't work
            try {
                const response = await fetch(`${API_BASE_URL}/session`, {
                    method: 'GET',
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.success && data.session) {
                    // Server session exists, use server data and update localStorage
                    currentUser = {
                        id: data.session.user_id,
                        username: data.session.username,
                        original_username: data.session.original_username,
                        is_admin_user: data.session.is_admin
                    };
                    
                    // Update localStorage with fresh data
                    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
                        session_id: data.session.session_id,
                        username: data.session.username,
                        original_username: data.session.original_username,
                        is_admin: data.session.is_admin,
                        user_id: data.session.user_id
                    }));
                }
            } catch (serverError) {
                // Server check failed, but we have localStorage, so continue
                console.log('Server session check failed, using localStorage:', serverError);
            }
            
            // Show appropriate panel based on admin status
            if (currentUser.is_admin_user) {
                showAdminPanel();
                loadComputers();
            } else {
                showNoPrivilegePage();
            }
            return;
        } catch (error) {
            // If localStorage parse fails, clear it and continue to server check
            console.error('Failed to parse localStorage session:', error);
            localStorage.removeItem(SESSION_STORAGE_KEY);
        }
    }
    
    // Check server session (if no localStorage)
    try {
        const response = await fetch(`${API_BASE_URL}/session`, {
            method: 'GET',
            credentials: 'include' // Include cookies for session
        });
        
        const data = await response.json();
        
        if (data.success && data.session) {
            // Restore user from session
            currentUser = {
                id: data.session.user_id,
                username: data.session.username,
                original_username: data.session.original_username,
                is_admin_user: data.session.is_admin
            };
            
            // Update localStorage as backup
            localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
                session_id: data.session.session_id,
                username: data.session.username,
                original_username: data.session.original_username,
                is_admin: data.session.is_admin,
                user_id: data.session.user_id
            }));
            
            // Show appropriate panel based on admin status
            if (data.session.is_admin) {
                showAdminPanel();
                loadComputers();
            } else {
                showNoPrivilegePage();
            }
        } else {
            // No session, show login page
            showLoginBox();
        }
    } catch (error) {
        // If session check fails, show login page
        console.error('Session check failed:', error);
        showLoginBox();
    }
}

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Store the ORIGINAL username input BEFORE sending to API
    // This is what we'll check, not the database result
    const originalUsername = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Include cookies for session
            body: JSON.stringify({ username: originalUsername, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            // Store the original username for later use
            currentUser.original_username = originalUsername;
            
            // Store session info in localStorage as backup
            if (data.session_id) {
                localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
                    session_id: data.session_id,
                    username: data.user.username,
                    original_username: originalUsername,
                    is_admin: data.user.is_admin_user,
                    user_id: data.user.id
                }));
            }
            
            // Check the ORIGINAL username input (not the database result)
            // This prevents SQL injection from bypassing the check
            if (originalUsername && originalUsername.toLowerCase() === 'admin') {
                showAdminPanel();
                loadComputers();
                showMessage('Login successful! Welcome, admin.', 'success');
            } else {
                // Show no privilege page for non-admin usernames
                showNoPrivilegePage();
            }
        } else {
            showMessage(data.message || 'Login failed. Try SQL injection!', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server: ' + error.message, 'error');
    }
});

// Search handler
document.getElementById('searchBtn').addEventListener('click', async () => {
    const searchTerm = document.getElementById('searchInput').value;
    await searchComputers(searchTerm);
});

// Enter key handler for search
document.getElementById('searchInput').addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const searchTerm = document.getElementById('searchInput').value;
        await searchComputers(searchTerm);
    }
});

// Logout handler
document.getElementById('logoutBtn').addEventListener('click', async () => {
    await logout();
});

// Back to login handler (user panel logout)
document.getElementById('backToLoginBtn').addEventListener('click', async () => {
    await logout();
});

async function logout() {
    try {
        // Clear session on server
        await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        // Clear local storage
        localStorage.removeItem(SESSION_STORAGE_KEY);
        
        // Clear current user
        currentUser = null;
        
        // Show login page
        showLoginBox();
        document.getElementById('loginForm').reset();
        document.getElementById('searchInput').value = '';
        showMessage('Logged out successfully.', 'success');
    } catch (error) {
        // Even if logout fails, clear local state
        localStorage.removeItem(SESSION_STORAGE_KEY);
        currentUser = null;
        showLoginBox();
        document.getElementById('loginForm').reset();
        showMessage('Logged out successfully.', 'success');
    }
}

async function loadComputers() {
    try {
        // Use original_username if available, otherwise fall back to username
        const usernameToSend = currentUser.original_username || currentUser.username;
        const response = await fetch(`${API_BASE_URL}/computers?username=${encodeURIComponent(usernameToSend)}`, {
            credentials: 'include' // Include cookies for session
        });
        const data = await response.json();
        
        if (data.success) {
            displayComputers(data.computers);
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error loading computers: ' + error.message, 'error');
    }
}

async function searchComputers(searchTerm) {
    try {
        // Use original_username if available, otherwise fall back to username
        const usernameToSend = currentUser.original_username || currentUser.username;
        const response = await fetch(`${API_BASE_URL}/search?username=${encodeURIComponent(usernameToSend)}&q=${encodeURIComponent(searchTerm)}`, {
            credentials: 'include' // Include cookies for session
        });
        const data = await response.json();
        
        if (data.success) {
            displayComputers(data.results);
            if (data.results.length === 0) {
                showMessage('No results found. Try SQL injection to extract schema!', 'error');
            }
        } else {
            // Show error message which might contain SQL error details
            showMessage(data.message || 'Search failed. Error: ' + (data.error_details || ''), 'error');
            // Still try to display if there are results
            if (data.results) {
                displayComputers(data.results);
            }
        }
    } catch (error) {
        showMessage('Error searching: ' + error.message, 'error');
    }
}

function displayComputers(computers) {
    const container = document.getElementById('computersList');
    
    if (!computers || computers.length === 0) {
        container.innerHTML = '<div class="no-results">No computers found</div>';
        return;
    }
    
    container.innerHTML = computers.map(comp => {
        // Handle cases where SQL injection might return unexpected columns
        const name = comp.computer_name || comp[Object.keys(comp)[0]] || 'Unknown';
        const ip = comp.ip_address || comp[Object.keys(comp)[1]] || 'N/A';
        const id = comp.id || comp[Object.keys(comp)[2]] || '';
        
        return `
            <div class="computer-card">
                <h3>${escapeHtml(String(name))}</h3>
                <p><strong>IP Address:</strong> <span class="ip">${escapeHtml(String(ip))}</span></p>
                <p><strong>ID:</strong> ${escapeHtml(String(id))}</p>
            </div>
        `;
    }).join('');
}

function showLoginBox() {
    document.getElementById('loginBox').style.display = 'block';
    document.getElementById('adminPanel').style.display = 'none';
    document.getElementById('userPanel').style.display = 'none';
}

function showAdminPanel() {
    document.getElementById('loginBox').style.display = 'none';
    document.getElementById('adminPanel').style.display = 'block';
    document.getElementById('userPanel').style.display = 'none';
    document.getElementById('currentUser').textContent = currentUser.username;
}

function showNoPrivilegePage() {
    document.getElementById('loginBox').style.display = 'none';
    document.getElementById('adminPanel').style.display = 'none';
    document.getElementById('userPanel').style.display = 'block';
    
    const loginId = currentUser.original_username || currentUser.username || 'Unknown';
    document.getElementById('loggedInUser').textContent = loginId;
    document.getElementById('userNameDisplay').textContent = loginId;
    document.getElementById('userLoginId').textContent = loginId;
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    
    setTimeout(() => {
        messageDiv.className = 'message';
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
