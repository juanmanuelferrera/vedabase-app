// Collapse/Expand functionality for Vedabase HTMLs
(function() {
    // Wait for page to load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // Find all outline containers (sections)
        const sections = document.querySelectorAll('div[id^="outline-container-"]');

        sections.forEach(section => {
            const heading = section.querySelector('h2, h3, h4, h5, h6');
            if (!heading) return;

            // Add collapse indicator
            const indicator = document.createElement('span');
            indicator.textContent = '▶ ';
            indicator.style.cssText = 'cursor: pointer; user-select: none; margin-right: 5px; display: inline-block; width: 15px; transition: transform 0.2s;';
            indicator.className = 'collapse-indicator';
            heading.insertBefore(indicator, heading.firstChild);

            // Make heading clickable
            heading.style.cursor = 'pointer';
            heading.style.userSelect = 'none';

            // Find content to collapse (everything except the heading)
            const content = Array.from(section.children).filter(child =>
                child !== heading && child.tagName !== 'H1' && child.tagName !== 'H2' &&
                child.tagName !== 'H3' && child.tagName !== 'H4' &&
                child.tagName !== 'H5' && child.tagName !== 'H6'
            );

            // Initially collapse all content
            content.forEach(el => {
                el.style.display = 'none';
            });

            // Toggle on click
            heading.addEventListener('click', function(e) {
                e.stopPropagation();
                const isCollapsed = content[0]?.style.display === 'none';

                content.forEach(el => {
                    el.style.display = isCollapsed ? '' : 'none';
                });

                // Rotate indicator
                indicator.style.transform = isCollapsed ? 'rotate(90deg)' : 'rotate(0deg)';
            });
        });

        // Add expand/collapse all buttons
        const contentDiv = document.getElementById('content');
        if (contentDiv) {
            const buttonContainer = document.createElement('div');
            buttonContainer.style.cssText = 'position: sticky; top: 10px; z-index: 1000; margin-bottom: 20px; text-align: right;';

            const expandAll = document.createElement('button');
            expandAll.textContent = 'Expand All';
            expandAll.style.cssText = 'margin-right: 10px; padding: 8px 16px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 4px;';
            expandAll.onclick = () => toggleAll(true);

            const collapseAll = document.createElement('button');
            collapseAll.textContent = 'Collapse All';
            collapseAll.style.cssText = 'padding: 8px 16px; cursor: pointer; background: #f44336; color: white; border: none; border-radius: 4px;';
            collapseAll.onclick = () => toggleAll(false);

            buttonContainer.appendChild(expandAll);
            buttonContainer.appendChild(collapseAll);
            contentDiv.insertBefore(buttonContainer, contentDiv.firstChild);
        }
    }

    function toggleAll(expand) {
        const sections = document.querySelectorAll('div[id^="outline-container-"]');
        sections.forEach(section => {
            const heading = section.querySelector('h2, h3, h4, h5, h6');
            const indicator = heading?.querySelector('.collapse-indicator');
            const content = Array.from(section.children).filter(child =>
                child !== heading && child.tagName !== 'H1' && child.tagName !== 'H2' &&
                child.tagName !== 'H3' && child.tagName !== 'H4' &&
                child.tagName !== 'H5' && child.tagName !== 'H6'
            );

            content.forEach(el => {
                el.style.display = expand ? '' : 'none';
            });

            if (indicator) {
                indicator.style.transform = expand ? 'rotate(90deg)' : 'rotate(0deg)';
            }
        });
    }
})();
