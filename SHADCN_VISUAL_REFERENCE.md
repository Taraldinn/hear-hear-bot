# 🎨 Shadcn UI Visual Reference

## Color Swatches

### Background Colors
```
┌─────────────────────────────────────────────┐
│ background: hsl(240 10% 3.9%)               │
│ ███████████████████████████████████████████ │
│ Deep dark background - primary surface     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ card: hsl(240 10% 3.9%)                     │
│ ███████████████████████████████████████████ │
│ Card background - same as background       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ muted: hsl(240 3.7% 15.9%)                  │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ Muted backgrounds - subtle elevation       │
└─────────────────────────────────────────────┘
```

### Text Colors
```
┌─────────────────────────────────────────────┐
│ foreground: hsl(0 0% 98%)                   │
│ ███████████████████████████████████████████ │
│ Near white - primary text                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ muted-foreground: hsl(240 5% 64.9%)         │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ Muted gray - secondary text                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ primary: hsl(0 0% 98%)                      │
│ ███████████████████████████████████████████ │
│ White - button backgrounds                 │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ primary-foreground: hsl(240 5.9% 10%)       │
│ ███████████████████████████████████████████ │
│ Very dark - button text                    │
└─────────────────────────────────────────────┘
```

### Border & Accents
```
┌─────────────────────────────────────────────┐
│ border: hsl(240 3.7% 15.9%)                 │
│ ─────────────────────────────────────────── │
│ Subtle borders - card edges                │
└─────────────────────────────────────────────┘
```

### Gradient Colors
```
Blue → Purple → Pink
#3b82f6 → #8b5cf6 → #ec4899
█████████░░░░░░░░░░░░████████
Used for hero text and accents
```

## Typography Scale

```
text-xs     (0.75rem / 12px)  : ᵗⁱⁿʸ
text-sm     (0.875rem / 14px) : small
text-base   (1rem / 16px)     : Base
text-lg     (1.125rem / 18px) : Large
text-xl     (1.25rem / 20px)  : X-Large
text-2xl    (1.5rem / 24px)   : 2X-Large
text-3xl    (1.875rem / 30px) : 3X-Large
text-4xl    (2.25rem / 36px)  : 4X-Large
text-5xl    (3rem / 48px)     : 5X-Large
text-6xl    (3.75rem / 60px)  : 6X-Large
text-7xl    (4.5rem / 72px)   : 7X-Large
text-8xl    (6rem / 96px)     : 8X-Large
```

## Font Weights

```
font-normal    (400) : Regular text
font-medium    (500) : Medium emphasis
font-semibold  (600) : Semi-bold
font-bold      (700) : Bold headings
font-extrabold (800) : Extra bold
font-black     (900) : Maximum weight
```

## Spacing System

```
4px Grid System:

0   : 0px
1   : 0.25rem (4px)   ▌
2   : 0.5rem  (8px)   ▌▌
3   : 0.75rem (12px)  ▌▌▌
4   : 1rem    (16px)  ▌▌▌▌
5   : 1.25rem (20px)  ▌▌▌▌▌
6   : 1.5rem  (24px)  ▌▌▌▌▌▌
8   : 2rem    (32px)  ▌▌▌▌▌▌▌▌
10  : 2.5rem  (40px)  ▌▌▌▌▌▌▌▌▌▌
12  : 3rem    (48px)  ▌▌▌▌▌▌▌▌▌▌▌▌
16  : 4rem    (64px)  ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌
20  : 5rem    (80px)  ▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌
```

## Border Radius

```
rounded-sm  (0.25rem / 4px)   : ▢ Small
rounded-md  (0.375rem / 6px)  : ▢ Medium
rounded-lg  (0.5rem / 8px)    : ▢ Large
rounded-xl  (0.75rem / 12px)  : ▢ Extra large
rounded-2xl (1rem / 16px)     : ▢ 2X large
rounded-3xl (1.5rem / 24px)   : ▢ 3X large
rounded-full (9999px)          : ● Circle
```

## Component Patterns

### Button - Primary
```
┌─────────────────────────┐
│  🚀 Add to Discord     │  ← Glow effect
└─────────────────────────┘
Height: 3rem (48px)
Padding: 2rem horizontal
Background: White
Text: Black
Hover: 90% opacity + glow
```

### Button - Secondary
```
┌─────────────────────────┐
│  📚 Documentation      │
└─────────────────────────┘
Height: 3rem (48px)
Padding: 2rem horizontal
Background: Transparent
Border: 1px subtle
Hover: Muted background
```

### Feature Card
```
┌──────────────────────────────┐
│                              │
│          ⏱️                  │
│                              │
│      Debate Timer            │
│                              │
│   Professional timing with   │
│   protected time tracking    │
│                              │
└──────────────────────────────┘
Border: 1px subtle
Padding: 1.5rem
Hover: Lift 4px + shadow
```

### Status Indicator
```
● ← Green dot (solid)
◉ ← Ping ring (animated)

Combined: ⊙ (dot + expanding ring)
```

### Navigation Bar
```
┌────────────────────────────────────────────────────┐
│  🎤 Bot Name ● | Docs | Commands | [Add to Discord]│
└────────────────────────────────────────────────────┘
Height: 4rem (64px)
Background: Backdrop blur
Border-bottom: 1px
Position: Sticky top
```

## Animation Curves

```
Float:
    │    ╱‾‾‾╲
    │   ╱     ╲
    │  ╱       ╲___╱
    └──────────────── 3s ease-in-out infinite

Pulse:
    │  ████
    │  ░░░░ ████
    │      ░░░░ ████
    └──────────────── 2s cubic-bezier infinite

Ping:
    │ ●
    │  ◉
    │   ◎
    │    ○
    └──────────────── 1s cubic-bezier infinite

Fade In:
    │         ▓▓▓▓
    │     ░░░░
    │ ░░░░
    └──────────────── 0.5s ease-out once
```

## Responsive Breakpoints

```
┌────────────────────────────────────────────┐
│ Mobile (< 640px)                           │
│ ┌────┐                                     │
│ │ F1 │                                     │
│ └────┘                                     │
│ ┌────┐                                     │
│ │ F2 │                                     │
│ └────┘                                     │
│ ┌────┐                                     │
│ │ F3 │                                     │
│ └────┘                                     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Tablet (640px - 1024px)                    │
│ ┌────────────┐  ┌────────────┐            │
│ │     F1     │  │     F2     │            │
│ └────────────┘  └────────────┘            │
│ ┌────────────┐                             │
│ │     F3     │                             │
│ └────────────┘                             │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Desktop (> 1024px)                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │    F1    │ │    F2    │ │    F3    │   │
│ └──────────┘ └──────────┘ └──────────┘   │
└────────────────────────────────────────────┘
```

## Grid Pattern

```
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
Grid: 4rem × 4rem
Opacity: 5% (rgba(255,255,255,0.05))
```

## Shadow Depths

```
None:      ▢
           No shadow

Subtle:    ▢
        ░  Hover state
       
Medium:    ▢
       ░░  Card elevation
      
Strong:    ▢
      ░░░  Modal/popup
     
Glow:      ◉
     ⊙⊙⊙⊙  CTA buttons
```

## Layout Structure

```
┌──────────────────────────────────────────────┐
│ Navigation (sticky)                          │
├──────────────────────────────────────────────┤
│ Grid Background (fixed)                      │
│                                              │
│ ┌──────────────────────────────────────┐   │
│ │ Hero Section                          │   │
│ │ ┌────────────────────────────────┐   │   │
│ │ │ Badge                           │   │   │
│ │ └────────────────────────────────┘   │   │
│ │ ┌────────────────────────────────┐   │   │
│ │ │ Title (gradient)                │   │   │
│ │ └────────────────────────────────┘   │   │
│ │ ┌────────────────────────────────┐   │   │
│ │ │ Description                     │   │   │
│ │ └────────────────────────────────┘   │   │
│ │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │   │
│ │ │Stats │ │Stats │ │Stats │ │Stats │ │   │
│ │ └──────┘ └──────┘ └──────┘ └──────┘ │   │
│ │ ┌───────────┐ ┌───────────┐        │   │
│ │ │ Primary   │ │ Secondary │        │   │
│ │ └───────────┘ └───────────┘        │   │
│ └──────────────────────────────────────┘   │
│                                              │
│ ┌──────────────────────────────────────┐   │
│ │ Features Section                      │   │
│ │ ┌─────┐ ┌─────┐ ┌─────┐              │   │
│ │ │ F1  │ │ F2  │ │ F3  │              │   │
│ │ └─────┘ └─────┘ └─────┘              │   │
│ │ ┌─────┐ ┌─────┐ ┌─────┐              │   │
│ │ │ F4  │ │ F5  │ │ F6  │              │   │
│ │ └─────┘ └─────┘ └─────┘              │   │
│ └──────────────────────────────────────┘   │
│                                              │
│ ┌──────────────────────────────────────┐   │
│ │ Commands Preview                      │   │
│ │ ┌────────────────────────────────┐   │   │
│ │ │ Command 1                       │   │   │
│ │ ├────────────────────────────────┤   │   │
│ │ │ Command 2                       │   │   │
│ │ ├────────────────────────────────┤   │   │
│ │ │ Command 3                       │   │   │
│ │ └────────────────────────────────┘   │   │
│ └──────────────────────────────────────┘   │
│                                              │
│ ┌──────────────────────────────────────┐   │
│ │ CTA Section                           │   │
│ │ ┌────────────────────────────────┐   │   │
│ │ │ Final call to action            │   │   │
│ │ └────────────────────────────────┘   │   │
│ └──────────────────────────────────────┘   │
│                                              │
├──────────────────────────────────────────────┤
│ Footer (border-top)                          │
└──────────────────────────────────────────────┘
```

## Icon Reference

```
🎤  Bot / Microphone
🚀  Launch / Add to Discord
📚  Documentation / Learn
⏱️  Timer / Timing
📋  Motion / List
🏆  Tournament / Trophy
✨  Special / Featured
● Green dot (status online)
○ Gray dot (status offline)
▢  Card / Container
```

## Accessibility

```
Text Contrast Ratios:
foreground on background:        14:1  ✅ AAA
muted-foreground on background:   4.5:1 ✅ AA
primary-foreground on primary:   14:1  ✅ AAA
```

## Quick Reference

```css
/* Most Used Classes */
.rounded-lg        /* 8px radius */
.border-border     /* Subtle borders */
.bg-background     /* Main background */
.text-foreground   /* Primary text */
.text-muted-foreground /* Secondary text */
.px-6 py-4         /* Common padding */
.gap-4             /* Common gap */
.transition-colors /* Color transitions */
.hover:bg-accent   /* Hover state */
```

---

**Color Mode**: Dark  
**Font**: Inter  
**Framework**: Tailwind CSS  
**Theme**: Shadcn UI  
