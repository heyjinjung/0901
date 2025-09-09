// Minimal vendor type stubs to unblock TS lint in React 19 migration phase.
// These are temporary and should be removed when proper types are resolved.
/* eslint-disable @typescript-eslint/no-explicit-any */
import type * as ReactNS from "react";

declare module "@radix-ui/react-switch" {
  import * as React from "react";
  export const Root: React.ComponentType<any>;
  export const Thumb: React.ComponentType<any>;
}

declare module "@radix-ui/react-select" {
  import * as React from "react";
  export const Root: React.ComponentType<any>;
  export const Group: React.ComponentType<any>;
  export const Value: React.ComponentType<any>;
  export const Trigger: React.ComponentType<any>;
  export const Icon: React.ComponentType<any>;
  export const Portal: React.ComponentType<any>;
  export const Content: React.ComponentType<any>;
  export const Viewport: React.ComponentType<any>;
  export const Label: React.ComponentType<any>;
  export const Item: React.ComponentType<any>;
  export const ItemText: React.ComponentType<any>;
  export const ItemIndicator: React.ComponentType<any>;
  export const Separator: React.ComponentType<any>;
  export const ScrollUpButton: React.ComponentType<any>;
  export const ScrollDownButton: React.ComponentType<any>;
}

declare module "@radix-ui/react-label" {
  import * as React from "react";
  export const Root: React.ComponentType<any>;
}

declare module "react-day-picker" {
  import * as React from "react";
  export const DayPicker: React.ComponentType<any>;
}

declare module "framer-motion" {
  import * as React from "react";
  export const motion: any;
  export const AnimatePresence: React.ComponentType<any>;
}

declare module "lucide-react" {
  import * as React from "react";
  export type IconProps = React.SVGProps<SVGSVGElement>;
  export const ArrowLeft: React.FC<IconProps>;
  export const Users: React.FC<IconProps>;
  export const Plus: React.FC<IconProps>;
  export const Gift: React.FC<IconProps>;
  export const Shield: React.FC<IconProps>;
  export const ShoppingCart: React.FC<IconProps>;
  export const BarChart3: React.FC<IconProps>;
  export const Percent: React.FC<IconProps>;
  export const AlertTriangle: React.FC<IconProps>;
  export const Eye: React.FC<IconProps>;
  export const Wifi: React.FC<IconProps>;
  export const Settings: React.FC<IconProps>;
  export const Database: React.FC<IconProps>;
  export const Server: React.FC<IconProps>;
  export const Video: React.FC<IconProps>;
  export const MessageSquare: React.FC<IconProps>;
  export const ChevronRight: React.FC<IconProps>;
  export const Activity: React.FC<IconProps>;
  export const DollarSign: React.FC<IconProps>;
  export const RefreshCw: React.FC<IconProps>;
  export const Home: React.FC<IconProps>;
  export const Heart: React.FC<IconProps>;
  export const Star: React.FC<IconProps>;
  export const ThumbsUp: React.FC<IconProps>;
  export const Share2: React.FC<IconProps>;
  export const Volume2: React.FC<IconProps>;
  export const VolumeX: React.FC<IconProps>;
  export const Send: React.FC<IconProps>;
  export const Play: React.FC<IconProps>;
  export const Pause: React.FC<IconProps>;
  export const Lock: React.FC<IconProps>;
  export const Info: React.FC<IconProps>;
  export const Image: React.FC<IconProps>;
  export const Sparkles: React.FC<IconProps>;
  export const Zap: React.FC<IconProps>;
  export const Diamond: React.FC<IconProps>;
  export const Calendar: React.FC<IconProps>;
  export const Crown: React.FC<IconProps>;
}
