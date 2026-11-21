// Progressive enhancement only: all content, language links and FAQs work without JavaScript.
(() => {
  const header = document.querySelector('.site-header');
  const update = () => header.classList.toggle('scrolled', window.scrollY > 12);
  window.addEventListener('scroll', update, {passive: true});
  update();
})();

(() => {
  const demo = document.getElementById('preview');
  if (!demo) return;

  const player = demo.querySelector('#lyrebird-video');
  const choices = demo.querySelector('.demo-versions');

  for (const video of demo.querySelectorAll('video')) {
    const error = video.parentElement.querySelector('.demo-error');
    const showError = () => {
      error.querySelector('a').href = video.currentSrc || video.src;
      error.hidden = false;
    };
    video.addEventListener('error', showError);
    video.addEventListener('loadstart', () => { error.hidden = true; });
    if (video.error) showError();
  }

  if (!player || !choices) return;

  let selected = choices.querySelector('[aria-current]');
  let pending = null;
  player.addEventListener('loadedmetadata', () => {
    if (!pending || player.currentSrc !== selected.href) return;
    const {time, playing} = pending;
    pending = null;
    player.currentTime = Math.min(time, player.duration);
    if (playing) player.play().catch(() => { /* Native controls allow resuming. */ });
  });

  choices.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
    event.preventDefault();
    if (link === selected && !player.error) return;

    // Keep the requested position through multiple clicks while a source is loading.
    pending ??= {time: player.currentTime, playing: !player.paused && !player.ended};
    selected.removeAttribute('aria-current');
    selected = link;
    selected.setAttribute('aria-current', 'true');
    player.pause();
    player.removeAttribute('poster');
    player.src = link.href;
    player.load();
  });
})();
