// Helper to show Bootstrap Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toastId = `toast-${Date.now()}`;
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
}

// Helper to control the loading bar
function showLoadingBar(show = true) {
    const loadingBarContainer = document.getElementById('loadingBarContainer');
    loadingBarContainer.style.display = show ? 'block' : 'none';
}

// Handle Form Submission via Fetch API
document.getElementById('analysisForm').addEventListener('submit', function (e) {
    e.preventDefault();  // Prevent default form submission behavior

    // Show notification and progress bar
    showToast('Running Analysis... Please wait.', 'primary');
    showLoadingBar(true);

    // Prepare form data
    const formData = new FormData(this);

    // Send data to the server via POST
    fetch("/config", {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showToast('Analysis Complete! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = "/";  // Redirect to main page
            }, 2000);
        } else {
            showToast('Analysis failed. Please check your inputs.', 'danger');
        }
    })
    .catch(() => {
        showToast('An error occurred while running the analysis.', 'danger');
    })
    .finally(() => {
        showLoadingBar(false);  // Hide loading bar after the process finishes
    });
});
