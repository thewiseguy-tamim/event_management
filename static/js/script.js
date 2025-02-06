
// Update the existing script section with these functions
function openEventModal(button) {
    const card = button.closest('.bg-white');
    
    // Extract event details from the card
    const title = card.querySelector('h3').textContent;
    const date = card.querySelectorAll('.flex.items-center.text-gray-600')[0].querySelector('span').textContent;
    const location = card.querySelectorAll('.flex.items-center.text-gray-600')[1].querySelector('span').textContent;
    const description = card.querySelector('p.text-gray-600').textContent;
    const imageSrc = card.querySelector('img').src;

    // Populate modal content
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalDate').textContent = date;
    document.getElementById('modalLocation').textContent = location;
    document.getElementById('modalDescription').textContent = description;
    document.getElementById('modalImage').src = imageSrc;

    // Show modal
    document.getElementById('eventModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('eventModal').classList.add('hidden');
}

// Add event listeners to all View Details buttons
document.querySelectorAll('.view-details-button').forEach(button => {
    button.addEventListener('click', function() {
        openEventModal(this);
    });
});

// Close modal when clicking outside
document.getElementById('eventModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Close modal on ESC key press
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !document.getElementById('eventModal').classList.contains('hidden')) {
        closeModal();
    }
});

function toggleFormFields() {
    const entryType = document.getElementById('entryType').value;
    document.getElementById('eventForm').classList.toggle('hidden', entryType !== 'event');
    document.getElementById('participantForm').classList.toggle('hidden', entryType !== 'participant');
    document.getElementById('categoryForm').classList.toggle('hidden', entryType !== 'category');
}

function toggleEventDetails(headerElement) {
    const eventItem = headerElement.closest('.border');
    const detailsSection = eventItem.querySelector('.event-details');
    const chevron = eventItem.querySelector('svg');

    // Toggle details visibility
    detailsSection.classList.toggle('hidden');
    
    // Rotate chevron icon
    chevron.classList.toggle('rotate-180');

    // Close other open event details
    document.querySelectorAll('.event-details').forEach(details => {
        if (details !== detailsSection && !details.classList.contains('hidden')) {
            details.classList.add('hidden');
            details.closest('.border').querySelector('svg').classList.remove('rotate-180');
        }
    });
}
