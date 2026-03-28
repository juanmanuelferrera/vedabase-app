// Smart TOC collapse + Lecture heading injection + Verse grouping v3.1
(function() {
    'use strict';

    // Inject CSS to hide all nested ULs by default
    const style = document.createElement('style');
    style.id = 'toc-collapse-style';
    style.textContent = `
        /* TOC hidden by default — parent app shows it via inline styles */
        #table-of-contents {
            display: none !important;
            position: absolute !important;
            left: -9999px !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        #content {
            margin-left: 0 !important;
        }
        #postamble {
            margin-left: 0 !important;
        }
        body.dark-mode #table-of-contents {
            background: #111 !important;
            border-right-color: #2a2a2a !important;
        }

        /* Hide ALL nested ULs in TOC */
        #text-table-of-contents ul ul {
            display: none !important;
        }

        /* Show when parent LI has 'expanded' class */
        #text-table-of-contents li.expanded > ul {
            display: block !important;
        }

        /* Indicator styles */
        .toc-indicator {
            display: inline-block;
            margin-right: 5px;
            transition: transform 0.2s;
            color: #ea580c;
            font-weight: bold;
            cursor: pointer;
        }

        li.expanded > .toc-indicator {
            transform: rotate(90deg);
        }

        /* Make collapsible items obvious */
        #text-table-of-contents li:has(> ul) > a {
            cursor: pointer;
            font-weight: 500;
        }

        /* Active TOC link highlighting */
        #text-table-of-contents a.toc-active {
            background: #fed7aa;
            color: #9a3412;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }

        /* Verse lines grouped by JS into .verse-group */
        .verse-group {
            margin-bottom: 16px;
        }
        .verse-group p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.8;
            font-style: italic;
        }
        .verse-group .stanza-break {
            margin-top: 12px !important;
        }
        /* Section labels (SYNONYMS, TRANSLATION, PURPORT) */
        .section-label {
            font-weight: 700 !important;
            margin-top: 16px !important;
            margin-bottom: 4px !important;
        }

        /* Injected lecture headings */
        h4.lecture-heading {
            font-size: 1em;
            font-weight: 600;
            color: #9a3412;
            margin: 1.5em 0 0.3em;
            padding: 4px 0;
            border-bottom: 1px solid #fed7aa;
        }
        body.dark-mode h4.lecture-heading {
            color: #fb923c;
            border-bottom-color: #44403c;
        }
        /* Section headings (Bg 1:, Canto 2:, etc.) */
        h3.lecture-section {
            font-size: 1.15em;
            font-weight: 700;
            color: #7c2d12;
            margin: 2em 0 0.5em;
            padding: 6px 0;
            border-bottom: 2px solid #ea580c;
        }
        body.dark-mode h3.lecture-section {
            color: #fb923c;
            border-bottom-color: #fb923c;
        }
    `;

    if (document.head) {
        document.head.appendChild(style);
    }

    // ========== Verse grouping ==========
    function isVerseLine(text) {
        if (!text || text.length === 0 || text.length >= 80) return false;
        if (/^(SYNONYMS|TRANSLATION|PURPORT)$/.test(text)) return false;
        if (text.endsWith('.') || text.includes(';')) return false;
        return true;
    }

    function groupVerseLines() {
        const sections = document.querySelectorAll('.outline-text-3, .outline-text-4, .outline-text-5');

        sections.forEach(section => {
            // Tag section labels
            section.querySelectorAll('p').forEach(p => {
                const t = p.textContent.trim();
                if (/^(SYNONYMS|TRANSLATION|PURPORT)$/.test(t)) {
                    p.classList.add('section-label');
                }
            });

            // Collect runs of verse lines and group them
            let p = section.firstElementChild;
            while (p) {
                if (p.tagName === 'P' && isVerseLine(p.textContent.trim())) {
                    // Start a verse group
                    const group = document.createElement('div');
                    group.className = 'verse-group';
                    section.insertBefore(group, p);

                    // Move consecutive verse <p>s into the group
                    while (p && p.tagName === 'P' && isVerseLine(p.textContent.trim())) {
                        const next = p.nextElementSibling;
                        group.appendChild(p);
                        p = next;
                    }

                    // Add stanza breaks every 4 lines
                    // Add stanza breaks: groups of 4 verse lines
                    // Speaker line (uvāca etc) sticks to the next 4 lines (group of 5)
                    // Then every 4 lines after. Remainder < 4 stays with last group.
                    const lines = Array.from(group.querySelectorAll('p'));
                    if (lines.length > 4) {
                        // If not a multiple of 4, absorb the remainder into the first group
                        const remainder = lines.length % 4;
                        const firstGroup = remainder === 0 ? 4 : remainder + 4;
                        for (let j = firstGroup; j < lines.length; j += 4) {
                            lines[j].classList.add('stanza-break');
                        }
                    }
                } else {
                    p = p.nextElementSibling;
                }
            }
        });
    }

    // ========== Generate TOC for pages that don't have one ==========
    function generateMissingTOC() {
        // If there's already a TOC with multiple items, skip
        const existingTOC = document.getElementById('text-table-of-contents');
        if (existingTOC) {
            const items = existingTOC.querySelectorAll('li');
            if (items.length > 1) return;
        }

        // Find all h2/h3 with IDs in the content
        const content = document.getElementById('content') || document.body;
        const headings = content.querySelectorAll('h2[id], h3[id]');
        if (headings.length < 2) return;

        // Create TOC container if it doesn't exist
        let tocDiv = document.getElementById('table-of-contents');
        let tocText = document.getElementById('text-table-of-contents');
        if (!tocDiv) {
            tocDiv = document.createElement('div');
            tocDiv.id = 'table-of-contents';
            tocDiv.setAttribute('role', 'doc-toc');
            const h2 = document.createElement('h2');
            h2.textContent = 'Table of Contents';
            tocDiv.appendChild(h2);
            tocText = document.createElement('div');
            tocText.id = 'text-table-of-contents';
            tocText.setAttribute('role', 'doc-toc');
            tocDiv.appendChild(tocText);
            document.body.insertBefore(tocDiv, content);
        }
        if (!tocText) return;

        const ul = document.createElement('ul');
        headings.forEach(h => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = h.textContent.trim();
            li.appendChild(a);
            ul.appendChild(li);
        });
        tocText.innerHTML = '';
        tocText.appendChild(ul);
    }

    // ========== Lecture heading injection ==========
    function injectLectureHeadings() {
        // Run on lecture/conversation/letter pages — detect by title or content
        const title = document.title || '';
        const isLecturePage = /lecture|conversation|letter|conv\d|missing_conv/i.test(title);
        if (!isLecturePage) return;

        const content = document.getElementById('content') || document.body;
        if (!content) return;

        // Pattern: single-line <p> containing "– City, Date" (lecture title pattern)
        // Section headers: start with "Bg X:", "Canto X:", "Festival", "General", "Arrival", "Initiation", "Wedding", "Funeral"
        const sectionPattern = /^(Bhagavad-gita Lectures Bg|Bg \d+:|Canto \d+:|SB Lectures|Festival Lectures|General Lectures|Arrival Address|Initiations|Wedding Ceremon|Funeral Lecture)/;
        const lecturePattern = /\u2013|&#x2013;/; // em-dash separates title from location

        const paragraphs = content.querySelectorAll('p');
        let injectedCount = 0;
        let idCounter = 0;

        paragraphs.forEach(p => {
            // Quick check: skip long innerHTML (body text)
            if (p.innerHTML.length > 300 || p.innerHTML.length < 10) return;

            // Must contain em-dash
            if (!lecturePattern.test(p.innerHTML)) return;

            const text = p.textContent.trim();
            if (!text || text.length > 200 || text.length < 10) return;
            if ((text.match(/\./g) || []).length > 3) return;

            // Determine if it's a section header or individual lecture
            const isSection = sectionPattern.test(text);

            const id = 'lec-' + (idCounter++);

            // Create heading element
            const heading = document.createElement(isSection ? 'h3' : 'h4');
            heading.id = id;
            heading.className = isSection ? 'lecture-section' : 'lecture-heading';
            heading.textContent = text;

            // Replace the <p> with the heading
            p.parentNode.replaceChild(heading, p);
            injectedCount++;
        });

        if (injectedCount > 0) {
            console.log(`✓ Injected ${injectedCount} lecture headings`);
            // Rebuild TOC from injected headings
            rebuildTOC();
        }
    }

    function rebuildTOC() {
        const tocContainer = document.getElementById('text-table-of-contents');
        if (!tocContainer) return;

        const sections = document.querySelectorAll('h3.lecture-section');
        const lectures = document.querySelectorAll('h4.lecture-heading');
        if (sections.length === 0 && lectures.length === 0) return;

        // Build hierarchical TOC: sections contain lectures
        const ul = document.createElement('ul');
        let currentSectionLi = null;
        let currentSubUl = null;

        // Get all headings in order
        const allHeadings = document.querySelectorAll('h3.lecture-section, h4.lecture-heading');

        allHeadings.forEach(h => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = h.textContent;
            li.appendChild(a);

            if (h.tagName === 'H3') {
                // Section heading — top level
                currentSubUl = document.createElement('ul');
                li.appendChild(currentSubUl);
                ul.appendChild(li);
                currentSectionLi = li;
            } else {
                // Lecture heading — nested under current section
                if (currentSubUl) {
                    currentSubUl.appendChild(li);
                } else {
                    ul.appendChild(li);
                }
            }
        });

        tocContainer.innerHTML = '';
        tocContainer.appendChild(ul);
    }

    // ========== TOC collapse ==========
    function collapseAll(parentLI) {
        parentLI.classList.remove('expanded');
        const descendants = parentLI.querySelectorAll('li.expanded');
        descendants.forEach(li => li.classList.remove('expanded'));
    }

    function toggleItem(li, link, hasChildren) {
        if (!hasChildren) return true;

        const wasExpanded = li.classList.contains('expanded');
        if (wasExpanded) {
            collapseAll(li);
        } else {
            li.classList.add('expanded');
        }
        return false;
    }

    function setupTOC() {
        const toc = document.getElementById('text-table-of-contents');
        if (!toc) return;

        const allLIs = toc.querySelectorAll('li');
        let setupCount = 0;

        allLIs.forEach((li) => {
            const hasNestedUL = li.querySelector(':scope > ul');
            const link = li.querySelector(':scope > a');
            if (!link) return;
            if (li.dataset.tocSetup === 'true') return;
            li.dataset.tocSetup = 'true';

            if (hasNestedUL) {
                setupCount++;

                if (!li.querySelector('.toc-indicator')) {
                    const indicator = document.createElement('span');
                    indicator.className = 'toc-indicator';
                    indicator.textContent = '▶ ';
                    li.insertBefore(indicator, li.firstChild);
                }

                link.style.userSelect = 'none';

                const clickHandler = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleItem(li, link, true);
                };

                const newLink = link.cloneNode(true);
                link.parentNode.replaceChild(newLink, link);
                newLink.addEventListener('click', clickHandler);

                const indicator = li.querySelector('.toc-indicator');
                if (indicator) {
                    const newIndicator = indicator.cloneNode(true);
                    indicator.parentNode.replaceChild(newIndicator, indicator);
                    newIndicator.addEventListener('click', clickHandler);
                }
            }
        });
    }

    // Run setup
    function expandFirstLevel() {
        const toc = document.getElementById('text-table-of-contents');
        if (!toc) return;
        // Expand all first-level LIs so content is visible
        const topLIs = toc.querySelectorAll(':scope > ul > li');
        topLIs.forEach(li => li.classList.add('expanded'));
    }

    // ========== Hide inline TOC sections ==========
    // Force-fix layout: reset margins, hide TOC unless parent says otherwise
    function fixLayout() {
        // If parent app has set data-toc-visible, don't override
        if (document.body.dataset.tocVisible === 'true') return;

        const content = document.getElementById('content');
        if (content) {
            content.style.setProperty('margin-left', '0', 'important');
            content.style.setProperty('max-width', '100%', 'important');
            content.style.setProperty('width', '100%', 'important');
            content.style.setProperty('box-sizing', 'border-box', 'important');
        }
        const toc = document.getElementById('table-of-contents');
        if (toc) {
            toc.style.setProperty('display', 'none', 'important');
            toc.style.setProperty('width', '0', 'important');
            toc.style.setProperty('height', '0', 'important');
            toc.style.setProperty('position', 'absolute', 'important');
            toc.style.setProperty('left', '-9999px', 'important');
        }
        const postamble = document.getElementById('postamble');
        if (postamble) postamble.style.setProperty('margin-left', '0', 'important');
        const toggle = document.getElementById('toggle-sidebar');
        if (toggle) toggle.style.setProperty('display', 'none', 'important');
        // Kill ALL fixed-position elements that might expand viewport
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            if (cs.position === 'fixed' && el.id !== 'content-frame') {
                el.style.setProperty('position', 'absolute', 'important');
            }
        });
        document.body.style.setProperty('overflow-x', 'hidden', 'important');
        document.documentElement.style.setProperty('overflow-x', 'hidden', 'important');
    }
    // Run after DOM + readtheorg.js
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { fixLayout(); setTimeout(fixLayout, 500); });
    } else {
        fixLayout();
        setTimeout(fixLayout, 500);
    }

    function hideInlineTOC() {
        // Hide any h2 section titled "Table of Contents" in the content
        const headings = document.querySelectorAll('h2');
        headings.forEach(h => {
            if (h.textContent.trim() === 'Table of Contents') {
                // Hide the entire outline-container parent
                const container = h.closest('.outline-2');
                if (container) {
                    container.style.display = 'none';
                } else {
                    // No container — hide the h2 and its sibling div
                    h.style.display = 'none';
                    const next = h.nextElementSibling;
                    if (next && next.classList.contains('outline-text-2')) {
                        next.style.display = 'none';
                    }
                }
            }
        });
    }

    function runSetup() {
        const title = (document.title || '').toLowerCase();
        const isBook = /gita|bhagavat|carit|krsna|kṛṣṇa|other/i.test(title);
        const isLecture = /lecture/i.test(title);
        const isConvOrLetter = /conversation|letter|conv/i.test(title);

        fixLayout();
        hideInlineTOC();

        if (isConvOrLetter) {
            // Conversations/letters: minimal setup — just expand TOC
            expandFirstLevel();
            return;
        }

        if (isLecture) {
            // Lectures: inject headings + rebuild TOC, but defer to avoid blocking
            setTimeout(() => {
                injectLectureHeadings();
                expandFirstLevel();
            }, 100);
            return;
        }

        // Books: full setup
        if (isBook) {
            groupVerseLines();
        }

        generateMissingTOC();
        setupTOC();
        expandFirstLevel();
        setTimeout(setupTOC, 300);
        setTimeout(expandFirstLevel, 500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runSetup);
    } else {
        runSetup();
    }
})();
