// Lightweight shim to avoid peer-dependency conflicts for react 19.
// Replace with real next-themes when a compatible version is installed.

export type Theme = "system" | "light" | "dark";
export type ThemeProviderProps = {
  attribute?: string;
  defaultTheme?: Theme;
  enableSystem?: boolean;
  children?: React.ReactNode;
};

export function ThemeProvider({ children }: ThemeProviderProps) {
  // No-op provider for build-time types; at runtime, do nothing
  return children as any;
}

export function useTheme(): { theme?: Theme; setTheme: (t: Theme) => void } {
  return { theme: "system", setTheme: () => {} };
}
