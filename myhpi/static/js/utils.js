/**
 * Converts a given rem value into pixel.
 *
 * @param {number} rem Rem value to convert.
 * @returns Number of pixel the given rem value corresponds to.
 *
 * Source: https://stackoverflow.com/questions/36532307/rem-px-in-javascript
 */
function remToPx(rem) {
    return rem * parseFloat(getComputedStyle(document.documentElement).fontSize)
}
