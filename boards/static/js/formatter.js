document.addEventListener('DOMContentLoaded', function() {
    const toolbars = document.querySelectorAll('.format-toolbar');

    toolbars.forEach(toolbar => {
        const form = toolbar.closest('form');
        if (!form) return;
        const textarea = form.querySelector('textarea');
        if (!textarea) return;

        if (textarea.parentNode) {
            textarea.parentNode.appendChild(toolbar);
        }

        toolbar.addEventListener('click', function(event) {
            const button = event.target.closest('.format-btn');
            if (button) {
                const format = button.dataset.format;
                applyFormat(textarea, format);
            }
        });
    });

    function applyFormat(textarea, format) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);

        let prefix = '';
        let suffix = '';

        switch (format) {
            case 'quote':
                if (selectedText) {
                    const replacement = selectedText.split('\n').map(line => '> ' + line).join('\n');
                    textarea.setRangeText(replacement, start, end, 'select');
                } else {
                    const replacement = '> ';
                    textarea.setRangeText(replacement, start, end, 'end');
                }
                textarea.focus();
                return; 

            case 'spoiler':
                prefix = '>!';
                suffix = '!<';
                break;
            case 'strike':
                prefix = '~~';
                suffix = '~~';
                break;
            case 'link':
                const linkTemplate = 'mkchtlnk:board:id';
                textarea.setRangeText(linkTemplate, start, end, 'select');
                textarea.focus();
                return;
        }

        const replacement = prefix + selectedText + suffix;
        textarea.setRangeText(replacement, start, end);
        textarea.focus();

        if (selectedText) {
            textarea.setSelectionRange(start, start + replacement.length);
        } else {
            textarea.setSelectionRange(start + prefix.length, start + prefix.length);
        }
    }
});
