/* Settings */

const isMobileLayoutActive = () => {
    return window.innerWidth < 1200
}

const numberOfSupportedLevels = 3
const defaultPagePadding = 1.5
const navbarBarHeight = 0.3
let previousScrollPosition = window.scrollY

/* Logic */

const enableLogout = () => {
    document.querySelector("#logout-link").onclick = () => {
        document.querySelector("#logout-form").submit()
    }
}

/**
 * Toggles whether the given element prevents an ancestor from being hidden when scrolling down.
 *
 * If the element has the class `block-ancestor-hide`, any ancestor may not be hidden when scrolling down.
 *
 * @param {Node} element Node to toggle the prevention on.
 */
const toggleHideOnScrollBlock = (element) => {
    element.classList.toggle("block-ancestor-hide")
}

/**
 * Hides all nodes with the class `xl-hide-on-scroll` when scrolling down.
 * When scrolling up, the nodes are displayed again.
 *
 * Exception: Elements having a descendant with the class `block-ancestor-hide` will always be displayed.
 *
 * @param {number} minScrollPosition The hide/show behaviour will only be activated after scrolling past this position.
 *   Before, the elements will always be displayed.
 */
const toggleElementVisibilityOnScroll = (minScrollPosition = 0) => {
    let currentScrollPosition = window.scrollY
    let elements = document.querySelectorAll(".xl-hide-on-scroll")
    if (
        previousScrollPosition < currentScrollPosition &&
        currentScrollPosition > minScrollPosition
    ) {
        elements.forEach((el) => {
            if (el.querySelector(".block-ancestor-hide")) return
            el.classList.add("hide-now")
        })
    } else {
        elements.forEach((el) => el.classList.remove("hide-now"))
    }
    previousScrollPosition = currentScrollPosition
}

const localizeLastPublished = () => {
    let lastPublished = new Date(document.getElementById("last-published").getAttribute("datetime"))
    document.getElementById("last-published-date").innerHTML = lastPublished.toLocaleDateString("de-DE", { dateStyle: "medium" })
    document.getElementById("last-published-time").innerHTML = lastPublished.toLocaleString("de-DE", { timeStyle: "short" })
}

const enableTooltips = () => {
    const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    )
    Array.from(tooltipTriggerList).map((tooltipTriggerEl) => {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })
}

window.onload = () => {
    updateNavbarPosition()
    addNavbarCollapses()
    adaptNavbarToWindowSize()
    toggleElementVisibilityOnScroll()
    respectNavbarHeight()
    enableLogout()

    initializeSearch()

    localizeLastPublished()

    enableTooltips()

}
window.onscroll = () => {
    updateNavbarPosition()
    toggleElementVisibilityOnScroll(_navbarTop.offsetHeight)
}
window.onresize = () => {
    adaptNavbarToWindowSize()
    updateNavbarPosition()
}
