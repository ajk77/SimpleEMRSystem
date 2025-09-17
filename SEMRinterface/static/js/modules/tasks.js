/**
 * Task management module for the SEMR interface.
 * 
 * This module handles task-related functionality including
 * item selection, navigation, and task completion.
 * 
 * @fileoverview Task management utilities for EMR interface
 * @author SimpleEMRSystem
 * @version 2024.1
 */

/**
 * Task manager class for handling user interactions and task flow
 */
class TaskManager {
    constructor() {
        this.selectedItems = [];
        this.apiClient = window.SEMRApi?.apiClient;
        this.utils = window.SEMRUtils;
        this.studyId = null;
        this.userId = null;
        this.caseId = null;
    }

    /**
     * Initialize the task manager with context
     * @param {string} studyId - Study ID
     * @param {string} userId - User ID
     * @param {string} caseId - Case ID
     */
    initialize(studyId, userId, caseId) {
        this.studyId = studyId;
        this.userId = userId;
        this.caseId = caseId;
        this.selectedItems = [];
    }

    /**
     * Save selected items to the backend
     * @param {Array<string>} selectedItems - Array of selected item IDs
     * @returns {Promise<Object>} Save result
     */
    async saveSelectedItems(selectedItems) {
        if (!this.apiClient) {
            throw new Error('API client not available');
        }

        if (!this.studyId || !this.userId || !this.caseId) {
            throw new Error('Task manager not properly initialized');
        }

        return this.apiClient.saveSelectedItems(
            this.studyId,
            this.userId,
            this.caseId,
            selectedItems
        );
    }

    /**
     * Navigate to the next step or mark case as complete
     * @param {string} nextStepUrl - URL for the next step
     * @param {string} caseCompleteUrl - URL to mark case as complete
     */
    navigateToNextStep(nextStepUrl, caseCompleteUrl) {
        if (nextStepUrl) {
            window.location.href = nextStepUrl;
        } else if (caseCompleteUrl) {
            window.location.href = caseCompleteUrl;
        } else {
            console.error('No valid navigation URL provided');
        }
    }

    /**
     * Handle the continue button click
     * @param {Array<string>} selectedItems - Currently selected items
     * @param {string} nextStepUrl - URL for the next step
     * @param {string} caseCompleteUrl - URL to mark case as complete
     */
    async handleContinueButton(selectedItems, nextStepUrl, caseCompleteUrl) {
        try {
            if (selectedItems && selectedItems.length > 0) {
                await this.saveSelectedItems(selectedItems);
                console.log('Items saved successfully');
            }
            this.navigateToNextStep(nextStepUrl, caseCompleteUrl);
        } catch (error) {
            this.utils?.ErrorUtils?.logError('TaskManager.handleContinueButton', error);
            console.error('Failed to save items or navigate:', error);
        }
    }

    /**
     * Toggle item selection
     * @param {string} itemId - The ID of the item to toggle
     * @param {Array<string>} selectedItems - Array of currently selected items
     */
    toggleSelection(itemId, selectedItems) {
        const itemIndex = selectedItems.indexOf(itemId);
        if (itemIndex > -1) {
            selectedItems.splice(itemIndex, 1);
            this.unhighlightItem(itemId);
        } else {
            selectedItems.push(itemId);
            this.highlightItem(itemId);
        }
    }

    /**
     * Highlight an item visually
     * @param {string} itemId - The ID of the item to highlight
     */
    highlightItem(itemId) {
        this.utils?.DOMUtils?.addClass(itemId, 'highlight') ||
        document.getElementById(itemId)?.classList.add('highlight');
    }

    /**
     * Remove highlight from an item
     * @param {string} itemId - The ID of the item to unhighlight
     */
    unhighlightItem(itemId) {
        this.utils?.DOMUtils?.removeClass(itemId, 'highlight') ||
        document.getElementById(itemId)?.classList.remove('highlight');
    }

    /**
     * Initialize task functionality for a page
     * @param {string} nextStepUrl - URL for the next step
     * @param {string} caseCompleteUrl - URL to mark case as complete
     * @param {string} continueButtonId - ID of the continue button
     * @param {string} selectableItemClass - CSS class for selectable items
     */
    initializeTasks(nextStepUrl, caseCompleteUrl, continueButtonId = 'continue_button', selectableItemClass = 'selectable-item') {
        const continueButton = document.getElementById(continueButtonId);
        const selectedItems = [];

        if (continueButton) {
            continueButton.addEventListener('click', () => {
                this.handleContinueButton(selectedItems, nextStepUrl, caseCompleteUrl);
            });
        } else {
            console.warn(`Continue button with ID '${continueButtonId}' not found`);
        }

        // Set up selectable item handlers
        document.querySelectorAll(`.${selectableItemClass}`).forEach((item) => {
            item.addEventListener('click', () => {
                this.toggleSelection(item.id, selectedItems);
            });
        });
    }

    /**
     * Get currently selected items
     * @returns {Array<string>} Array of selected item IDs
     */
    getSelectedItems() {
        return [...this.selectedItems];
    }

    /**
     * Clear all selected items
     */
    clearSelectedItems() {
        this.selectedItems.forEach(itemId => {
            this.unhighlightItem(itemId);
        });
        this.selectedItems = [];
    }

    /**
     * Set selected items programmatically
     * @param {Array<string>} items - Array of item IDs to select
     */
    setSelectedItems(items) {
        this.clearSelectedItems();
        items.forEach(itemId => {
            this.selectedItems.push(itemId);
            this.highlightItem(itemId);
        });
    }

    /**
     * Check if an item is selected
     * @param {string} itemId - The ID of the item to check
     * @returns {boolean} True if the item is selected
     */
    isItemSelected(itemId) {
        return this.selectedItems.includes(itemId);
    }

    /**
     * Get the count of selected items
     * @returns {number} Number of selected items
     */
    getSelectedCount() {
        return this.selectedItems.length;
    }
}

// Create and export a singleton instance
const taskManager = new TaskManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TaskManager, taskManager };
} else {
    // Browser environment - attach to window
    window.TaskManager = { TaskManager, taskManager };
}
