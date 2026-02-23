
let lastScroll = 0;

window.addEventListener("scroll", () => {

    const currentScroll =
        window.pageYOffset || document.documentElement.scrollTop;

    if (currentScroll > lastScroll && currentScroll > 120) {
        document.body.classList.add("header-hide");
    } else {
        document.body.classList.remove("header-hide");
    }

    lastScroll = currentScroll <= 0 ? 0 : currentScroll;
});
    
// Floating CTA — urgent pulse periodically (gentle, non-intrusive)
document.addEventListener('DOMContentLoaded', function(){
  const hot = document.querySelector('.floating-cta .fab');
  const zaloBtn = document.querySelector('.floating-cta .fab-sm');
  if (!hot) return;

  // thời gian vòng lặp (ms)
  const PERIOD = 4500;
  // hiệu ứng: pulse + shake shortly after
  function triggerUrgentOnce() {
    // pulse
    hot.classList.add('urgent');
    zaloBtn && zaloBtn.classList.add('urgent');
    // remove pulse after its duration (match CSS 900ms)
    setTimeout(()=> {
      hot.classList.remove('urgent');
      zaloBtn && zaloBtn.classList.remove('urgent');
      // short shake
      hot.classList.add('urgent-shake');
      zaloBtn && zaloBtn.classList.add('urgent-shake');
      setTimeout(()=> {
        hot.classList.remove('urgent-shake');
        zaloBtn && zaloBtn.classList.remove('urgent-shake');
      }, 420);
    }, 900);
  }

  // run once on load after small delay to catch attention
  setTimeout(triggerUrgentOnce, 700);

  // then periodic every PERIOD
  const intervalId = setInterval(triggerUrgentOnce, PERIOD);

  // tidy up if page unloads (optional)
  window.addEventListener('beforeunload', ()=> clearInterval(intervalId));
});