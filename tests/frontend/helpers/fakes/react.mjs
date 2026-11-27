// A minimal stand-in for React, just enough to RUN components and hooks in Node: state, refs, memo, effects with
// dependencies and cleanups, and re-rendering until things settle. It renders ONE component "shallowly": the elements it
// returns are plain objects, so a test can read the props handed to child components and call their callbacks.
let current = null;

const changed = (a, b) => !a || !b || a.length !== b.length || a.some((v, i) => !Object.is(v, b[i]));

class Root {
  constructor(component) {
    this.component = component;
    this.hooks = [];
    this.cursor = 0;
    this.dirty = false;
    this.flushing = false;
    this.mounted = true;
    this.output = null;
    this.props = undefined;
    this.renders = 0;
  }

  slot(init) {
    const i = this.cursor++;
    if (i >= this.hooks.length) this.hooks.push(init());
    return this.hooks[i];
  }

  schedule() {
    if (!this.mounted) return;
    this.dirty = true;
    if (!this.flushing) this.flush();
  }

  flush() {
    if (this.flushing || !this.mounted) return;
    this.flushing = true;
    try {
      let guard = 0;
      while (this.dirty) {
        if (++guard > 100) throw new Error('render loop: state keeps changing');
        this.dirty = false;
        this.renderOnce();
      }
    } finally {
      this.flushing = false;
    }
  }

  renderOnce() {
    this.cursor = 0;
    this.renders++;
    const previous = current;
    current = this;
    try {
      this.output = this.component(this.props);
    } finally {
      current = previous;
    }
    // cleanups of all changed effects first, then the new effects, in declaration order (as React does)
    const due = this.hooks.filter((h) => h.kind === 'effect' && h.pending);
    for (const h of due) if (typeof h.cleanup === 'function') h.cleanup();
    for (const h of due) {
      h.pending = false;
      h.cleanup = h.fn();
    }
  }

  unmount() {
    for (const h of this.hooks) if (h.kind === 'effect' && typeof h.cleanup === 'function') h.cleanup();
    this.mounted = false;
  }
}

/** Run a component or hook. `result()` is whatever it returned on the latest render. */
export function render(component, props) {
  const root = new Root(component);
  root.props = props;
  root.dirty = true;
  root.flush();
  return {
    result: () => root.output,
    rerender(nextProps) {
      root.props = nextProps === undefined ? root.props : nextProps;
      root.schedule();
    },
    unmount: () => root.unmount(),
    renders: () => root.renders,
  };
}

export function useState(initial) {
  const root = current;
  const h = root.slot(() => {
    const state = { kind: 'state', value: typeof initial === 'function' ? initial() : initial };
    state.set = (next) => {
      const value = typeof next === 'function' ? next(state.value) : next;
      if (Object.is(value, state.value)) return;
      state.value = value;
      root.schedule();
    };
    return state;
  });
  return [h.value, h.set];
}

export function useRef(initial) {
  return current.slot(() => ({ kind: 'ref', ref: { current: initial } })).ref;
}

export function useMemo(factory, deps) {
  const h = current.slot(() => ({ kind: 'memo' }));
  if (!('value' in h) || !deps || changed(h.deps, deps)) {
    h.value = factory();
    h.deps = deps;
  }
  return h.value;
}

export function useCallback(fn, deps) {
  return useMemo(() => fn, deps);
}

export function useEffect(fn, deps) {
  const h = current.slot(() => ({ kind: 'effect', first: true }));
  if (h.first || !deps || changed(h.deps, deps)) {
    h.first = false;
    h.fn = fn;
    h.deps = deps;
    h.pending = true;
  }
}
export const useLayoutEffect = useEffect;

export const Fragment = Symbol.for('fake.fragment');
export const jsx = (type, props, key) => ({ type, props: props || {}, key });
export const jsxs = jsx;
export const createElement = (type, props, ...children) =>
  jsx(type, { ...(props || {}), ...(children.length ? { children: children.length === 1 ? children[0] : children } : {}) });
export const forwardRef = (fn) => {
  const Component = (props) => fn(props, null);
  return Component;
};
export const memo = (c) => c;
export const createContext = (value) => ({ Provider: ({ children }) => children, _value: value });
export const useContext = (ctx) => ctx._value;

// ---------------------------------------------------------------- helpers to read the returned element tree
export function walk(node, visit) {
  if (Array.isArray(node)) return node.forEach((n) => walk(n, visit));
  if (!node || typeof node !== 'object') return;
  visit(node);
  walk(node.props?.children, visit);
}

export const nameOf = (type) => (typeof type === 'string' ? type : type?.displayName || type?.name || '');

export function findAll(tree, match) {
  const out = [];
  const test = typeof match === 'string' ? (el) => nameOf(el.type) === match : match;
  walk(tree, (el) => test(el) && out.push(el));
  return out;
}

export const find = (tree, match) => findAll(tree, match)[0] ?? null;

export function textOf(node) {
  if (node === null || node === undefined || typeof node === 'boolean') return '';
  if (Array.isArray(node)) return node.map(textOf).join('');
  if (typeof node !== 'object') return String(node);
  return textOf(node.props?.children);
}

export default { useState, useRef, useMemo, useCallback, useEffect, useLayoutEffect, createElement, forwardRef, memo, Fragment, createContext, useContext };
