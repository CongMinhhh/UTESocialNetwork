document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const toggleBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            mainContent.classList.toggle('full-width');
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc chắn muốn xóa?')) {
                e.preventDefault();
            }
        });
    });

    // Table row hover effect
    const tableRows = document.querySelectorAll('tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseover', function() {
            this.style.backgroundColor = 'var(--light-gray)';
        });
        row.addEventListener('mouseout', function() {
            this.style.backgroundColor = '';
        });
    });

    // Responsive sidebar
    function checkWidth() {
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            mainContent.classList.remove('full-width');
        }
    }

    window.addEventListener('resize', checkWidth);
    checkWidth();
}); 