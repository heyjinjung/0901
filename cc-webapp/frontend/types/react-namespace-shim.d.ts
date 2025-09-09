// Lightweight React namespace shims for common DOM event types used in client components
// This helps avoid importing React.ChangeEvent in strict isolatedModules setups
declare namespace React {
	type FC<P = {}> = (props: P) => any;
	type Key = string | number;
}

// Global DOM event type aliases for convenience
type InputChangeEvent = Event & { target: HTMLInputElement };
type TextareaChangeEvent = Event & { target: HTMLTextAreaElement };
type SelectChangeEvent = Event & { target: HTMLSelectElement };
