/*
The `AltMenu` provides a context menu (right click) on a target object.
It's designed to be minimal, quick to change, and easy to adapt.

Fundamentally it is a fancy div positioning, and 'contextmenu' event handler.

        let am = window.am = new AltMenu()
        am.install(window)

Once active a `contextmenu` event activates a target test. If the correct
attribute exists on the target, we activate a new alt-menu.

---

As the handler is actioned through active bluring, the position and styling of
the alt-menu is arbitrary.

 */
console.log('AltMenu')

const autoMain = function(){
    let am = window.am = new AltMenu()
    am.install(window)
}


const inParentClass = function(className, node) {
     while (node != null) {
        if(node.classList?.contains(className)) {
            return true
        }
        node = node.parentNode;
     }

     return false;
}


const getParentByClassName = function(target, className) {
    // .getBoundingClientRect()
    let node = target//.parentNode
    while (node != null) {
        if(node.classList?.contains(className)) {
            return node
        }
        node = node.parentNode;
     }

     return node
}


function isDescendant(parent, child) {
     var node = child.parentNode;
     while (node != null) {
         if (node == parent) {
             return true;
         }
         node = node.parentNode;
     }
     return false;
}



class Menu {

    targetMenuClass = 'alt-click-menu'

    show(menu){
        menu = (menu || this.getMenuEntity())
        this.sendToTop(menu)
        menu.classList.remove('hidden')
        this.showing = true
    }

    getMenuClass() {
        return this.targetMenuClass
    }

    hide(menu){
        menu = menu || this.getMenuEntity();
        menu?.classList.add('hidden')
        menu.style.left = "-400px"
        this.subMenu?.hide()
        this.showing = false

    }

    destroy() {
        this.hide()
        this.menuNode = undefined
    }

    getMenuEntity(){
        if(!this.menuNode) {
            this.menuNode = document.getElementsByClassName(this.getMenuClass())[0]
            this.internalHooks(this.menuNode)
        }

        return this.menuNode
    }

    getPrimaryParent(){
        return window.document.body
    }

    ensureWithinPrimary(menu) {
        menu = (menu || this.getMenuEntity())
        const primary = this.getPrimaryParent()
        if(menu.parentNode != primary) {
            this.moveTo(primary, menu)
        }
    }

    moveToBody(menu) {
        menu = (menu || this.getMenuEntity())
        this.moveTo(window.document.body, menu)
    }

    moveTo(primary, menu){
        primary.appendChild(menu)
    }

    sendToTop(menu) {
        menu = (menu || this.getMenuEntity())
        menu.parentNode.appendChild(menu)
    }

    spawnByRect(clientRect) {
        /* Given a rectangle, spawn the menu relative to the left or right
        of the rect.

            ev.target.getBoundingClientRect()
        */
        let point = this.shiftPointFromRect(clientRect)
        console.log(point)
        this.spawnAt(point)
    }

    shiftPointFromRect(clientRect){
        let point = clientRect.right
        let menu = this.getMenuEntity()
        let menuWidth = menu.clientWidth
        if(menuWidth == 0) {
            console.warn('no client width')
        }
        let rightTip = point + menuWidth
        let viewport = window.visualViewport
        let viewWidth = viewport.width
        if(rightTip > viewWidth) {
            // try the left side, flowing left.
            console.warn('overflow')
            let leftPoint = [clientRect.left, clientRect.y]
            let newLeft = leftPoint[0] - menuWidth
            // if(newLeft > viewport.pageLeft) {
                // Point is moved over to the left a lot.
                point = newLeft
            // }
        }

        return [point, clientRect.y]
    }

    spawnAtPageXY(ev) {
        let point = [ev.pageX, ev.pageY]
        this.spawnAt(point)
    }

    spawnAt(point, viewport) {
        // let point = [ev.screenX, ev.screenY]
        let menu = this.getMenuEntity()
        let menuWidth = menu.clientWidth
        let menuHeight = menu.clientHeight
        let shape = [menuWidth, menuHeight]
        // let left = point[0]
        // let top = point[1]
        let [left, top] = this.shiftPoint(point, viewport || window.visualViewport, shape)

        menu.style.top = `${top}px`
        menu.style.left = `${left}px`
        // console.log('contextmenu_path', ev, point)
        // console.log('contextmenu_path', point)
        // If the left + menuWidth > screenwidth, move the div.
        this.show(menu)
        menu.querySelector('a').focus()
    }

    shiftPoint(point, viewport, shape) {
        /* Given a "point", its viewpoint, and the 'shape' to position,
        return an adjusted "point" as the best place to spawn the shape.

            shiftPoint([100, 100], [100, 100], [50, 50])
            [50, 50]

         */
        let left = point[0]
        let top = point[1]

        let viewWidth = viewport.width
        let viewHeight = viewport.height

        let rightPoint = left + shape[0]
        let leftOverflow = viewWidth - rightPoint;
        if(leftOverflow < 0) {
            // move left by the leftOverflow
            left += leftOverflow - 1
            if(left < 0) {
                left = 0
            }
        }


        let bottomPoint = top + shape[1]
        let topOverflow = viewHeight - bottomPoint;
        if(topOverflow < 0) {
            // move top by the topOverflow
            top += topOverflow - 1
            if(top < 0) {
                top = 0
            }
        }

        return [left, top]
    }

    internalHooks(entity) {
    }

}


class AltMenu extends Menu {

    /* If `true` hide the alt-menu upon a 'blur' event.
       If `false` the menu will persist on the page, waiting for an esc or `click`.
     */
    blurHide = false

    /* If `true` supress the context menu on this alt-menu.
       If `false`, the context menu will appear over the alt-menu in the default
         manner.
     */
    supressSubContextMenu = true

    /*
    Populated upon a context menu spawn.
     */
    originNode = undefined

    oncontextmenu(ev){
        if(this.isChild(ev.target) ) {
            // A click on a menu inner item.
            if(this.supressSubContextMenu) {
                // Force stop the inner context menu.
                ev.preventDefault()
            }
            // Allow the context menu to present on this inner item.
            return
        }

        if(this.showing) {
            // Naturally perform a hide to ensure any old context menus
            // are removed.
            this.hide()
        }


        let t = this.getDetectValue(ev)
        let funcName = `contextmenu_${t}`

        if(this[funcName] != undefined) {
            // ev.stopImmediatePropagation()
            ev.preventDefault()

            // The target function exists.
            return this[funcName](ev)
        }
    }

    getDetectValue(ev) {
        let target = ev.target;
        // console.log('oncontextmenu', target)
        let t = target.dataset['type']
        return t
    }

    internalHooks(entity) {
        entity.addEventListener('mouseover', this.menuMouseover.bind(this));
    }

    contextmenu_path(ev) {
        /*
        Called by the handoff from oncontextmenu upon the target node
        `data-type="path"`

        Spawn a new path menu at the pointer page location.
         */
        let target = ev.target;
        this.originNode = target
        this.spawnAtPageXY(ev)
    }

    keydown(ev){
        // console.log('keydown', ev.keyCode)
        let escKey = ev.keyCode == 27
        if(this.showing && escKey) {
            this.hide()
        }
    }

    onclick(ev){
        if(!this.showing) {
            return
        }

        this.clickActionOrHide(ev)
    }

    clickActionOrHide(ev){
        if(!this.isChild(ev.target) ) {
            this.hide()
        }

        return this.tryInnerAction(ev)
        // console.log('Is child', ev.target)
    }

    tryInnerAction(ev) {
        // console.log('Is child', ev.target)
        let action = ev.target.dataset.action
        if(!action) {
            // no data-action=function
            return
        }

        const ma = this.getMenuActions()
        if(ma.contains(action)) {
            return ma.performAction(action, ev, this)
        }
    }

    getMenuActions() {
        if(!this._menuActions) {
            let Klass = this.getMenuActionsClass()
            this._menuActions = new Klass()
        }

        return this._menuActions
    }

    getMenuActionsClass() {
        return MenuActions
    }

    isChild(target, includeSub=true) {
        // console.log('Is showing.')
        let menu = this.getMenuEntity()
            ;

        if(menu.contains(target)) {
            // Clicked within
            return true
        }

        if(!includeSub) {
            return false
        }

        if(this.subMenu?.showing
            && this.subMenu.getMenuEntity().contains(target) ) {
            // This item is from a submenu.
            return true
        }

        return false
    }

    onblur(ev){
        // console.log('onblur', ev.target)
        if(this.showing && this.blurHide) {
            this.hide()
        }
    }

    menuMouseover(ev){
        let isHover = inParentClass('sub-hover-show', ev.target)
        if(isHover) {
            // console.log(ev, ev.target)
            // console.log('Show')
            parent = getParentByClassName(ev.target, 'sub-hover-show')
            this.spawnSubMenu(ev, parent)
        }
    }

    spawnSubMenu(ev, target) {
        /* Spawn a menu at this point.*/
        let sm = this.subMenu
            ;
        target = target || ev.target

        if(!sm) {
            let targetMenuClass = target.dataset.menu
            sm = new SubMenu(this, target, this.getNamespace(target), targetMenuClass)
            this.subMenu = sm
            sm.ensureWithinPrimary()
            console.log('Creating sub menu')
        } else {
            const namespace = this.getNamespace(target)
            if(sm.namespace != namespace) {
                // This menu is not the same as the existing.
                console.log('Rebuilding sub menu')
                sm.destroy()

                let targetMenuClass = target.dataset.menu
                sm = new SubMenu(this, target, namespace, targetMenuClass)
                this.subMenu = sm
                sm.ensureWithinPrimary()
            } else {
                console.log('Already presented')
            }
        }

        const parent = getParentByClassName(ev.target, 'sub-hover-show')
        if(parent) {
            console.log('Spawning by parent', parent)
            sm.spawnByRect(parent.getBoundingClientRect())
        } else {
            console.warn('Could not find "sub-hover-show" parent')
        }
    }

    getNamespace(node) {
        let r = node.dataset.namespace
        return r
    }

    install(entity){
        entity.addEventListener('contextmenu', this.oncontextmenu.bind(this));
        entity.addEventListener('keydown', this.keydown.bind(this));
        entity.addEventListener('click', this.onclick.bind(this));
        window.addEventListener('blur', this.onblur.bind(this));

        let menu = this.getMenuEntity()
        this.hide(menu)
        this.moveToBody(menu)
    }

    uninstall(entity) {
        entity.removeEventListener('contextmenu', this.oncontextmenu.bind(this));
        entity.removeEventListener('keydown', this.keydown.bind(this));
        entity.removeEventListener('click', this.onclick.bind(this));
        window.removeEventListener('blur', this.onblur.bind(this));
    }

}


class SubMenu extends Menu {
    /* The sub-menu acts extremely similar to the standard alt-click except
    it spawns from a hover of an internal action.

    + [auto] Spawns from an internal node.
    + When active, mouseout will close.
    + is aware of the parent menu.
    + can spawn left/right of a target entity (given possible space.)
    */
    targetMenuClass = 'copy-menu'

    constructor(parent, node, namespace, targetMenuClass) {
        console.log('SubMenu of', namespace)
        super()
        this.parent = parent
        this.spawnNode = node
        this.namespace = namespace
        this.targetMenuClass = targetMenuClass
    }

}


class MenuActions {
    contains(name) {
        return this[name] != undefined
    }

    performAction(action, ev, menu) {
        return this[action](ev, menu)
    }

    copyName(ev, menu) {
        let text = menu.originNode.textContent
        let bits = text.split('\\')
        let leaf = bits[bits.length - 1]
        console.log('copyName', leaf)
    }

    copyPath(ev, menu) {
        let text = menu.originNode.textContent
        console.log('copyPath', text)
    }

    copyFile(ev, menu) {
        console.log('copyFile', ev, menu)
    }

}

;autoMain()