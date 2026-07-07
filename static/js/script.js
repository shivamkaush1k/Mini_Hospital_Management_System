/* =========================================================================
   MINI HMS — static/js/script.js
   Site-wide behavior: mobile sidebar drawer, Django-message toasts/alerts,
   active nav-link highlighting, and opt-in delete confirmation.
   Form validation lives separately in validation.js.
   Requires Bootstrap 5's JS bundle (already loaded in base.html) for the
   Toast component. Every block checks the elements it needs exist first,
   so this file is safe to include on every page.
   ========================================================================= */
document.addEventListener('DOMContentLoaded', function () {

  /* -----------------------------------------------------------------------
     1. Mobile sidebar (off-canvas drawer)
     Requires a toggle button with id="sidebarToggle" in the navbar — see
     the comment above #sidebarToggle in style.css for the markup to add
     to base.html. Pages with no .sidebar (home, login, register) skip
     this block entirely.
     ------------------------------------------------------------------- */
  var sidebar = document.querySelector('.sidebar');
  var toggleBtn = document.getElementById('sidebarToggle');

  if (sidebar) {
    var scrim = document.createElement('div');
    scrim.className = 'sidebar-scrim';
    document.body.appendChild(scrim);

    function openSidebar() {
      sidebar.classList.add('is-open');
      scrim.classList.add('is-visible');
      document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
      sidebar.classList.remove('is-open');
      scrim.classList.remove('is-visible');
      document.body.style.overflow = '';
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        sidebar.classList.contains('is-open') ? closeSidebar() : openSidebar();
      });
    }
    scrim.addEventListener('click', closeSidebar);

    sidebar.querySelectorAll('.sidebar-link').forEach(function (link) {
      link.addEventListener('click', closeSidebar);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 991.98) closeSidebar();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSidebar();
    });
  }

  /* -----------------------------------------------------------------------
     2. Django messages rendered as Bootstrap toasts (base.html's
     .toast-container). Auto-shows and auto-dismisses each one.
     ------------------------------------------------------------------- */
  document.querySelectorAll('.toast-container .toast').forEach(function (el) {
    if (window.bootstrap && bootstrap.Toast) {
      var t = new bootstrap.Toast(el, { delay: 4500 });
      t.show();
    }
  });

  /* -----------------------------------------------------------------------
     3. Django messages rendered as plain dismissible alerts (the
     {% if messages %}...alert-dismissible...{% endif %} block used
     directly inside several page templates, as opposed to the toast).
     ------------------------------------------------------------------- */
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(function (alertEl) {
    setTimeout(function () {
      alertEl.style.transition = 'opacity .4s ease';
      alertEl.style.opacity = '0';
      setTimeout(function () {
        if (alertEl.parentNode) alertEl.remove();
      }, 400);
    }, 4500);
  });

  /* -----------------------------------------------------------------------
     4. Active sidebar link — highlights the entry matching the current URL.
     ------------------------------------------------------------------- */
  var path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(function (link) {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });

  /* -----------------------------------------------------------------------
     5. Confirm-before-delete for destructive buttons.
     Scoped to an explicit opt-in (`data-confirm="..."`) rather than every
     .btn-danger — several templates already route deletes through their
     own dedicated "are you sure?" confirmation page, so a second native
     confirm() on top would be a redundant popup.
     Usage: <button class="btn btn-danger" data-confirm="Delete this slot?">
     ------------------------------------------------------------------- */
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!window.confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

});