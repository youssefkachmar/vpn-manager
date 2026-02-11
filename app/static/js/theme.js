// Dark Mode Toggle - VPN Manager
(function() {
    'use strict';
    
    // Initialize theme on page load
    document.addEventListener('DOMContentLoaded', function() {
        initTheme();
        setupThemeToggle();
    });
    
    function initTheme() {
        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateToggleButton(savedTheme);
    }
    
    function setupThemeToggle() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) {
            console.warn('Theme toggle button not found');
            return;
        }
        
        toggleBtn.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Apply new theme
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleButton(newTheme);
            
            // Add smooth transition
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        });
    }
    
    function updateToggleButton(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
            toggleBtn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }
    
    // Copy to clipboard function
    window.copyToClipboard = function(text, button) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function() {
                showCopyFeedback(button);
            }).catch(function(err) {
                console.error('Failed to copy:', err);
                fallbackCopy(text, button);
            });
        } else {
            fallbackCopy(text, button);
        }
    };
    
    function showCopyFeedback(button) {
        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        button.innerHTML = '<i class="bi bi-check-circle"></i> Copied!';
        button.classList.add('btn-success');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.className = originalClass;
        }, 2000);
    }
    
    function fallbackCopy(text, button) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            showCopyFeedback(button);
        } catch (err) {
            console.error('Fallback copy failed:', err);
            alert('Failed to copy to clipboard');
        }
        
        document.body.removeChild(textarea);
    }
})();
