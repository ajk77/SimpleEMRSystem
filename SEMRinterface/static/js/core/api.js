/**
 * API communication module for the SEMR interface.
 * 
 * This module handles all API calls to the Django backend,
 * including CSRF token management, error handling, and
 * response processing.
 * 
 * @fileoverview API communication utilities for SEMR interface
 * @author SimpleEMRSystem
 * @version 2024.1
 */

/**
 * API client for communicating with the SEMR backend
 */
class SEMRApiClient {
    constructor() {
        this.baseUrl = '';
        this.csrfToken = null;
        this.init();
    }

    /**
     * Initialize the API client
     * @private
     */
    init() {
        this.csrfToken = window.SEMRUtils?.CookieUtils?.get('csrftoken') || this.getCookie('csrftoken');
    }

    /**
     * Fallback cookie getter (in case SEMRUtils is not loaded)
     * @param {string} name - Cookie name
     * @returns {string|null} Cookie value
     * @private
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Make an API request
     * @param {string} url - The URL to request
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Parsed JSON response
     */
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Get case data for a specific study and case
     * @param {string} studyId - The study ID
     * @param {string} caseId - The case ID
     * @returns {Promise<Object>} Case data
     */
    async getCaseData(studyId, caseId) {
        const url = `/api/get_case_data/?study_id=${encodeURIComponent(studyId)}&case_id=${encodeURIComponent(caseId)}`;
        return this.request(url, { method: 'GET' });
    }

    /**
     * Get user details for a study
     * @param {string} studyId - The study ID
     * @returns {Promise<Object>} User details
     */
    async getUsers(studyId) {
        const formData = new FormData();
        formData.append('type', 'fetch_users');
        formData.append('study_id', studyId);

        return this.request('', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
            },
            body: formData,
        });
    }

    /**
     * Get case assignments for a user
     * @param {string} studyId - The study ID
     * @param {string} userId - The user ID
     * @returns {Promise<Object>} Case assignments
     */
    async getCases(studyId, userId) {
        const formData = new FormData();
        formData.append('type', 'fetch_cases');
        formData.append('study_id', studyId);
        formData.append('user_id', userId);

        return this.request('', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
            },
            body: formData,
        });
    }

    /**
     * Save selected items for a case
     * @param {string} studyId - The study ID
     * @param {string} userId - The user ID
     * @param {string} caseId - The case ID
     * @param {Array<string>} selectedItems - Array of selected item IDs
     * @returns {Promise<Object>} Save result
     */
    async saveSelectedItems(studyId, userId, caseId, selectedItems) {
        const url = `/SEMRinterface/selected_items/${encodeURIComponent(studyId)}/${encodeURIComponent(userId)}/${encodeURIComponent(caseId)}/`;
        
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify({ selected_ids: selectedItems }),
        });
    }

    /**
     * Mark a case as complete
     * @param {string} studyId - The study ID
     * @param {string} userId - The user ID
     * @param {string} caseId - The case ID
     * @returns {Promise<Object>} Completion result
     */
    async markCaseComplete(studyId, userId, caseId) {
        const url = `/SEMRinterface/markcompleteurl/${encodeURIComponent(studyId)}/${encodeURIComponent(userId)}/${encodeURIComponent(caseId)}/`;
        return this.request(url, { method: 'POST' });
    }
}

// Create and export a singleton instance
const apiClient = new SEMRApiClient();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SEMRApiClient, apiClient };
} else {
    // Browser environment - attach to window
    window.SEMRApi = { SEMRApiClient, apiClient };
}
