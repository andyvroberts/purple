// create virtual node types as an enumeration constant
// A TEXT node contains just text content. 
// A ELEMENT node is an HTML element such as a div or a p
// A FRAGMENT node is a collection of the other nodes that don't yet have a parent to be attached to
export const DOM_TYPES = {
    TEXT: 'text',
    ELEMENT: 'element',
    FRAGMENT: 'fragment',
}

// Create an ELEMENT node. 
// each node has a tag, a set of properties (element attributes) and maybe an array of children.
export function h(tag, props = {}, children = []) {
    return {
        tag,
        props,
        children: mapTextNodes(withoutNulls(children)),
        type: DOM_TYPES.ELEMENT,
    }
}

// Create a TEXT node.
// each node only has a string.
export function hstring(str) {
    return { type: DOM_TYPES.TEXT, value: str}
}

// Create a FRAGMENT node(S)
// each node has an array of other nodes.
export function hFragment(vNodes) {
    return {
        type: DOM_TYPES.FRAGMENT,
        children: mapTextNodes(withoutNulls(vNodes)),
    }
}

// Node Utilities.
export function mapTextNodes(children) {
    return children.map((child) =>
        typeof child === 'string' ? hstring(child) : child
    )
}


// Display debug type message Text
export function messageComponent({level, msg}) {
    return h('div', {class: `message message--${level}`}, [
        h('p', {}, [msg])
    ])
}



