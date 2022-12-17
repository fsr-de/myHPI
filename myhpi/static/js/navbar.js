/**
 * Navbar script. Contains logic for:
 *
 * - Collapse behaviour
 * - Toggle between mobile and desktop layout
 *
 */

/**
 * Collapsing -----------------------------------------------
 */

/**
 * Returns whether the given navItemContainer is currently collapsed.
 *
 * @param {Node} navItemContainer Container to check.
 * @returns True if it is collapsed, false otherwise.
 */
const isCollapsed = (navItemContainer) => {
    return !navItemContainer.classList.contains("show")
}

/**
 * Returns node of the navbar level below the given navItemContainer's level.
 *
 * Example: If the navItemContainer is on navbar level 1, the node for level 2 is returned.
 *
 * @param {Node} navItemContainer Container to return lower level for.
 * @returns Level node of lower level. Null if there is no lower level (depends on `numberOfSupportedLevels`).
 */
const getLevelBelow = (navItemContainer) => {
    const levelId = parseInt(
        navItemContainer.getAttribute("data-navbar-level").slice(11)
    )
    return levelId + 1 === numberOfSupportedLevels
        ? null
        : document.querySelector(`#nav-level-${levelId + 1}`)
}

/**
 * Collapses all navItemContainers which are direct children of the given navItemContainers.
 *
 * The children are not determined by the DOM, but the wagtail page tree encoded in the node ids, data-attributes, etc.
 * Thus we can arrange the navItemContainers to our liking, not necessarily in a tree layout, while keeping the collapse
 *   logic as one would expect from the wagtail page tree.
 *
 * Example: Given the container of a root navbar item, the containers of that item's children pages are collapsed,
 *   even if they are no children in the DOM (e.g. in the desktop layout).
 *
 * @param {Node} navItemContainer Container whose children containers should be collapsed.
 */
const collapseChildren = (navItemContainer) => {
    const collapseLevelId =
        "#" + getLevelBelow(navItemContainer)?.getAttribute("id")
    if (!collapseLevelId) return
    const navContainersToCollapse = document.querySelectorAll(
        `.nav-item-container[data-navbar-level="${collapseLevelId}"]`
    )
    navContainersToCollapse.forEach((navItemContainerToCollapse) => {
        if (isCollapsed(navItemContainerToCollapse)) return
        bootstrap.Collapse.getOrCreateInstance(
            navItemContainerToCollapse
        ).hide()
    })
}

/**
 * Collapses all navItemContainers on the same navbar level as the given navItemContainer, except for the given one.
 *
 * The level containers are not determined by the DOM, but the wagtail page tree encoded in the node ids, data-attributes, etc.
 * Thus we can arrange the containers to our liking, not necessarily in a tree layout, while still collapsing the containers
 *   on the same wagtail page tree level.
 *
 * @param {Node} navItemContainer Container on whose level the other containers should be collapsed.
 */
const collapseOthersOnSameLevel = (navItemContainer) => {
    const collapseLevelId = navItemContainer.getAttribute("data-navbar-level")
    const navContainersOnSameLevel = document.querySelectorAll(
        `.nav-item-container[data-navbar-level="${collapseLevelId}"]`
    )
    navContainersOnSameLevel.forEach((navContainerOnSameLevel) => {
        if (navContainerOnSameLevel === navItemContainer) return
        if (isCollapsed(navContainerOnSameLevel)) return
        bootstrap.Collapse.getOrCreateInstance(navContainerOnSameLevel).hide()
    })
}

/**
 * Gives the wanted collapse behaviour to a navItemContainer.
 *
 * With that behaviour, the container for example collapses other containers on the same navbar level
 *   when it expands.
 *
 * @param {*} navItemContainer Container to apply behaviour to.
 * @param {*} sender Node (usually navItem) that toggles the collapse of the navItemContainer.
 */
const applyCollapseBehaviour = (navItemContainer, sender) => {
    navItemContainer.addEventListener("hide.bs.collapse", (e) => {
        sender.setAttribute("aria-expanded", "false")
        e.stopPropagation()
        collapseChildren(e.target)
        toggleHideOnScrollBlock(sender)
    })
    navItemContainer.addEventListener("show.bs.collapse", (e) => {
        sender.setAttribute("aria-expanded", "true")
        e.stopPropagation()
        collapseOthersOnSameLevel(e.target)
        toggleHideOnScrollBlock(sender)
    })
}

/**
 * Toggles the right-aligned user navbar.
 */
const toggleUserNavbar = (e) => {
    const userNavContainer = document.querySelector("#nav-item-container-user")
    bootstrap.Collapse.getOrCreateInstance(userNavContainer).toggle()
    e.stopPropagation()
}

/**
 * Toggles the navbar in mobile mode.
 */
const toggleMobileNavbar = (e) => {
    if (isNavbarInDesktopMode) return
    const rootNavContainer = document.querySelector("#nav-item-container-root")
    bootstrap.Collapse.getOrCreateInstance(rootNavContainer).toggle()
    e.stopPropagation()
}

/**
 * Adds the collapse behaviour to the navbar.
 *
 * Despite using the Bootstrap Collapse feature, we control the collapses entirely on our own.
 * We cannot simply use the Boostrap Collapse via data-attributes, as they are too limited in their functionality
 *   to fully realize our navbar collapse logic.
 * So instead of mixing own logic and data-attributes, we do it completely on our own.
 * This facilitates the logic due to reduced side effects.
 */
const addNavbarCollapses = () => {
    const navDropdowns = document.querySelectorAll(
        ".nav-item.dropdown>.nav-link"
    )
    navDropdowns.forEach((navDropdown) => {
        const controlledNavContainer = document.querySelector(
            navDropdown.getAttribute("href")
        )
        navDropdown.addEventListener("click", (e) => {
            bootstrap.Collapse.getOrCreateInstance(
                controlledNavContainer
            ).toggle()
            e.stopPropagation()
        })
        applyCollapseBehaviour(controlledNavContainer, navDropdown)
    })

    const userNavToggle = document.querySelector("#nav-user-toggle")
    const userNavContainer = document.querySelector("#nav-item-container-user")
    applyCollapseBehaviour(userNavContainer, userNavToggle)

    const mobileNavToggle = document.querySelector("#nav-mobile-toggle")
    const mobileNavContainer = document.querySelector(
        "#nav-item-container-root"
    )

    applyCollapseBehaviour(mobileNavContainer, mobileNavToggle)
}

/**
 * Layout -----------------------------------------------------
 */

/**
 * Depends on the initial navbar build in the DOM.
 */
let isNavbarInDesktopMode = false

const adjustUserNavContainerLevel = () => {
    const userNavContainer = document.querySelector("#nav-item-container-user")
    userNavContainer.setAttribute(
        "data-navbar-level",
        isNavbarInDesktopMode ? "#nav-level-1" : "#nav-level-0"
    )
}

const adjustNavbarCollapseOnLayoutChange = () => {
    const rootNavContainer = document.querySelector("#nav-item-container-root")
    const expandedContainer = rootNavContainer.querySelector(
        ".nav-item-container.show"
    )
    if (expandedContainer && isCollapsed(rootNavContainer)) {
        bootstrap.Collapse.getOrCreateInstance(rootNavContainer).show()
    } else if (!expandedContainer && !isCollapsed(rootNavContainer)) {
        // By temporarily setting the transition duration to 0s we prevent
        //   the navbar items from shortly disappearing when collapsing the container.
        const originalTransitionDuration =
            rootNavContainer.style.transitionDuration
        rootNavContainer.style.transitionDuration = "0s"
        bootstrap.Collapse.getOrCreateInstance(rootNavContainer).hide()
        rootNavContainer.style.transitionDuration = originalTransitionDuration
    }
}

/**
 * Moves the nodes of navbar level 1 and higher from the mobile to the desktop layout.
 * The number of levels is determined by `numberOfSupportedLevels`.
 */
const moveNonRootLevelsToDesktopLayout = () => {
    const levels = [...Array(numberOfSupportedLevels).keys()].slice(1)
    levels.forEach((levelId) => {
        const navItemContainers = document.querySelectorAll(
            `*:not(#nav-level-right)>.nav-item-container[data-navbar-level='#nav-level-${levelId}']`
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

/**
 * Moves the nodes of the root navbar level from the mobile to the desktop layout.
 */
const moveRootLevelToDesktopLayout = () => {
    const rootNavLevelContainer = document.querySelector("#nav-level-0")
    const rootLevel = document.querySelector("#nav-item-container-root")
    rootNavLevelContainer.appendChild(rootLevel)
    document.getElementById("user-information-username").hidden = false
}
const setDesktopNavbar = () => {
    if (isNavbarInDesktopMode) return
    isNavbarInDesktopMode = true
    adjustNavbarCollapseOnLayoutChange()
    moveNonRootLevelsToDesktopLayout()
    moveRootLevelToDesktopLayout()
}

/**
 * Moves the nodes of navbar level 1 and higher from the desktop to the mobile layout.
 * The number of levels is determined by `numberOfSupportedLevels`.
 */
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


/**
 * Moves the nodes of the root navbar level from the desktop to the mobile layout.
 */
const moveRootLevelToMobileLayout = () => {
    const bottomNavContainer = document.querySelector(".navbar-bottom-content")
    const rootLevel = document.querySelector("#nav-item-container-root")
    bottomNavContainer.appendChild(rootLevel)
    document.getElementById("user-information-username").hidden = true
}

const setMobileNavbar = () => {
    if (!isNavbarInDesktopMode) return
    isNavbarInDesktopMode = false
    moveNonRootLevelsToMobileLayout()
    moveRootLevelToMobileLayout()
    adjustNavbarCollapseOnLayoutChange()
}

/**
 * Make the navbar adapt to the current size of the window.
 */
const adaptNavbarToWindowSize = () => {
    isMobileLayoutActive() ? setMobileNavbar() : setDesktopNavbar()
    adjustUserNavContainerLevel()
}

const _navbar = document.querySelector("#navbar")
const _navbarTop = _navbar.querySelector(".navbar-top")
const _page = document.querySelector("#page")

/**
 * Emulate sticky position on Desktop.
 */
const updateNavbarPosition = () => {
    const pageClientY = _page.getBoundingClientRect().top
    _navbar.style.top = (pageClientY < 0 ? 0 : pageClientY) + "px"
}

/**
 * Make sure the page always has enough padding to not be overlayed by the navbar.
 */
const respectNavbarHeight = () => {
    const resizeObserver = new ResizeObserver((entries) => {
        _page.style.paddingTop = isNavbarInDesktopMode
            ? _navbarTop.offsetHeight + "px"
            : _navbarTop.offsetHeight +
              remToPx(defaultPagePadding + navbarBarHeight) +
              "px"
    })
    resizeObserver.observe(_navbarTop)
}
