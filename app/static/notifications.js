/**
 * Notifications handling for Brama-UA e.V
 * Handles WebSocket-based notifications for founders
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if the user is logged in and is a founder
    const isFounder = document.body.classList.contains('founder-user');
    
    if (isFounder) {
        initNotifications();
    }
});

/**
 * Initialize WebSocket connection for notifications
 */
function initNotifications() {
    // Create socket connection if it doesn't exist
    if (!window.socket) {
        window.socket = io();
        
        // Setup event handlers
        window.socket.on('connect', function() {
            console.log('Connected to notification system');
        });
        
        window.socket.on('notification', function(data) {
            handleNotification(data);
        });
        
        window.socket.on('disconnect', function() {
            console.log('Disconnected from notification system');
        });
        
        window.socket.on('connect_error', function(error) {
            console.error('Connection error:', error);
        });
    }
}

/**
 * Handle incoming notifications
 * @param {Object} data - Notification data
 */
function handleNotification(data) {
    if (data.type === 'new_agenda_item') {
        showNewAgendaItemNotification(data);
    }
}

/**
 * Show notification about new agenda item
 * @param {Object} data - Notification data
 */
function showNewAgendaItemNotification(data) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'toast show';
    notification.role = 'alert';
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    // Create header with meeting title
    const header = document.createElement('div');
    header.className = 'toast-header';
    header.innerHTML = `
        <i class="fas fa-list-alt text-primary me-2"></i>
        <strong class="me-auto">${data.meeting_title}</strong>
        <small>${data.created_at}</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    `;
    
    // Create body with agenda item info
    const body = document.createElement('div');
    body.className = 'toast-body';
    
    const votingBadge = data.requires_voting ? 
        '<span class="badge bg-warning ms-2">Requires Voting</span>' : '';
    
    body.innerHTML = `
        <p>New agenda item added: <strong>${data.agenda_item_title}</strong> ${votingBadge}</p>
        <div class="mt-2 pt-2 border-top">
            <a href="/meetings/${data.meeting_id}" class="btn btn-sm btn-primary">
                View Meeting
            </a>
        </div>
    `;
    
    // Combine elements
    notification.appendChild(header);
    notification.appendChild(body);
    
    // Create or get notification container
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Add notification to container
    container.appendChild(notification);
    
    // Create toast instance and show it
    const toast = new bootstrap.Toast(notification, {
        autohide: false
    });
    toast.show();
    
    // Play notification sound if available
    playNotificationSound();
}

/**
 * Play a notification sound
 */
function playNotificationSound() {
    const audio = new Audio('/static/notification-sound.mp3');
    audio.volume = 0.5;
    audio.play().catch(error => {
        // Browser may block autoplay
        console.log('Could not play notification sound:', error);
    });
}
