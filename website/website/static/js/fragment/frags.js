
console.log('AsyncFragment')

const asyncCache = {
    DOMContentLoaded: false,
}

document.addEventListener("DOMContentLoaded", (event) => {
    asyncCache.DOMContentLoaded = true
});


// Create a class for the element
class AsyncFragment extends HTMLElement {
    /* load:
        immediate
        domload
        click
        intersection
     */

    static CLICK = 'click'
    static IMMEDIATE = 'immediate'
    static DOM_LOAD = 'domload'

    static observedAttributes = ["url", "load"]

    constructor() {
        // Always call super first in constructor
        super();
        this.hostNode = this.renderShadow()
        this._loaded = false
        this._internals = this.attachInternals();
        this.addEventListener('click', this.clickHandler.bind(this))
    }

    connectedCallback() {
        console.log("Custom element added to page.");
        if(this.loadState == AsyncFragment.DOM_LOAD) {
            if(this._loaded) { return }

            if(asyncCache.DOMContentLoaded) {
                return this.renderFragment()
            }

            document.addEventListener(
                "DOMContentLoaded",
                (event) => this.renderFragment()
            );
        }
    }

    disconnectedCallback() {
        console.log("Custom element removed from page.");
    }

    adoptedCallback() {
        console.log("Custom element moved to new page.");
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(`Attribute ${name} has changed.`);
        const fm = {
            url: this.actionAttrChange.bind(this),
            load: this.loadAttrChange.bind(this),
        }

        return fm[name](newValue)
    }

    get loadState(){
        return this.attributes.load.value
    }

    clickHandler(){
        if(this.loadState == AsyncFragment.CLICK) {
            if(this._loaded) { return }
            this.renderFragment()
        }
    }

    actionAttrChange(value) {
        if(this.loadState == AsyncFragment.IMMEDIATE) {
            this.actionUrl(value)
        }
    }

    loadAttrChange() {}

    renderFragment(){
        return this.actionUrl(this.attributes.url.value)
    }

    actionUrl(url) {
        // given a url. Render the view.
        fetch(url)
            .then(this._setState.bind(this))
            .then(resp => resp.text())
            .then(this.renderFetchResponse.bind(this))
            ;
    }

    _setState(resp) {
        this._loaded = resp.ok
        return resp
    }

    renderShadow(){
        const parent = document.createElement("div");
        const div = document.createElement("div");
        div.textContent = this.textContent
        const button = document.createElement("button");
        button.textContent = 'Load'
        button.addEventListener('click', ()=>this.renderFragment())
        parent.appendChild(div)
        parent.appendChild(button)

        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(parent)

        return div
    }

    renderFetchResponse(textContent) {
        // this._internals.states.add("populated");
        // console.log(this, resp)
        this.hostNode.innerHTML = textContent
    }
}

customElements.define("async-fragment", AsyncFragment);