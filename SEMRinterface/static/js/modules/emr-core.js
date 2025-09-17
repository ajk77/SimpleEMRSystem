/**
 * Core EMR functionality module.
 * 
 * This module handles the main EMR interface functionality including
 * case management, item selection, and navigation.
 * 
 * @fileoverview Core EMR functionality for case viewing and interaction
 * @author SimpleEMRSystem
 * @version 2024.1
 */

/**
 * EMR Core application class
 */
class EMRCore {
    constructor() {
        this.selectedItems = new Set();
        this.chartsContainers = [];
        this.chartRowIds = [];
        this.selectedMin = null;
        this.selectedMax = null;
        this.displayedMinT = null;
        this.displayedMaxT = null;
        this.step = 0;
        this.caseDetails = null;
        this.caseCompleteUrl = null;
        this.nextStepUrl = null;
        this.studyId = null;
        this.userId = null;
        this.caseId = null;
        
        this.apiClient = window.SEMRApi?.apiClient;
        this.utils = window.SEMRUtils;
    }

    /**
     * Initialize case details
     * @param {Object} details - Case details object
     * @param {string} studyId - Study ID
     * @param {string} userId - User ID
     * @param {string} caseId - Case ID
     * @param {number} timeStep - Current time step
     */
    setCaseDetails(details, studyId, userId, caseId, timeStep = 0) {
        this.caseDetails = details;
        this.step = timeStep;
        this.studyId = studyId;
        this.userId = userId;
        this.caseId = caseId;
    }

    /**
     * Set URLs for case completion and next step
     */
    setUrls() {
        this.caseCompleteUrl = `/SEMRinterface/markcompleteurl/${this.studyId}/${this.userId}/${this.caseId}/`;
        this.nextStepUrl = `/SEMRinterface/${this.studyId}/${this.userId}/${this.caseId}/${this.step + 1}/`;
    }

    /**
     * Show loading screen
     */
    showLoading() {
        this.utils?.DOMUtils?.show('loading_new_patient') || 
        document.getElementById('loading_new_patient').style.display = 'block';
    }

    /**
     * Hide loading screen
     */
    hideLoading() {
        this.utils?.DOMUtils?.hide('loading_new_patient') || 
        document.getElementById('loading_new_patient').style.display = 'none';
    }

    /**
     * Navigate to the next step or mark case as complete
     */
    async advanceToNextStep() {
        try {
            if (this.selectedItems.size > 0) {
                await this.saveSelectedItems(Array.from(this.selectedItems));
            }
            
            const nextUrl = this.step < this.caseDetails.length - 1 ? this.nextStepUrl : this.caseCompleteUrl;
            window.location.href = nextUrl;
        } catch (error) {
            this.utils?.ErrorUtils?.logError('EMRCore.advanceToNextStep', error);
            console.error('Failed to advance to next step:', error);
        }
    }

    /**
     * Save selected items to the backend
     * @param {Array<string>} selectedIds - Array of selected item IDs
     * @returns {Promise<Object>} Save result
     */
    async saveSelectedItems(selectedIds) {
        if (!this.apiClient) {
            throw new Error('API client not available');
        }

        return this.apiClient.saveSelectedItems(
            this.studyId, 
            this.userId, 
            this.caseId, 
            selectedIds
        );
    }

    /**
     * Update selection state for an item
     * @param {string} id - Item ID
     * @param {boolean} add - Whether to add or remove the item
     */
    updateSelectionState(id, add) {
        if (add) {
            this.selectedItems.add(id);
        } else {
            this.selectedItems.delete(id);
        }
    }

    /**
     * Toggle selection for an item
     * @param {string} id - Item ID
     */
    toggleSelection(id) {
        const isSelected = this.selectedItems.has(id);
        this.updateSelectionState(id, !isSelected);
        
        if (isSelected) {
            this.unhighlightChartRow(id);
        } else {
            this.highlightChartRow(id);
        }
    }

    /**
     * Highlight a chart row
     * @param {string} id - Element ID
     */
    highlightChartRow(id) {
        this.utils?.DOMUtils?.addClass(id, 'highlight') ||
        document.getElementById(id)?.classList.add('highlight');
    }

    /**
     * Remove highlight from a chart row
     * @param {string} id - Element ID
     */
    unhighlightChartRow(id) {
        this.utils?.DOMUtils?.removeClass(id, 'highlight') ||
        document.getElementById(id)?.classList.remove('highlight');
    }

    /**
     * Update time extremes for all charts
     * @param {number} minTime - Minimum time
     * @param {number} maxTime - Maximum time
     */
    updateTimeExtremes(minTime, maxTime) {
        this.selectedMin = minTime;
        this.selectedMax = maxTime;
        
        // Process charts in batches to avoid performance issues
        for (let i = 0; i < this.chartsContainers.length; i += 10) {
            const batch = this.chartsContainers.slice(i, i + 10);
            batch.forEach(containerId => {
                const chart = Highcharts.chart(containerId);
                if (chart) {
                    chart.xAxis[0].setExtremes(this.selectedMin, this.selectedMax);
                }
            });
        }
    }

    /**
     * Add vertical plot line to all charts
     * @param {number} time - Time value for the plot line
     */
    addVerticalPlotLine(time) {
        this.chartsContainers.forEach(containerId => {
            const chart = Highcharts.chart(containerId);
            if (chart) {
                chart.xAxis[0].addPlotLine({
                    value: time,
                    color: 'black',
                    dashStyle: 'dash',
                    width: 1,
                    id: 'plot-line-1',
                });
            }
        });
    }

    /**
     * Initialize the page with data
     * @param {Object} caseDetailsData - Case details data
     * @param {string} studyId - Study ID
     * @param {string} userId - User ID
     * @param {string} caseId - Case ID
     * @param {number} timeStep - Time step
     */
    initializePage(caseDetailsData, studyId, userId, caseId, timeStep = 0) {
        this.setCaseDetails(caseDetailsData, studyId, userId, caseId, timeStep);
        this.setUrls();
        this.showLoading();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Set up event listeners for the interface
     * @private
     */
    setupEventListeners() {
        const nextScreenButton = document.getElementById('next_screen_button');
        if (nextScreenButton) {
            nextScreenButton.addEventListener('click', () => this.advanceToNextStep());
        } else {
            console.error("Element with ID 'next_screen_button' not found.");
        }

        // Set up chart row click handlers
        document.querySelectorAll('.chart-row').forEach(row => {
            row.addEventListener('click', () => this.toggleSelection(row.id));
        });
    }
}

// Create and export a singleton instance
const emrCore = new EMRCore();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EMRCore, emrCore };
} else {
    // Browser environment - attach to window
    window.EMRCore = { EMRCore, emrCore };
}
