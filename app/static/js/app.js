document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggling (Checkbox version)
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        
        // Initial set based on current theme
        if (document.body.classList.contains('dark-mode')) {
            themeToggleBtn.checked = true;
        }
        
        themeToggleBtn.addEventListener('change', function() {
            if (themeToggleBtn.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('linkvault-theme', 'dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('linkvault-theme', 'light-mode');
            }
        });
    }
    
    // Mobile Sidebar
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenuClose = document.getElementById('mobileMenuClose');
    const sidebar = document.getElementById('sidebar');
    
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.add('open');
        });
    }
    
    if (mobileMenuClose && sidebar) {
        mobileMenuClose.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }
    
    // Toast Auto-hide
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.remove();
                }
            }, 300);
        }, 5000);
    });
    
    // Profile Dropdown
    const profileBtn = document.getElementById('profileDropdownBtn');
    const profileMenu = document.getElementById('profileDropdownMenu');
    
    if (profileBtn && profileMenu) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileMenu.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
                profileMenu.classList.remove('show');
            }
        });
    }

    // --- Custom Select Initialization ---
    const customSelects = document.querySelectorAll('.custom-select-wrapper');
    customSelects.forEach(wrapper => {
        const select = wrapper.querySelector('select');
        if (!select) return;

        // Hide original select
        select.style.display = 'none';

        // Create trigger
        const trigger = document.createElement('div');
        trigger.className = 'custom-select-trigger form-control';
        
        const iconTextContainer = document.createElement('div');
        iconTextContainer.className = 'icon-text';
        
        const triggerText = document.createElement('span');
        const triggerIcon = document.createElement('i');
        
        iconTextContainer.appendChild(triggerIcon);
        iconTextContainer.appendChild(triggerText);
        trigger.appendChild(iconTextContainer);
        
        const chevronIcon = document.createElement('i');
        chevronIcon.setAttribute('data-lucide', 'chevron-down');
        trigger.appendChild(chevronIcon);
        
        wrapper.appendChild(trigger);

        // Create options container
        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'custom-options';
        wrapper.appendChild(optionsContainer);

        // Populate options
        Array.from(select.options).forEach((option, index) => {
            const customOption = document.createElement('div');
            customOption.className = 'custom-option';
            if (option.selected) {
                customOption.classList.add('selected');
                updateTrigger(option);
            }
            
            const optIcon = document.createElement('i');
            optIcon.setAttribute('data-lucide', getIconForType(option.value));
            
            const optText = document.createElement('span');
            optText.textContent = option.text;
            
            customOption.appendChild(optIcon);
            customOption.appendChild(optText);
            
            customOption.addEventListener('click', function(e) {
                e.stopPropagation();
                select.selectedIndex = index;
                select.dispatchEvent(new Event('change')); // Trigger any native change events
                
                // Update selection UI
                wrapper.querySelectorAll('.custom-option').forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                
                updateTrigger(option);
                wrapper.classList.remove('open');
                trigger.classList.remove('open');
            });
            
            optionsContainer.appendChild(customOption);
        });
        
        // Render the icons in the dropdown
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Trigger click event
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = wrapper.classList.contains('open');
            // Close all other custom selects first
            document.querySelectorAll('.custom-select-wrapper').forEach(w => {
                w.classList.remove('open');
                w.querySelector('.custom-select-trigger').classList.remove('open');
            });
            
            if (!isOpen) {
                wrapper.classList.add('open');
                trigger.classList.add('open');
            }
        });

        function updateTrigger(option) {
            triggerText.textContent = option.text;
            
            // Lucide replaces the <i> tag with an <svg>, so we need to recreate the <i> tag
            iconTextContainer.innerHTML = '';
            const newIcon = document.createElement('i');
            newIcon.setAttribute('data-lucide', getIconForType(option.value));
            
            iconTextContainer.appendChild(newIcon);
            iconTextContainer.appendChild(triggerText);
            
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
        
        // Listen to native select changes (e.g. from javascript update)
        select.addEventListener('change', function() {
            const selectedOpt = select.options[select.selectedIndex];
            updateTrigger(selectedOpt);
            
            wrapper.querySelectorAll('.custom-option').forEach((opt, idx) => {
                if(idx === select.selectedIndex) {
                    opt.classList.add('selected');
                } else {
                    opt.classList.remove('selected');
                }
            });
        });
    });

    // Close custom select when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.custom-select-wrapper').forEach(wrapper => {
            wrapper.classList.remove('open');
            const trigger = wrapper.querySelector('.custom-select-trigger');
            if (trigger) trigger.classList.remove('open');
        });
    });

});

// Helper function mapping types to icons
function getIconForType(type) {
    const iconMap = {
        'Website': 'globe',
        'GitHub': 'code',
        'Documentation': 'book',
        'YouTube': 'play',
        'Article': 'file-text',
        'Research Paper': 'graduation-cap',
        'AI Tool': 'bot',
        'Development Tool': 'wrench',
        'Repository': 'folder-git',
        'Course': 'monitor-play',
        'Reference': 'bookmark',
        'Portfolio': 'briefcase',
        'Design': 'pen-tool',
        'Social Media': 'share-2',
        'Podcast': 'headphones',
        'Video': 'video',
        'E-commerce': 'shopping-cart',
        'Other': 'link'
    };
    return iconMap[type] || 'link';
}
