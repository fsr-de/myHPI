/* Settings */

const isMobileLayoutActive = () => {
    return window.innerWidth < 1200
}

const navbarHeight = remToPx(4.3)
const numberOfSupportedLevels = 3
let previousScrollPosition = window.scrollY

/* Logic */

const toggleHideOnScrollBlock = (e) => {
    e.target.classList.toggle("block-parent-hide")
}

const toggleElementVisibilityOnScroll = (minScrollPosition = 0) => {
    let currentScrollPosition = window.scrollY
    let elements = document.querySelectorAll(".xl-hide-on-scroll")
    if (
        previousScrollPosition < currentScrollPosition &&
        currentScrollPosition > minScrollPosition
    ) {
        elements.forEach((el) => {
            if (el.querySelector(".block-parent-hide")) return
            el.classList.add("hide-now")
        })
    } else {
        elements.forEach((el) => el.classList.remove("hide-now"))
    }
    previousScrollPosition = currentScrollPosition
}

window.onload = () => {
    addNavbarCollapses()
    adaptNavbarToWindowSize()
    toggleElementVisibilityOnScroll()
}
window.onscroll = () =>
    toggleElementVisibilityOnScroll(navbarHeight - remToPx(0.5))
window.onresize = adaptNavbarToWindowSize
