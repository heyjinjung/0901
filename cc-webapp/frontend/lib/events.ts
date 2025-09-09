export function emitEvent(name: string, detail?: any) {
    try {
        window.dispatchEvent(new CustomEvent(name, { detail }));
    } catch (e) {
        // noop in non-browser or SSR
    }
}

export function onEvent(name: string, handler: (e: CustomEvent) => void) {
    if (typeof window === 'undefined') return () => { };
    const listener = (ev: Event) => handler(ev as CustomEvent);
    window.addEventListener(name, listener as EventListener);
    return () => window.removeEventListener(name, listener as EventListener);
}
