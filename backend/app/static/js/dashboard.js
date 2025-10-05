// Dashboard JavaScript utilities
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh upcoming flights countdown
    updateFlightCountdowns();
    setInterval(updateFlightCountdowns, 60000); // Update every minute

    // Auto-refresh page every 30 seconds to check for payment status updates
    setTimeout(function() {
        // Only refresh if there are pending payments
        const pendingPayments = document.querySelectorAll('.badge:contains("Ожидает оплаты")');
        if (pendingPayments.length > 0) {
            window.location.reload();
        }
    }, 30000);

    // Enhanced tooltips for cancellation policy
    initializeTooltips();

    // Confirmation dialogs with enhanced messaging
    setupCancellationDialogs();
});

function updateFlightCountdowns() {
    const now = new Date();
    const countdownElements = document.querySelectorAll('[data-departure-time]');
    
    countdownElements.forEach(function(element) {
        const departureTime = new Date(element.dataset.departureTime);
        const timeDiff = departureTime - now;
        
        if (timeDiff > 0) {
            const hours = Math.floor(timeDiff / (1000 * 60 * 60));
            const days = Math.floor(hours / 24);
            const remainingHours = hours % 24;
            
            let countdownText = '';
            if (days > 0) {
                countdownText = `${days}d ${remainingHours}h`;
            } else if (hours > 0) {
                countdownText = `${hours}h`;
            } else {
                const minutes = Math.floor(timeDiff / (1000 * 60));
                countdownText = `${minutes}m`;
            }
            
            element.textContent = `Departs in ${countdownText}`;
            
            // Update refund eligibility indicator
            const refundIndicator = element.closest('tr').querySelector('.refund-indicator');
            if (refundIndicator) {
                if (hours >= 24) {
                    refundIndicator.className = 'badge bg-success refund-indicator';
                    refundIndicator.innerHTML = '<i class="fas fa-check"></i> Refundable';
                } else {
                    refundIndicator.className = 'badge bg-warning refund-indicator';
                    refundIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Non-refundable';
                }
            }
        }
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupCancellationDialogs() {
    const cancelButtons = document.querySelectorAll('[data-bs-target^="#cancelModal"]');
    
    cancelButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const modalId = this.dataset.bsTarget;
            const modal = document.querySelector(modalId);
            
            if (modal) {
                // Add loading state simulation
                const confirmButton = modal.querySelector('.btn-success, .btn-danger');
                if (confirmButton) {
                    confirmButton.addEventListener('click', function() {
                        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                        this.disabled = true;
                    });
                }
            }
        });
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Enhanced search functionality for ticket filtering
function setupTicketFiltering() {
    const searchInput = document.getElementById('ticketSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const ticketRows = document.querySelectorAll('#ticketsTable tbody tr');
            
            ticketRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}