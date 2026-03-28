// Listen for messages from parent window to control font size
(function() {
    'use strict';

    function getOrCreateStyle(id) {
        let style = document.getElementById(id);
        if (!style) {
            style = document.createElement('style');
            style.id = id;
            document.head.appendChild(style);
        }
        return style;
    }

    window.addEventListener('message', function(event) {
        if (event.data.type === 'setFontSize') {
            const fontSize = event.data.fontSize;
            const style = getOrCreateStyle('custom-font-style');
            style.textContent = `
                #content > .outline-2 p, #content > .outline-2 li,
                #content > .outline-2 dd, #content > .outline-2 td,
                #content > .outline-2 th, #content > .outline-2 blockquote,
                #content > .outline-2 span, #content > .outline-2 a,
                #content > .outline-2 code {
                    font-size: ${fontSize}px !important;
                    line-height: 1.8 !important;
                }
                #content > .outline-2 h2 { font-size: ${fontSize * 1.5}px !important; }
                #content > .outline-2 h3 { font-size: ${fontSize * 1.25}px !important; }
                #content > .outline-2 h4 { font-size: ${fontSize * 1.1}px !important; }
            `;
        }
    });

    // Tell parent we're ready
    if (window.parent !== window) {
        window.parent.postMessage({ type: 'iframeReady' }, '*');
    }
})();
