document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dash-dropdown select');

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('keydown', function(event) {
            if (event.shiftKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
                event.preventDefault();
                const options = Array.from(dropdown.options);
                const currentIndex = dropdown.selectedIndex;

                let startIndex = dropdown.dataset.startIndex !== undefined ? parseInt(dropdown.dataset.startIndex) : currentIndex;
                let endIndex = event.key === 'ArrowDown' ? Math.min(options.length - 1, currentIndex + 1) : Math.max(0, currentIndex - 1);
                
                // Update selected options based on startIndex and endIndex
                if (startIndex !== endIndex) {
                    const [minIndex, maxIndex] = [Math.min(startIndex, endIndex), Math.max(startIndex, endIndex)];
                    for (let i = minIndex; i <= maxIndex; i++) {
                        options[i].selected = true;
                    }
                    dropdown.dataset.startIndex = endIndex;
                }
                
                // Trigger a change event to update Dash callbacks
                const changeEvent = new Event('change', { bubbles: true });
                dropdown.dispatchEvent(changeEvent);
            } else if (!event.shiftKey) {
                dropdown.dataset.startIndex = undefined;
            }
        });
    });
});
