/* MOI Panel — JavaScript */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});

// Confirm before unpublish / delete actions from dashboard
document.addEventListener('DOMContentLoaded', function () {
  // Delete confirmation is handled by the confirm delete page, not JS
  // Unpublish confirmation
  document.querySelectorAll('form[action*="unpublish"]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm('Unpublish this page? The static file will be removed.')) {
        e.preventDefault();
      }
    });
  });
});
