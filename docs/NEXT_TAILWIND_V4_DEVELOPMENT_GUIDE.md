# Next.js 15.4.5 + Tailwind CSS v4 Development Guide

## Table of Contents
- [Project Overview](#project-overview)
- [Technical Stack](#technical-stack)
- [Local Development Environment](#local-development-environment)
- [VSCode Configuration](#vscode-configuration)
- [Tailwind CSS v4 Integration](#tailwind-css-v4-integration)
- [Component Development Guidelines](#component-development-guidelines)
- [Common Issues and Solutions](#common-issues-and-solutions)

## Project Overview

This project is a Next.js 15.4.5 application with Tailwind CSS v4 integration for the Casino-Club F2P gaming platform. The application uses the App Router architecture and leverages React Server Components for optimized performance.

## Technical Stack

- **Frontend**:
  - Next.js 15.4.5
  - React 19.1.0
  - Tailwind CSS v4
  - TypeScript 5.2+
  - Radix UI for UI components
  - Shadcn UI for component library
  - clsx/cva for class composition

- **Backend**:
  - FastAPI
  - PostgreSQL
  - Redis
  - Kafka for event streaming
  - Celery for background tasks

## Local Development Environment

### Prerequisites

- Node.js 18.x or higher
- Python 3.10 or higher
- VSCode with recommended extensions

### Setup Local Development

Instead of using Docker for frontend development, we've created a local development setup:

1. Run the setup script:
```powershell
.\setup-local-dev.ps1
```

This script will:
- Create necessary directories
- Install frontend dependencies
- Set up Python virtual environment for backend
- Create local environment files

### Starting Development Servers

**Frontend**:
```powershell
cd cc-webapp/frontend
npm run dev
```

**Backend**:
```powershell
cd cc-webapp/backend
python -m uvicorn app.main:app --reload --port 8000
```

## VSCode Configuration

We've set up a comprehensive VSCode configuration for optimal development experience. Key features:

- Tailwind CSS v4 IntelliSense
- ESLint integration
- TypeScript support
- Code snippets for React components
- Debugging configurations for Next.js and FastAPI

### Recommended Extensions

The `.vscode/extensions.json` file includes recommended extensions. Install them by:
1. Opening the Extensions view (`Ctrl+Shift+X`)
2. Typing `@recommended` in the search box
3. Installing all workspace recommendations

### Editor Settings

Key editor settings include:
- Relative imports
- Format on Save enabled
- ESLint auto-fix on save
- Tab size of 2 spaces
- Tailwind CSS class regex patterns for utility functions

## Tailwind CSS v4 Integration

Tailwind CSS v4 works differently from previous versions:

### Key Differences in v4

1. **CSS Variables Approach**: Uses CSS variables instead of utility classes directly in HTML
2. **@theme Directive**: Uses the @theme directive in CSS for theming
3. **Config-less Design**: Configuration is now embedded directly in CSS
4. **New Syntax**: Uses a new opacity notation (e.g., `bg-blue/50` instead of `bg-blue-500/50`)

### Usage Example

```jsx
// Component Example with Tailwind CSS v4
import { cn } from '@/lib/utils'

interface ButtonProps {
  variant?: 'default' | 'outline' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  className?: string
  children: React.ReactNode
}

export function Button({ 
  variant = 'default', 
  size = 'md', 
  className, 
  children 
}: ButtonProps) {
  return (
    <button 
      className={cn(
        // Base styles
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        // Size variants
        size === 'sm' && 'h-8 px-3 text-xs',
        size === 'md' && 'h-10 px-4 py-2',
        size === 'lg' && 'h-12 px-6 py-3 text-lg',
        // Color variants
        variant === 'default' && 'bg-primary text-primary-foreground hover:bg-primary/90',
        variant === 'outline' && 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        variant === 'secondary' && 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        // Additional classes
        className
      )}
    >
      {children}
    </button>
  )
}
```

## Component Development Guidelines

### Directory Structure

```
cc-webapp/frontend/
├── app/
│   ├── (auth)/
│   ├── (dashboard)/
│   ├── (game)/
│   └── layout.tsx
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   └── ...
│   └── common/
├── lib/
│   └── utils.ts
└── styles/
    └── globals.css
```

### Component Best Practices

1. **Use TypeScript interfaces** for all component props
2. **Implement className prop** for all components to allow style overrides
3. **Use cn utility** from utils.ts for class name composition
4. **Follow atomic design principles** for component organization
5. **Use Server Components by default** unless client-side interactivity is needed

### Example Component Structure

```tsx
// Standard Component Structure
import { cn } from '@/lib/utils'

interface CardProps {
  className?: string
  title: string
  children: React.ReactNode
}

export function Card({ className, title, children }: CardProps) {
  return (
    <div className={cn('rounded-lg border bg-card p-4 shadow-sm', className)}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="mt-2">{children}</div>
    </div>
  )
}
```

## Common Issues and Solutions

### Issue: CSS Values Not Applying

**Solution**: Ensure Tailwind CSS v4 is properly configured with @theme directives in your CSS files.

### Issue: Import Paths with Version Numbers

**Solution**: Use the fix-imports-v2.ps1 script to correct import paths:

```powershell
.\fix-imports-v2.ps1
```

### Issue: File Encoding Problems

**Solution**: Fix file encoding issues with:

```powershell
.\fix-encoding.ps1
```

### Issue: Infinite Recursion in utils.ts

**Solution**: Update the cn function to use clsx directly:

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(...inputs)
}
```

---

For more information, check the project documentation in the docs/ directory.
