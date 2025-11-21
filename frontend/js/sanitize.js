/**
 * Security utilities for sanitizing user input and preventing XSS attacks
 */

/**
 * Escapes HTML special characters to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text safe for HTML insertion
 */
export function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }

    const str = String(text);
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    };

    return str.replace(/[&<>"'/]/g, (char) => map[char]);
}
