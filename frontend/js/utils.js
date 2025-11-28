/**
 * Utility functions shared across the application
 */

export function formatCurrency(val) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
}

// Trim string inputs to avoid sending only-whitespace values to the API
export function normalizeText(value) {
    if (value === undefined || value === null) return '';
    return String(value).trim();
}
