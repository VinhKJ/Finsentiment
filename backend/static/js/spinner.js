/**
 * Loading Spinner Management
 * 
 * Controls the display of loading spinners when data is being fetched.
 */

// Initialize spinner on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create spinner overlay if it doesn't exist
    if (!document.querySelector('.spinner-overlay')) {
        const spinnerHTML = `
            <div class="spinner-overlay">
                <div class="spinner-container">
                    <img src="/static/images/loading.gif" alt="Loading..." class="spinner-gif">
                    <div class="spinner-message">Loading market data...</div>
                </div>
            </div>
        `;


        document.body.insertAdjacentHTML('beforeend', spinnerHTML);
    }
    
    // Initialize spinner event listeners
    initSpinnerEvents();
});

/**
 * Set up event listeners for spinner interactions
 */
function initSpinnerEvents() {
    // Show spinner for links that fetch data
    document.querySelectorAll('[data-spinner="true"]').forEach(element => {
        element.addEventListener('click', function(e) {
            // Only show spinner for non-ajax navigation
            if(!this.hasAttribute('data-ajax')) {
                showSpinner();
            }
        });
    });
    
    // Show spinner for form submissions
    document.querySelectorAll('form[data-spinner="true"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            showSpinner();
        });
    });
    
    // AJAX request handling with spinner
    document.querySelectorAll('[data-ajax="true"]').forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href') || this.getAttribute('data-url');
            const target = this.getAttribute('data-target');
            const message = this.getAttribute('data-spinner-message') || 'Loading data...';
            
            if (url && target) {
                showSpinner(message);
                
                fetch(url)
                    .then(response => response.text())
                    .then(html => {
                        document.querySelector(target).innerHTML = html;
                        hideSpinner();
                    })
                    .catch(error => {
                        console.error('Fetch error:', error);
                        hideSpinner();
                        showError('Failed to load data. Please try again.');
                    });
            }
        });
    });
}

/**
 * Show the loading spinner with optional custom message
 * @param {string} message - Optional custom loading message
 */
function showSpinner(message = 'Loading market data...') {
    const overlay = document.querySelector('.spinner-overlay');
    const messageElement = document.querySelector('.spinner-message');
    
    if (messageElement) {
        messageElement.textContent = message;
    }
    
    if (overlay) {
        overlay.classList.add('active');
    }
    
    // Prevent scrolling of the body when spinner is shown
    document.body.style.overflow = 'hidden';
}

/**
 * Hide the loading spinner
 */
function hideSpinner() {
    const overlay = document.querySelector('.spinner-overlay');
    
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Re-enable scrolling
    document.body.style.overflow = '';
}

/**
 * Show an error message to the user
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorContainer = document.getElementById('error-container');
    
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    } else {
        // Fallback to alert if error container doesn't exist
        alert(message);
    }
}

/**
 * Add a card spinner to a specific container
 * @param {string} containerId - ID of the container to add spinner to
 */
function addCardSpinner(containerId) {
    const container = document.getElementById(containerId);
    
    if (container) {
        container.innerHTML = `
            <div class="card-spinner-container">
                <div class="card-spinner"></div>
            </div>
        `;
    }
}

/**
 * Add a button spinner to a specific button
 * @param {string} buttonId - ID of the button to add spinner to
 * @param {boolean} disable - Whether to disable the button while spinning
 */
function addButtonSpinner(buttonId, disable = true) {
    const button = document.getElementById(buttonId);
    
    if (button) {
        // Store original button text
        button.setAttribute('data-original-text', button.innerHTML);
        
        // Add spinner and loading text
        button.innerHTML = `<span class="btn-spinner"></span> Analyzing...`;
        
        if (disable) {
            button.disabled = true;
        }
    }
}

/**
 * Remove button spinner and restore original text
 * @param {string} buttonId - ID of the button to remove spinner from
 * @param {boolean} enable - Whether to enable the button after removing spinner
 */
function removeButtonSpinner(buttonId, enable = true) {
    const button = document.getElementById(buttonId);
    
    if (button) {
        // Restore original button text
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
        
        if (enable) {
            button.disabled = false;
        }
    }
}