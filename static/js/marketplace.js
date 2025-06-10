document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const createListingModal = document.getElementById('create-listing-modal');
    const editListingModal = document.getElementById('edit-listing-modal');
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');
    
    // Buttons
    const createListingBtn = document.querySelector('.create-listing-btn');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const editBtns = document.querySelectorAll('.edit-product-btn');
    const deleteBtns = document.querySelectorAll('.delete-product-btn');
    const messageSellerBtns = document.querySelectorAll('.message-seller-btn');
    const optionsBtns = document.querySelectorAll('.options-btn');

    // Show create listing modal
    createListingBtn.addEventListener('click', () => {
        createListingModal.style.display = 'block';
    });

    // Handle image preview for create listing
    const imageInput = document.getElementById('images');
    const imagePreview = document.getElementById('image-preview');

    imageInput.addEventListener('change', function() {
        imagePreview.innerHTML = '';
        for (let file of this.files) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                imagePreview.appendChild(img);
            }
            reader.readAsDataURL(file);
        }
    });

    // Handle edit listing
    editBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            // Fetch product details and populate form
            fetch(`/api/product/${productId}/`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('edit-title').value = data.title;
                    document.getElementById('edit-description').value = data.description;
                    document.getElementById('edit-price').value = data.price;
                    document.getElementById('edit-category').value = data.category;
                    document.getElementById('edit-location').value = data.location;
                    editListingModal.style.display = 'block';
                    
                    // Update form action
                    const form = document.getElementById('edit-listing-form');
                    form.action = `/edit-product/${productId}/`;
                });
        });
    });

    // Handle delete confirmation
    let productToDelete = null;
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            productToDelete = btn.dataset.productId;
            deleteConfirmModal.style.display = 'block';
        });
    });

    // Handle delete confirmation
    const confirmDeleteBtn = document.querySelector('.confirm-delete-btn');
    confirmDeleteBtn.addEventListener('click', () => {
        if (productToDelete) {
            window.location.href = `/delete-product/${productToDelete}/`;
        }
    });

    // Handle messaging with seller
    messageSellerBtns.forEach(button => {
        button.addEventListener('click', function() {
            const sellerId = this.dataset.sellerId;
            window.location.href = `/messages/?user_id=${sellerId}`;
        });
    });

    // Handle options dropdown
    optionsBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const dropdown = btn.nextElementSibling;
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.options-dropdown').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    });

    // Close modals
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            createListingModal.style.display = 'none';
            editListingModal.style.display = 'none';
            deleteConfirmModal.style.display = 'none';
        });
    });

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === createListingModal) createListingModal.style.display = 'none';
        if (e.target === editListingModal) editListingModal.style.display = 'none';
        if (e.target === deleteConfirmModal) deleteConfirmModal.style.display = 'none';
    });
}); 