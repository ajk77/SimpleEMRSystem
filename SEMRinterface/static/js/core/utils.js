/**
 * Core utility functions for the SEMR interface.
 * 
 * This module provides common utilities used across the application,
 * including CSRF token handling, DOM manipulation helpers, and
 * common validation functions.
 * 
 * @fileoverview Core utilities for SEMR interface
 * @author SimpleEMRSystem
 * @version 2024.1
 */

/**
 * Cookie utility functions
 */
const CookieUtils = {
    /**
     * Get a cookie value by name
     * @param {string} name - The name of the cookie
     * @returns {string|null} The cookie value or null if not found
     */
    get(name) {
        if (!document.cookie || document.cookie === '') {
            return null;
        }
        
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    },

    /**
     * Set a cookie with optional parameters
     * @param {string} name - The name of the cookie
     * @param {string} value - The value of the cookie
     * @param {Object} options - Cookie options (expires, path, domain, secure)
     */
    set(name, value, options = {}) {
        let cookieString = `${name}=${encodeURIComponent(value)}`;
        
        if (options.expires) {
            cookieString += `; expires=${options.expires.toUTCString()}`;
        }
        if (options.path) {
            cookieString += `; path=${options.path}`;
        }
        if (options.domain) {
            cookieString += `; domain=${options.domain}`;
        }
        if (options.secure) {
            cookieString += `; secure`;
        }
        
        document.cookie = cookieString;
    }
};

/**
 * DOM manipulation utilities
 */
const DOMUtils = {
    /**
     * Show an element by ID
     * @param {string} elementId - The ID of the element to show
     */
    show(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
        }
    },

    /**
     * Hide an element by ID
     * @param {string} elementId - The ID of the element to hide
     */
    hide(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    },

    /**
     * Add a CSS class to an element
     * @param {string} elementId - The ID of the element
     * @param {string} className - The class name to add
     */
    addClass(elementId, className) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add(className);
        }
    },

    /**
     * Remove a CSS class from an element
     * @param {string} elementId - The ID of the element
     * @param {string} className - The class name to remove
     */
    removeClass(elementId, className) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove(className);
        }
    },

    /**
     * Toggle a CSS class on an element
     * @param {string} elementId - The ID of the element
     * @param {string} className - The class name to toggle
     */
    toggleClass(elementId, className) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.toggle(className);
        }
    }
};

/**
 * Validation utilities
 */
const ValidationUtils = {
    /**
     * Check if a value is not empty
     * @param {*} value - The value to check
     * @returns {boolean} True if the value is not empty
     */
    isNotEmpty(value) {
        return value !== null && value !== undefined && value !== '';
    },

    /**
     * Check if a value is a valid ID
     * @param {string} id - The ID to validate
     * @returns {boolean} True if the ID is valid
     */
    isValidId(id) {
        return typeof id === 'string' && id.length > 0;
    },

    /**
     * Validate required parameters
     * @param {Object} params - Object containing parameters to validate
     * @param {string[]} requiredFields - Array of required field names
     * @returns {boolean} True if all required fields are present and valid
     */
    validateRequired(params, requiredFields) {
        return requiredFields.every(field => 
            params.hasOwnProperty(field) && this.isNotEmpty(params[field])
        );
    }
};

/**
 * Error handling utilities
 */
const ErrorUtils = {
    /**
     * Log an error with context
     * @param {string} context - The context where the error occurred
     * @param {Error} error - The error object
     * @param {Object} additionalInfo - Additional information about the error
     */
    logError(context, error, additionalInfo = {}) {
        console.error(`[${context}] Error:`, error.message);
        if (Object.keys(additionalInfo).length > 0) {
            console.error('Additional info:', additionalInfo);
        }
    },

    /**
     * Handle API errors consistently
     * @param {Response} response - The fetch response object
     * @param {string} context - The context where the error occurred
     * @returns {Promise<Object>} Parsed error response
     */
    async handleApiError(response, context) {
        try {
            const errorData = await response.json();
            this.logError(context, new Error(errorData.message || 'API Error'), {
                status: response.status,
                statusText: response.statusText
            });
            return errorData;
        } catch (parseError) {
            this.logError(context, new Error('Failed to parse error response'), {
                originalError: parseError,
                status: response.status
            });
            return { message: 'An unexpected error occurred' };
        }
    }
};

// Export utilities for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CookieUtils, DOMUtils, ValidationUtils, ErrorUtils };
} else {
    // Browser environment - attach to window
    window.SEMRUtils = { CookieUtils, DOMUtils, ValidationUtils, ErrorUtils };
}
