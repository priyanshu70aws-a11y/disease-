// Shows a loading spinner while the prediction request is being submitted.
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictForm');
  const spinner = document.getElementById('loadingSpinner');
  if (form && spinner) {
    form.addEventListener('submit', () => spinner.classList.remove('d-none'));
  }
});
