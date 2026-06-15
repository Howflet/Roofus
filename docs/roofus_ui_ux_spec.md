# Roofus — UI/UX Design Specification

## Design Language

### Brand Identity
- **Name:** Roofus
- **Tagline:** "Atlanta's smartest rooftops, scored for urban agriculture"
- **Personality:** Clean, data-driven, optimistic, environmental. Feels like a premium PropTech/CleanTech dashboard — not a government GIS tool.
- **Logo concept:** A minimalist rooftop silhouette with a small leaf/sprout growing from the peak. Geometric, modern, works at small sizes.

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0B1120` | Page background (deep navy-black) |
| `--bg-surface` | `#111827` | Cards, panels, modals |
| `--bg-surface-glass` | `rgba(17, 24, 39, 0.7)` + `backdrop-filter: blur(20px)` | Floating panels (glassmorphism) |
| `--bg-surface-hover` | `#1F2937` | Hover states on surfaces |
| `--border-subtle` | `rgba(255, 255, 255, 0.08)` | Card borders, dividers |
| `--border-glow` | `rgba(16, 185, 129, 0.3)` | Active/focused element borders |
| `--text-primary` | `#F9FAFB` | Headings, primary text |
| `--text-secondary` | `#9CA3AF` | Labels, descriptions, metadata |
| `--text-muted` | `#6B7280` | Placeholders, disabled text |
| `--accent-emerald` | `#10B981` | Primary CTA, high scores, brand accent |
| `--accent-emerald-dark` | `#059669` | Hover/pressed states on primary |
| `--accent-cyan` | `#06B6D4` | Secondary accent, links, info badges |
| `--score-excellent` | `#10B981` | Score 85–100 (emerald green) |
| `--score-good` | `#84CC16` | Score 70–84 (lime green) |
| `--score-moderate` | `#F59E0B` | Score 50–69 (warm amber) |
| `--score-below-avg` | `#F97316` | Score 30–49 (orange) |
| `--score-poor` | `#EF4444` | Score 0–29 (red) |
| `--gradient-primary` | `linear-gradient(135deg, #10B981, #06B6D4)` | Buttons, accents, logo glow |
| `--gradient-score-bar` | `linear-gradient(90deg, #EF4444, #F97316, #F59E0B, #84CC16, #10B981)` | Legend gradient bar |

### Typography

| Element | Font | Weight | Size | Line Height | Letter Spacing |
|---------|------|--------|------|-------------|----------------|
| H1 (page title) | Inter | 700 (Bold) | 28px | 1.2 | -0.02em |
| H2 (section title) | Inter | 600 (Semibold) | 20px | 1.3 | -0.01em |
| H3 (card title) | Inter | 600 (Semibold) | 16px | 1.4 | 0 |
| Body | Inter | 400 (Regular) | 14px | 1.5 | 0 |
| Body small | Inter | 400 (Regular) | 12px | 1.5 | 0.01em |
| Label | Inter | 500 (Medium) | 12px | 1.4 | 0.04em (uppercase) |
| Score number (gauge) | Inter | 700 (Bold) | 48px | 1.0 | -0.03em |
| Stat number | Inter | 600 (Semibold) | 24px | 1.2 | -0.02em |
| Button | Inter | 600 (Semibold) | 14px | 1.0 | 0.01em |

### Spacing & Layout

- **Base unit:** 4px
- **Border radius:** 12px (cards), 8px (buttons, inputs), 999px (pills/badges)
- **Desktop layout:** Full-screen map with floating overlay panels
- **Panel widths:** Detail panel = 420px, Legend = 240px, Header height = 64px
- **Shadows:** `0 8px 32px rgba(0, 0, 0, 0.4)` on floating panels
- **Grid:** No traditional grid — this is a map-first layout with overlaid UI

### Glassmorphism Recipe

All floating panels use this treatment:
```
background: rgba(17, 24, 39, 0.75);
backdrop-filter: blur(20px) saturate(150%);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 12px;
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
```

---

## Screen 1: Map View (Default / Home)

This is the primary screen. The entire viewport is a dark-themed satellite/vector map of Atlanta with colored building polygons overlaid. All UI is floating on top of the map.

### Layout (Desktop — 1440×900)

```
┌──────────────────────────────────────────────────────────┐
│ [Header Bar — full width, floating, glassmorphism]       │
│  🌿 Roofus    "1,247 rooftops scored"    [Filter] [?]   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                                                          │
│              FULL-SCREEN MAPBOX MAP                      │
│           (dark style, satellite optional)               │
│                                                          │
│     ┌─────┐   Buildings are colored polygons:            │
│     │ 78  │   Green = high score                         │
│     └─────┘   Amber = moderate                           │
│               Red = poor                                 │
│                                                          │
│                                                          │
│  ┌──────────────────┐                                    │
│  │ [Legend — bottom  │                                    │
│  │  left, floating]  │                                    │
│  │  0 ████████ 100   │                                    │
│  │  Poor → Excellent │                                    │
│  └──────────────────┘                                    │
└──────────────────────────────────────────────────────────┘
```

### Map Behavior

- **Base style:** `mapbox://styles/mapbox/dark-v11` — dark desaturated streets with subtle labels
- **Initial center:** Atlanta, GA (33.749, -84.388), zoom level 14
- **Building polygons:** Each building footprint is rendered as a filled polygon. Fill color is determined by the viability score using discrete steps (see color tokens above). Fill opacity: 0.70 at rest.
- **Building outlines:** 1px white outline at 15% opacity on all buildings. Grows to 2px emerald glow on hover.

### Hover State (Building)

When the cursor hovers over a building polygon:
1. The polygon fill opacity increases from 0.70 → 0.90
2. The outline changes to 2px `--accent-emerald` with a subtle outer glow (`0 0 8px rgba(16, 185, 129, 0.4)`)
3. A **tooltip** appears near the cursor (offset 12px above):

```
┌───────────────────────────┐
│ 📍 523 Auburn Ave NE      │
│ Score: 78 ●●●●●●●●○○      │
│ 4,500 sq ft · Commercial  │
└───────────────────────────┘
```
- Tooltip: glassmorphism background, `--text-primary` text, 12px rounded corners
- The colored dots `●` match the score color
- Appears with a 100ms fade-in, follows cursor with 16ms debounce

### Click State (Building)

Clicking a building:
1. Map smoothly flies/zooms to center the selected building (animated over 500ms, ease-in-out)
2. Selected building gets a persistent pulsing emerald outline (2px, subtle pulse animation: opacity 0.5 → 1.0 over 1.5s, infinite)
3. The **Detail Panel** slides in from the right edge (see Screen 2)
4. Other buildings dim slightly (opacity drops to 0.40) to focus attention

---

## Screen 2: Detail Panel (Sidebar)

Slides in from the right when a building is clicked. On desktop it overlays the right edge of the map (map stays visible behind it). On mobile it slides up from the bottom as a draggable sheet.

### Layout (Desktop — 420px wide, full height minus header)

```
┌─────────────────────────────────┐
│ ✕ Close                        │
│                                 │
│     ┌─────────────────┐        │
│     │                 │        │
│     │   SCORE GAUGE   │        │
│     │      78         │        │
│     │     /100        │        │
│     │                 │        │
│     └─────────────────┘        │
│   "Good Viability"             │
│                                 │
│ ─────────────────────────────  │
│                                 │
│ SCORE BREAKDOWN                 │
│                                 │
│ Roof Area           85         │
│ [████████████████░░░░░░] 4500sf│
│                                 │
│ Solar Exposure      84         │
│ [████████████████░░░░░░] 5.1GHI│
│                                 │
│ Zoning             100         │
│ [██████████████████████] C-1   │
│                                 │
│ Food Desert Impact  100        │
│ [██████████████████████] Yes   │
│                                 │
│ Building Age        65         │
│ [█████████████░░░░░░░░░] 1985  │
│                                 │
│ Vacancy Signal      45         │
│ [█████████░░░░░░░░░░░░░] Low   │
│                                 │
│ ─────────────────────────────  │
│                                 │
│ PROPERTY DETAILS                │
│ 📍 523 Auburn Ave NE           │
│ 🏢 Commercial · C-1 Zoning    │
│ 📐 4,500 sq ft roof area      │
│ 🏗️ Built 1985                  │
│                                 │
│ ─────────────────────────────  │
│                                 │
│ OWNER CONTACT INFO                 │
│ 👤 Peachtree Properties LLC        │
│ 📬 456 Spring St NW                │
│    Atlanta, GA 30303               │
│ 📧 info@peachtreeprops.com  [📋]   │
│ 📞 (404) 555-0142            [📋]  │
│                                     │
│  ℹ️ Contact info from public        │
│  Fulton County parcel records       │
│                                     │
└─────────────────────────────────────┘
```

### Component Details

#### Score Gauge (top of panel)
- **Size:** 160×160px centered in the panel
- **Shape:** SVG circular arc (270° sweep, open at the bottom)
- **Track:** 8px wide, `rgba(255,255,255,0.06)` (barely visible background arc)
- **Fill arc:** 8px wide, color matches score tier, rounded line caps
- **Animation:** On mount, the arc sweeps from 0° to the proportional angle over 800ms with an `ease-out` curve. The number counts up from 0 simultaneously.
- **Center text:** Score number (48px, bold, `--text-primary`), "/100" below it (14px, `--text-secondary`)
- **Glow:** The fill arc has a subtle drop shadow in its own color: `drop-shadow(0 0 6px [score-color])`
- **Label below gauge:** Text like "Good Viability" or "Excellent Viability" in the score's color, 16px semibold

#### Score Breakdown Bars
- **Layout:** Each factor is a row with: label (left), score number (right), then a full-width bar below
- **Bar:** 6px tall, rounded ends, background `rgba(255,255,255,0.06)`, fill color matches per-factor score tier
- **Bar animation:** Each bar fills from left to right on mount, staggered by 100ms per row (so they cascade down)
- **Sub-label:** Small text on the right below each bar showing the raw value (e.g., "4,500 sq ft", "5.1 GHI", "C-1", "Yes", "1985")
- **Spacing:** 16px between each factor row

#### Property Details Section
- **Section header:** "PROPERTY DETAILS" in uppercase label style (12px, medium, `--text-muted`, 0.04em letter-spacing)
- **Items:** Each line has an emoji icon + text in `--text-primary`, 14px regular
- **Spacing:** 8px between items, 24px section padding top

#### Owner Contact Info Section
- **Section header:** "OWNER CONTACT INFO" in uppercase label style
- Owner name: 16px, semibold, `--text-primary`
- Mailing address: 14px, `--text-secondary`
- **Email/Phone:** Displayed with copy buttons (📋).
- **Direct Message Area:** Inline textarea for quick messaging embedded directly in the panel.
- **Send button:** Gradient button labeled "Send Message".
- **Source attribution:** Small italic text: "Contact info from public Fulton County parcel records" in `--text-muted`, 11px

### Panel Animation
- **Enter:** Slides in from right, 350ms, `ease-out` (CSS transform: `translateX(100%)` → `translateX(0)`)
- **Exit:** Slides out to right, 250ms, `ease-in`
- **The map viewport adjusts** (pads right) so the selected building stays visible and isn't hidden behind the panel

### Mobile Behavior (< 768px)
- Panel becomes a **bottom sheet** that slides up from the bottom
- Initial height: 40% of viewport (shows gauge + score breakdown)
- Draggable handle bar at top (40px wide, 4px tall, rounded, `rgba(255,255,255,0.2)`)
- Can be dragged up to 90% viewport height to see full content
- Can be swiped down to dismiss
- Score gauge shrinks to 120×120px

---

- **Animation enter:** Fades in (opacity 0→1) + scales up (0.95→1.0), 250ms ease-out
- **Animation exit:** Fades out + scales down, 200ms ease-in

#### Header Area
- Close button (✕): top-right corner, 32×32px, `--text-muted`, hover → `--text-primary`
- Building icon (🌿) + title "Contact Building Owner" (H2 style)
- Building address in `--text-secondary`
- Small score badge: pill-shaped (rounded-full), score-colored background at 15% opacity, score-colored text, e.g., `78/100`

#### Form Fields
- **Label:** 12px, medium weight, `--text-secondary`, 8px margin-bottom
- **Input/Textarea:**
  - Background: `rgba(255, 255, 255, 0.04)`
  - Border: `1px solid rgba(255, 255, 255, 0.08)`
  - Border radius: 8px
  - Padding: 12px 16px
  - Text: 14px, `--text-primary`
  - Placeholder: `--text-muted`
  - **Focus state:** Border transitions to `--border-glow` (emerald at 30% opacity), subtle outer glow `0 0 0 3px rgba(16, 185, 129, 0.1)`
  - Transition: border-color 150ms ease
- **Textarea:** 120px min-height, resizable vertically
- **Required fields** marked with `*` in `--accent-emerald`
- **Spacing:** 20px between fields

#### Pre-filled Message
The message textarea is pre-populated with:
> "Hi [Owner Name], I'm interested in exploring the rooftop at [Address] for an urban agriculture project. The building scored [Score]/100 on our viability assessment. I'd love to discuss leasing opportunities. Would you be open to a conversation?"

User can edit this freely.

#### Submit Button
- Same style as "Contact Owner" button (gradient, full-width, 48px)
- **Loading state:** Text changes to "Sending...", a small spinner appears (16px, white, rotating), button is disabled with reduced opacity (0.7)
- **Transition:** 150ms ease

#### Success State (replaces form content)
After successful submission, the form content transitions to:
```
┌────────────────────────────┐
│                            │
│         ✅                 │
│   (animated checkmark)     │
│                            │
│   Message Sent!            │
│                            │
│   We've notified the owner │
│   of 523 Auburn Ave NE.    │
│   They'll receive your     │
│   message via email.       │
│                            │
│   ┌──────────────────────┐ │
│   │    Close              │ │
│   └──────────────────────┘ │
│                            │
└────────────────────────────┘
```
- Checkmark: animated SVG stroke-draw (green circle + check, 600ms)
- Text fades in after checkmark animation completes
- "Close" button: outlined style (transparent bg, 1px emerald border)

#### Error State
- Red banner appears above the submit button: `"Something went wrong. Please try again."` with a red background at 10% opacity, red text, 8px rounded
- Submit button returns to default state

---

## Screen 4: Header Bar

Floats at the top of the map view, always visible.

### Layout (Full width, 64px tall)

```
┌──────────────────────────────────────────────────────────────────┐
│  🌿 Roofus          │  1,247 scored · 312 high-potential   │ ⚙️  │
└──────────────────────────────────────────────────────────────────┘
```

### Details

- **Position:** Fixed, top 16px, left 16px, right 16px (16px inset from all edges)
- **Height:** 56px
- **Background:** Glassmorphism
- **Layout:** Flexbox, space-between, vertically centered

#### Left: Brand
- Leaf icon (🌿 or custom SVG) in `--accent-emerald`, 24px
- "Roofus" wordmark in 20px, bold, `--text-primary`, 8px gap from icon
- On hover, the leaf icon subtly rotates 15° (200ms ease)

#### Center: Stats
- Dynamic stats that update based on loaded data
- Format: `"1,247 scored · 312 high-potential"` in 13px, `--text-secondary`
- Numbers in `--text-primary` and semibold
- "high-potential" in `--accent-emerald`
- These numbers animate (count up) when the page first loads (800ms, ease-out)

#### Right: Controls
- **Filter button:** Pill-shaped, outlined, "Filters" with a sliders icon. Opens filter dropdown.
- **Info button:** Circle, 32px, `?` icon, opens an about/help modal

### Filter Dropdown (from Filter button)

```
┌──────────────────────────┐
│ SCORE RANGE              │
│ [====●==========] 0–100  │
│  Min: 40                 │
│                          │
│ BUILDING TYPE            │
│ ☑ Commercial             │
│ ☑ Industrial             │
│ ☐ Residential            │
│ ☑ Mixed-Use              │
│                          │
│ ROOF SIZE                │
│ [====●==========]        │
│  Min: 1,000 sq ft        │
│                          │
│ ☑ Food desert areas only │
│                          │
│ [Apply Filters]  [Reset] │
└──────────────────────────┘
```
- Glassmorphism panel, 280px wide, drops below the filter button
- Range sliders with emerald-colored track fill
- Checkbox items with custom styled checkboxes (emerald when checked)
- Apply: primary gradient button. Reset: text-only link.
- Opens with fade + slide-down (200ms)

---

## Screen 5: Legend (Floating)

Always visible on the map, bottom-left corner.

### Layout (240px wide, auto height)

```
┌────────────────────────────┐
│ VIABILITY SCORE            │
│                            │
│ [█████████████████████████]│
│  0    25    50    75   100 │
│                            │
│ ● Excellent (85-100)  142  │
│ ● Good (70-84)        298  │
│ ● Moderate (50-69)    412  │
│ ● Below Avg (30-49)   287  │
│ ● Poor (0-29)         108  │
│                            │
│ Total: 1,247 buildings     │
└────────────────────────────┘
```

### Details
- **Position:** Fixed, bottom 24px, left 16px
- **Background:** Glassmorphism
- **Gradient bar:** 8px tall, rounded, uses `--gradient-score-bar` (red → orange → amber → lime → emerald)
- **Tick labels:** 12px, `--text-muted`, evenly spaced below bar
- **Category list:** Each row has a colored circle (8px, matching score color), label, and count. 6px spacing between rows.
- **Counts** are right-aligned, `--text-secondary`, tabular-nums font feature
- **Total** at bottom in `--text-muted`, separated by a subtle divider line
- **Interactive:** Clicking a category row toggles that tier's visibility on the map (strikes through the label, dims the dot). This is a quick filter.

---

## Interaction Patterns

### Transitions & Timing

| Interaction | Duration | Easing | Property |
|---|---|---|---|
| Hover tooltip appear | 100ms | ease-out | opacity, transform |
| Building hover highlight | 150ms | ease | fill-opacity, stroke |
| Detail panel slide in | 350ms | ease-out | transform (translateX) |
| Detail panel slide out | 250ms | ease-in | transform (translateX) |
| Score gauge fill | 800ms | ease-out | stroke-dashoffset |
| Score number count-up | 800ms | ease-out | text content (JS) |
| Score bar fill | 500ms each, 100ms stagger | ease-out | width |
| Map fly-to on click | 500ms | ease-in-out | center, zoom |
| Button hover lift | 150ms | ease | transform, box-shadow |
| Copy-to-clipboard toast | 200ms in, 1.5s visible, 200ms out | ease | opacity |
| Stats count-up on load | 800ms | ease-out | text content (JS) |

### Cursor States
- **Default (over map):** Crosshair or default
- **Over a building polygon:** Pointer (hand)
- **Over UI elements:** Pointer
- **Dragging (mobile sheet):** Grab → Grabbing

### Keyboard Navigation
- `Escape` — close detail panel
- Map supports standard Mapbox keyboard controls (arrow keys to pan, +/- to zoom)

---

## Mobile Layout (< 768px)

### Map View
- Map takes full screen
- Header shrinks to 48px height, logo only (stats hidden), hamburger menu on right
- Legend collapses to a small pill showing just the gradient bar (tap to expand)

### Detail Panel → Bottom Sheet
```
┌──────────────────────────┐
│        ——                │  ← drag handle
│   SCORE GAUGE (120px)    │
│   78 / 100               │
│   "Good Viability"       │
│                          │
│   Score Breakdown...     │
│   (scroll for more)     │
│                          │
│   Owner: Peachtree Props │
│   📧 info@...  📞 (404)..│
└──────────────────────────┘
```
- Initial snap point: 40% viewport height
- Full snap point: 90% viewport height
- Dismiss: swipe below 20% or tap outside
- Rounded top corners (20px radius)
- Drag handle: 40×4px rounded bar, centered, `rgba(255,255,255,0.2)`


---

## Figma AI Prompt Suggestions

Use these as direct prompts when generating screens:

### Prompt 1: Map View
> "A dark-themed full-screen map application showing Atlanta, Georgia. Building footprints are overlaid as colored polygons — green for high scores, amber for moderate, red for poor. A glassmorphic floating header bar at the top reads '🌿 Roofus' with stats '1,247 scored · 312 high-potential'. A floating legend in the bottom-left shows a gradient color scale from 0 to 100. The design is premium, modern, dark mode with emerald green accents. Inter font throughout."

### Prompt 2: Detail Panel Open
> "Same dark map application, but now a 420px wide glassmorphic sidebar is open on the right. At the top is an animated circular score gauge showing 78/100 in emerald green. Below are 6 horizontal progress bars showing score breakdown: Roof Area 85, Solar Exposure 84, Zoning 100, Food Desert Impact 100, Building Age 65, Vacancy Signal 45. Each bar is colored by its score. Below is property info (address, sq ft, year built). At the bottom is an Owner Contact Info section showing owner name 'Peachtree Properties LLC', mailing address, email as a clickable cyan link with a small copy button, and phone number as a clickable cyan link with a copy button. Small attribution text: 'Contact info from public Fulton County parcel records'. Premium dark mode design, Inter font."

### Prompt 3: Mobile Bottom Sheet
> "A mobile phone screen (375px wide) showing a dark map with colored building polygons. A bottom sheet is dragged up to 40% of the screen showing a circular score gauge (78/100), score breakdown bars, and owner contact info with clickable email and phone links. A drag handle bar is at the top of the sheet. The header is minimal with just the Roofus leaf logo. Premium dark mode, glassmorphism, emerald green accents, Inter font."
