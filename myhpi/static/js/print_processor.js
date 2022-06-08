
function processPageForPrinting() {
    moveLinksToFooter();
    expandAbbreviations();
}

function moveLinksToFooter() {
    let content = document.getElementsByClassName("minutes-text")[0];
    if (!content) return;

    let footer = document.getElementById("minutes-footer");
    let linkList = document.createElement("ol");

    let articleLinks = content.getElementsByTagName("a");
    for (let i = 0; i < articleLinks.length; i++) {
        const articleLink = articleLinks[i];
        articleLink.innerHTML += "<sup class='print-generated-tag'>[" + (i + 1) + "]</sup>";
        let footnote = document.createElement("li");
        footnote.innerText = articleLink.href;
        linkList.appendChild(footnote);
    }
    footer.appendChild(linkList);
}

function expandAbbreviations() {
    let content = document.getElementsByClassName("minutes-text")[0];
    if (!content) return;
    let abbreviations = content.getElementsByTagName("abbr");
    for (let i = 0; i < abbreviations.length; i++) {
        let short = abbreviations[i].innerText;
        let long = abbreviations[i].getAttribute("title");

        let replacement = document.createElement("span");
        replacement.classList.add("print-expanded-abbr");
        replacement.setAttribute("short", short);
        replacement.setAttribute("long", long);
        replacement.innerText = long;
        abbreviations[i].parentNode.replaceChild(replacement, abbreviations[i]);
    }
}

function removePrintingProcessing() {
    let content = document.getElementsByClassName("minutes-text")[0];
    if (!content) return;
    let footer = document.getElementById("minutes-footer");
    footer.innerText = "";

    let generated = document.getElementsByClassName('print-generated-tag');
    while (generated.length > 0) {
        generated[0].remove();
    }

    let abbreviationReplacements = content.getElementsByClassName("print-expanded-abbr");
    for (let i = 0; i < abbreviationReplacements.length; i++) {
        let replacement = abbreviationReplacements[i];
        let short = replacement.getAttribute("short");
        let long = replacement.getAttribute("long");

        let abbr = document.createElement("abbr");
        abbr.setAttribute("title", long);
        abbr.innerText = short;
        replacement.parentNode.replaceChild(abbr, replacement);
    }
}

addEventListener("beforeprint", processPageForPrinting);
addEventListener("afterprint", removePrintingProcessing);
