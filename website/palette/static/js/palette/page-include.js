
let autoMain = function() {
    console.log('palette page include')
    let p = window.p = new Palette()
    p.addCommand(GotoCommand)
}


class Palette {
    selector = '.palette-container'
    open = false

    constructor() {
        this.hook()
        this.commands = []
    }

    hook() {
        document.addEventListener('keydown', this.keydownHandler.bind(this))
        this.hide()
    }

    addCommand(commandClass) {
        let com = new commandClass()
        this.commands.push(com)
    }

    keydownHandler(ev) {
        if(ev.key == 'Escape' && this.open) {
            // close
            return this.hide()
        }

        if(this.isActivationKeys(ev)) {
            ev.preventDefault()
            if(this.open) {
                return this.hide()
            }

            return this.show()
        }

        console.log(ev)
    }


    isActivationKeys(ev) {
        return (ev.ctrlKey
                && ev.shiftKey
                && ev.key.toLowerCase() == 'p')
    }

    getEntity() {
        return document.querySelector(this.selector)
    }

    show() {
        this.getEntity().classList.remove('display-none')
        this.open = true
        this.setFocus()
    }

    setFocus() {
        this.getEntity().querySelector('.pseudo-field').focus()
    }

    hide() {
        this.getEntity().classList.add('display-none')
        this.open = false
    }
}


class Command {
    /* An entry to the palette */

    // A name for the command, prefer unique for this unit.
    name = 'uniqueName'
    // A user-friendly name label for printing
    label = 'Command Label'
    // A range of searchable keys.
    keywords = [
        "Command",
    ]

    onExecute() {
        /* Request a command execution, likely in the form of a user-field
        entry then an activation [enter]. */
    }

    onHit() {
        /* This command is listed as one of many hits.
        Preferably don't perform a lot of work here. */
    }

    onHitOne() {
        /* This command is the single hit for the given input.
        The command has an opportunity to hot-load immediate information
        before the user presses activate [enter] */
    }
}


class GotoCommand {
    /* The user can navigate to any file or directory using a "goto ..." command

    1. The user can type "goto" [select] and enter the DEST
    2. A Special hook for "CTRL + /", activating the command panel in goto mode.
    */
   name = 'goto'
   label = 'Goto'
   keywords = ['goto']
}


;autoMain();