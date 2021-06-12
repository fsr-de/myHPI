/*
 * vim:sw=4 ts=4 et:
 * Copyright (c) 2015 Torchbox Ltd.
 * felicity@torchbox.com 2015-09-14
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely. This software is provided 'as-is', without any express or implied
 * warranty.
 */

/*
 * Used to initialize Simple MDE when Markdown blocks are used in StreamFields
 */
function easymdeAttach(id) {
    var mde = new EasyMDE({
        element: document.getElementById(id),
        autofocus: false,
        toolbar: ["bold", "italic", "heading-1", "heading-2", "unordered-list",
            {
                name: "start meeting",
                action: startMeeting,
                className: "fa fa-play", // Look for a suitable icon
                title: "start or continue meeting (Ctrl/Cmd-Alt-R)",
            },
            {
               name: "end meeting",
               action: endMeeting,
               className: "fa fa-stop",
               title: "end meeting"
            },
            {
                name: "pause",
                action: pauseMeeting,
                className: "fa fa-pause",
                title: "pause meeting"
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
                            imageChosen: function (t) {
                                editor.codemirror.replaceSelection("![" + t.title + "](" + t.preview.url + ")")
                            }
                        },

                    })
                },
                className: "fa fa-image",
                title: "Add image"
            },
             "fullscreen"
        ],
    });
    mde.render();

    mde.codemirror.on("change", function () {
        $('#' + id).val(mde.value());
    });
}

/*
* Used to initialize Simple MDE when MarkdownFields are used on a page.
*/
$(document).ready(function () {
    $(".object.markdown textarea").each(function (index, elem) {
        easymdeAttach(elem.id);
    });
});

/*
* Used to initialize content when MarkdownFields are used in admin panels.
*/
$(document).on('shown.bs.tab', function (e) {
    $('.CodeMirror').each(function (i, el) {
        setTimeout(
            function () {
                el.CodeMirror.refresh();
            }, 100
        );
    });
});

// convenience function
function getCurrentTime(){
    return new Date().toLocaleTimeString([], {timeStyle: 'short'})
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
    var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();

    output = "\n|end|(" + getCurrentTime() + ")";
    cm.replaceSelection(output);
}

function pauseMeeting(editor){
    var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();

    output = "\n|break|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function enterMeeting(editor){
    var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();

    output = "\n|enter|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function leaveMeeting(editor){
    var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();

    output = "\n|leave|(" + getCurrentTime() + ")()";
    cm.replaceSelection(output);
}

function addQuorum(editor){
     var cm = editor.codemirror;
    var output = '';
    var selectedText = cm.getSelection();

    output = "\n|quorum|(/)";
    cm.replaceSelection(output);
}
