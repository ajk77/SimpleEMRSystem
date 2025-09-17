# Frontend Documentation

## Overview

The Simple EMR System frontend is built using modern JavaScript with a modular architecture, responsive HTML templates, and organized CSS. The frontend provides an intuitive interface for healthcare professionals to interact with medical data.

## Architecture

### JavaScript Modules

The frontend uses a modular JavaScript architecture with clear separation of concerns:

```
static/js/
├── core/                    # Core utilities and API layer
│   ├── utils.js            # Common utilities
│   └── api.js              # API communication
├── modules/                 # Feature-specific modules
│   ├── emr-core.js         # Main EMR functionality
│   ├── charts.js           # Chart management
│   └── tasks.js            # Task management
└── legacy/                 # Legacy JavaScript files
```

### Template Structure

Templates use Django's inheritance system for maintainability:

```
templates/SEMRinterface/
├── base.html                    # Base template
├── components/                  # Reusable components
│   ├── loading.html
│   └── selection_form.html
├── unified_selection_new.html   # Modern selection interface
└── case_viewer_new.html        # Modern case viewer
```

## Core Modules

### Utils Module (`core/utils.js`)

Provides common utilities used throughout the application.

#### CookieUtils
```javascript
// Get a cookie value
const token = CookieUtils.get('csrftoken');

// Set a cookie
CookieUtils.set('preference', 'value', {
    expires: new Date(Date.now() + 86400000), // 1 day
    path: '/',
    secure: true
});
```

#### DOMUtils
```javascript
// Show/hide elements
DOMUtils.show('element-id');
DOMUtils.hide('element-id');

// Add/remove CSS classes
DOMUtils.addClass('element-id', 'highlight');
DOMUtils.removeClass('element-id', 'highlight');
```

#### ValidationUtils
```javascript
// Validate required parameters
const isValid = ValidationUtils.validateRequired(
    { studyId: 'study1', userId: 'user1' },
    ['studyId', 'userId']
);
```

#### ErrorUtils
```javascript
// Log errors with context
ErrorUtils.logError('ModuleName.functionName', error, { additionalInfo: 'value' });

// Handle API errors
const errorData = await ErrorUtils.handleApiError(response, 'API call');
```

### API Module (`core/api.js`)

Handles all backend communication with proper error handling and CSRF protection.

#### SEMRApiClient Class

```javascript
// Initialize API client
const apiClient = new SEMRApiClient();

// Get case data
const caseData = await apiClient.getCaseData('study1', 'case1');

// Save selected items
await apiClient.saveSelectedItems('study1', 'user1', 'case1', ['item1', 'item2']);

// Get users for a study
const users = await apiClient.getUsers('study1');

// Get cases for a user
const cases = await apiClient.getCases('study1', 'user1');
```

## Feature Modules

### EMR Core Module (`modules/emr-core.js`)

Main application logic for case viewing and interaction.

#### EMRCore Class

```javascript
// Initialize EMR core
const emrCore = new EMRCore();

// Set case details
emrCore.setCaseDetails(caseData, 'study1', 'user1', 'case1', 0);

// Toggle item selection
emrCore.toggleSelection('item-id');

// Update time extremes for charts
emrCore.updateTimeExtremes(minTime, maxTime);

// Add vertical plot line
emrCore.addVerticalPlotLine(timeValue);

// Initialize page
emrCore.initializePage(caseData, 'study1', 'user1', 'case1', 0);
```

### Charts Module (`modules/charts.js`)

Chart management using Highcharts library.

#### ChartManager Class

```javascript
// Initialize chart manager
const chartManager = new ChartManager();

// Create a line chart
const chart = chartManager.createLineChart('container-id', 'Chart Title', 
    ['Jan', 'Feb', 'Mar'], 
    [{ name: 'Series 1', data: [1, 2, 3] }]
);

// Create a bar chart
const barChart = chartManager.createBarChart('container-id', 'Bar Chart', 
    categories, seriesData
);

// Create a scatter plot
const scatterChart = chartManager.createScatterPlot('container-id', 'Scatter Plot', 
    seriesData
);

// Update chart data
chartManager.updateChart('container-id', { series: newSeriesData });

// Set time extremes for all charts
chartManager.setTimeExtremes(minTime, maxTime);

// Add vertical plot line
chartManager.addVerticalPlotLine(timeValue, { color: 'red', width: 2 });
```

### Tasks Module (`modules/tasks.js`)

Task management and user interaction handling.

#### TaskManager Class

```javascript
// Initialize task manager
const taskManager = new TaskManager();

// Initialize with context
taskManager.initialize('study1', 'user1', 'case1');

// Toggle item selection
taskManager.toggleSelection('item-id', selectedItems);

// Handle continue button
await taskManager.handleContinueButton(selectedItems, nextStepUrl, completeUrl);

// Get selected items
const selected = taskManager.getSelectedItems();

// Clear selections
taskManager.clearSelectedItems();

// Set selections programmatically
taskManager.setSelectedItems(['item1', 'item2']);

// Check if item is selected
const isSelected = taskManager.isItemSelected('item-id');
```

## Templates

### Base Template (`base.html`)

The base template provides the common structure for all pages:

- HTML5 document structure
- Meta tags and SEO optimization
- CSS and JavaScript includes
- Navigation components
- Loading overlays
- Modal dialogs
- Footer and branding

#### Template Blocks

```html
{% block title %}Page Title{% endblock %}
{% block meta_description %}Page description{% endblock %}
{% block extra_css %}{% endblock %}
{% block extra_js %}{% endblock %}
{% block navigation %}{% endblock %}
{% block content %}{% endblock %}
{% block footer %}{% endblock %}
{% block page_js %}{% endblock %}
```

### Component Templates

#### Loading Component (`components/loading.html`)

Reusable loading indicator with spinner and overlay.

#### Selection Form Component (`components/selection_form.html`)

Form component for study, user, and case selection with:
- Dropdown menus
- Dynamic content loading
- Error handling
- Responsive design

### Page Templates

#### Unified Selection (`unified_selection_new.html`)

Modern selection interface with:
- Step-by-step wizard
- Progress indicators
- Real-time validation
- Error messaging
- Responsive design

#### Case Viewer (`case_viewer_new.html`)

Main case viewing interface with:
- Demographics display
- Data panels (physiological, medications, labs)
- Notes section with tabs
- Task instructions
- Interactive charts
- Selection highlighting

## Styling

### CSS Architecture

The styling system uses a combination of:
- Bootstrap 4.6.2 for base components
- Custom CSS for application-specific styles
- Responsive design principles
- Consistent color scheme
- Accessible design patterns

### Key Style Classes

#### Layout Classes
```css
.selection-container     /* Main container for selection pages */
.case-viewer-container   /* Main container for case viewer */
.scroll-box             /* Scrollable content areas */
.panel-container        /* Data panel styling */
```

#### Interactive Classes
```css
.highlight              /* Selection highlighting */
.loading-overlay        /* Full-screen loading indicator */
.note-tab.active        /* Active note tab */
.panel-content.active   /* Active panel content */
```

#### Component Classes
```css
.selection-form         /* Form styling */
.chart-container        /* Chart wrapper */
.task-panel            /* Task instruction panel */
.demographics-bar       /* Demographics display */
```

### Responsive Design

The interface is fully responsive with breakpoints:
- Mobile: < 768px
- Tablet: 768px - 991px
- Desktop: > 992px

### Color Scheme

- Primary: #007bff (Bootstrap blue)
- Success: #28a745 (Bootstrap green)
- Warning: #ffc107 (Bootstrap yellow)
- Danger: #dc3545 (Bootstrap red)
- Info: #17a2b8 (Bootstrap cyan)
- Light: #f8f9fa (Bootstrap light)
- Dark: #343a40 (Bootstrap dark)

## Event Handling

### Event Delegation

The system uses event delegation for dynamic content:

```javascript
// Chart row click handlers
document.querySelectorAll('.chart-row').forEach(row => {
    row.addEventListener('click', () => emrCore.toggleSelection(row.id));
});

// Selectable item handlers
document.querySelectorAll('.selectable-item').forEach(item => {
    item.addEventListener('click', () => taskManager.toggleSelection(item.id, selectedItems));
});
```

### AJAX Handling

AJAX requests include proper error handling and loading indicators:

```javascript
$(document).ajaxStart(function() {
    utils.DOMUtils.show('loading_new_patient');
}).ajaxStop(function() {
    utils.DOMUtils.hide('loading_new_patient');
});
```

## Performance Optimization

### Lazy Loading

Charts and heavy content are loaded on demand:

```javascript
// Load chart data when panel is opened
function togglePanel(panelId) {
    const content = $(`#${panelId} .panel-content`);
    if (!content.hasClass('loaded')) {
        loadPanelContent(panelId);
        content.addClass('loaded');
    }
    content.toggleClass('active');
}
```

### Batch Processing

Chart updates are batched for performance:

```javascript
// Process charts in batches
for (let i = 0; i < chartsContainers.length; i += 10) {
    const batch = chartsContainers.slice(i, i + 10);
    batch.forEach(containerId => {
        // Update chart
    });
}
```

## Error Handling

### Client-Side Error Handling

All modules include comprehensive error handling:

```javascript
try {
    const result = await apiClient.getCaseData(studyId, caseId);
    // Handle success
} catch (error) {
    utils.ErrorUtils.logError('Case data fetch', error);
    // Show user-friendly error message
    showError('Failed to load case data. Please try again.');
}
```

### User Feedback

Error messages are displayed to users in a consistent format:

```javascript
function showError(message) {
    $('#error-message').text(message).show();
    $('#success-message').hide();
}
```

## Accessibility

### ARIA Labels

Interactive elements include proper ARIA labels:

```html
<button id="next_screen_button" class="btn btn-primary btn-lg" 
        aria-label="Continue to next step">
    Continue
</button>
```

### Keyboard Navigation

All interactive elements are keyboard accessible:

```css
.note-tab:focus,
.panel-header:focus {
    outline: 2px solid #007bff;
    outline-offset: 2px;
}
```

### Screen Reader Support

Content is structured for screen readers:

```html
<div role="tablist" aria-label="Clinical notes">
    <button role="tab" aria-selected="true" aria-controls="note-panel-1">
        Admission Notes
    </button>
</div>
```

## Browser Support

The frontend supports:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Development Guidelines

### Code Organization

- Use meaningful variable and function names
- Include JSDoc comments for all functions
- Follow consistent indentation (2 spaces)
- Use const/let instead of var
- Avoid global variables

### Error Handling

- Always wrap async operations in try-catch
- Log errors with context information
- Provide user-friendly error messages
- Handle edge cases gracefully

### Performance

- Minimize DOM queries
- Use event delegation for dynamic content
- Batch DOM updates
- Lazy load heavy content
- Optimize images and assets

## Testing

### Unit Testing

Test individual modules in isolation:

```javascript
// Test utility functions
describe('CookieUtils', () => {
    test('should get cookie value', () => {
        document.cookie = 'test=value';
        expect(CookieUtils.get('test')).toBe('value');
    });
});
```

### Integration Testing

Test module interactions:

```javascript
// Test API integration
describe('API Client', () => {
    test('should fetch case data', async () => {
        const data = await apiClient.getCaseData('study1', 'case1');
        expect(data.status).toBe('success');
    });
});
```

## Deployment

### Production Build

For production deployment:

1. Minify JavaScript files
2. Compress CSS files
3. Optimize images
4. Enable gzip compression
5. Set up CDN for static assets

### Environment Configuration

Configure environment-specific settings:

```javascript
const config = {
    development: {
        apiBaseUrl: 'http://localhost:8000',
        debug: true
    },
    production: {
        apiBaseUrl: 'https://api.example.com',
        debug: false
    }
};
```

## Troubleshooting

### Common Issues

1. **Charts not loading**: Check Highcharts library inclusion
2. **AJAX errors**: Verify CSRF token and API endpoints
3. **Styling issues**: Check CSS file loading order
4. **Module errors**: Ensure proper script loading order

### Debug Mode

Enable debug mode for development:

```javascript
window.SEMR_DEBUG = true;

if (window.SEMR_DEBUG) {
    console.log('Debug mode enabled');
}
```

## Changelog

### Version 2024.1
- Modular JavaScript architecture
- Comprehensive error handling
- Responsive design improvements
- Accessibility enhancements
- Performance optimizations
- Updated documentation
