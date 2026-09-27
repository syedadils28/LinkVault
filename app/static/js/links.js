document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const collectionFilter = document.getElementById('collectionFilter');
    const favoriteFilterBtn = document.getElementById('favoriteFilterBtn');
    
    const linkCards = document.querySelectorAll('.link-card');
    
    const bulkActions = document.getElementById('bulkActions');
    const selectedCount = document.getElementById('selectedCount');
    const linkCheckboxes = document.querySelectorAll('.link-checkbox');
    const bulkExportBtn = document.getElementById('bulkExportBtn');
    const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
    
    let isFavoritesOnly = false;
    
    // Filtering Logic
    function applyFilters() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const typeValue = typeFilter ? typeFilter.value : 'all';
        const collectionValue = collectionFilter ? collectionFilter.value : 'all';
        
        let visibleCount = 0;
        
        linkCards.forEach(card => {
            const title = card.dataset.title;
            const url = card.dataset.url;
            const type = card.dataset.type;
            const collection = card.dataset.collection;
            const favorite = card.dataset.favorite === 'true';
            const tags = card.dataset.tags;
            
            // Search Match
            const matchSearch = !searchTerm || title.includes(searchTerm) || url.includes(searchTerm) || tags.includes(searchTerm);
            
            // Type Match
            const matchType = typeValue === 'all' || type === typeValue;
            
            // Collection Match
            const matchCollection = collectionValue === 'all' || collection === collectionValue;
            
            // Favorite Match
            const matchFavorite = !isFavoritesOnly || favorite;
            
            if (matchSearch && matchType && matchCollection && matchFavorite) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (typeFilter) typeFilter.addEventListener('change', applyFilters);
    if (collectionFilter) collectionFilter.addEventListener('change', applyFilters);
    
    if (favoriteFilterBtn) {
        favoriteFilterBtn.addEventListener('click', function() {
            isFavoritesOnly = !isFavoritesOnly;
            if (isFavoritesOnly) {
                this.classList.remove('btn-outline');
                this.classList.add('btn-primary');
            } else {
                this.classList.add('btn-outline');
                this.classList.remove('btn-primary');
            }
            applyFilters();
        });
    }
    
    // Bulk Selection Logic
    function updateBulkActions() {
        const selected = Array.from(linkCheckboxes).filter(cb => cb.checked);
        if (selected.length > 0) {
            bulkActions.style.display = 'flex';
            selectedCount.textContent = selected.length;
        } else {
            bulkActions.style.display = 'none';
        }
        
        // Highlight selected cards
        linkCheckboxes.forEach(cb => {
            const card = cb.closest('.link-card');
            if (cb.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    linkCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateBulkActions);
    });
    
    // Action: Copy URL
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;
            navigator.clipboard.writeText(url).then(() => {
                const icon = this.querySelector('i');
                const oldIcon = icon.getAttribute('data-lucide');
                icon.setAttribute('data-lucide', 'check');
                lucide.createIcons();
                this.style.color = 'var(--success-color)';
                
                setTimeout(() => {
                    icon.setAttribute('data-lucide', oldIcon);
                    lucide.createIcons();
                    this.style.color = '';
                }, 2000);
            });
        });
    });
    
    // Action: Toggle Favorite
    const favBtns = document.querySelectorAll('.favorite-btn');
    favBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const icon = this.querySelector('i');
            const card = this.closest('.link-card');
            
            fetch(`/links/${id}/toggle-favorite`, {
                method: 'POST'
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.is_favorite) {
                        this.classList.add('active');
                        icon.classList.add('filled');
                        card.dataset.favorite = 'true';
                    } else {
                        this.classList.remove('active');
                        icon.classList.remove('filled');
                        card.dataset.favorite = 'false';
                    }
                }
            });
        });
    });
    
    // Action: Delete Single
    const deleteBtns = document.querySelectorAll('.delete-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this link?')) {
                const id = this.dataset.id;
                fetch(`/links/${id}/delete`, {
                    method: 'POST'
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        this.closest('.link-card').remove();
                    }
                });
            }
        });
    });
    
    // Bulk Actions Setup
    if (bulkExportBtn) {
        bulkExportBtn.addEventListener('click', function() {
            const selected = Array.from(linkCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
            document.getElementById('bulkSelectedIds').value = selected.join(',');
            document.getElementById('bulkExportForm').submit();
            
            // Optionally uncheck after export
            linkCheckboxes.forEach(cb => cb.checked = false);
            updateBulkActions();
        });
    }
    
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', function() {
            if (confirm(`Are you sure you want to delete ${Array.from(linkCheckboxes).filter(cb => cb.checked).length} links?`)) {
                const selected = Array.from(linkCheckboxes).filter(cb => cb.checked);
                let deletedCount = 0;
                
                selected.forEach(cb => {
                    const id = cb.value;
                    fetch(`/links/${id}/delete`, {
                        method: 'POST'
                    }).then(() => {
                        deletedCount++;
                        if (deletedCount === selected.length) {
                            window.location.reload();
                        }
                    });
                });
            }
        });
    }
});
