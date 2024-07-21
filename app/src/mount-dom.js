import { DOM_TYPES } from './h'

/**
 * Creates the DOM nodes for a virtual DOM tree, mounts them in the DOM, and
 * modifies the vdom tree to include the corresponding DOM nodes and event listeners.
 *
 * @param {import('./h').VNode} vdom the virtual DOM node to mount
 * @param {HTMLElement} parentEl the host element to mount the virtual DOM node to
 * @param {number} [index] the index at the parent element to mount the virtual DOM node to
 * @param {import('./component').Component} [hostComponent] The component that the listeners are added to
 */
export function mountDOM(vdom, parentEl) {

    switch (vdom.type) {
        case DOM_TYPES.TEXT: {
            createTextNode(vdom, parentEl)
            break
        }
        case DOM_TYPES.ELEMENT: {
            createElementNode(vdom, parentEl)
            break
        }
        case DOM_TYPES.FRAGMENT: {
            createFragmentNodes(vdom, parentEl)
            break
        }
        default: {
            throw new Error(`Cannot mound DOM of type: ${vdom.type}`)
        }
    }

}

/**
 * Creates the text node for a virtual DOM text node.
 * The created `Text` is added to the `el` property of the vdom.
 *
 * @param {import('./h').TextVNode} vdom the virtual DOM node of type "text"
 * @param {Element} parentEl the host element to mount the virtual DOM node to
 * @param {number} [index] the index at the parent element to mount the virtual DOM node to
 */
function createTextNode(vdom, parentEl) {
    const { value } = vdom

    const textNode = document.createTextNode(value)
    vdom.el = textNode

    parentEl.append(textNode)
}

// TODO: implement createElementNode()


/**
 * Creates the nodes for the children of a virtual DOM fragment node and appends them to the
 * parent element.
 *
 * @param {import('./h').FragmentVNode} vdom the virtual DOM node of type "fragment"
 * @param {Element} parentEl the host element to mount the virtual DOM node to
 * @param {number} [index] the index at the parent element to mount the virtual DOM node to
 * @param {import('./component').Component} [hostComponent] The component that the listeners are added to
 */
function createFragmentNodes(vdom, parentEl) {
    const { children } = vdom 
    vdom.el = parentEl

    children.forEach((child) => mountDOM(child, parentEl))
}