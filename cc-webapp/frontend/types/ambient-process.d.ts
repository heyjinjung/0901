// Minimal ambient declaration to silence process type errors without pulling full Node types if build strips server-only code.
// If full Node.js lib types become necessary, add 'node' to tsconfig types instead.
declare const process: {
    env: Record<string, string | undefined>;
    [k: string]: any;
};
