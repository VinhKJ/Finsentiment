/**
 * FinSentiment - Chart utilities
 * For sentiment trend analysis
 */

/**
 * Create or update a sentiment trend chart
 * @param {string} canvasId - ID of the canvas element to render the chart on
 * @param {Array} dates - Array of date strings
 * @param {Array} positive - Array of positive sentiment values
 * @param {Array} negative - Array of negative sentiment values
 * @param {Array} neutral - Array of neutral sentiment values
 */
function createSentimentTrendChart(canvasId, dates, positive, negative, neutral) {
    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Create new chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Positive',
                    data: positive,
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    pointBackgroundColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Negative',
                    data: negative,
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    borderColor: 'rgba(244, 67, 54, 1)',
                    pointBackgroundColor: 'rgba(244, 67, 54, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Neutral',
                    data: neutral,
                    backgroundColor: 'rgba(158, 158, 158, 0.2)',
                    borderColor: 'rgba(158, 158, 158, 1)',
                    pointBackgroundColor: 'rgba(158, 158, 158, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Trends Over Time',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += (context.parsed.y * 100).toFixed(1) + '%';
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sentiment Ratio'
                    },
                    min: 0,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100) + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a sentiment distribution pie chart
 * @param {string} canvasId - ID of the canvas element to render the chart on
 * @param {number} positive - Percentage of positive sentiment
 * @param {number} negative - Percentage of negative sentiment
 * @param {number} neutral - Percentage of neutral sentiment
 */
function createSentimentPieChart(canvasId, positive, negative, neutral) {
    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Create new chart
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [positive, negative, neutral],
                backgroundColor: [
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(244, 67, 54, 0.8)',
                    'rgba(158, 158, 158, 0.8)'
                ],
                borderColor: [
                    'rgba(76, 175, 80, 1)',
                    'rgba(244, 67, 54, 1)',
                    'rgba(158, 158, 158, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Distribution',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += context.parsed.toFixed(1) + '%';
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'right',
                }
            },
            cutout: '50%'
        }
    });
}

/**
 * Create a sentiment bar chart for entities
 * @param {string} canvasId - ID of the canvas element to render the chart on
 * @param {Array} labels - Array of entity names
 * @param {Array} scores - Array of compound sentiment scores
 */
function createEntitySentimentChart(canvasId, labels, scores) {
    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Generate colors based on sentiment
    const backgroundColors = scores.map(score => {
        if (score >= 0.05) return 'rgba(76, 175, 80, 0.6)';
        if (score <= -0.05) return 'rgba(244, 67, 54, 0.6)';
        return 'rgba(158, 158, 158, 0.6)';
    });
    
    const borderColors = scores.map(score => {
        if (score >= 0.05) return 'rgba(76, 175, 80, 1)';
        if (score <= -0.05) return 'rgba(244, 67, 54, 1)';
        return 'rgba(158, 158, 158, 1)';
    });
    
    // Create new chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sentiment Score',
                data: scores,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Entity Sentiment Analysis',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Entities'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sentiment Score'
                    },
                    min: -1,
                    max: 1
                }
            }
        }
    });
}

/**
 * Create comment sentiment timeline chart
 * @param {string} canvasId - ID of the canvas element to render the chart on
 * @param {Array} timestamps - Array of timestamps
 * @param {Array} scores - Array of sentiment scores
 */
function createCommentTimelineChart(canvasId, timestamps, scores) {
    // Get canvas element
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Generate colors based on sentiment
    const pointColors = scores.map(score => {
        if (score >= 0.05) return 'rgba(76, 175, 80, 1)';
        if (score <= -0.05) return 'rgba(244, 67, 54, 1)';
        return 'rgba(158, 158, 158, 1)';
    });
    
    // Create new chart
    new Chart(canvas, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Comment Sentiment',
                data: timestamps.map((time, i) => ({
                    x: new Date(time),
                    y: scores[i]
                })),
                backgroundColor: pointColors,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Comment Sentiment Timeline',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            const sentiment = point.y >= 0.05 ? 'Positive' : 
                                             (point.y <= -0.05 ? 'Negative' : 'Neutral');
                            return `${sentiment} (${point.y.toFixed(2)}) at ${new Date(point.x).toLocaleTimeString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sentiment Score'
                    },
                    min: -1,
                    max: 1
                }
            }
        }
    });
}
