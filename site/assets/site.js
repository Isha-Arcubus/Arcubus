/* Arcubus Advisors — the only script on the site.
   Mobile nav toggle. Everything else is static HTML so that search
   engines and LLM crawlers get the full page on first request. */
(function () {
  var t = document.querySelector('.navtoggle');
  var l = document.querySelector('.navlinks');
  if (!t || !l) return;
  t.addEventListener('click', function () {
    var open = l.classList.toggle('open');
    t.setAttribute('aria-expanded', open ? 'true' : 'false');
    t.textContent = open ? 'Close' : 'Menu';
  });
})();
