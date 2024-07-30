const addTextArrayItem = function (id) {
  // create a new item
  const container = document.getElementById(`text-array-${id}`)
  const wrapper = document.createElement("div")
  const input = document.createElement("input")
  const remover = document.createElement("span")
  wrapper.append(input)
  wrapper.append(remover)
  container.append(wrapper)
  input.type = "text"
  // prevent submission on enter
  input.addEventListener("keydown", function (event) {
    onTextArrayItemInputKeyDown(id, event, this)
  })
  // synchronize AFTER the character has been written
  input.addEventListener("keyup", function () {
    synchronizeTextArray(id)
  })
  remover.innerText = "X"
  remover.addEventListener("click", function () {
    removeTextArrayItem(id, this)
  })
  synchronizeTextArray(id)
  return input
}

const removeTextArrayItem = function (id, inputNode) {
  inputNode.parentNode.remove()
  synchronizeTextArray(id)
}

const onTextArrayItemInputKeyDown = function (id, event, inputNode) {
  if (event.key === "Enter") {
    // prevent form from being submitted
    event.preventDefault()
    // add new item
    addTextArrayItem(id).focus()
  }
  synchronizeTextArray(id)
}

const synchronizeTextArray = function (id) {
  const container = document.getElementById(`text-array-${id}`)
  const syncInput = document.getElementById(`id-${id}`)
  const inputs = container.querySelectorAll("input")
  // get all items, filter for empty inputs and write serialized list to dedicated input
  const items = Array.from(inputs)
    .map(function (input) {
      return input.value.trim()
    })
    .filter(function (item) {
      return item.length !== 0
    })
  syncInput.value = JSON.stringify(items)
}
