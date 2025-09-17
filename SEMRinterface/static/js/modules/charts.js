/**
 * Chart management module for the SEMR interface.
 * 
 * This module provides utilities for creating and managing
 * Highcharts visualizations used in the EMR interface.
 * 
 * @fileoverview Chart management utilities for EMR interface
 * @author SimpleEMRSystem
 * @version 2024.1
 */

/**
 * Chart manager class for handling Highcharts instances
 */
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            chart: {
                backgroundColor: '#ffffff',
                style: {
                    fontFamily: 'Arial, sans-serif'
                }
            },
            credits: {
                enabled: false
            },
            legend: {
                enabled: true
            },
            tooltip: {
                enabled: true
            }
        };
    }

    /**
     * Initialize a chart with the given options
     * @param {string} containerId - The ID of the container element
     * @param {Object} chartOptions - Highcharts configuration options
     * @returns {Object|null} The created chart instance or null if failed
     */
    initializeChart(containerId, chartOptions) {
        try {
            if (!containerId || !document.getElementById(containerId)) {
                console.error(`Chart container '${containerId}' not found`);
                return null;
            }

            const mergedOptions = this.mergeOptions(this.defaultOptions, chartOptions);
            const chart = Highcharts.chart(containerId, mergedOptions);
            this.charts.set(containerId, chart);
            return chart;
        } catch (error) {
            console.error('Failed to initialize chart:', error);
            return null;
        }
    }

    /**
     * Create a line chart
     * @param {string} containerId - The ID of the container element
     * @param {string} title - Chart title
     * @param {Array} categories - X-axis categories
     * @param {Array} seriesData - Chart series data
     * @param {Object} customOptions - Additional chart options
     * @returns {Object|null} The created chart instance
     */
    createLineChart(containerId, title, categories, seriesData, customOptions = {}) {
        const chartOptions = {
            chart: {
                type: 'line',
                ...customOptions.chart
            },
            title: {
                text: title,
                ...customOptions.title
            },
            xAxis: {
                categories: categories,
                title: {
                    text: customOptions.xAxisTitle || 'Time'
                },
                ...customOptions.xAxis
            },
            yAxis: {
                title: {
                    text: customOptions.yAxisTitle || 'Values'
                },
                ...customOptions.yAxis
            },
            series: seriesData,
            ...customOptions
        };

        return this.initializeChart(containerId, chartOptions);
    }

    /**
     * Create a bar chart
     * @param {string} containerId - The ID of the container element
     * @param {string} title - Chart title
     * @param {Array} categories - X-axis categories
     * @param {Array} seriesData - Chart series data
     * @param {Object} customOptions - Additional chart options
     * @returns {Object|null} The created chart instance
     */
    createBarChart(containerId, title, categories, seriesData, customOptions = {}) {
        const chartOptions = {
            chart: {
                type: 'bar',
                ...customOptions.chart
            },
            title: {
                text: title,
                ...customOptions.title
            },
            xAxis: {
                categories: categories,
                title: {
                    text: customOptions.xAxisTitle || 'Categories'
                },
                ...customOptions.xAxis
            },
            yAxis: {
                title: {
                    text: customOptions.yAxisTitle || 'Values'
                },
                ...customOptions.yAxis
            },
            series: seriesData,
            ...customOptions
        };

        return this.initializeChart(containerId, chartOptions);
    }

    /**
     * Create a scatter plot
     * @param {string} containerId - The ID of the container element
     * @param {string} title - Chart title
     * @param {Array} seriesData - Chart series data
     * @param {Object} customOptions - Additional chart options
     * @returns {Object|null} The created chart instance
     */
    createScatterPlot(containerId, title, seriesData, customOptions = {}) {
        const chartOptions = {
            chart: {
                type: 'scatter',
                zoomType: 'xy',
                ...customOptions.chart
            },
            title: {
                text: title,
                ...customOptions.title
            },
            xAxis: {
                title: {
                    text: customOptions.xAxisTitle || 'X-axis'
                },
                ...customOptions.xAxis
            },
            yAxis: {
                title: {
                    text: customOptions.yAxisTitle || 'Y-axis'
                },
                ...customOptions.yAxis
            },
            series: seriesData,
            ...customOptions
        };

        return this.initializeChart(containerId, chartOptions);
    }

    /**
     * Update an existing chart with new data
     * @param {string} containerId - The ID of the chart container
     * @param {Object} newOptions - New chart options
     * @returns {boolean} True if update was successful
     */
    updateChart(containerId, newOptions) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart '${containerId}' not found`);
            return false;
        }

        try {
            chart.update(newOptions);
            return true;
        } catch (error) {
            console.error('Failed to update chart:', error);
            return false;
        }
    }

    /**
     * Destroy a chart
     * @param {string} containerId - The ID of the chart container
     * @returns {boolean} True if destruction was successful
     */
    destroyChart(containerId) {
        const chart = this.charts.get(containerId);
        if (!chart) {
            console.error(`Chart '${containerId}' not found`);
            return false;
        }

        try {
            chart.destroy();
            this.charts.delete(containerId);
            return true;
        } catch (error) {
            console.error('Failed to destroy chart:', error);
            return false;
        }
    }

    /**
     * Get a chart instance
     * @param {string} containerId - The ID of the chart container
     * @returns {Object|null} The chart instance or null if not found
     */
    getChart(containerId) {
        return this.charts.get(containerId) || null;
    }

    /**
     * Merge chart options with defaults
     * @param {Object} defaults - Default options
     * @param {Object} custom - Custom options
     * @returns {Object} Merged options
     * @private
     */
    mergeOptions(defaults, custom) {
        const merged = { ...defaults };
        
        for (const key in custom) {
            if (custom.hasOwnProperty(key)) {
                if (typeof custom[key] === 'object' && custom[key] !== null && !Array.isArray(custom[key])) {
                    merged[key] = this.mergeOptions(merged[key] || {}, custom[key]);
                } else {
                    merged[key] = custom[key];
                }
            }
        }
        
        return merged;
    }

    /**
     * Set time extremes for all charts
     * @param {number} minTime - Minimum time value
     * @param {number} maxTime - Maximum time value
     */
    setTimeExtremes(minTime, maxTime) {
        this.charts.forEach((chart, containerId) => {
            try {
                if (chart && chart.xAxis && chart.xAxis[0]) {
                    chart.xAxis[0].setExtremes(minTime, maxTime);
                }
            } catch (error) {
                console.error(`Failed to set extremes for chart ${containerId}:`, error);
            }
        });
    }

    /**
     * Add a vertical plot line to all charts
     * @param {number} time - Time value for the plot line
     * @param {Object} options - Plot line options
     */
    addVerticalPlotLine(time, options = {}) {
        const defaultOptions = {
            value: time,
            color: 'black',
            dashStyle: 'dash',
            width: 1,
            id: 'plot-line-1'
        };

        const plotLineOptions = { ...defaultOptions, ...options };

        this.charts.forEach((chart, containerId) => {
            try {
                if (chart && chart.xAxis && chart.xAxis[0]) {
                    chart.xAxis[0].addPlotLine(plotLineOptions);
                }
            } catch (error) {
                console.error(`Failed to add plot line to chart ${containerId}:`, error);
            }
        });
    }
}

// Create and export a singleton instance
const chartManager = new ChartManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartManager, chartManager };
} else {
    // Browser environment - attach to window
    window.ChartManager = { ChartManager, chartManager };
}
