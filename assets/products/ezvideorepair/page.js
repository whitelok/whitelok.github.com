// Progressive enhancement only: all content, language links and FAQs work without JavaScript.
(() => {
  const header = document.querySelector('.site-header');
  const update = () => header.classList.toggle('scrolled', window.scrollY > 12);
  window.addEventListener('scroll', update, {passive: true});
  update();
})();
