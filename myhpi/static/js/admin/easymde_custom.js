window.wagtailMarkdown = {};
window.wagtailMarkdown.options = {
    spellChecker: false,
    toolbar: ["bold", "italic", "heading-1", "heading-2", "unordered-list",
            {
                name: "start meeting",
                action: startMeeting,
                className: "fa fa-play", // Look for a suitable icon
                title: "Start or continue meeting (Ctrl/Cmd-Alt-R)",
            },
            {
               name: "end meeting",
               action: endMeeting,
               className: "fa fa-stop",
               title: "End meeting"
            },
            {
                name: "pause",
                action: pauseMeeting,
                className: "fa fa-pause",
                title: "Pause meeting"
            },
            {
                name: "enter",
                action: enterMeeting,
                className: "fa fa-user-plus",
                title: "Enter the meeting"
            },
            {
               name: "leave",
               action: leaveMeeting,
               className: "fa fa-user-times",
               title: "Leave the meeting"
            },
            {
                name: "quorum",
                action: addQuorum,
                className: "fa fa-users",
                title: "Add quorum text"
            },
            {
                name: "resolution",
                action: addResolution,
                className: "fa fa-euro",
                title: "Add resolution"
            },
            {
                name: "Internal link",
                action: function (editor) {
                    ModalWorkflow({
                        onError: function (error) {
                            console.log(error)
                        },
                        url: "/admin/choose-page/",
                        onload: PAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
                        responses: {
                            pageChosen: function (t) {
                                editor.codemirror.replaceSelection("[" + t.title + "](page:" + t.id + ")");
                            }
                        },

                    })
                },
                className: "fa fa-link",
                title: "Add internal link"
            },
            {
                name: "Image",
                action: function (editor) {
                    ModalWorkflow({
                        onError: function (error) {
                            console.log(error)
                        },
                        url: "/admin/images/chooser/",
                        onload: IMAGE_CHOOSER_MODAL_ONLOAD_HANDLERS,
                        responses: {
                            chosen: function (t) {
                                editor.codemirror.replaceSelection("![" + t.title + "](image:" + t.id + ",class=rendered-image,filter=width-800)");
                            }
                        },

                    })
                },
                className: "fa fa-image",
                title: "Add image"
            },
             "fullscreen"
        ],

}


// convenience function
function getCurrentTime(){
    return new Date().toLocaleTimeString("de-DE", {timeStyle: 'short'})
}

// Custom button actions

function startMeeting(editor) {
    const cm = editor.codemirror;
    let output = '';
    const currentTime = getCurrentTime()

    const unfinishedBreak = cm.getValue().match(/\|break\|\((\d+):(\d+)\)\(\)/);
    const startedMeeting = cm.getValue().match(/\|start\|\((\d+):(\d+)\)/);

    if (unfinishedBreak) {
        const cursor = cm.getSearchCursor(/\|break\|\((\d+):(\d+)\)\(\)/);
        cursor.findNext();
        const unfinishedBreakPosition = cursor.from();
        const relativeInsertPosition = unfinishedBreak[0].search(/\(\)/) + 1;

        // set cursor position to absolute insert position
        cm.setCursor({line: unfinishedBreakPosition.line, ch: unfinishedBreakPosition.ch + relativeInsertPosition});

        output = currentTime;
        cm.replaceSelection(output);
    }
    else if (!startedMeeting) {
        output = "\n|start|(" + getCurrentTime() + ")";
        cm.replaceSelection(output);
    }
}

function endMeeting(editor) {
    const cm = editor.codemirror;
    let output = '';

    output = "\n|end|(" + getCurrentTime() + ")";
    cm.replaceSelection(output);
}

function pauseMeeting(editor){
    const cm = editor.codemirror;
    let output = '';

    output = "\n|break|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function enterMeeting(editor){
    const cm = editor.codemirror;
    let output = '';

    output = "\n|enter|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function leaveMeeting(editor){
    const cm = editor.codemirror;
    let output = '';

    output = "\n|leave|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function addQuorum(editor){
    const cm = editor.codemirror;
    let output = '';

    output = "\n|quorum|(/)";
    cm.replaceSelection(output);
}

function addResolution(editor){
    const cm = editor.codemirror;

    const output = "\n|resolution|()()() [||]";
    cm.replaceSelection(output);

    // move the cursor to the first missing field
    const position = cm.getCursor();
    position.ch = "|resolution|(".length;
    cm.focus();
    cm.setCursor(position);
}
