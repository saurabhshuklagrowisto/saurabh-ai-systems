# React — Reference Patterns for Figma Implementation

## File Structure

For a new component from a Figma design:
```
src/
  components/
    ComponentName/
      ComponentName.tsx       ← main component
      ComponentName.types.ts  ← props interface (if large)
      ComponentName.module.css ← CSS modules (if not using Tailwind)
      index.ts                ← re-export
```

For a simple component, a single file is fine:
```
src/components/ComponentName.tsx
```

---

## Basic Component Structure (TypeScript + Tailwind)

```tsx
interface ComponentNameProps {
  title: string
  description?: string
  variant?: 'primary' | 'secondary'
  onClick?: () => void
  children?: React.ReactNode
  className?: string
}

const ComponentName = ({
  title,
  description,
  variant = 'primary',
  onClick,
  children,
  className,
}: ComponentNameProps) => {
  return (
    <div className={cn('base-classes-here', className)}>
      <h2 className="text-xl font-semibold">{title}</h2>
      {description && <p className="text-sm text-gray-600">{description}</p>}
      {children}
    </div>
  )
}

export default ComponentName
```

---

## Tailwind — Mapping Figma Values

Always map Figma design tokens to Tailwind classes, not hardcoded values:

| Figma Value | Tailwind Class |
|---|---|
| padding: 16px | `p-4` |
| padding: 20px | `p-5` |
| padding: 24px | `p-6` |
| gap: 8px | `gap-2` |
| gap: 12px | `gap-3` |
| gap: 16px | `gap-4` |
| border-radius: 4px | `rounded` |
| border-radius: 8px | `rounded-lg` |
| border-radius: 12px | `rounded-xl` |
| border-radius: full | `rounded-full` |
| font-size: 12px | `text-xs` |
| font-size: 14px | `text-sm` |
| font-size: 16px | `text-base` |
| font-size: 18px | `text-lg` |
| font-size: 20px | `text-xl` |
| font-size: 24px | `text-2xl` |
| font-weight: 400 | `font-normal` |
| font-weight: 500 | `font-medium` |
| font-weight: 600 | `font-semibold` |
| font-weight: 700 | `font-bold` |

If a value doesn't map cleanly to a Tailwind scale (e.g. padding: 18px), use arbitrary value: `p-[18px]` — but flag it in the Implementation Notes.

---

## Colour Tokens

If the project has a Tailwind config with custom colours, use those:
```tsx
// Good — uses design system token
<div className="bg-brand-primary text-brand-on-primary">

// Avoid — hardcoded
<div className="bg-[#1E3A5F] text-white">
```

Check `tailwind.config.js` or `tailwind.config.ts` for the project's colour tokens before hardcoding anything.

---

## cn() Utility — Conditional Classes

Always use `cn()` (from `clsx` or `tailwind-merge`) for conditional or merged classes:

```tsx
import { cn } from '@/lib/utils' // or wherever it's exported in the project

<div className={cn(
  'base flex items-center gap-4 rounded-lg p-4',
  variant === 'primary' && 'bg-brand-primary text-white',
  variant === 'secondary' && 'bg-gray-100 text-gray-900',
  isDisabled && 'opacity-50 cursor-not-allowed',
  className
)}>
```

---

## Variants Pattern (using cva)

When a Figma design has multiple variants of a component:

```tsx
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  // base classes always applied
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-brand-primary text-white hover:bg-brand-primary-hover',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
        ghost: 'bg-transparent text-gray-700 hover:bg-gray-100',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode
}

const Button = ({ variant, size, className, children, ...props }: ButtonProps) => (
  <button className={cn(buttonVariants({ variant, size }), className)} {...props}>
    {children}
  </button>
)
```

---

## Layout Patterns from Figma Auto Layout

| Figma Auto Layout Setting | React + Tailwind |
|---|---|
| Horizontal, gap 16 | `flex flex-row gap-4` |
| Vertical, gap 16 | `flex flex-col gap-4` |
| Horizontal, space between | `flex flex-row justify-between` |
| Wrap | `flex flex-wrap gap-4` |
| Fill container | `w-full` |
| Hug contents | (no width class needed) |
| Fixed width | `w-[240px]` or `w-60` |
| Center aligned | `flex items-center justify-center` |
| Grid, 3 columns | `grid grid-cols-3 gap-4` |
| Responsive grid | `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4` |

---

## Responsive Breakpoints

Match Tailwind's default breakpoints to Figma frame sizes:

| Figma Frame | Tailwind Prefix |
|---|---|
| Mobile (375px) | default (no prefix) |
| Tablet (768px) | `md:` |
| Desktop (1280px) | `lg:` or `xl:` |

```tsx
<div className="flex flex-col gap-4 md:flex-row md:gap-6 lg:gap-8">
```

---

## Images

```tsx
// Next.js project
import Image from 'next/image'

<Image
  src={imageSrc}
  alt={imageAlt}
  width={400}
  height={300}
  className="rounded-lg object-cover"
/>

// Plain React
<img
  src={imageSrc}
  alt={imageAlt}
  className="rounded-lg object-cover w-full h-auto"
  loading="lazy"
/>
```

---

## Icons

Check what icon library the project uses before creating SVGs from scratch:

```tsx
// Lucide React (most common)
import { ArrowRight, ChevronDown, X } from 'lucide-react'
<ArrowRight className="w-4 h-4" />

// Heroicons
import { ArrowRightIcon } from '@heroicons/react/24/outline'
<ArrowRightIcon className="w-4 h-4" />
```

Check `package.json` for `lucide-react`, `@heroicons/react`, or `react-icons` before assuming which to use.

---

## Existing Component Imports

Before building a component from scratch, check these common locations in the codebase:

```
src/components/ui/          ← shadcn/ui or shared primitives (Button, Input, Card, Modal)
src/components/common/      ← shared team components
src/components/[feature]/   ← feature-specific components
```

If a `Button`, `Card`, `Input`, `Modal`, `Badge`, or `Avatar` already exists — import it, don't rebuild it.

---

## Common Mistakes to Avoid

- Don't hardcode hex values — check `tailwind.config` for tokens first
- Don't use inline `style={{}}` unless a value truly can't be expressed in Tailwind (e.g. dynamic rotation)
- Don't skip the `className` prop — always allow consumers to extend styles
- Don't create a new icon as an SVG if the project has an icon library
- Don't use `px-` and `py-` when Figma shows equal padding on all sides — use `p-` instead
- Don't forget `alt` text on images
- Don't use `div` for interactive elements — use `button` for clickable things
- Don't skip TypeScript props interface — even for simple components
