/* Settings */

const isMobileLayoutActive = () => {
    return window.innerWidth < 1200
}

const navbarHeight = remToPx(4.3)
const numberOfSupportedLevels = 3
let previousScrollPosition = window.scrollY
let isNavbarInDesktopMode = true

/* Logic */

/**
 * Makes second level navbar items collapse when a root level navbar item is toggled.
 * Only needed for the desktop layout, as the mobile layout differs a lot.
 *
 * The Bootstrap Collapse Plugin only supports toggling collapsed states between
 * containers with the same parent. This means for the navbar: Supposed a navbar structure of
 * A > A1 > A2 and B > B1, with A and B being root level navbar items always shown in the
 * navigation bar. If A1 and A2 are expanded and then the root navbar item B is clicked
 * (which expands B1), A1 would be replaced with B1, but A2 would still be expanded.
 * This method makes A2 collapse as well.
 */
const addCollapseToDesktopLevel2NavContainers = () => {
    let levelOneItemContainers = document.querySelectorAll(
        "#nav-level-1 .nav-item-container"
    )
    levelOneItemContainers.forEach((itemContainer) => {
        itemContainer.addEventListener("hide.bs.collapse", () => {
            if (!isNavbarInDesktopMode) return
            const levelTwoItemContainers = document.querySelectorAll(
                "#nav-level-2 .nav-item-container"
            )
            levelTwoItemContainers.forEach((itemContainer) =>
                bootstrap.Collapse.getOrCreateInstance(itemContainer, {
                    toggle: false,
                }).hide()
            )
        })
    })
}

const addCollapseForMobileNavItems = () => {
    let allNavItemContainers = document.querySelectorAll(".nav-item-container")
    allNavItemContainers.forEach((navItemContainer) => {
        navItemContainer.addEventListener("hide.bs.collapse", (e) => {
            if (isNavbarInDesktopMode) return
            e.stopPropagation()
            const collapsingNavContainer = navItemContainer
            const childNavItemContainers =
                collapsingNavContainer.querySelectorAll(".nav-item-container")
            childNavItemContainers.forEach((childNavItemContainer) => {
                if (
                    !childNavItemContainer.classList.contains("show") ||
                    childNavItemContainer.classList.contains("collapsing")
                )
                    return
                bootstrap.Collapse.getOrCreateInstance(childNavItemContainer, {
                    toggle: false,
                }).hide()
            })
        })
        navItemContainer.addEventListener("show.bs.collapse", (e) => {
            if (isNavbarInDesktopMode) return
            e.stopPropagation()
            const sameLevelNavItemContainer =
                navItemContainer.parentNode.parentNode
            if (!sameLevelNavItemContainer) return

            const childNavItemContainers =
                sameLevelNavItemContainer.querySelectorAll(
                    ".nav-item-container"
                )
            childNavItemContainers.forEach((childNavItemContainer) => {
                if (e.target === childNavItemContainer) return
                bootstrap.Collapse.getOrCreateInstance(childNavItemContainer, {
                    toggle: false,
                }).hide()
            })
        })
    })
}

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

const moveNonRootLevelsToDesktopLayout = () => {
    const levels = [...Array(numberOfSupportedLevels).keys()].slice(1)
    levels.forEach((levelId) => {
        const navItemContainers = document.querySelectorAll(
            `.nav-item-container[layout-parent-desktop='#nav-level-${levelId}']`
        )
        const bottomNavLevelContainer = document.querySelector(
            `#nav-level-${levelId}`
        )
        for (const navItemContainer of navItemContainers) {
            navItemContainer.setAttribute(
                "data-bs-parent",
                `#nav-level-${levelId}`
            )
            bottomNavLevelContainer.appendChild(navItemContainer)
        }
    })
}

const moveRootLevelToDesktopLayout = () => {
    const rootNavLevelContainer = document.querySelector("#nav-level-0")
    const rootLevel = document.querySelector("#nav-item-container-root")
    rootNavLevelContainer.appendChild(rootLevel)

    rootNavLevelContainer
        .querySelectorAll(`.nav-item.dropdown .nav-link-title`)
        .forEach((navLinkTitle) => {
            navLinkTitle.classList.add("dropdown-toggle")
        })
}

const setDesktopNavbar = () => {
    if (isNavbarInDesktopMode) return
    isNavbarInDesktopMode = true
    moveNonRootLevelsToDesktopLayout()
    moveRootLevelToDesktopLayout()
}

const moveNonRootLevelsToMobileLayout = () => {
    const levels = [...Array(numberOfSupportedLevels).keys()].slice(1)
    levels
        .sort((a, b) => b - a)
        .forEach((levelId) => {
            const levelNavItemContainer = document.querySelector(
                `#nav-level-${levelId}`
            )
            const parentNavItems = document.querySelectorAll(
                `#nav-level-${levelId - 1} .nav-item.dropdown`
            )
            for (const parentNavItem of parentNavItems) {
                const levelNavItem = levelNavItemContainer.querySelector(
                    `#${parentNavItem
                        .querySelector(".nav-link")
                        .getAttribute("aria-controls")}`
                )
                parentNavItem.appendChild(levelNavItem)
            }
        })
}

const moveRootLevelToMobileLayout = () => {
    const bottomNavContainer = document.querySelector(".navbar-bottom-content")
    const rootLevel = document.querySelector("#nav-item-container-root")
    bottomNavContainer.appendChild(rootLevel)

    rootLevel
        .querySelectorAll(`.nav-item.dropdown .nav-link-title`)
        .forEach((navLinkTitle) => {
            navLinkTitle.classList.remove("dropdown-toggle")
        })
}

const setMobileNavbar = () => {
    if (!isNavbarInDesktopMode) return
    isNavbarInDesktopMode = false
    moveNonRootLevelsToMobileLayout()
    moveRootLevelToMobileLayout()
}

const adaptNavbarToDisplaySize = () => {
    isMobileLayoutActive() ? setMobileNavbar() : setDesktopNavbar()
}

window.onload = () => {
    addCollapseToDesktopLevel2NavContainers()
    addCollapseForMobileNavItems()
    adaptNavbarToDisplaySize()
    toggleElementVisibilityOnScroll()
}
window.onscroll = () =>
    toggleElementVisibilityOnScroll(navbarHeight - remToPx(0.5))
window.onresize = adaptNavbarToDisplaySize
