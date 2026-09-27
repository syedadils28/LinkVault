function toggleCollectionSelect() {
    const scopeCollection = document.getElementById('scopeCollection');
    const collectionSelectGroup = document.getElementById('collectionSelectGroup');
    
    if (scopeCollection && collectionSelectGroup) {
        if (scopeCollection.checked) {
            collectionSelectGroup.style.display = 'block';
        } else {
            collectionSelectGroup.style.display = 'none';
        }
    }
}
