// Temporary compatibility shim: allow using React.ComponentProps, React.ElementRef, etc.
// with @types/react v19+, where these are exported types, not namespace members.
// This avoids mass refactors by mapping legacy namespace type access to module exports.
import type {
  ComponentProps as _ComponentProps,
  ComponentPropsWithoutRef as _ComponentPropsWithoutRef,
  ElementRef as _ElementRef,
  ReactNode as _ReactNode,
  ComponentType as _ComponentType,
  CSSProperties as _CSSProperties,
  KeyboardEvent as _KeyboardEvent,
  FormEvent as _FormEvent,
  Ref as _Ref,
  ForwardedRef as _ForwardedRef,
  SVGProps as _SVGProps,
} from "react";

declare global {
  namespace React {
    // Map legacy React.ComponentProps<T> to the module-exported type
    type ComponentProps<T> = _ComponentProps<T>;
    type ComponentPropsWithoutRef<T> = _ComponentPropsWithoutRef<T>;
    type ElementRef<T> = _ElementRef<T>;
  type ReactNode = _ReactNode;
  type ComponentType<P = {}> = _ComponentType<P>;
  type CSSProperties = _CSSProperties;
  type KeyboardEvent<T = Element> = _KeyboardEvent<T>;
  type FormEvent<T = Element> = _FormEvent<T>;
  type Ref<T> = _Ref<T>;
  type ForwardedRef<T> = _ForwardedRef<T>;
  type SVGProps<T> = _SVGProps<T>;
  }
}

export {};

// Also augment the 'react' module so that types can be accessed via
// the namespace import (e.g., React.ComponentProps) in type positions.
declare module "react" {
  // Re-export type aliases for namespace-style access
  export type ComponentProps<T> = _ComponentProps<T>;
  export type ComponentPropsWithoutRef<T> = _ComponentPropsWithoutRef<T>;
  export type ElementRef<T> = _ElementRef<T>;
  export type ReactNode = _ReactNode;
  export type ComponentType<P = {}> = _ComponentType<P>;
  export type CSSProperties = _CSSProperties;
  export type KeyboardEvent<T = Element> = _KeyboardEvent<T>;
  export type FormEvent<T = Element> = _FormEvent<T>;
  export type Ref<T> = _Ref<T>;
  export type ForwardedRef<T> = _ForwardedRef<T>;
  export type SVGProps<T> = _SVGProps<T>;
}
