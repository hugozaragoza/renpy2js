// --------------------------------------------------------
// GLOBALS
// --------------------------------------------------------
const CHOICE_STACK = "__CHOICE_STACK"
const CHOICES_TAKEN = "__CHOICES_TAKEN"
const SHOW_DEBUG = "__SHOW_DEBUG"
const CHAR_IMGS = "CHAR_IMGS"
const PREFIX_CHOICEID = ""

var idCounter = 0
var currentLabel = ""
van
currentPosition = 0

function render_init() {
    log("=============================================================================")
    log("=============================================================================")
    hlog("render_init")
    idCounter = 0
    window.debug = true
    window.context = new Map()
    window.context.set(SHOW_DEBUG, false)
    window.context.set(CHOICES_TAKEN, [])
    window.context.set(CHAR_IMGS, {})

    let s = localStorage.getItem(CHOICE_STACK) === null ? [] : localStorage.getItem(CHOICE_STACK).split(",")
    window.context.set(CHOICE_STACK, s); // if persisted
    localStorage.removeItem(CHOICE_STACK)
    log(window.context.get(CHOICE_STACK), "loaded CHOICE_STACK (type:" + (typeof window.context.get(CHOICE_STACK))
    );


    render_par("Click to start...", canvas, false)
    render_debug()
    render_start()
}

// --------------------------------------------------------
// UTILS
// --------------------------------------------------------

function deleteAllCookies() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
}

function log(msg, header = "") {
    if (window.debug) {
        console.log(header ? header + ":: " : "", msg)
    }
}

function hlog(msg) {
    if (window.debug) {
        console.log(msg + " <========================")
    }
}

function warn(msg) {
    console.assert(false, msg)
}

function assert(act, des, msg = "") {
    console.assert(act == des, "ASSERT FAILED: Expected:" + des + "\nGot:" + act + "\n" + msg)

}

// --------------------------------------------------------
// NAVIGATION
// --------------------------------------------------------

function render_debug() {
    debug_str = "<ul>"
    for ([k, v] of window.context.entries()) {
        debug_str += "<li class='debug'>" + k + "=" + v + "</li>"
    }
    debug_str += "<li class='debug'> localStorage." + CHOICE_STACK + " = " + localStorage.getItem(CHOICE_STACK) + "</li>"

    debug_str += "</ul>"

    var debugNode = document.getElementById("debug")
    if (window.context.get("__SHOW_DEBUG")) {
        debugNode.innerHTML = debug_str;
    } else {
        debugNode.innerHTML = "";
    }

}

function revealItem(n) {
    //hlog("revealItem")
    render_debug();
    var div = document.getElementById("canvas")
    while (n > 0) {
        n--;
        lis = document.getElementsByClassName("showOnClick")
        if (lis.length < 1) {
            break
        }
        lis[0].classList.remove("showOnClick")
        div.scrollTop = div.scrollHeight * 100;
    }
}

function fixedbutton_click(event) {
//    hlog("----- fixedbutton_click")
    revealItem(10)
}

// --------------------------------------------------------
// RENDER
// --------------------------------------------------------


function toChoiceId(id) {
    return PREFIX_CHOICEID + id
}

function fromChoiceId(id) {
    return id.substring(PREFIX_CHOICEID.length)
}

function click_on_choice(event, id = null) {
    revealItem(999) // when clicking from stack we need to force reveal anything unrevealed
    hlog("click_on_choice" + (id ? " " + id : ""))
    if (id == null) { // get info from event
        var parent = event.path[1]
        var divid = parent.id
        id = fromChoiceId(event.path[0].id)
    } else { // get info from id
        var parent = document.getElementById(id).parentElement
        var divid = parent.id
    }
    console.assert(parent, "!!! failed to find choice parent")
    console.assert(divid, "!!! failed to find choice divid")
    console.assert(id, "!!! failed to find id")

    arr = (window.context.get(CHOICES_TAKEN) || [])
    arr.push(id)
    window.context.set(CHOICES_TAKEN, arr)
    log(window.context.get(CHOICES_TAKEN), "NEW CHOICES_TAKEN")

    var sayblocks = data[id]
//    log(sayblocks, "sayblock")

    // 1. Remove Menu
    lis = document.getElementsByClassName(divid)
    console.assert(lis.length > 0, "FAILED TO FIND MENU DIV?")
    for (e of lis) {
        e.onclick = null
        if (e.id == id) {
            e.classList.remove("choice_pending");
            e.classList.add("choice_selected");
        } else {
            e.classList.remove("choice_pending");
            e.classList.add("choice_unselected");
        }
        e.removeEventListener("click", click_on_choice);
    }

    // 2. Record choice (for display)
    document.cookie = id + "=true"

    // 3. Render new content
    for (sayblock of sayblocks) {
        render_block(sayblock, parent)
    }
    revealItem(1)


}


function render_start() {
    var canvas = document.getElementById("canvas")
    currentLabel = "start"
    currentPosition = 0
    render()
}

function render(n = 1) {
    if (currentPosition > 0) {
        log("NOT IMPLEMENTED!!!")
    } else {
        render_labelblock('start', 0, canvas)
        currentPosition += 1
    }

}

function render_charImage(char) {
    
    if (!char) {
        return;
    }
    render_img("joanna3.png", char)
}

function

function render_img(img_url, name) {
    bottom = document.getElementById('bottom')
    var div = appendChild(bottom, 'div')
    div.classList.add("bottom_image")
    img = appendChild(div, 'img');
    img.src = "img/" + img_url

    title = appendChild(div, 'p');
    title.classList.add("bottom_image_title")
    title.innerHTML = name
}

function render_choices(choices, parent) {
    hlog("render_choices")
    log(choices, "choices")
    var div = appendChild(parent, 'div')
    div.classList.add("showOnClick")
    parent = div

    var newParagraph
    for (choice of choices) {
        //log(choice,"choice")
        var choice_msg = choice[1]
        var choice_id = toChoiceId(choice[0])
        log(choice_id, "choice_id")
        newParagraph = render_par(choice_msg, parent, false)
        newParagraph.id = choice_id
        newParagraph.classList.add("choice_pending", parent.id);
        newParagraph.addEventListener('click', click_on_choice)
        if (read_cookies()[choice_id]) {
            newParagraph.classList.add("choice_visited");
        }
    }
    // document.getElementById(newParagraph.id).scrollIntoView(true);

}

function add_click_reveal(parent) {
    parent.addEventListener('click', (event) => {
        if (event.target == parent) {
            log("CLICK reveal on [" + parent + "]");
            revealItem(1);
        }
    }, true);

}

function render_par(txt, parent, hide = true) {
    // hlog("render_par")
    var newParagraph = document.createElement('p');
    add_click_reveal(newParagraph)
    if (txt && txt.length > 0 && txt[0] != txt[0].toUpperCase()) {
        txt = "&nbsp;&nbsp;" + txt
    }
    newParagraph.innerHTML = txt;
    if (hide) {
        newParagraph.classList.add("showOnClick")
    }
    parent.appendChild(newParagraph, parent)
    return newParagraph
}

function style_renpyline(line) {
    line = line.replace("{b}", "<b>")
    line = line.replace("{/b}", "</b>")
    line = line.replace("{i}", "<i>")
    line = line.replace("{/i}", "</i>")
    return line
}

function var_inc(name, increment = 1) {
    var val = window.context.get(name) || 0
    // log("var_inc " + name + " by [" + increment + "], was [" + val + "]")
    window.context.set(name, val + increment)
}

function render_sayline(sayline, parent) {
    //hlog("render_sayline")
    assert(sayline[0], "say_line")
    sayline = sayline[1]
    //log(sayline, "sayline")
    assert(sayline.length, 2, "par element should be (character,line), was: [" + sayline + "]")
    var say = style_renpyline(sayline[1])
    var char = sayline[0]
    var line = say
    render_charImage(char)
    if (char && char.length > 0) {
        line = "<strong>" + char.toUpperCase() + ":</strong>&nbsp;&nbsp;&nbsp;&nbsp;" + say
    }
    //log("-----")
    var_inc("__saylines")
    return render_par(line, parent)


}

function appendChild(parent, type, id = null) {
    if (id == null) {
        id = idCounter++
    }
    var newDiv = document.createElement(type);
    newDiv.id = id
    parent.appendChild(newDiv, parent)
    return newDiv
}

function render_block(block, parent) {
    //hlog("render_block")
    //log(block, "block")
    if (block.length < 1) {
        return
    }

    var newDiv = parent
    var etype, evalue
    [etype, evalue] = block
//    log(etype, "etype")
//    log(evalue, "evalue")
    switch (etype) {
        case "code_line":
            log("case code_line")
            var script = document.createElement("script");
            script.innerHTML = evalue
            newDiv.appendChild(script);
            currentPosition += 1
            break;
        case "say_line":
//            log("case say_line")
            render_sayline(block, newDiv)
            currentPosition += 1
            break;
        case "jump_line":
            log("case jump_line")
            render_labelblock(evalue, newDiv)
            break;
        case "menu_tree":
            log("case menu_tree")
            render_menu_tree(block, newDiv)
            let s = window.context.get(CHOICE_STACK) || []
            log(s, "S <---")
            if (s.length > 0) {
                hlog("CHOOSING FIRST FROM STACK: " + s)
                log(typeof s)
                let choice = s.shift()
                window.context.set(CHOICE_STACK, s)
                click_on_choice(null, choice)
            }
            break;
        case "if_tree":
            log("case if_tree")
            render_if_tree(block, newDiv)
            break;
        default:
            console.error("!! UNKNOWN render_block RENDER TYPE: [" + etype + "]")
    }
    return newDiv.id
}

function render_if_tree(tree, parent) {
    hlog("render_if_tree")
    log(tree, "lis")
    assert(tree[0], "if_tree")
    var lis = tree[1];
    if (lis.length > 2 || lis.length < 1) {
        assert(false, "If block length should be 1 or 2")
    }
    var if_start = lis[0]
    var if_else = lis.length == 2 ? lis[1] : null;
    assert(if_start[0], "if_start")
    if (if_else) {
        assert(if_else[0], "if_else")
    }

    var exp = if_start[1];
    var if_block = if_start[2];
    var cond = Function('"use strict";return (' + exp + ')')()
    log(cond, "cond")
    if (cond) {
        log("IF " + exp)
        for (b of if_block) {
            render_block(b, parent)
        }
    } else if (if_else) {
        log("ELSE " + exp)
        for (b of if_else[1]) {
            render_block(b, parent)
        }
    } else {
        log("IF skipped because no ELSE")
    }
}

function render_menu_tree(menu_tree, parent) {
    hlog("render_menu_tree")
    log(menu_tree, "lis")
    assert(menu_tree[0], "menu_tree")
    var lis = menu_tree[1]
    choices = []
    var i = 0;
    while (lis[i][0] != "menu_choice") {
        render_block(lis[i], parent)
        i += 1
    }
    for (; i < lis.length; i++) {
        var choicetree = lis[i]
        //log(choicetree, "choicetree")
        assert(choicetree[0], "menu_choice")
        assert(choicetree.length, 2)
        var choice = [choicetree[1][0], choicetree[1][1]]
        //log(choice, "choice_item")
        choices.push(choice)
    }
    render_choices(choices, parent)
}

function read_cookies() {
    var ret = {};
    const cookies = document.cookie.split('; ')
    for (let cookie of cookies) {
        var c = cookie.split('=')
        ret[c[0]] = c[1]
    }
    return ret
}

function render_end(parent) {
    var current = window.context.get("__saylines")
    var cookies = read_cookies()
    var max = cookies["__max_lines"] || 0
    if (current > max) {
        max = current
        document.cookie = "__max_lines=" + max
    }
    render_par("<b>THE END</b> <wbr> ", parent);
    render_par("(You read " + current + " lines of the story in this run)", parent);
    render_par("(Your record is: " + max + ")", parent);
    render_par('<a class="choice_pending" href=\".\">RELOAD page to re-start</a>', parent)
    return
}

function render_labelblock(label, parent) {
    hlog("render_labelblock")
    log(label, "label")
    log(position, "position")
    currentPosition = 0
    currentLabel = label
    if (label == "__END") {
        render_end(parent)
    } else {
        var value = data[label]
        console.assert(value != null, "ERROR: Content missing for label: " + label)
        render_block(value[position], parent)
    }
}

