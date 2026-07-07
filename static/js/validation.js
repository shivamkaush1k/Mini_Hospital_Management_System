/* =========================================================================
   MINI HMS — static/js/validation.js
   Inline, non-blocking required-field validation for every form on the
   page. Pairs with forms.css's .is-invalid and .field-error styles.
   Flags the specific empty field(s) instead of a single browser alert()
   that doesn't say which field is the problem — much better on mobile,
   where alert() dialogs are especially disruptive.
   Load this after script.js (order between the two doesn't actually
   matter — they don't share state — but keeping form-related JS grouped
   together makes the load order easier to reason about).
   ========================================================================= */
document.addEventListener('DOMContentLoaded', function () {

  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var firstInvalid = null;

      form.querySelectorAll('input[required], textarea[required], select[required]').forEach(function (field) {
        var isEmpty = field.type === 'checkbox' ? !field.checked : field.value.trim() === '';
        var existingMsg = field.parentNode.querySelector('.field-error');

        if (isEmpty) {
          field.classList.add('is-invalid');
          if (!existingMsg) {
            var msg = document.createElement('div');
            msg.className = 'field-error';
            msg.textContent = 'This field is required.';
            field.insertAdjacentElement('afterend', msg);
          }
          if (!firstInvalid) firstInvalid = field;
        } else {
          field.classList.remove('is-invalid');
          if (existingMsg) existingMsg.remove();
        }
      });

      if (firstInvalid) {
        e.preventDefault();
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus();
      }
    });

    // Clear the error state as soon as the person starts fixing a field
    form.querySelectorAll('input, textarea, select').forEach(function (field) {
      field.addEventListener('input', function () {
        field.classList.remove('is-invalid');
        var msg = field.parentNode.querySelector('.field-error');
        if (msg) msg.remove();
      });
    });
  });

});