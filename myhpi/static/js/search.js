const initializeSearch = () => {
  const searchModal = document.querySelector("#searchModal")

  /**
   * Focus input in search modal when showing.
   * We use both events:
   *   - `show.bs.modal` focuses immediately (with a short delay), so the user can start typing before the popup is completely visible
   *   - `shown.bs.modal` refocuses the input once the popup is completely visible. Without, the input would loose its focus at that point
   */
  searchModal.addEventListener("show.bs.modal", () =>
    setTimeout(() => document.querySelector("#searchInput").focus(), 200),
  )
  searchModal.addEventListener("shown.bs.modal", () =>
    document.querySelector("#searchInput").focus(),
  )

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "k") {
      showSearchModal()
      event.preventDefault()
    }
  })
}

const showSearchModal = () => {
  const searchModal = document.querySelector("#searchModal")
  bootstrap.Modal.getOrCreateInstance(searchModal).show()
}
