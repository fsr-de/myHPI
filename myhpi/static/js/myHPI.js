window.onload = () => {
    addCollapseToLevel2NavContainers()
}

/**
 * Makes second level menu items collapse when a root level menu item is toggled.
 * 
 * The Bootstrap Collapse Plugin only supports toggling collapsed states between
 * containers with the same parent. This means for the menu: Supposed a menu structure of
 * A > A1 > A2 and B > B1, with A and B being root level menu items always shown in the
 * navigation bar. If A1 and A2 are expanded and then the root menu item B is clicked 
 * (which expands B1), A1 would be replaced with B1, but A2 would still be expanded.
 * This method makes A2 collapse as well.
 */
function addCollapseToLevel2NavContainers() {
    let levelOneItemContainers = document.querySelectorAll('.nav-level-1 .nav-item-container')
    levelOneItemContainers.forEach(itemContainer => {
        itemContainer.addEventListener('hide.bs.collapse', () => {
            const levelTwoItemContainers = document.querySelectorAll('.nav-level-2 .nav-item-container')
            levelTwoItemContainers.forEach(itemContainer => bootstrap.Collapse.getOrCreateInstance(itemContainer, { toggle: false, parent: '.nav-level-2' }).hide())
        })
    })
}
