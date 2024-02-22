/**
 * Sidebar script. Contains:
 *
 * - Hiding table of contents offcanvas on anchor click
 *
 */

/**
 * Initialization
 */

/**
 * Applies necessary JS handlers to sidebar.
 * Call when sidebar HTML was loaded. Call handler only once per page.
 */
const initializeSidebar = () => {
  applyTocOffcanvasBehaviour()
}

/**
 * Hide ToC offcanvas on anchor click -----------------------------------------------
 */

const applyTocOffcanvasBehaviour = () => {
  const anchors = document.querySelectorAll("#sidebar-offcanvas a")
  const offcanvas = new bootstrap.Offcanvas(
    document.querySelector("#sidebar-offcanvas")
  )
  anchors.forEach((anchor) =>
    anchor.addEventListener("click", () => offcanvas.hide())
  )
}
