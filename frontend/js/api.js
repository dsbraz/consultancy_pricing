const API_BASE_URL = window.location.origin;

async function throwApiError(response) {
    if (response.status === 401) {
        // Redirect to login if unauthorized
        window.location.href = '/auth/login';
        // Throw an error to stop execution chain, though the page will reload soon
        throw new Error('Unauthorized');
    }

    const errorData = await response.json().catch(() => ({}));
    
    let message = response.statusText;
    if (typeof errorData.detail === 'string') {
        message = errorData.detail;
    } else if (errorData.error && typeof errorData.error === 'string') {
        message = errorData.error;
    } else if (errorData.message) {
        message = errorData.message;
    }

    const error = new Error(message);
    error.status = response.status;
    Object.assign(error, errorData);
    throw error;
}

export const api = {
    async get(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            await throwApiError(response);
        }
        return response.json();
    },

    async post(endpoint, data) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            await throwApiError(response);
        }
        return response.json();
    },

    async put(endpoint, data) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            await throwApiError(response);
        }
        return response.json();
    },

    async patch(endpoint, data) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            await throwApiError(response);
        }
        return response.json();
    },

    async delete(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            await throwApiError(response);
        }
        return response.json();
    },

    async downloadBlob(endpoint, fallbackFilename = null) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            await throwApiError(response);
        }
        const blob = await response.blob();

        // Try to extract filename from Content-Disposition header
        let filename = fallbackFilename;
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }

        // Criar link temporário para download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'download';
        document.body.appendChild(a);
        a.click();

        // Limpar
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};
