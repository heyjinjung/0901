// Minimal shims to satisfy TypeScript for external modules without local type declarations
declare module "lucide-react" {
  import * as React from "react";
  export type Icon = React.ComponentType<React.SVGProps<SVGSVGElement>>;
  // Export a subset of commonly used icons to satisfy imports
  export const ArrowLeft: Icon; export const ArrowRight: Icon; export const PanelLeftIcon: Icon; export const Users: Icon; export const Plus: Icon; export const Gift: Icon; export const Shield: Icon;
  export const ShoppingCart: Icon; export const BarChart3: Icon; export const Percent: Icon; export const AlertTriangle: Icon; export const Eye: Icon;
  export const Wifi: Icon; export const Settings: Icon; export const Database: Icon; export const Server: Icon; export const Video: Icon; export const MessageSquare: Icon;
  export const ChevronRight: Icon; export const Activity: Icon; export const DollarSign: Icon; export const RefreshCw: Icon; export const Home: Icon; export const Terminal: Icon;
  export const Heart: Icon; export const Star: Icon; export const ThumbsUp: Icon; export const Share2: Icon; export const Volume2: Icon; export const VolumeX: Icon;
  export const Send: Icon; export const Play: Icon; export const Pause: Icon; export const Lock: Icon; export const Info: Icon; export const Image: Icon;
  export const Sparkles: Icon; export const Zap: Icon; export const Diamond: Icon; export const Calendar: Icon; export const Clock: Icon;
  // Icons used by Select UI
  export const CheckIcon: Icon; export const ChevronDownIcon: Icon; export const ChevronUpIcon: Icon;
  // Common close icon alias
  export const X: Icon;
}

declare module "embla-carousel-react" {
  export type UseEmblaCarouselType = any;
  const useEmblaCarousel: any;
  export default useEmblaCarousel;
}

declare module "framer-motion" {
  import * as React from "react";
  export const motion: any;
  export const AnimatePresence: React.ComponentType<any>;
}

declare module "react-day-picker" {
  export const DayPicker: any;
}

// Minimal typings for Radix Select to unblock TS during stabilization
declare module "@radix-ui/react-select" {
  import * as React from "react";
  export const Root: React.FC<React.PropsWithChildren<any>>;
  export const Group: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Value: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Trigger: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Icon: React.FC<React.PropsWithChildren<any>>;
  export const Portal: React.FC<React.PropsWithChildren<any>>;
  export const Content: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Viewport: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Label: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Item: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const ItemIndicator: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const ItemText: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Separator: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const ScrollUpButton: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const ScrollDownButton: React.ForwardRefExoticComponent<any> & { displayName?: string };
}

declare module "@radix-ui/react-switch" {
  import * as React from "react";
  export const Root: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Thumb: React.ForwardRefExoticComponent<any> & { displayName?: string };
}

declare module "@radix-ui/react-slot" {
  import * as React from "react";
  export const Slot: React.ForwardRefExoticComponent<any>;
}

declare module "class-variance-authority" {
  // minimal cva typing sufficient for our usage pattern
  export type VariantProps<T> = any;
  export function cva(base?: string, config?: any): (...args: any[]) => string;
}

// Radix Dialog / Tabs / Toggle Group minimal shims
declare module "@radix-ui/react-dialog" {
  import * as React from "react";
  export const Root: React.FC<any> & { displayName?: string };
  export const Trigger: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Portal: React.FC<any>;
  export const Close: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Overlay: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Content: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Title: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Description: React.ForwardRefExoticComponent<any> & { displayName?: string };
}

declare module "@radix-ui/react-tabs" {
  import * as React from "react";
  export const Root: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const List: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Trigger: React.ForwardRefExoticComponent<any> & { displayName?: string };
  export const Content: React.ForwardRefExoticComponent<any> & { displayName?: string };
}

declare module "@radix-ui/react-toggle-group" {
  import * as React from "react";
  export const Root: React.FC<any>;
  export const Item: React.FC<any>;
}

declare module "@radix-ui/react-label" {
  import * as React from "react";
  export const Root: React.ForwardRefExoticComponent<any> & { displayName?: string };
}

declare module "react-hook-form" {
  // Minimal types to satisfy our usage
  export type FieldValues = any;
  export type FieldPath<T> = string;
  export type ControllerProps<TFieldValues, TName> = any;
  export const Controller: any;
  export const FormProvider: any;
  export function useFormContext(): any;
  export function useFormState(opts?: any): any;
}

declare module "recharts" {
  const Recharts: any;
  export = Recharts;
}

// next/navigation 간단 shim (로컬 타입 인식 실패 시 임시 완화)
declare module 'next/navigation' {
  export function useRouter(): { push: (path: string) => void; replace: (path: string) => void; back: () => void; prefetch?: (path: string) => Promise<void>; };
  export function useSearchParams(): any;
  export function usePathname(): string;
}

// next/server 간단 shim (에디터 타입 인식 실패 시 임시 완화)
declare module 'next/server' {
  export type NextRequest = any;
  export class NextResponse {
    static next(): NextResponse;
  }
}
