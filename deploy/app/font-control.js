// Listen for messages from parent window to control font size and dark mode
(function() {
    'use strict';

    console.log('Font control script loaded in iframe');

    // Listen for messages from parent
    window.addEventListener('message', function(event) {
        console.log('Iframe received message:', event.data);

        if (event.data.type === 'setFontSize') {
            const fontSize = event.data.fontSize;
            console.log('Setting font size to:', fontSize);

            // Remove existing style
            let style = document.getElementById('custom-font-style');
            if (!style) {
                style = document.createElement('style');
                style.id = 'custom-font-style';
                document.head.appendChild(style);
            }

            style.textContent = `
                html { font-size: ${fontSize}px !important; }
                #content p, #content li, #content dd, #content td, #content th,
                #content blockquote, #content .verse, #content .example,
                #content pre.src, #content code {
                    line-height: 1.8 !important;
                }
            `;

            console.log('Font size applied:', fontSize);
        }

        if (event.data.type === 'setDarkMode') {
            const isDark = event.data.isDark;
            console.log('Setting dark mode to:', isDark);

            // Remove existing style
            let style = document.getElementById('custom-dark-style');
            if (!style) {
                style = document.createElement('style');
                style.id = 'custom-dark-style';
                document.head.appendChild(style);
            }

            if (isDark) {
                style.textContent = `
                    body {
                        background: #121212 !important;
                    }
                    body, p, h1, h2, h3, h4, h5, h6, div, span, li, td, th, blockquote, pre, code, dd, dt, label, legend, .footpara, .timestamp {
                        color: #e0e0e0 !important;
                    }
                    a {
                        color: #f59e0b !important;
                    }
                    a:visited {
                        color: #d97706 !important;
                    }
                    #table-of-contents, .nav {
                        background: #1a1a1a !important;
                    }
                    #copyright, #postamble {
                        background: #1a1a1a !important;
                    }
                    table td, table th {
                        background-color: #1e1e1e !important;
                        border-color: #333 !important;
                    }
                    table tr:nth-child(2n-1) td {
                        background-color: #1e1e1e !important;
                    }
                    table tr:nth-child(2n) td {
                        background-color: #252525 !important;
                    }
                    blockquote, .verse {
                        background-color: #1e1e1e !important;
                        border-color: #444 !important;
                    }
                    .example, pre.src, .codeblock, #content .literal-block {
                        background: #2d2d2d !important;
                        border-color: #444 !important;
                    }
                    code {
                        background: #2d2d2d !important;
                        border-color: #444 !important;
                    }
                    #content {
                        background: #121212 !important;
                    }
                    .note + div, #content .note, #content .seealso, .seealso + div {
                        background: #1e1e1e !important;
                    }
                    .admonition-title + div {
                        background: #1e1e1e !important;
                    }
                `;
                console.log('Dark mode enabled');
            } else {
                style.textContent = '';
                console.log('Dark mode disabled');
            }
        }
    });

    // Tell parent we're ready
    if (window.parent !== window) {
        window.parent.postMessage({ type: 'iframeReady' }, '*');
        console.log('Told parent iframe is ready');
    }
})();
