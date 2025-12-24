# React Animation Patterns

**Purpose**: Comprehensive patterns for implementing smooth, accessible, performant animations in React + TypeScript applications

**When to use**: Adding transitions, gestures, motion effects, loading states, and interactive animations to your UI

**Last Updated**: 2025-12-09

**Stack**: React 18, TypeScript, Vite, Framer Motion (Motion), CSS Transitions, View Transitions API

**Key Principle**: The best animation is the one users don't notice until it's missing. Prioritize performance, accessibility, and purpose over flash.

---

## Table of Contents

1. [Decision Framework](#decision-framework)
2. [Library Comparison](#library-comparison)
3. [CSS Transitions & Animations](#css-transitions--animations)
4. [Framer Motion Patterns](#framer-motion-patterns)
5. [View Transitions API](#view-transitions-api)
6. [React Spring Patterns](#react-spring-patterns)
7. [GSAP Patterns](#gsap-patterns)
8. [Common Animation Patterns](#common-animation-patterns)
9. [Accessibility](#accessibility)
10. [Performance Optimization](#performance-optimization)
11. [Advanced Patterns](#advanced-patterns)

---

## Decision Framework

### Animation Library Decision Tree

```
START
  │
  ├─ Simple hover/focus states?
  │    └─ YES → Use CSS transitions
  │         └─ STOP (no JS needed)
  │
  ├─ Page/route transitions in 2025+?
  │    └─ YES → Use View Transitions API
  │         └─ Fallback to Framer Motion for older browsers
  │         └─ STOP (browser-native)
  │
  └─ Complex interactive animations?
       │
       ├─ Gestures (drag, swipe, tap)?
       │    └─ YES → Use Framer Motion
       │         └─ STOP (best gesture support)
       │
       ├─ Physics-based, spring animations?
       │    └─ YES → Use React Spring
       │         └─ Consider Framer Motion (easier API)
       │         └─ STOP (natural motion)
       │
       ├─ Complex timelines, ScrollTrigger?
       │    └─ YES → Use GSAP
       │         └─ STOP (professional control)
       │
       └─ General UI animations?
            └─ Use Framer Motion (most versatile)
                 └─ STOP (best React integration)
```

### Quick Selection Guide

| Use Case | Recommended Solution | Why |
|----------|---------------------|-----|
| Hover effects, focus states | CSS Transitions | Zero JS, best performance |
| Loading spinners | CSS Animations + Tailwind | Built-in utilities |
| Page transitions (2025+) | View Transitions API | Browser-native, future-proof |
| Modal enter/exit | Framer Motion AnimatePresence | Easiest implementation |
| List animations | Framer Motion + AnimatePresence | Built-in layout animations |
| Drag and drop | Framer Motion | Best gesture support |
| Swipe actions | Framer Motion | Built-in drag + inertia |
| Scroll parallax | Framer Motion useScroll | Simple API |
| Complex scroll timelines | GSAP ScrollTrigger | Most powerful |
| Spring physics | React Spring | Pure physics-based |
| SVG path animations | Framer Motion or GSAP | Both excellent |
| Timeline orchestration | GSAP | Industry standard |
| Data visualization | React Spring or D3 + Framer Motion | Smooth transitions |

---

## Library Comparison

### Bundle Size & Performance (2025)

| Library | Gzipped Size | Tree-shakable | GPU Accelerated | Bundle Optimization |
|---------|--------------|---------------|-----------------|---------------------|
| **CSS Transitions** | 0 KB | N/A | ✅ Yes | N/A (native) |
| **View Transitions API** | 0 KB | N/A | ✅ Yes | N/A (browser-native) |
| **Framer Motion** | 32 KB (full)<br>4.6 KB (LazyMotion + m) | ✅ Yes (partial) | ✅ Yes | Use `m` + `LazyMotion` |
| **React Spring** | ~20 KB | ✅ Yes | ✅ Yes | Import specific hooks only |
| **GSAP Core** | 23 KB | ✅ Yes (modular) | ✅ Yes | Import plugins separately |
| **Motion One** | ~5 KB | ✅ Yes | ✅ Yes | WAAPI-based, very lightweight |

### Feature Comparison

| Feature | CSS | Framer Motion | React Spring | GSAP | View Transitions |
|---------|-----|---------------|--------------|------|------------------|
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Gesture support | ❌ No | ✅ Excellent | ❌ No | ⚠️ Plugin | ❌ No |
| Physics-based | ❌ No | ✅ Yes | ✅ Excellent | ⚠️ Basic | ❌ No |
| Layout animations | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| Timeline control | ❌ No | ⚠️ Basic | ❌ No | ✅ Excellent | ❌ No |
| Scroll animations | ⚠️ Basic | ✅ Good | ✅ Good | ✅ Excellent | ❌ No |
| React integration | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| TypeScript support | N/A | ✅ Excellent | ✅ Good | ✅ Good | ✅ Native |
| Browser support | ✅ All | ✅ Modern | ✅ Modern | ✅ All | ⚠️ Chrome 111+ |

### When to Use Each Library

#### CSS Transitions & Animations
**Use for**: Simple state changes, hover effects, focus states, loading spinners
**Pros**: Zero bundle size, best performance, GPU-accelerated by default
**Cons**: Limited control, no gesture support, no React state integration
**Learning curve**: ⭐ (easiest)

#### Framer Motion
**Use for**: 90% of React animation needs, gestures, layout animations, general UI
**Pros**: Excellent React integration, gesture support, intuitive API, AnimatePresence
**Cons**: Larger bundle (mitigated with LazyMotion), less timeline control than GSAP
**Learning curve**: ⭐⭐ (easy)
**Who uses it**: Stripe, Notion, Framer

#### React Spring
**Use for**: Physics-based animations, natural motion, data visualization
**Pros**: Pure spring physics, smooth interpolations, excellent for realistic motion
**Cons**: Steeper learning curve, no gesture support, less documentation
**Learning curve**: ⭐⭐⭐ (moderate)
**Who uses it**: CodeSandbox, Next.js, Aragon

#### GSAP
**Use for**: Complex timelines, professional animations, scroll-triggered sequences
**Pros**: Most powerful, excellent timeline control, ScrollTrigger, wide browser support
**Cons**: Larger learning curve, imperative API (less React-like), paid plugins
**Learning curve**: ⭐⭐⭐⭐ (advanced)
**Who uses it**: Apple, Google, Nike (production sites)

#### View Transitions API
**Use for**: Page/route transitions in SPAs (2025+)
**Pros**: Browser-native, zero bundle, smooth, future-proof
**Cons**: Browser support limited (Chrome 111+, Firefox 144+ Oct 2025), requires fallback
**Learning curve**: ⭐⭐ (easy)

---

## CSS Transitions & Animations

### Basic Transitions

**Problem**: Need simple hover/focus effects without JavaScript

**Solution**: Use CSS transitions with pseudo-classes

**Implementation**:

```css
/* ✅ CORRECT: Basic transition */
.button {
  background-color: #3b82f6;
  transform: scale(1);
  transition: all 0.2s ease-in-out;
}

.button:hover {
  background-color: #2563eb;
  transform: scale(1.05);
}

/* ❌ WRONG: Transitioning non-GPU properties */
.button-slow {
  width: 100px;
  transition: width 0.2s; /* Triggers layout reflow */
}

/* ✅ CORRECT: GPU-accelerated properties only */
.button-fast {
  transform: scale(1);
  opacity: 1;
  transition: transform 0.2s, opacity 0.2s;
}
```

**Key Points**:
- Only animate `transform`, `opacity`, `filter` for best performance
- Use `transition: all` sparingly (harder to control)
- Keep durations short (150-300ms for micro-interactions)
- Use `ease-in-out` for natural feel

### Keyframe Animations

**Problem**: Need repeating or complex multi-step animations

**Solution**: Use `@keyframes` with CSS animations

**Implementation**:

```css
/* ✅ CORRECT: Skeleton loading animation */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}

/* ✅ CORRECT: Pulse animation (Tailwind-style) */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### Tailwind CSS Animations

**Problem**: Need quick animations without writing CSS

**Solution**: Use Tailwind's built-in animate utilities

**Implementation**:

```tsx
// ✅ CORRECT: Tailwind built-in animations
function LoadingSpinner() {
  return (
    <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
  );
}

function PulsingDot() {
  return <div className="animate-pulse bg-blue-500 rounded-full h-3 w-3" />;
}

function BouncingBall() {
  return <div className="animate-bounce bg-red-500 rounded-full h-8 w-8" />;
}

// ✅ CORRECT: Custom animation with Tailwind v4 (2025)
// In your CSS file:
/*
@theme {
  --animate-slide-in: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
}
*/

function SlideInPanel() {
  return <div className="animate-slide-in">Content</div>;
}

// ❌ WRONG: Tailwind v3 config approach in v4
// Don't put animations in tailwind.config.js in v4
```

**Available Tailwind Animations**:
- `animate-spin`: 360° rotation (loading spinners)
- `animate-ping`: Scale + fade (notification badges)
- `animate-pulse`: Fade in/out (skeleton screens)
- `animate-bounce`: Bounce up/down (scroll indicators)

### CSS Variables for Dynamic Animations

**Problem**: Need to control animation values from React state

**Solution**: Use CSS custom properties (variables)

**Implementation**:

```tsx
// ✅ CORRECT: Dynamic animation with CSS variables
interface ProgressBarProps {
  progress: number; // 0-100
}

function ProgressBar({ progress }: ProgressBarProps) {
  return (
    <div className="progress-container">
      <div
        className="progress-bar"
        style={{ '--progress': `${progress}%` } as React.CSSProperties}
      />
    </div>
  );
}

// CSS:
/*
.progress-bar {
  width: var(--progress, 0%);
  height: 8px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.3s ease-out;
}
*/
```

### Performance Best Practices

**Problem**: Animations causing jank or layout thrashing

**Solution**: Follow the FLIP technique and GPU-accelerated properties

**Implementation**:

```css
/* ✅ CORRECT: GPU-accelerated animations */
.fast-animation {
  /* Hint to browser: this will change */
  will-change: transform, opacity;

  /* Only animate GPU-friendly properties */
  transform: translateX(0);
  opacity: 1;
  transition: transform 0.3s, opacity 0.3s;
}

.fast-animation.moved {
  transform: translateX(100px);
  opacity: 0.5;
}

/* ❌ WRONG: CPU-bound animations */
.slow-animation {
  width: 100px; /* Triggers layout */
  height: 100px; /* Triggers layout */
  top: 0; /* Triggers layout */
  left: 0; /* Triggers layout */
  transition: all 0.3s;
}

/* ✅ CORRECT: Remove will-change after animation */
.optimized {
  transition: transform 0.3s;
}

.optimized.animating {
  will-change: transform; /* Only during animation */
}
```

**Key Points**:
- Only animate `transform`, `opacity`, `filter` (GPU-accelerated)
- Use `will-change` sparingly (only during animation, remove after)
- Avoid animating `width`, `height`, `top`, `left`, `margin`, `padding`
- Use `transform: translate()` instead of `left/top`
- Use `transform: scale()` instead of `width/height`

---

## Framer Motion Patterns

### Installation & Setup

```bash
npm install motion
# or
yarn add motion
```

**Note**: Framer Motion rebranded to "Motion" in 2025. Import from `motion` or `framer-motion`.

### Basic Motion Components

**Problem**: Need simple enter/exit animations

**Solution**: Use motion components with animation props

**Implementation**:

```tsx
import { motion } from 'motion/react';

// ✅ CORRECT: Basic motion component
function FadeInBox() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      Content fades in
    </motion.div>
  );
}

// ✅ CORRECT: Multiple properties
function SlideInCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="card"
    >
      Card content
    </motion.div>
  );
}

// ❌ WRONG: Animating layout properties (use transform instead)
function SlowAnimation() {
  return (
    <motion.div
      animate={{ width: 200, height: 200 }} // Triggers layout
    >
      Slow!
    </motion.div>
  );
}

// ✅ CORRECT: Use transform for size changes
function FastAnimation() {
  return (
    <motion.div
      animate={{ scale: 1.5 }} // GPU-accelerated
    >
      Fast!
    </motion.div>
  );
}
```

### Variants Pattern (Reusable Animation Configs)

**Problem**: Need to reuse animation configs and orchestrate complex animations

**Solution**: Use Framer Motion variants with TypeScript

**Implementation**:

```tsx
import { motion, Variants } from 'motion/react';

// ✅ CORRECT: Type-safe variants
const fadeInVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3 }
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.2 }
  }
};

function FadeInComponent() {
  return (
    <motion.div
      variants={fadeInVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      Content
    </motion.div>
  );
}

// ✅ CORRECT: Variants with orchestration
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.2,
      staggerChildren: 0.1
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 }
};

function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item, i) => (
        <motion.li key={i} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}

// ✅ CORRECT: Dynamic variants (custom values)
const cardVariants: Variants = {
  rest: { scale: 1 },
  hover: { scale: 1.05 },
  tap: { scale: 0.95 }
};

function InteractiveCard() {
  return (
    <motion.div
      variants={cardVariants}
      initial="rest"
      whileHover="hover"
      whileTap="tap"
      className="card"
    >
      Click me!
    </motion.div>
  );
}
```

**Key Points**:
- Use `Variants` type from Framer Motion for TypeScript
- Variants propagate to children automatically
- Use `delayChildren` and `staggerChildren` for orchestration
- Dynamic variants can accept custom props via `custom` prop

### AnimatePresence (Enter/Exit Animations)

**Problem**: Need exit animations when components unmount

**Solution**: Wrap conditionally rendered components in AnimatePresence

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';
import { useState } from 'react';

// ✅ CORRECT: Modal with enter/exit animations
function Modal({ isOpen, onClose, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <motion.div
            key="modal"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 flex items-center justify-center z-50"
          >
            <div className="bg-white rounded-lg p-6 max-w-md">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ✅ CORRECT: List with enter/exit animations
function AnimatedList({ items }: { items: Item[] }) {
  return (
    <ul>
      <AnimatePresence>
        {items.map((item) => (
          <motion.li
            key={item.id} // Key is required!
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {item.name}
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  );
}

// ❌ WRONG: Missing key prop
function BrokenList({ items }: { items: Item[] }) {
  return (
    <AnimatePresence>
      {items.map((item) => (
        <motion.li exit={{ opacity: 0 }}>
          {/* Missing key! AnimatePresence won't work */}
          {item.name}
        </motion.li>
      ))}
    </AnimatePresence>
  );
}

// ❌ WRONG: AnimatePresence outside conditional
function BrokenModal({ isOpen }: { isOpen: boolean }) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {/* This won't work - AnimatePresence must wrap the conditional */}
      <motion.div>Modal</motion.div>
    </AnimatePresence>
  );
}
```

**Key Points**:
- `AnimatePresence` must wrap the conditional rendering
- Each child must have a unique `key` prop
- Use `mode="wait"` to wait for exit before entering next component
- Use `mode="popLayout"` to prevent layout shift during exit

### Gesture Animations

**Problem**: Need interactive animations for hover, tap, drag

**Solution**: Use Framer Motion gesture props

**Implementation**:

```tsx
// ✅ CORRECT: Hover and tap animations
function InteractiveButton() {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className="px-4 py-2 bg-blue-500 text-white rounded"
    >
      Click me
    </motion.button>
  );
}

// ✅ CORRECT: Drag with constraints
function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
      dragElastic={0.1}
      whileDrag={{ scale: 1.1, cursor: 'grabbing' }}
      className="w-32 h-32 bg-blue-500 rounded-lg cursor-grab"
    >
      Drag me
    </motion.div>
  );
}

// ✅ CORRECT: Drag on single axis
function SwipeableCard({ onSwipeLeft, onSwipeRight }: SwipeProps) {
  return (
    <motion.div
      drag="x" // Only horizontal
      dragConstraints={{ left: -200, right: 200 }}
      onDragEnd={(event, info) => {
        if (info.offset.x > 100) {
          onSwipeRight();
        } else if (info.offset.x < -100) {
          onSwipeLeft();
        }
      }}
      className="card"
    >
      Swipe left or right
    </motion.div>
  );
}

// ✅ CORRECT: Advanced drag controls
import { useDragControls } from 'motion/react';

function AdvancedDrag() {
  const controls = useDragControls();

  function startDrag(event: React.PointerEvent) {
    controls.start(event);
  }

  return (
    <>
      <div onPointerDown={startDrag} className="handle">
        Drag handle
      </div>
      <motion.div
        drag
        dragControls={controls}
        dragListener={false} // Only drag from handle
        className="draggable"
      >
        Content
      </motion.div>
    </>
  );
}
```

**Gesture Props**:
- `whileHover`: Animate on hover
- `whileTap`: Animate on click/touch
- `whileFocus`: Animate on focus
- `whileDrag`: Animate while dragging
- `whileInView`: Animate when in viewport
- `drag`: Enable dragging (true, "x", "y")
- `dragConstraints`: Limit drag area
- `dragElastic`: Bounce-back elasticity (0-1)
- `dragMomentum`: Continue motion after release

### Scroll Animations

**Problem**: Need parallax or scroll-triggered animations

**Solution**: Use `useScroll` and `useTransform` hooks

**Implementation**:

```tsx
import { motion, useScroll, useTransform } from 'motion/react';
import { useRef } from 'react';

// ✅ CORRECT: Scroll progress indicator
function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
        transformOrigin: '0%'
      }}
    />
  );
}

// ✅ CORRECT: Parallax effect
function ParallaxSection() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start']
  });

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0]);

  return (
    <div ref={ref} className="relative h-screen overflow-hidden">
      <motion.div
        style={{ y, opacity }}
        className="absolute inset-0 bg-cover"
      >
        Parallax content
      </motion.div>
    </div>
  );
}

// ✅ CORRECT: Reveal on scroll
function RevealOnScroll({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
}

// ✅ CORRECT: Stagger children on scroll
function StaggerReveal({ items }: { items: string[] }) {
  return (
    <motion.ul
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.3 }}
      variants={{
        visible: {
          transition: { staggerChildren: 0.1 }
        }
      }}
    >
      {items.map((item, i) => (
        <motion.li
          key={i}
          variants={{
            hidden: { opacity: 0, x: -20 },
            visible: { opacity: 1, x: 0 }
          }}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

**Key Points**:
- `useScroll()` returns `scrollYProgress` (0-1) and `scrollY` (pixels)
- `useTransform()` maps input range to output range
- `whileInView` is simpler than `useScroll` for basic reveal effects
- Set `viewport.once: true` to only animate once (performance)

### Layout Animations

**Problem**: Need smooth transitions when layout changes

**Solution**: Use `layout` prop for automatic FLIP animations

**Implementation**:

```tsx
import { motion } from 'motion/react';
import { useState } from 'react';

// ✅ CORRECT: Expanding card with layout animation
function ExpandableCard() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      layout // Automatically animates layout changes
      onClick={() => setIsExpanded(!isExpanded)}
      style={{
        width: isExpanded ? 400 : 200,
        height: isExpanded ? 300 : 100
      }}
      transition={{ layout: { duration: 0.3 } }}
      className="bg-white rounded-lg shadow-lg cursor-pointer"
    >
      <motion.h2 layout="position">
        {isExpanded ? 'Expanded' : 'Click to expand'}
      </motion.h2>
      {isExpanded && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          Additional content
        </motion.p>
      )}
    </motion.div>
  );
}

// ✅ CORRECT: Shared layout animation (element morphs between components)
function SharedLayoutExample() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div>
      {items.map((item) => (
        <motion.div
          key={item.id}
          layoutId={item.id} // Shared layout ID
          onClick={() => setSelected(item.id)}
          className="card"
        >
          {item.title}
        </motion.div>
      ))}

      <AnimatePresence>
        {selected && (
          <motion.div
            layoutId={selected} // Same ID morphs element
            className="expanded-card"
          >
            Expanded view
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

**Layout Props**:
- `layout`: Animate all layout changes
- `layout="position"`: Only animate position changes
- `layout="size"`: Only animate size changes
- `layoutId`: Create shared layout animations across components

### Bundle Size Optimization

**Problem**: Framer Motion adds 32KB to bundle

**Solution**: Use `LazyMotion` with feature-based loading

**Implementation**:

```tsx
// ✅ CORRECT: Reduce bundle size with LazyMotion
import { LazyMotion, domAnimation, m } from 'motion/react';

// App.tsx - wrap your app
function App() {
  return (
    <LazyMotion features={domAnimation}> {/* 15KB instead of 32KB */}
      <YourApp />
    </LazyMotion>
  );
}

// Use 'm' instead of 'motion' (tree-shakable)
function OptimizedComponent() {
  return (
    <m.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      Smaller bundle!
    </m.div>
  );
}

// ✅ CORRECT: Only load features you need
import { LazyMotion, domMax } from 'motion/react';

// Use domMax (25KB) if you need layout/drag
function AppWithDrag() {
  return (
    <LazyMotion features={domMax}>
      <YourApp />
    </LazyMotion>
  );
}

// ❌ WRONG: Using 'motion' with LazyMotion (no benefit)
import { motion } from 'motion/react';

function NotOptimized() {
  return (
    <motion.div> {/* Still loads full 32KB */}
      Not optimized
    </motion.div>
  );
}
```

**Feature Packages**:
- `domAnimation` (15KB): Basic animations, variants, gestures (no drag/layout)
- `domMax` (25KB): All features (drag, layout, pan)
- Use `m` instead of `motion` to get tree-shaking benefits

---

## View Transitions API

### Browser-Native Page Transitions (2025+)

**Problem**: Need smooth page transitions without JavaScript libraries

**Solution**: Use View Transitions API with React Router

**Implementation**:

```tsx
import { Link, useNavigate } from 'react-router-dom';

// ✅ CORRECT: View Transitions with React Router (2025)
function NavigationLink({ to, children }: { to: string; children: React.ReactNode }) {
  const navigate = useNavigate();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();

    // Check if browser supports View Transitions
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        navigate(to);
      });
    } else {
      // Fallback for browsers without support
      navigate(to);
    }
  };

  return (
    <a href={to} onClick={handleClick}>
      {children}
    </a>
  );
}

// ✅ CORRECT: React Router v6.4+ with View Transitions prop
import { Link } from 'react-router-dom';

function ModernNavigationLink() {
  return (
    <Link
      to="/about"
      viewTransition // Automatically uses View Transitions API
    >
      About
    </Link>
  );
}

// CSS for View Transitions
/*
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.3s;
}

::view-transition-old(root) {
  animation-name: fade-out;
}

::view-transition-new(root) {
  animation-name: fade-in;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
}
*/
```

### Custom View Transition Names

**Problem**: Need different transitions for different elements

**Solution**: Use `view-transition-name` CSS property

**Implementation**:

```tsx
// ✅ CORRECT: Named view transitions
function ProductCard({ product }: { product: Product }) {
  return (
    <div
      style={{ viewTransitionName: `product-${product.id}` } as React.CSSProperties}
      className="product-card"
    >
      <img
        src={product.image}
        style={{ viewTransitionName: `product-image-${product.id}` } as React.CSSProperties}
        alt={product.name}
      />
      <h3>{product.name}</h3>
    </div>
  );
}

// CSS for custom transitions
/*
::view-transition-old(product-image-1),
::view-transition-new(product-image-1) {
  animation-duration: 0.5s;
  /* Image morphs smoothly between pages */
}
*/
```

### Fallback Pattern for Older Browsers

**Problem**: View Transitions API not supported in all browsers (2025)

**Solution**: Progressive enhancement with Framer Motion fallback

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

// ✅ CORRECT: Progressive enhancement pattern
const supportsViewTransitions = typeof document !== 'undefined' && 'startViewTransition' in document;

function PageTransition({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  // Use View Transitions API if supported
  if (supportsViewTransitions) {
    return <>{children}</>;
  }

  // Fallback to Framer Motion
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

// App.tsx
function App() {
  return (
    <Router>
      <PageTransition>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </PageTransition>
    </Router>
  );
}
```

**Browser Support (2025)**:
- Chrome/Edge 111+ ✅
- Firefox 144+ (October 2025) ✅
- Safari: Not yet supported ❌
- Always provide fallback for unsupported browsers

---

## React Spring Patterns

### Installation & Basic Usage

```bash
npm install @react-spring/web
# or
yarn add @react-spring/web
```

**Implementation**:

```tsx
import { useSpring, animated } from '@react-spring/web';

// ✅ CORRECT: Basic spring animation
function SpringBox() {
  const springs = useSpring({
    from: { opacity: 0, transform: 'translateY(20px)' },
    to: { opacity: 1, transform: 'translateY(0px)' }
  });

  return <animated.div style={springs}>Smooth spring animation</animated.div>;
}

// ✅ CORRECT: Interactive spring
function InteractiveSpring() {
  const [isHovered, setIsHovered] = useState(false);

  const springs = useSpring({
    transform: isHovered ? 'scale(1.1)' : 'scale(1)',
    config: { tension: 300, friction: 10 } // Physics config
  });

  return (
    <animated.div
      style={springs}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      Hover me
    </animated.div>
  );
}
```

### Physics-Based Configs

**Problem**: Need natural, realistic motion

**Solution**: Use React Spring's physics presets

**Implementation**:

```tsx
import { useSpring, animated, config } from '@react-spring/web';

// ✅ CORRECT: Preset configs
function PhysicsAnimations() {
  const defaultSpring = useSpring({
    to: { opacity: 1 },
    config: config.default // tension: 170, friction: 26
  });

  const gentleSpring = useSpring({
    to: { scale: 1 },
    config: config.gentle // tension: 120, friction: 14
  });

  const wobbleSpring = useSpring({
    to: { rotate: 0 },
    config: config.wobbly // tension: 180, friction: 12
  });

  const stiffSpring = useSpring({
    to: { x: 100 },
    config: config.stiff // tension: 210, friction: 20
  });

  const slowSpring = useSpring({
    to: { y: 100 },
    config: config.slow // tension: 280, friction: 60
  });

  const molassesSpring = useSpring({
    to: { opacity: 1 },
    config: config.molasses // tension: 280, friction: 120
  });

  // ✅ CORRECT: Custom physics
  const customSpring = useSpring({
    to: { x: 200 },
    config: {
      mass: 1,
      tension: 170,
      friction: 26,
      clamp: false,
      precision: 0.01,
      velocity: 0
    }
  });

  return <animated.div style={customSpring}>Physics!</animated.div>;
}
```

**Physics Properties**:
- `tension`: Higher = faster, snappier (default: 170)
- `friction`: Higher = less oscillation (default: 26)
- `mass`: Higher = heavier, slower (default: 1)
- `clamp`: Stop animation at target (no overshoot)
- `velocity`: Initial velocity

### useTrail (Staggered Animations)

**Problem**: Need staggered list animations

**Solution**: Use `useTrail` hook

**Implementation**:

```tsx
import { useTrail, animated } from '@react-spring/web';

// ✅ CORRECT: Staggered list animation
function StaggeredList({ items }: { items: string[] }) {
  const trail = useTrail(items.length, {
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    config: config.gentle
  });

  return (
    <div>
      {trail.map((style, index) => (
        <animated.div key={index} style={style}>
          {items[index]}
        </animated.div>
      ))}
    </div>
  );
}
```

### useTransition (Enter/Exit Animations)

**Problem**: Need enter/exit animations for conditional rendering

**Solution**: Use `useTransition` hook

**Implementation**:

```tsx
import { useTransition, animated } from '@react-spring/web';

// ✅ CORRECT: Conditional rendering with transitions
function Modal({ isOpen, children }: ModalProps) {
  const transitions = useTransition(isOpen, {
    from: { opacity: 0, transform: 'scale(0.95)' },
    enter: { opacity: 1, transform: 'scale(1)' },
    leave: { opacity: 0, transform: 'scale(0.95)' },
    config: config.stiff
  });

  return transitions(
    (style, item) =>
      item && (
        <animated.div style={style} className="modal">
          {children}
        </animated.div>
      )
  );
}

// ✅ CORRECT: List transitions
function AnimatedList({ items }: { items: Item[] }) {
  const transitions = useTransition(items, {
    keys: (item) => item.id,
    from: { opacity: 0, height: 0 },
    enter: { opacity: 1, height: 80 },
    leave: { opacity: 0, height: 0 },
    config: config.gentle
  });

  return (
    <div>
      {transitions((style, item) => (
        <animated.div style={style}>
          {item.name}
        </animated.div>
      ))}
    </div>
  );
}
```

### React Spring vs Framer Motion

**Use React Spring when**:
- Pure physics-based animations are critical
- Need fine-grained control over spring physics
- Building data visualizations with smooth transitions
- Performance is critical (React Spring is very optimized)

**Use Framer Motion when**:
- Need gesture support (drag, swipe, tap)
- Building UI animations (modals, menus, cards)
- Want declarative, props-based API
- Need layout animations
- Team prefers easier learning curve

---

## GSAP Patterns

### Installation & Setup

```bash
npm install gsap
# or
yarn add gsap
```

**Implementation**:

```tsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugins
gsap.registerPlugin(ScrollTrigger);

// ✅ CORRECT: Basic GSAP animation in React
function GSAPAnimation() {
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!boxRef.current) return;

    // Animate on mount
    gsap.from(boxRef.current, {
      opacity: 0,
      y: 20,
      duration: 0.5,
      ease: 'power2.out'
    });
  }, []);

  return <div ref={boxRef}>Animated with GSAP</div>;
}

// ✅ CORRECT: Timeline animations
function TimelineAnimation() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const tl = gsap.timeline();

    tl.from('.logo', { opacity: 0, scale: 0.3, duration: 1 })
      .from('.title', { opacity: 0, y: -30, duration: 0.5 }, '-=0.3')
      .from('.subtitle', { opacity: 0, y: 20, duration: 0.5 }, '-=0.2')
      .from('.cta', { opacity: 0, scale: 0.8, duration: 0.3 });

    return () => {
      tl.kill(); // Cleanup
    };
  }, []);

  return (
    <div ref={containerRef}>
      <div className="logo">Logo</div>
      <h1 className="title">Title</h1>
      <p className="subtitle">Subtitle</p>
      <button className="cta">Call to Action</button>
    </div>
  );
}
```

### ScrollTrigger Pattern

**Problem**: Need scroll-triggered animations

**Solution**: Use GSAP ScrollTrigger plugin

**Implementation**:

```tsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// ✅ CORRECT: ScrollTrigger in React
function ScrollAnimation() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.from('.animated-element', {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%', // When top of element hits 80% of viewport
          end: 'bottom 20%',
          toggleActions: 'play none none reverse',
          markers: false // Set to true for debugging
        },
        opacity: 0,
        y: 50,
        duration: 1,
        stagger: 0.2
      });
    }, sectionRef);

    return () => {
      ctx.revert(); // Cleanup
    };
  }, []);

  return (
    <div ref={sectionRef}>
      <div className="animated-element">Item 1</div>
      <div className="animated-element">Item 2</div>
      <div className="animated-element">Item 3</div>
    </div>
  );
}

// ✅ CORRECT: Parallax with ScrollTrigger
function ParallaxSection() {
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!bgRef.current) return;

    gsap.to(bgRef.current, {
      scrollTrigger: {
        trigger: bgRef.current,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true // Smooth scrubbing
      },
      y: -200,
      ease: 'none'
    });
  }, []);

  return (
    <div className="parallax-container">
      <div ref={bgRef} className="parallax-bg">
        Background moves slower
      </div>
    </div>
  );
}

// ✅ CORRECT: Pin element during scroll
function PinnedSection() {
  const pinRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pinRef.current) return;

    ScrollTrigger.create({
      trigger: pinRef.current,
      start: 'top top',
      end: '+=500',
      pin: true,
      pinSpacing: true
    });
  }, []);

  return (
    <div ref={pinRef} className="pinned-section">
      This stays pinned while scrolling
    </div>
  );
}
```

### GSAP Context for React

**Problem**: GSAP animations causing issues with React re-renders

**Solution**: Use `gsap.context()` for proper cleanup

**Implementation**:

```tsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';

// ✅ CORRECT: GSAP context for React components
function ProperGSAPComponent() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // All GSAP animations inside this context
      gsap.from('.element', { opacity: 0, y: 20 });
      gsap.to('.another', { rotation: 360 });
    }, containerRef); // Scope to containerRef

    return () => {
      ctx.revert(); // Automatically kills all animations and ScrollTriggers
    };
  }, []);

  return (
    <div ref={containerRef}>
      <div className="element">Element</div>
      <div className="another">Another</div>
    </div>
  );
}

// ❌ WRONG: No cleanup
function BrokenGSAPComponent() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.from(ref.current, { opacity: 0 });
    // No cleanup! Animation continues after unmount
  }, []);

  return <div ref={ref}>Broken</div>;
}
```

**Key Points**:
- Always use `gsap.context()` in React components
- Always return cleanup function with `ctx.revert()`
- Scope context to container ref for better performance
- Context automatically cleans up ScrollTriggers

---

## Common Animation Patterns

### Loading States

#### Skeleton Loading

**Problem**: Need loading placeholders that don't feel empty

**Solution**: Use CSS shimmer animation

**Implementation**:

```tsx
// ✅ CORRECT: Skeleton loading with CSS
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-image" />
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text short" />
    </div>
  );
}

// CSS:
/*
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
  border-radius: 4px;
}

.skeleton-image { height: 200px; margin-bottom: 16px; }
.skeleton-title { height: 24px; width: 60%; margin-bottom: 8px; }
.skeleton-text { height: 16px; margin-bottom: 8px; }
.skeleton-text.short { width: 40%; }
*/

// ✅ CORRECT: Conditional skeleton
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId)
  });

  if (isLoading) {
    return <SkeletonCard />;
  }

  return (
    <div className="user-card">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  );
}
```

#### Loading Spinners

**Problem**: Need loading indicators

**Solution**: Use Tailwind's built-in spinner or custom CSS

**Implementation**:

```tsx
// ✅ CORRECT: Tailwind spinner
function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-4'
  };

  return (
    <div
      className={`
        ${sizeClasses[size]}
        animate-spin
        rounded-full
        border-blue-500
        border-t-transparent
      `}
    />
  );
}

// ✅ CORRECT: Button with loading state
function LoadingButton({ isLoading, children, ...props }: ButtonProps) {
  return (
    <button disabled={isLoading} {...props}>
      {isLoading ? (
        <div className="flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading...</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
}
```

#### Progress Bars

**Problem**: Need to show progress for long operations

**Solution**: Use Framer Motion or CSS transitions

**Implementation**:

```tsx
import { motion } from 'motion/react';

// ✅ CORRECT: Animated progress bar
function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      />
    </div>
  );
}

// ✅ CORRECT: Circular progress
function CircularProgress({ progress }: { progress: number }) {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (progress / 100) * circumference;

  return (
    <svg className="transform -rotate-90" width="100" height="100">
      <circle
        cx="50"
        cy="50"
        r="45"
        stroke="#e5e7eb"
        strokeWidth="10"
        fill="none"
      />
      <motion.circle
        cx="50"
        cy="50"
        r="45"
        stroke="#3b82f6"
        strokeWidth="10"
        fill="none"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />
    </svg>
  );
}
```

### Toast Notifications

**Problem**: Need animated toast notifications

**Solution**: Use Framer Motion with AnimatePresence

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';
import { createContext, useContext, useState } from 'react';

// ✅ CORRECT: Toast system with animations
type Toast = {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
};

const ToastContext = createContext<{
  toasts: Toast[];
  addToast: (message: string, type: Toast['type']) => void;
  removeToast: (id: string) => void;
}>({
  toasts: [],
  addToast: () => {},
  removeToast: () => {}
});

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: Toast['type']) => {
    const id = Math.random().toString(36);
    setToasts((prev) => [...prev, { id, message, type }]);

    // Auto-remove after 5s
    setTimeout(() => removeToast(id), 5000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: string) => void }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 50, scale: 0.3 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 200, scale: 0.5 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            className={`
              px-4 py-3 rounded-lg shadow-lg
              ${toast.type === 'success' ? 'bg-green-500' : ''}
              ${toast.type === 'error' ? 'bg-red-500' : ''}
              ${toast.type === 'info' ? 'bg-blue-500' : ''}
              text-white
            `}
          >
            <div className="flex items-center gap-2">
              <span>{toast.message}</span>
              <button onClick={() => onRemove(toast.id)}>×</button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

// Usage
export function useToast() {
  return useContext(ToastContext);
}

function MyComponent() {
  const { addToast } = useToast();

  return (
    <button onClick={() => addToast('Success!', 'success')}>
      Show Toast
    </button>
  );
}
```

### Modal/Dialog Animations

**Problem**: Need smooth modal enter/exit animations

**Solution**: Use AnimatePresence with backdrop

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';
import { useEffect } from 'react';

// ✅ CORRECT: Modal with backdrop and animations
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

function Modal({ isOpen, onClose, children }: ModalProps) {
  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              key="modal"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            >
              {children}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

// ✅ CORRECT: Drawer from side
function Drawer({ isOpen, onClose, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          <motion.div
            key="drawer"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-50"
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### List Animations

**Problem**: Need smooth list add/remove animations

**Solution**: Use AnimatePresence with layout animations

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';

// ✅ CORRECT: List with enter/exit/reorder animations
function AnimatedList({ items }: { items: Item[] }) {
  return (
    <ul className="space-y-2">
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <motion.li
            key={item.id}
            layout // Smooth reordering
            initial={{ opacity: 0, height: 0, x: -20 }}
            animate={{ opacity: 1, height: 'auto', x: 0 }}
            exit={{ opacity: 0, height: 0, x: 20 }}
            transition={{
              opacity: { duration: 0.2 },
              height: { duration: 0.2 },
              x: { type: 'spring', stiffness: 400, damping: 25 }
            }}
            className="bg-white rounded-lg p-4 shadow"
          >
            {item.name}
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  );
}

// ✅ CORRECT: Staggered list reveal
function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2
          }
        }
      }}
    >
      {items.map((item, i) => (
        <motion.li
          key={i}
          variants={{
            hidden: { opacity: 0, x: -20 },
            visible: { opacity: 1, x: 0 }
          }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### Accordion/Collapse Animations

**Problem**: Need smooth expand/collapse animations

**Solution**: Use Framer Motion layout animations

**Implementation**:

```tsx
import { motion, AnimatePresence } from 'motion/react';
import { useState } from 'react';

// ✅ CORRECT: Accordion with smooth height animation
function AccordionItem({ title, children }: { title: string; children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border rounded-lg overflow-hidden">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100"
      >
        <span className="font-medium">{title}</span>
        <motion.span
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </motion.button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="overflow-hidden"
          >
            <div className="p-4">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ✅ CORRECT: Multiple accordions (only one open at a time)
function Accordion({ items }: { items: AccordionItem[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <AccordionItem
          key={index}
          title={item.title}
          isOpen={openIndex === index}
          onToggle={() => setOpenIndex(openIndex === index ? null : index)}
        >
          {item.content}
        </AccordionItem>
      ))}
    </div>
  );
}
```

### Card Hover Effects

**Problem**: Need subtle hover interactions

**Solution**: Use CSS transitions or Framer Motion gestures

**Implementation**:

```tsx
import { motion } from 'motion/react';

// ✅ CORRECT: CSS hover effect (performant)
function CSSCard() {
  return (
    <div className="card hover-card">
      <img src="image.jpg" alt="Card" />
      <h3>Title</h3>
      <p>Description</p>
    </div>
  );
}

// CSS:
/*
.hover-card {
  transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
}

.hover-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
*/

// ✅ CORRECT: Framer Motion hover (more control)
function MotionCard() {
  return (
    <motion.div
      whileHover={{
        y: -4,
        scale: 1.02,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className="card"
    >
      <img src="image.jpg" alt="Card" />
      <h3>Title</h3>
      <p>Description</p>
    </motion.div>
  );
}

// ✅ CORRECT: Card with tilt effect
function TiltCard() {
  return (
    <motion.div
      whileHover={{ rotateY: 5, rotateX: 5 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      style={{ perspective: 1000 }}
      className="card"
    >
      Content
    </motion.div>
  );
}
```

---

## Accessibility

### Respecting prefers-reduced-motion

**Problem**: Animations can cause motion sickness for some users

**Solution**: Respect `prefers-reduced-motion` media query

**Implementation**:

```tsx
import { useEffect, useState } from 'react';

// ✅ CORRECT: Custom hook for reduced motion
function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = () => {
      setPrefersReducedMotion(mediaQuery.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

// ✅ CORRECT: Conditional animation with hook
function AccessibleAnimation() {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: prefersReducedMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: prefersReducedMotion ? 0 : 0.5
      }}
    >
      Content
    </motion.div>
  );
}

// ✅ CORRECT: Framer Motion built-in support
import { useReducedMotion } from 'motion/react';

function MotionAccessible() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ scale: shouldReduceMotion ? 1 : 1.5 }}
      transition={{ duration: shouldReducedMotion ? 0 : 0.5 }}
    >
      Respects user preference
    </motion.div>
  );
}

// ✅ CORRECT: CSS approach (no-motion-first)
// Start with no animation, add animations only for users who allow motion
/*
.animated {
  // No animation by default
}

@media (prefers-reduced-motion: no-preference) {
  .animated {
    transition: transform 0.3s, opacity 0.3s;
  }

  .animated:hover {
    transform: scale(1.05);
  }
}
*/
```

### MotionConfig for Global Accessibility

**Problem**: Need to disable/reduce all animations globally

**Solution**: Use MotionConfig at app level

**Implementation**:

```tsx
import { MotionConfig } from 'motion/react';
import { usePrefersReducedMotion } from './hooks/usePrefersReducedMotion';

// ✅ CORRECT: Global motion configuration
function App() {
  const shouldReduceMotion = usePrefersReducedMotion();

  return (
    <MotionConfig reducedMotion={shouldReduceMotion ? 'always' : 'never'}>
      <YourApp />
    </MotionConfig>
  );
}

// All motion components inside will respect this setting
```

**ReducedMotion Options**:
- `"always"`: Disable all transform/layout animations, preserve opacity/color
- `"never"`: Always animate (ignore user preference)
- `"user"`: Respect user's OS setting (default)

### Focus Management

**Problem**: Animations interfering with keyboard navigation

**Solution**: Ensure focus is managed during animations

**Implementation**:

```tsx
import { motion } from 'motion/react';
import { useEffect, useRef } from 'react';

// ✅ CORRECT: Focus management in modal
function AccessibleModal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Focus modal when opened
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      firstElement?.focus();
    }
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={modalRef}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          role="dialog"
          aria-modal="true"
          tabIndex={-1}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

### Screen Reader Considerations

**Problem**: Screen readers announcing elements during animations

**Solution**: Use `aria-live` regions appropriately

**Implementation**:

```tsx
// ✅ CORRECT: Accessible toast notifications
function AccessibleToast({ message }: { message: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 200 }}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      {message}
    </motion.div>
  );
}

// For urgent messages (errors)
function ErrorToast({ message }: { message: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      {message}
    </motion.div>
  );
}
```

**Key Points**:
- Always respect `prefers-reduced-motion`
- Use "no-motion-first" approach in CSS
- Manage focus during modal/dialog animations
- Use appropriate ARIA attributes
- Test with keyboard navigation
- Test with screen readers

---

## Performance Optimization

### GPU-Accelerated Properties

**Problem**: Animations causing jank and low frame rates

**Solution**: Only animate GPU-friendly properties

**Implementation**:

```tsx
// ✅ CORRECT: GPU-accelerated properties
const gpuAnimations = {
  transform: 'translateX(100px)', // ✅ GPU
  opacity: 0.5,                   // ✅ GPU
  filter: 'blur(5px)',            // ✅ GPU (modern browsers)
  scale: 1.5,                     // ✅ GPU (transform: scale)
  rotate: '45deg',                // ✅ GPU (transform: rotate)
  x: 100,                         // ✅ GPU (Framer Motion → translate)
  y: 100,                         // ✅ GPU (Framer Motion → translate)
};

// ❌ WRONG: CPU-bound properties (trigger layout/paint)
const cpuAnimations = {
  width: '200px',      // ❌ Triggers layout
  height: '200px',     // ❌ Triggers layout
  top: '100px',        // ❌ Triggers layout
  left: '100px',       // ❌ Triggers layout
  padding: '20px',     // ❌ Triggers layout
  margin: '20px',      // ❌ Triggers layout
  fontSize: '20px',    // ❌ Triggers layout
  lineHeight: '1.5',   // ❌ Triggers layout
};

// ✅ CORRECT: Use transform instead of position
function FastSlide() {
  return (
    <motion.div
      animate={{ x: 100 }} // GPU-accelerated translateX
    >
      Fast!
    </motion.div>
  );
}

// ❌ WRONG: Animating position
function SlowSlide() {
  return (
    <motion.div
      animate={{ left: 100 }} // CPU-bound, triggers layout
    >
      Slow!
    </motion.div>
  );
}
```

**Performance Hierarchy**:
1. **Best**: `transform`, `opacity` (GPU, no layout/paint)
2. **Good**: `filter` (GPU on modern browsers, may trigger paint)
3. **Bad**: `color`, `background-color` (triggers paint)
4. **Worst**: `width`, `height`, `top`, `left`, `margin`, `padding` (triggers layout + paint)

### will-change Property

**Problem**: Need to hint browser about upcoming animations

**Solution**: Use `will-change` sparingly and remove after animation

**Implementation**:

```tsx
// ✅ CORRECT: will-change only during animation
function OptimizedAnimation() {
  const [isAnimating, setIsAnimating] = useState(false);

  return (
    <motion.div
      style={{
        willChange: isAnimating ? 'transform, opacity' : 'auto'
      }}
      onAnimationStart={() => setIsAnimating(true)}
      onAnimationComplete={() => setIsAnimating(false)}
      animate={{ x: 100, opacity: 0.5 }}
    >
      Optimized
    </motion.div>
  );
}

// ❌ WRONG: will-change on every element
function OverOptimized() {
  return (
    <div style={{ willChange: 'transform' }}> {/* Always on = bad */}
      {items.map(item => (
        <div key={item.id} style={{ willChange: 'transform' }}>
          {/* Too many layers, memory issues */}
          {item.name}
        </div>
      ))}
    </div>
  );
}

// ✅ CORRECT: CSS hover-only will-change
/*
.card:hover {
  will-change: transform;
  transform: scale(1.05);
}
*/
```

**Key Points**:
- Don't set `will-change` on too many elements (memory issues)
- Remove `will-change` after animation completes
- Use `auto` to reset
- Only use for animations that actually need optimization
- Prefer CSS `will-change` for hover states

### Avoiding Layout Thrashing

**Problem**: Reading and writing to DOM in loops causes forced reflows

**Solution**: Batch DOM reads, then batch DOM writes

**Implementation**:

```tsx
import { useEffect, useRef } from 'react';

// ❌ WRONG: Layout thrashing (read-write-read-write)
function LayoutThrashing() {
  useEffect(() => {
    const elements = document.querySelectorAll('.item');

    elements.forEach((el) => {
      const height = el.clientHeight; // READ (forces reflow)
      el.style.height = `${height * 2}px`; // WRITE
      // Next iteration: READ (forced reflow), WRITE, repeat...
    });
  }, []);

  return <div>Slow!</div>;
}

// ✅ CORRECT: Batch reads, then batch writes
function NoThrashing() {
  useEffect(() => {
    const elements = document.querySelectorAll('.item');

    // Batch all reads first
    const heights = Array.from(elements).map((el) => el.clientHeight);

    // Then batch all writes
    elements.forEach((el, i) => {
      el.style.height = `${heights[i] * 2}px`;
    });
  }, []);

  return <div>Fast!</div>;
}

// ✅ CORRECT: Use requestAnimationFrame for animations
function SmoothAnimation() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let animationId: number;
    let progress = 0;

    const animate = () => {
      if (!ref.current) return;

      progress += 0.01;

      // Only write, no reads
      ref.current.style.transform = `translateX(${progress * 100}px)`;

      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, []);

  return <div ref={ref}>Smooth!</div>;
}
```

### requestAnimationFrame Pattern

**Problem**: Need frame-perfect animations without library

**Solution**: Use `requestAnimationFrame` with React refs

**Implementation**:

```tsx
import { useEffect, useRef } from 'react';

// ✅ CORRECT: requestAnimationFrame with cleanup
function RAFAnimation() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    let animationId: number;
    let startTime: number | null = null;
    const duration = 1000; // 1 second

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = (timestamp - startTime) / duration;

      if (!ref.current) return;

      // Easing function (ease-out)
      const eased = 1 - Math.pow(1 - progress, 3);

      // Update DOM (write only)
      ref.current.style.transform = `translateX(${eased * 100}px)`;
      ref.current.style.opacity = `${eased}`;

      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId); // Cleanup
    };
  }, []);

  return <div ref={ref}>RAF Animation</div>;
}

// ✅ CORRECT: Reusable RAF hook
function useAnimationFrame(callback: (deltaTime: number) => void) {
  const requestRef = useRef<number>();
  const previousTimeRef = useRef<number>();

  useEffect(() => {
    const animate = (time: number) => {
      if (previousTimeRef.current !== undefined) {
        const deltaTime = time - previousTimeRef.current;
        callback(deltaTime);
      }
      previousTimeRef.current = time;
      requestRef.current = requestAnimationFrame(animate);
    };

    requestRef.current = requestAnimationFrame(animate);

    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [callback]);
}

// Usage
function AnimatedComponent() {
  const [position, setPosition] = useState(0);

  useAnimationFrame((deltaTime) => {
    setPosition((prev) => prev + deltaTime * 0.1);
  });

  return (
    <div style={{ transform: `translateX(${position}px)` }}>
      Moving!
    </div>
  );
}
```

### Lazy Loading Animation Libraries

**Problem**: Animation libraries add significant bundle size

**Solution**: Lazy load heavy libraries, use code splitting

**Implementation**:

```tsx
import { lazy, Suspense } from 'react';

// ✅ CORRECT: Lazy load GSAP animations
const GSAPAnimation = lazy(() => import('./components/GSAPAnimation'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GSAPAnimation />
    </Suspense>
  );
}

// ✅ CORRECT: Conditional loading
function ConditionalAnimation({ useHeavyAnimation }: { useHeavyAnimation: boolean }) {
  const [Animation, setAnimation] = useState<React.ComponentType | null>(null);

  useEffect(() => {
    if (useHeavyAnimation) {
      import('./components/HeavyAnimation').then((module) => {
        setAnimation(() => module.default);
      });
    }
  }, [useHeavyAnimation]);

  if (!Animation) {
    return <SimpleCSAnimation />; // Fallback
  }

  return <Animation />;
}

// ✅ CORRECT: Route-based code splitting
const AnimatedPage = lazy(() => import('./pages/AnimatedPage'));

function Router() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route
        path="/animated"
        element={
          <Suspense fallback={<Spinner />}>
            <AnimatedPage />
          </Suspense>
        }
      />
    </Routes>
  );
}
```

### Performance Monitoring

**Problem**: Need to measure animation performance

**Solution**: Use browser DevTools and Performance API

**Implementation**:

```tsx
// ✅ CORRECT: Performance monitoring
function MonitoredAnimation() {
  useEffect(() => {
    // Mark start
    performance.mark('animation-start');

    const animate = () => {
      // Animation code...

      // Mark end
      performance.mark('animation-end');

      // Measure
      performance.measure(
        'animation-duration',
        'animation-start',
        'animation-end'
      );

      // Get measurement
      const measure = performance.getEntriesByName('animation-duration')[0];
      console.log(`Animation took ${measure.duration}ms`);
    };

    animate();
  }, []);

  return <div>Monitored</div>;
}

// ✅ CORRECT: FPS monitoring
function useFPS() {
  const [fps, setFPS] = useState(60);

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();

    const countFrames = () => {
      frameCount++;
      const currentTime = performance.now();

      if (currentTime >= lastTime + 1000) {
        setFPS(frameCount);
        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(countFrames);
    };

    const id = requestAnimationFrame(countFrames);
    return () => cancelAnimationFrame(id);
  }, []);

  return fps;
}

function FPSCounter() {
  const fps = useFPS();

  return (
    <div className="fixed top-4 right-4 bg-black text-white px-2 py-1 rounded">
      {fps} FPS
    </div>
  );
}
```

**Performance Tips**:
- Use Chrome DevTools Performance tab to record animations
- Look for long frames (>16.67ms = below 60fps)
- Check for "Forced reflow" warnings
- Monitor memory usage for layout animations
- Use "Rendering" tab to see paint flashing
- Enable FPS meter in DevTools

---

## Advanced Patterns

### Stagger Animations

**Problem**: Need to animate list items one after another

**Solution**: Use Framer Motion variants with `staggerChildren`

**Implementation**:

```tsx
import { motion, Variants } from 'motion/react';

// ✅ CORRECT: Staggered list animation
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // 100ms delay between children
      delayChildren: 0.2    // Wait 200ms before starting
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item, i) => (
        <motion.li key={i} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}

// ✅ CORRECT: Reverse stagger on exit
const exitVariants: Variants = {
  exit: {
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1 // Reverse order
    }
  }
};
```

### Orchestrated Animations (Sequences)

**Problem**: Need complex animation sequences

**Solution**: Use GSAP timeline or Framer Motion orchestration

**Implementation**:

```tsx
// ✅ CORRECT: GSAP timeline
import gsap from 'gsap';

function GSAPSequence() {
  useEffect(() => {
    const tl = gsap.timeline();

    tl.from('.logo', { opacity: 0, scale: 0.3, duration: 1 })
      .from('.title', { opacity: 0, y: -30, duration: 0.5 }, '-=0.3') // Start 0.3s before prev ends
      .from('.subtitle', { opacity: 0, y: 20, duration: 0.5 }, '-=0.2')
      .from('.cta', { opacity: 0, scale: 0.8, duration: 0.3 });

    return () => tl.kill();
  }, []);

  return (
    <div>
      <div className="logo">Logo</div>
      <h1 className="title">Title</h1>
      <p className="subtitle">Subtitle</p>
      <button className="cta">CTA</button>
    </div>
  );
}

// ✅ CORRECT: Framer Motion orchestration
const sequenceVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: 'beforeChildren',
      staggerChildren: 0.2,
      delayChildren: 0.3
    }
  }
};

const childVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 }
  }
};

function MotionSequence() {
  return (
    <motion.div variants={sequenceVariants} initial="hidden" animate="visible">
      <motion.div variants={childVariants}>First</motion.div>
      <motion.div variants={childVariants}>Second</motion.div>
      <motion.div variants={childVariants}>Third</motion.div>
    </motion.div>
  );
}
```

### Gesture-Based Animations (Swipe, Drag)

**Problem**: Need swipe-to-delete or drag-to-reorder

**Solution**: Use Framer Motion drag with `onDragEnd`

**Implementation**:

```tsx
// ✅ CORRECT: Swipe to delete
function SwipeToDelete({ item, onDelete }: { item: Item; onDelete: () => void }) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -200, right: 0 }}
      dragElastic={0.1}
      onDragEnd={(event, info) => {
        if (info.offset.x < -100) {
          onDelete();
        }
      }}
      className="relative bg-white"
    >
      <div className="absolute inset-y-0 right-0 flex items-center pr-4 bg-red-500">
        <TrashIcon className="text-white" />
      </div>
      <div className="relative bg-white p-4">
        {item.name}
      </div>
    </motion.div>
  );
}

// ✅ CORRECT: Drag to reorder
import { Reorder } from 'motion/react';

function DragToReorder({ items }: { items: Item[] }) {
  const [orderedItems, setOrderedItems] = useState(items);

  return (
    <Reorder.Group axis="y" values={orderedItems} onReorder={setOrderedItems}>
      {orderedItems.map((item) => (
        <Reorder.Item key={item.id} value={item}>
          <div className="p-4 bg-white border mb-2 cursor-grab active:cursor-grabbing">
            {item.name}
          </div>
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}
```

### Morph Animations (Element to Element)

**Problem**: Need element to morph between different states/pages

**Solution**: Use Framer Motion shared layout animations

**Implementation**:

```tsx
// ✅ CORRECT: Shared layout animation (morphing element)
function Gallery() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <div>
      {/* Grid of items */}
      <div className="grid grid-cols-3 gap-4">
        {items.map((item) => (
          <motion.div
            key={item.id}
            layoutId={item.id} // Shared layout ID
            onClick={() => setSelectedId(item.id)}
            className="cursor-pointer"
          >
            <img src={item.thumbnail} alt={item.title} />
          </motion.div>
        ))}
      </div>

      {/* Expanded view */}
      <AnimatePresence>
        {selectedId && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedId(null)}
              className="fixed inset-0 bg-black/50 z-40"
            />

            <motion.div
              layoutId={selectedId} // Same ID = morphs from grid item
              className="fixed inset-0 flex items-center justify-center z-50"
            >
              <motion.img
                src={items.find((i) => i.id === selectedId)?.fullSize}
                className="max-w-4xl max-h-screen"
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
```

### SVG Path Animations

**Problem**: Need to animate SVG paths (line drawing effect)

**Solution**: Use Framer Motion with `pathLength`

**Implementation**:

```tsx
import { motion } from 'motion/react';

// ✅ CORRECT: Line drawing animation
function LineDrawing() {
  return (
    <svg width="200" height="200">
      <motion.path
        d="M10 10 L190 190 M10 190 L190 10"
        stroke="#3b82f6"
        strokeWidth="4"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 2, ease: 'easeInOut' }}
      />
    </svg>
  );
}

// ✅ CORRECT: Animated checkmark
function AnimatedCheckmark() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      <motion.circle
        cx="32"
        cy="32"
        r="30"
        stroke="#10b981"
        strokeWidth="4"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5 }}
      />
      <motion.path
        d="M20 32 L28 40 L44 24"
        stroke="#10b981"
        strokeWidth="4"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      />
    </svg>
  );
}

// ✅ CORRECT: SVG morph animation
function SVGMorph() {
  const [isCircle, setIsCircle] = useState(true);

  return (
    <svg width="200" height="200" onClick={() => setIsCircle(!isCircle)}>
      <motion.path
        d={isCircle
          ? "M100 20 A 80 80 0 1 1 100 180 A 80 80 0 1 1 100 20" // Circle
          : "M20 100 L100 20 L180 100 L100 180 Z" // Diamond
        }
        fill="#3b82f6"
        transition={{ duration: 0.5, ease: 'easeInOut' }}
      />
    </svg>
  );
}
```

### Spring Physics (Natural Motion)

**Problem**: Need realistic, natural motion

**Solution**: Use Framer Motion or React Spring with physics configs

**Implementation**:

```tsx
import { motion } from 'motion/react';

// ✅ CORRECT: Spring animation (bouncy)
function BouncyButton() {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 17
      }}
    >
      Bouncy!
    </motion.button>
  );
}

// ✅ CORRECT: Different spring feels
const springConfigs = {
  // Gentle (soft landing)
  gentle: {
    type: 'spring',
    stiffness: 120,
    damping: 14
  },

  // Snappy (quick response)
  snappy: {
    type: 'spring',
    stiffness: 400,
    damping: 25
  },

  // Wobbly (bouncy)
  wobbly: {
    type: 'spring',
    stiffness: 180,
    damping: 12
  },

  // Stiff (minimal overshoot)
  stiff: {
    type: 'spring',
    stiffness: 500,
    damping: 30
  }
};

function SpringExamples() {
  return (
    <div className="space-y-4">
      <motion.div animate={{ x: 100 }} transition={springConfigs.gentle}>
        Gentle
      </motion.div>
      <motion.div animate={{ x: 100 }} transition={springConfigs.snappy}>
        Snappy
      </motion.div>
      <motion.div animate={{ x: 100 }} transition={springConfigs.wobbly}>
        Wobbly
      </motion.div>
      <motion.div animate={{ x: 100 }} transition={springConfigs.stiff}>
        Stiff
      </motion.div>
    </div>
  );
}
```

**Spring Physics Properties**:
- `stiffness`: Higher = faster, snappier (default: 100)
- `damping`: Higher = less oscillation (default: 10)
- `mass`: Higher = heavier, slower (default: 1)
- `velocity`: Initial velocity (default: 0)

---

## Summary

### Key Patterns

1. **Start Simple**: Use CSS transitions for basic effects, upgrade to libraries only when needed
2. **Choose the Right Tool**:
   - CSS: Hover effects, focus states, simple transitions
   - Framer Motion: 90% of React animation needs
   - React Spring: Physics-based, natural motion
   - GSAP: Complex timelines, ScrollTrigger
   - View Transitions API: Page transitions (2025+)

3. **Performance First**:
   - Only animate `transform`, `opacity`, `filter`
   - Use `will-change` sparingly
   - Avoid layout thrashing (batch reads, then writes)
   - Use `requestAnimationFrame` for custom animations

4. **Accessibility Always**:
   - Respect `prefers-reduced-motion`
   - Use "no-motion-first" approach
   - Manage focus during animations
   - Use appropriate ARIA attributes

5. **Bundle Size**:
   - Use LazyMotion with Framer Motion (4.6KB vs 32KB)
   - Lazy load heavy animations
   - Code split animation-heavy routes

### Common Mistakes

| Mistake | Solution |
|---------|----------|
| Animating `width`, `height`, `top`, `left` | Use `transform` (scale, translate) instead |
| Using `will-change` on all elements | Only use during animation, remove after |
| No `prefers-reduced-motion` support | Always respect user preferences |
| Missing `key` props in AnimatePresence | Each child needs unique `key` |
| Layout thrashing (read-write loops) | Batch reads, then batch writes |
| Not cleaning up GSAP animations | Use `gsap.context()` and `ctx.revert()` |
| Animating non-GPU properties | Stick to `transform`, `opacity`, `filter` |
| Not removing `will-change` after animation | Set to `auto` when done |

### Quick Reference

#### Framer Motion Cheat Sheet

```tsx
// Basic animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
/>

// Gestures
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  drag
  dragConstraints={{ left: 0, right: 300 }}
/>

// Variants
const variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

<motion.div variants={variants} initial="hidden" animate="visible">
  <motion.div variants={itemVariants} />
</motion.div>

// AnimatePresence
<AnimatePresence>
  {isOpen && <motion.div exit={{ opacity: 0 }} />}
</AnimatePresence>

// Layout animations
<motion.div layout layoutId="shared-id" />

// Scroll animations
<motion.div whileInView={{ opacity: 1 }} viewport={{ once: true }} />
```

#### CSS Animation Cheat Sheet

```css
/* Transition */
.element {
  transition: transform 0.3s ease-out;
}

.element:hover {
  transform: scale(1.05);
}

/* Keyframe animation */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.element {
  animation: fade-in 0.5s ease-out;
}

/* Reduced motion */
@media (prefers-reduced-motion: no-preference) {
  .element {
    transition: transform 0.3s;
  }
}
```

#### Performance Checklist

- [ ] Only animating `transform`, `opacity`, `filter`
- [ ] Using `will-change` only during animation
- [ ] Respecting `prefers-reduced-motion`
- [ ] Cleaning up animations on unmount
- [ ] No layout thrashing (batched reads/writes)
- [ ] Using `requestAnimationFrame` for custom animations
- [ ] Lazy loading heavy animation libraries
- [ ] Testing on low-end devices
- [ ] Measuring FPS (should be 60fps)

---

## Related Skills

- [React Performance Patterns](03-react-performance.md) - Bundle optimization, code splitting
- [TanStack Query Patterns](04-tanstack-query.md) - Optimistic updates (pairs well with animations)
- [State Management](07-state-management.md) - Managing animation state globally
- [React Router Patterns](06-react-router-patterns.md) - Page transitions
- [Form Handling](05-form-handling.md) - Form validation animations
- [Frontend Development](../frontend-development.md) - General React patterns
- [Testing Strategy](../testing-strategy/04-frontend-component-testing.md) - Testing animations

---

**Last Updated**: 2025-12-09

**Sources**:
- [Motion (Framer Motion) Official Docs](https://motion.dev/)
- [React Labs: View Transitions](https://react.dev/blog/2025/04/23/react-labs-view-transitions-activity-and-more)
- [Chrome for Developers: View Transitions 2025](https://developer.chrome.com/blog/view-transitions-in-2025)
- [Josh W. Comeau: Accessible Animations](https://www.joshwcomeau.com/react/prefers-reduced-motion/)
- [Smashing Magazine: CSS GPU Animation](https://www.smashingmagazine.com/2016/12/gpu-animation-doing-it-right/)
- [GSAP ScrollTrigger Docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [React Spring Official Docs](https://www.react-spring.dev/)
- [Tailwind CSS Animation Docs](https://tailwindcss.com/docs/animation)
- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [React Router: View Transitions](https://reactrouter.com/how-to/view-transitions)
