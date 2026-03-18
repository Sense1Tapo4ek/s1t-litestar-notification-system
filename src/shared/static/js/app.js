/* ============================================================
   Bot Monitor — app.js
   Vanilla JS: server clock tick + confirm dialogs
   ============================================================ */

(function () {
  'use strict';

  // --- Server clock -----------------------------------------
  // The server passes a Unix timestamp via data-server-ts on the <time> element.
  // We derive local offset and tick every second.
  const clockEl = document.getElementById('server-clock');
  if (clockEl) {
    const serverTs = parseInt(clockEl.dataset.serverTs, 10);
    const clientTs = Math.floor(Date.now() / 1000);
    const offsetSeconds = serverTs - clientTs;

    function formatClock() {
      const now = new Date((Math.floor(Date.now() / 1000) + offsetSeconds) * 1000);
      const pad = (n) => String(n).padStart(2, '0');
      return (
        now.getUTCFullYear() + '-' +
        pad(now.getUTCMonth() + 1) + '-' +
        pad(now.getUTCDate()) + ' ' +
        pad(now.getUTCHours()) + ':' +
        pad(now.getUTCMinutes()) + ':' +
        pad(now.getUTCSeconds()) + ' UTC'
      );
    }

    clockEl.textContent = formatClock();
    setInterval(function () {
      clockEl.textContent = formatClock();
    }, 1000);
  }

  // --- Confirm dialogs --------------------------------------
  // Add data-confirm="message" to any <button type="submit"> inside a <form>.
  // Clicking it will show a confirm() dialog; form submits only on OK.
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.js-confirm');
    if (!btn) return;

    const message = btn.dataset.confirm || 'Are you sure?';
    if (!confirm(message)) {
      e.preventDefault();
      e.stopPropagation();
    }
  });

})();
