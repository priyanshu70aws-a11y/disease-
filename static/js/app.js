// Handles UX enhancements: loading states, password toggles, and quick search feedback.
document.addEventListener('DOMContentLoaded', () => {
  const predictForm = document.getElementById('predictForm');
  const spinner = document.getElementById('loadingSpinner');
  if (predictForm && spinner) {
    predictForm.addEventListener('submit', () => spinner.classList.remove('d-none'));
  }

  document.querySelectorAll('[data-toggle-password]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-toggle-password');
      const input = document.getElementById(targetId);
      if (!input) return;
      const current = input.getAttribute('type');
      input.setAttribute('type', current === 'password' ? 'text' : 'password');
      btn.textContent = current === 'password' ? 'Hide' : 'Show';
    });
  });

  document.querySelectorAll('form[data-loading-btn]').forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"]');
      if (!btn) return;
      btn.disabled = true;
      btn.dataset.originalText = btn.innerHTML;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
      setTimeout(() => { btn.disabled = false; btn.innerHTML = btn.dataset.originalText; }, 3000);
    });
  });
});
