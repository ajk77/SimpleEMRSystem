/**
 * Interactive tutorial system for Simple EMR System
 * 
 * Provides step-by-step guidance for new users
 * 
 * @fileoverview Tutorial system for user onboarding
 * @author SimpleEMRSystem
 * @version 2024.2
 */

/**
 * Tutorial system class for guiding users through the interface
 */
class TutorialSystem {
    constructor() {
        this.steps = [];
        this.currentStep = 0;
        this.isActive = false;
        this.overlay = null;
        this.tooltip = null;
        this.callbacks = {
            onStart: null,
            onStep: null,
            onComplete: null,
            onSkip: null
        };
    }

    /**
     * Initialize the tutorial system
     * @param {Object} options - Configuration options
     */
    init(options = {}) {
        this.steps = options.steps || this.getDefaultSteps();
        this.callbacks = { ...this.callbacks, ...options.callbacks };
        this.createOverlay();
        this.createTooltip();
    }

    /**
     * Get default tutorial steps
     * @returns {Array} Default tutorial steps
     */
    getDefaultSteps() {
        return [
            {
                id: 'welcome',
                title: 'Welcome to Simple EMR System',
                content: 'This tutorial will guide you through the basic features of the system. Click "Next" to continue or "Skip" to exit.',
                target: 'body',
                position: 'center',
                showSkip: true
            },
            {
                id: 'study-selection',
                title: 'Select a Study',
                content: 'First, choose a research study from the dropdown menu. This will load the available users for that study.',
                target: '#study-dropdown',
                position: 'bottom',
                showSkip: true
            },
            {
                id: 'user-selection',
                title: 'Choose a User',
                content: 'Next, select your user profile from the list. This determines which cases you can access.',
                target: '#user-dropdown',
                position: 'bottom',
                showSkip: true,
                condition: () => document.querySelector('#user-dropdown').style.display !== 'none'
            },
            {
                id: 'case-selection',
                title: 'Select a Case',
                content: 'Finally, click on a case to view patient data. You can see both assigned and completed cases.',
                target: '.case-item',
                position: 'right',
                showSkip: true,
                condition: () => document.querySelector('.case-item') !== null
            },
            {
                id: 'case-viewer',
                title: 'Case Viewer Interface',
                content: 'In the case viewer, you can review patient demographics, medical data, and complete research tasks.',
                target: '.case-viewer-container',
                position: 'center',
                showSkip: true,
                condition: () => document.querySelector('.case-viewer-container') !== null
            },
            {
                id: 'charts',
                title: 'Interactive Charts',
                content: 'Use the interactive charts to explore patient data over time. Click on chart elements to select them.',
                target: '.chart-container',
                position: 'top',
                showSkip: true,
                condition: () => document.querySelector('.chart-container') !== null
            },
            {
                id: 'selection',
                title: 'Item Selection',
                content: 'Selected items will be highlighted. Use these selections to complete your research tasks.',
                target: '.highlight',
                position: 'bottom',
                showSkip: true,
                condition: () => document.querySelector('.highlight') !== null
            },
            {
                id: 'completion',
                title: 'Complete Tasks',
                content: 'When you\'re ready, click the "Continue" button to save your selections and proceed.',
                target: '#next_screen_button',
                position: 'top',
                showSkip: true,
                condition: () => document.querySelector('#next_screen_button') !== null
            }
        ];
    }

    /**
     * Start the tutorial
     */
    start() {
        if (this.isActive) {
            return;
        }

        this.isActive = true;
        this.currentStep = 0;
        this.showOverlay();
        
        if (this.callbacks.onStart) {
            this.callbacks.onStart();
        }

        this.showStep(0);
    }

    /**
     * Show a specific tutorial step
     * @param {number} stepIndex - Index of the step to show
     */
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            this.complete();
            return;
        }

        const step = this.steps[stepIndex];
        
        // Check if step condition is met
        if (step.condition && !step.condition()) {
            this.next();
            return;
        }

        this.currentStep = stepIndex;
        this.highlightElement(step.target);
        this.showTooltip(step);

        if (this.callbacks.onStep) {
            this.callbacks.onStep(step, stepIndex);
        }
    }

    /**
     * Move to the next step
     */
    next() {
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        } else {
            this.complete();
        }
    }

    /**
     * Move to the previous step
     */
    previous() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }

    /**
     * Skip the tutorial
     */
    skip() {
        this.isActive = false;
        this.hideOverlay();
        this.hideTooltip();
        this.removeHighlight();

        if (this.callbacks.onSkip) {
            this.callbacks.onSkip();
        }
    }

    /**
     * Complete the tutorial
     */
    complete() {
        this.isActive = false;
        this.hideOverlay();
        this.hideTooltip();
        this.removeHighlight();

        if (this.callbacks.onComplete) {
            this.callbacks.onComplete();
        }
    }

    /**
     * Create the tutorial overlay
     */
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tutorial-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9998;
            display: none;
        `;
        document.body.appendChild(this.overlay);
    }

    /**
     * Create the tutorial tooltip
     */
    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tutorial-tooltip';
        this.tooltip.style.cssText = `
            position: absolute;
            background: white;
            border: 2px solid #007bff;
            border-radius: 8px;
            padding: 20px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            display: none;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(this.tooltip);
    }

    /**
     * Show the overlay
     */
    showOverlay() {
        if (this.overlay) {
            this.overlay.style.display = 'block';
        }
    }

    /**
     * Hide the overlay
     */
    hideOverlay() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }

    /**
     * Show the tooltip for a step
     * @param {Object} step - Tutorial step
     */
    showTooltip(step) {
        if (!this.tooltip) return;

        const targetElement = document.querySelector(step.target);
        if (!targetElement) {
            console.warn(`Tutorial target not found: ${step.target}`);
            return;
        }

        // Position the tooltip
        const rect = targetElement.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        let left, top;
        
        switch (step.position) {
            case 'top':
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                top = rect.top - tooltipRect.height - 10;
                break;
            case 'bottom':
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                top = rect.bottom + 10;
                break;
            case 'left':
                left = rect.left - tooltipRect.width - 10;
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'right':
                left = rect.right + 10;
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'center':
                left = (window.innerWidth - tooltipRect.width) / 2;
                top = (window.innerHeight - tooltipRect.height) / 2;
                break;
            default:
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                top = rect.bottom + 10;
        }

        // Ensure tooltip stays within viewport
        left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        top = Math.max(10, Math.min(top, window.innerHeight - tooltipRect.height - 10));

        this.tooltip.style.left = `${left}px`;
        this.tooltip.style.top = `${top}px`;

        // Set tooltip content
        this.tooltip.innerHTML = `
            <div class="tutorial-header">
                <h3 style="margin: 0 0 10px 0; color: #007bff;">${step.title}</h3>
            </div>
            <div class="tutorial-content">
                <p style="margin: 0 0 15px 0; line-height: 1.4;">${step.content}</p>
            </div>
            <div class="tutorial-actions">
                <button class="btn btn-primary btn-sm" onclick="tutorial.next()">
                    ${this.currentStep === this.steps.length - 1 ? 'Finish' : 'Next'}
                </button>
                ${this.currentStep > 0 ? '<button class="btn btn-secondary btn-sm" onclick="tutorial.previous()" style="margin-left: 10px;">Previous</button>' : ''}
                ${step.showSkip ? '<button class="btn btn-outline-secondary btn-sm" onclick="tutorial.skip()" style="margin-left: 10px;">Skip Tutorial</button>' : ''}
            </div>
            <div class="tutorial-progress" style="margin-top: 15px; text-align: center; font-size: 12px; color: #666;">
                Step ${this.currentStep + 1} of ${this.steps.length}
            </div>
        `;

        this.tooltip.style.display = 'block';
    }

    /**
     * Hide the tooltip
     */
    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.style.display = 'none';
        }
    }

    /**
     * Highlight an element
     * @param {string} selector - CSS selector for the element to highlight
     */
    highlightElement(selector) {
        this.removeHighlight();
        
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('tutorial-highlight');
            element.style.position = 'relative';
            element.style.zIndex = '10000';
        }
    }

    /**
     * Remove highlight from all elements
     */
    removeHighlight() {
        const highlighted = document.querySelectorAll('.tutorial-highlight');
        highlighted.forEach(el => {
            el.classList.remove('tutorial-highlight');
            el.style.position = '';
            el.style.zIndex = '';
        });
    }

    /**
     * Check if tutorial is active
     * @returns {boolean} True if tutorial is active
     */
    isRunning() {
        return this.isActive;
    }

    /**
     * Get current step information
     * @returns {Object|null} Current step or null if not active
     */
    getCurrentStep() {
        if (!this.isActive || this.currentStep >= this.steps.length) {
            return null;
        }
        return this.steps[this.currentStep];
    }
}

// Create global tutorial instance
const tutorial = new TutorialSystem();

// Add tutorial styles
const tutorialStyles = document.createElement('style');
tutorialStyles.textContent = `
    .tutorial-highlight {
        outline: 3px solid #007bff !important;
        outline-offset: 2px !important;
        background-color: rgba(0, 123, 255, 0.1) !important;
    }
    
    .tutorial-tooltip .btn {
        padding: 5px 15px;
        border-radius: 4px;
        border: 1px solid transparent;
        cursor: pointer;
        font-size: 14px;
    }
    
    .tutorial-tooltip .btn-primary {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .tutorial-tooltip .btn-secondary {
        background-color: #6c757d;
        color: white;
        border-color: #6c757d;
    }
    
    .tutorial-tooltip .btn-outline-secondary {
        background-color: transparent;
        color: #6c757d;
        border-color: #6c757d;
    }
    
    .tutorial-tooltip .btn:hover {
        opacity: 0.8;
    }
`;

document.head.appendChild(tutorialStyles);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TutorialSystem, tutorial };
} else {
    // Browser environment - attach to window
    window.TutorialSystem = TutorialSystem;
    window.tutorial = tutorial;
}
