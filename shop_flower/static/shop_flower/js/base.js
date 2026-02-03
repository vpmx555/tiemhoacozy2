
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
    
