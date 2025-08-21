/**
 * FinSentiment - Reddit-style Financial Sentiment Analysis
 * Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('FinSentiment initialized');
    
    // Initialize all components
    initVoteButtons();
    initExpandTextButtons();
    initPostActions();
    initCommentActions();
    initFormSubmissions();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Initialize vote buttons (upvote/downvote)
 */
function initVoteButtons() {
    // Get all vote buttons
    const voteButtons = document.querySelectorAll('.vote-button');
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get parent post/comment element
            const parentEl = this.closest('.post, .comment');
            if (!parentEl) return;
            
            // Get vote count element
            const voteCountEl = parentEl.querySelector('.vote-count');
            if (!voteCountEl) return;
            
            // Get current vote count
            let voteCount = parseInt(voteCountEl.textContent);
            
            // Get other vote button in the same container
            const isUpvote = this.classList.contains('upvote');
            const siblingButton = isUpvote 
                ? parentEl.querySelector('.downvote')
                : parentEl.querySelector('.upvote');
            
            // Handle vote logic
            if (this.classList.contains('active')) {
                // User is un-voting
                this.classList.remove('active');
                voteCount += isUpvote ? -1 : 1;
            } else {
                // User is voting
                this.classList.add('active');
                
                // Remove active class from sibling if it has it
                if (siblingButton && siblingButton.classList.contains('active')) {
                    siblingButton.classList.remove('active');
                    voteCount += isUpvote ? 2 : -2;
                } else {
                    voteCount += isUpvote ? 1 : -1;
                }
            }
            
            // Update vote count
            voteCountEl.textContent = voteCount;
            
            // Simulate API call for vote
            const postId = parentEl.dataset.id;
            const voteType = isUpvote ? 'upvote' : 'downvote';
            const active = this.classList.contains('active');
            
            console.log(`Vote ${active ? 'added' : 'removed'}: ${voteType} on post/comment ${postId}`);
        });
    });
}

/**
 * Initialize expand text buttons for long posts
 */
function initExpandTextButtons() {
    const expandButtons = document.querySelectorAll('.expand-button');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get parent post element
            const parentEl = this.closest('.post');
            if (!parentEl) return;
            
            // Get text container
            const textEl = parentEl.querySelector('.post-text');
            if (!textEl) return;
            
            // Get fade element
            const fadeEl = parentEl.querySelector('.post-text-fade');
            
            // Toggle expanded state
            textEl.classList.toggle('expanded');
            
            // Update button text
            if (textEl.classList.contains('expanded')) {
                this.textContent = 'Show less';
                if (fadeEl) fadeEl.style.display = 'none';
            } else {
                this.textContent = 'Read more';
                if (fadeEl) fadeEl.style.display = 'block';
            }
        });
    });
}

/**
 * Initialize post actions (comment, share, save, etc.)
 */
function initPostActions() {
    const postActions = document.querySelectorAll('.post-action');
    
    postActions.forEach(action => {
        action.addEventListener('click', function(e) {
            e.preventDefault();
            
            const actionType = this.dataset.action;
            const postId = this.closest('.post').dataset.id;
            
            // Handle different action types
            switch(actionType) {
                case 'comment':
                    // Scroll to comment form or open comment modal
                    const commentForm = document.getElementById('comment-form');
                    if (commentForm) {
                        commentForm.scrollIntoView({ behavior: 'smooth' });
                        const commentInput = commentForm.querySelector('textarea');
                        if (commentInput) commentInput.focus();
                    }
                    break;
                    
                case 'share':
                    // Copy current URL to clipboard
                    const currentUrl = window.location.href;
                    navigator.clipboard.writeText(currentUrl).then(() => {
                        alert('Link copied to clipboard!');
                    });
                    break;
                    
                case 'save':
                    // Toggle saved state
                    this.classList.toggle('saved');
                    const isSaved = this.classList.contains('saved');
                    
                    // Update icon and text
                    const icon = this.querySelector('i');
                    const text = this.querySelector('span');
                    
                    if (isSaved) {
                        if (icon) icon.className = 'fas fa-bookmark';
                        if (text) text.textContent = 'Saved';
                    } else {
                        if (icon) icon.className = 'far fa-bookmark';
                        if (text) text.textContent = 'Save';
                    }
                    
                    console.log(`Post ${postId} ${isSaved ? 'saved' : 'unsaved'}`);
                    break;
                    
                default:
                    console.log(`Action ${actionType} clicked for post ${postId}`);
            }
        });
    });
}

/**
 * Initialize comment actions (reply, share, report, etc.)
 */
function initCommentActions() {
    const commentActions = document.querySelectorAll('.comment-action');
    
    commentActions.forEach(action => {
        action.addEventListener('click', function(e) {
            e.preventDefault();
            
            const actionType = this.dataset.action;
            const commentId = this.closest('.comment').dataset.id;
            
            // Handle different action types
            switch(actionType) {
                case 'reply':
                    // Show reply form
                    const commentEl = this.closest('.comment');
                    let replyForm = commentEl.querySelector('.reply-form');
                    
                    if (replyForm) {
                        // Toggle form visibility
                        const isVisible = replyForm.style.display !== 'none';
                        replyForm.style.display = isVisible ? 'none' : 'block';
                        
                        if (!isVisible) {
                            // Focus textarea
                            const textarea = replyForm.querySelector('textarea');
                            if (textarea) textarea.focus();
                        }
                    } else {
                        // Create reply form
                        replyForm = document.createElement('div');
                        replyForm.className = 'reply-form mt-2';
                        replyForm.innerHTML = `
                            <textarea class="form-control mb-2" placeholder="What are your thoughts?"></textarea>
                            <div class="d-flex">
                                <button class="btn btn-primary btn-sm">Reply</button>
                                <button class="btn btn-secondary btn-sm ml-2 cancel-reply">Cancel</button>
                            </div>
                        `;
                        
                        // Add after comment actions
                        const actionsEl = this.closest('.comment-actions');
                        actionsEl.after(replyForm);
                        
                        // Focus textarea
                        const textarea = replyForm.querySelector('textarea');
                        if (textarea) textarea.focus();
                        
                        // Add cancel handler
                        const cancelButton = replyForm.querySelector('.cancel-reply');
                        if (cancelButton) {
                            cancelButton.addEventListener('click', function() {
                                replyForm.style.display = 'none';
                            });
                        }
                    }
                    break;
                    
                default:
                    console.log(`Action ${actionType} clicked for comment ${commentId}`);
            }
        });
    });
}

/**
 * Initialize form submissions (search, filters, etc.)
 */
function initFormSubmissions() {
    // Search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (!searchInput || !searchInput.value.trim()) {
                e.preventDefault();
            } else {
                // Show loading spinner when submitting search
                showSpinner('Searching...');
            }
        });
    }
    
    // Filter changes
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Show loading spinner
            showSpinner('Updating filters...');
            
            // Get all current parameters
            const urlParams = new URLSearchParams(window.location.search);
            
            // Update the changed parameter
            urlParams.set(this.name, this.value);
            
            // Redirect with new parameters
            window.location.href = window.location.pathname + '?' + urlParams.toString();
        });
    });
    
    // Add spinner to any forms with data-show-spinner attribute
    document.querySelectorAll('form[data-show-spinner]').forEach(form => {
        form.addEventListener('submit', function() {
            const message = this.getAttribute('data-spinner-message') || 'Processing...';
            showSpinner(message);
        });
    });
}

/**
 * Format a date relative to now (e.g., "5 hours ago")
 */
function formatRelativeDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSeconds < 60) {
        return 'just now';
    } else if (diffMinutes < 60) {
        return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 30) {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
        // Format as MM/DD/YYYY
        return date.toLocaleDateString();
    }
}

/**
 * Get sentiment class based on compound score
 */
function getSentimentClass(score) {
    if (score >= 0.05) {
        return 'sentiment-positive';
    } else if (score <= -0.05) {
        return 'sentiment-negative';
    } else {
        return 'sentiment-neutral';
    }
}

/**
 * Get sentiment text based on compound score
 */
function getSentimentText(score) {
    if (score >= 0.05) {
        return 'Positive';
    } else if (score <= -0.05) {
        return 'Negative';
    } else {
        return 'Neutral';
    }
}

/**
 * Format a number with k/m suffixes for large numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'm';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    } else {
        return num;
    }
}
