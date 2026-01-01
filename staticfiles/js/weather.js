/**
 * AI Weather Prediction System - JavaScript
 * Enhanced interactivity and animations
 */

// Global variables
let weatherChart = null;
let animationFrameId = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize components based on current page
    const currentPage = getCurrentPage();
    
    switch(currentPage) {
        case 'home':
            initializeHomePage();
            break;
        case 'predict':
            initializePredictPage();
            break;
        case 'result':
            initializeResultPage();
            break;
        case 'history':
            initializeHistoryPage();
            break;
    }
    
    // Initialize common components
    initializeCommonComponents();
}

/**
 * Get current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/' || path.includes('home')) return 'home';
    if (path.includes('predict')) return 'predict';
    if (path.includes('result')) return 'result';
    if (path.includes('history')) return 'history';
    
    return 'unknown';
}

/**
 * Initialize common components across all pages
 */
function initializeCommonComponents() {
    // Smooth scrolling for anchor links
    initializeSmoothScrolling();
    
    // Enhanced tooltips
    initializeTooltips();
    
    // Navbar scroll effects
    initializeNavbarEffects();
    
    // Loading states for buttons
    initializeButtonLoadingStates();
    
    // Form enhancements
    initializeFormEnhancements();
    
    // Weather animations
    initializeWeatherAnimations();
}

/**
 * Initialize home page specific features
 */
function initializeHomePage() {
    // Parallax scrolling effect
    initializeParallaxScrolling();
    
    // Counter animations
    initializeCounterAnimations();
    
    // Feature card hover effects
    initializeFeatureCardEffects();
    
    // Hero section animations
    initializeHeroAnimations();
}

/**
 * Initialize predict page specific features
 */
function initializePredictPage() {
    // City input enhancements
    initializeCityInput();
    
    // Form validation
    initializePredictFormValidation();
    
    // Loading modal
    initializeLoadingModal();
    
    // Auto-suggestions
    initializeCitySuggestions();
}

/**
 * Initialize result page specific features
 */
function initializeResultPage() {
    // Result animations
    initializeResultAnimations();
    
    // Weather comparison charts
    initializeWeatherCharts();
    
    // Interactive elements
    initializeResultInteractions();
}

/**
 * Initialize history page specific features
 */
function initializeHistoryPage() {
    // Table enhancements
    initializeHistoryTable();
    
    // Search and filter
    initializeHistoryFilters();
    
    // Export functionality
    initializeExportFeatures();
}

/**
 * Smooth scrolling for anchor links
 */
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Initialize enhanced tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Navbar scroll effects
 */
function initializeNavbarEffects() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add/remove scrolled class
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

/**
 * Button loading states
 */
function initializeButtonLoadingStates() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                setButtonLoading(submitBtn, true);
            }
        });
    });
}

/**
 * Set button loading state
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }
}

/**
 * Form enhancements
 */
function initializeFormEnhancements() {
    // Real-time validation
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // City name validation
    if (field.name === 'city' && value) {
        const cityPattern = /^[a-zA-Z\s\-']+$/;
        if (!cityPattern.test(value) || value.length < 2) {
            isValid = false;
            errorMessage = 'Please enter a valid city name (letters only, minimum 2 characters).';
        }
    }
    
    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Update error message
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = errorMessage;
        }
    }
    
    return isValid;
}

/**
 * Weather animations
 */
function initializeWeatherAnimations() {
    // Floating weather icons
    const weatherIcons = document.querySelectorAll('.weather-icon-large i, .weather-icon i');
    
    weatherIcons.forEach(icon => {
        let startTime = Date.now() + Math.random() * 2000;
        
        function animateIcon() {
            const elapsed = Date.now() - startTime;
            const y = Math.sin(elapsed / 1000) * 5;
            const rotation = Math.sin(elapsed / 2000) * 10;
            
            icon.style.transform = `translateY(${y}px) rotate(${rotation}deg)`;
            
            requestAnimationFrame(animateIcon);
        }
        
        animateIcon();
    });
}

/**
 * Parallax scrolling effect
 */
function initializeParallaxScrolling() {
    const parallaxElements = document.querySelectorAll('.weather-animation');
    
    if (parallaxElements.length === 0) return;
    
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        parallaxElements.forEach(element => {
            element.style.transform = `translateY(${rate}px)`;
        });
    });
}

/**
 * Counter animations
 */
function initializeCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

/**
 * Animate counter
 */
function animateCounter(element) {
    const target = element.textContent;
    const isPercentage = target.includes('%');
    const isTime = target.includes('/');
    
    if (isTime || target === 'AI') return; // Skip non-numeric counters
    
    const numericTarget = parseInt(target.replace(/\D/g, ''));
    const duration = 2000;
    const startTime = Date.now();
    
    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(numericTarget * easeOutQuart(progress));
        element.textContent = currentValue + (isPercentage ? '%' : '');
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    updateCounter();
}

/**
 * Easing function
 */
function easeOutQuart(t) {
    return 1 - (--t) * t * t * t;
}

/**
 * Feature card hover effects
 */
function initializeFeatureCardEffects() {
    const featureCards = document.querySelectorAll('.feature-card, .step-card, .info-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

/**
 * Hero section animations
 */
function initializeHeroAnimations() {
    const heroElements = document.querySelectorAll('.hero-content > *');
    
    heroElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'all 0.8s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

/**
 * City input enhancements
 */
function initializeCityInput() {
    const cityInput = document.getElementById('city');
    if (!cityInput) return;
    
    // Auto-focus
    cityInput.focus();
    
    // Enter key support
    cityInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const form = this.closest('form');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });
    
    // Clear button
    addClearButton(cityInput);
}

/**
 * Add clear button to input
 */
function addClearButton(input) {
    const inputGroup = input.closest('.input-group');
    if (!inputGroup) return;
    
    const clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'btn btn-outline-secondary';
    clearBtn.innerHTML = '<i class="fas fa-times"></i>';
    clearBtn.style.display = 'none';
    
    clearBtn.addEventListener('click', function() {
        input.value = '';
        input.focus();
        this.style.display = 'none';
        input.classList.remove('is-valid', 'is-invalid');
    });
    
    input.addEventListener('input', function() {
        clearBtn.style.display = this.value ? 'block' : 'none';
    });
    
    inputGroup.appendChild(clearBtn);
}

/**
 * Predict form validation
 */
function initializePredictFormValidation() {
    const form = document.getElementById('predictionForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        let isValid = true;
        
        // Validate all fields
        const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        if (isValid) {
            submitPredictionForm();
        }
        
        form.classList.add('was-validated');
    });
}

/**
 * Submit prediction form
 */
function submitPredictionForm() {
    const form = document.getElementById('predictionForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Show loading state
    setButtonLoading(submitBtn, true);
    
    // Show loading modal
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(loadingModal);
        modal.show();
    }
    
    // Submit form after short delay for UX
    setTimeout(() => {
        form.submit();
    }, 1000);
}

/**
 * Loading modal
 */
function initializeLoadingModal() {
    const loadingModal = document.getElementById('loadingModal');
    if (!loadingModal) return;
    
    // Add loading animation
    const modalBody = loadingModal.querySelector('.modal-body');
    if (modalBody) {
        const dots = document.createElement('div');
        dots.className = 'loading-dots mt-3';
        dots.innerHTML = '<span></span><span></span><span></span>';
        modalBody.appendChild(dots);
        
        // Animate dots
        let dotIndex = 0;
        setInterval(() => {
            const dotElements = dots.querySelectorAll('span');
            dotElements.forEach((dot, index) => {
                dot.style.opacity = index === dotIndex ? '1' : '0.3';
            });
            dotIndex = (dotIndex + 1) % 3;
        }, 500);
    }
}

/**
 * City suggestions
 */
function initializeCitySuggestions() {
    const cityInput = document.getElementById('city');
    if (!cityInput) return;
    
    const popularCities = [
        'London', 'New York', 'Tokyo', 'Paris', 'Sydney', 'Mumbai', 'Berlin',
        'Toronto', 'Dubai', 'Singapore', 'Los Angeles', 'Chicago', 'Madrid',
        'Rome', 'Amsterdam', 'Barcelona', 'Moscow', 'Istanbul', 'Bangkok',
        'Seoul', 'Hong Kong', 'Vienna', 'Prague', 'Budapest', 'Warsaw'
    ];
    
    // Create suggestions dropdown
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'suggestions-dropdown glass-card';
    suggestionsContainer.style.display = 'none';
    cityInput.parentNode.appendChild(suggestionsContainer);
    
    cityInput.addEventListener('input', function() {
        const value = this.value.toLowerCase().trim();
        
        if (value.length >= 2) {
            const suggestions = popularCities.filter(city =>
                city.toLowerCase().includes(value)
            ).slice(0, 5);
            
            if (suggestions.length > 0) {
                showSuggestions(suggestions, suggestionsContainer, cityInput);
            } else {
                hideSuggestions(suggestionsContainer);
            }
        } else {
            hideSuggestions(suggestionsContainer);
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!cityInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            hideSuggestions(suggestionsContainer);
        }
    });
}

/**
 * Show city suggestions
 */
function showSuggestions(suggestions, container, input) {
    container.innerHTML = '';
    
    suggestions.forEach(city => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = city;
        
        item.addEventListener('click', function() {
            input.value = city;
            hideSuggestions(container);
            validateField(input);
        });
        
        container.appendChild(item);
    });
    
    container.style.display = 'block';
}

/**
 * Hide city suggestions
 */
function hideSuggestions(container) {
    container.style.display = 'none';
}

/**
 * Result page animations
 */
function initializeResultAnimations() {
    // Animate prediction cards
    const predictionItems = document.querySelectorAll('.prediction-item');
    predictionItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(50px)';
        item.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 300);
    });
    
    // Animate progress bars
    setTimeout(() => {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            bar.style.transition = 'width 1.5s ease-in-out';
            
            setTimeout(() => {
                bar.style.width = width;
            }, 200);
        });
    }, 1500);
}

/**
 * Weather comparison charts
 */
function initializeWeatherCharts() {
    // This would integrate with Chart.js if needed
    // For now, we'll use CSS animations for the progress bars
    const progressBars = document.querySelectorAll('.confidence-item .progress-bar');
    
    progressBars.forEach(bar => {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateProgressBar(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(bar);
    });
}

/**
 * Animate progress bar
 */
function animateProgressBar(bar) {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    
    setTimeout(() => {
        bar.style.transition = 'width 1s ease-out';
        bar.style.width = targetWidth;
    }, 100);
}

/**
 * Result interactions
 */
function initializeResultInteractions() {
    // Add click-to-copy functionality for values
    const copyableValues = document.querySelectorAll('.prediction-value, .feature-value');
    
    copyableValues.forEach(value => {
        value.style.cursor = 'pointer';
        value.title = 'Click to copy';
        
        value.addEventListener('click', function() {
            copyToClipboard(this.textContent);
            showCopyFeedback(this);
        });
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

/**
 * Show copy feedback
 */
function showCopyFeedback(element) {
    const originalText = element.textContent;
    element.textContent = 'Copied!';
    element.style.color = '#4facfe';
    
    setTimeout(() => {
        element.textContent = originalText;
        element.style.color = '';
    }, 1000);
}

/**
 * History table enhancements
 */
function initializeHistoryTable() {
    const table = document.querySelector('.glass-table');
    if (!table) return;
    
    // Add row hover effects
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        });
    });
    
    // Add sorting functionality
    const headers = table.querySelectorAll('th');
    headers.forEach(header => {
        if (header.textContent.trim()) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, Array.from(headers).indexOf(this));
            });
        }
    });
}

/**
 * Sort table by column
 */
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = table.dataset.sortOrder !== 'asc';
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers first
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * History filters
 */
function initializeHistoryFilters() {
    // Add search functionality
    addHistorySearch();
    
    // Add date filters
    addDateFilters();
}

/**
 * Add search to history
 */
function addHistorySearch() {
    const tableContainer = document.querySelector('.history-table-container');
    if (!tableContainer) return;
    
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container mb-3';
    searchContainer.innerHTML = `
        <div class="input-group">
            <span class="input-group-text glass-input">
                <i class="fas fa-search"></i>
            </span>
            <input type="text" class="form-control glass-input" id="historySearch" placeholder="Search predictions...">
        </div>
    `;
    
    tableContainer.insertBefore(searchContainer, tableContainer.firstChild);
    
    const searchInput = document.getElementById('historySearch');
    searchInput.addEventListener('input', function() {
        filterHistoryTable(this.value);
    });
}

/**
 * Filter history table
 */
function filterHistoryTable(searchTerm) {
    const table = document.querySelector('.glass-table');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

/**
 * Add date filters
 */
function addDateFilters() {
    // Implementation for date range filtering
    // This would add date picker inputs to filter by date range
}

/**
 * Export features
 */
function initializeExportFeatures() {
    // Add export button to history page
    const tableActions = document.querySelector('.table-actions');
    if (!tableActions) return;
    
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn btn-outline-success btn-sm';
    exportBtn.innerHTML = '<i class="fas fa-download me-1"></i>Export CSV';
    exportBtn.addEventListener('click', exportHistoryToCSV);
    
    tableActions.appendChild(exportBtn);
}

/**
 * Export history to CSV
 */
function exportHistoryToCSV() {
    const table = document.querySelector('.glass-table');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csvContent = [];
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        const rowData = Array.from(cells).map(cell => {
            return '"' + cell.textContent.trim().replace(/"/g, '""') + '"';
        });
        csvContent.push(rowData.join(','));
    });
    
    const csvString = csvContent.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'weather_predictions_' + new Date().toISOString().split('T')[0] + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Utility functions
 */

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show glass-alert notification`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notification.style.position = 'fixed';
    notification.style.top = '100px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // You could send this to a logging service
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page Load Time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }, 0);
    });
}