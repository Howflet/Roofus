# Roofus — Revenue & Profit Calculator (UI/UX Spec)

> Addendum to the main [UI/UX Spec](file:///home/kevon/.gemini/antigravity/brain/743c02d7-b237-4852-8183-e510892a1788/roofus_ui_ux_spec.md). Describes the revenue calculator feature for building owners and developers.

---

## Feature Concept

A **dual-perspective financial calculator** that answers two questions:

| Audience | Question It Answers |
|----------|-------------------|
| **Building Owner** | "How much could I earn by leasing my rooftop for urban agriculture?" |
| **Developer / Farmer** | "How much profit could I make by operating a greenhouse on this rooftop?" |

The calculator lives inside the **Detail Panel** as a tabbed section, and can also be expanded to a full-screen financial breakdown.

---

## Economics Model (Baked-In Defaults)

These are realistic defaults used in calculations. Users can adjust them via sliders.

### Building Owner Revenue Streams

| Revenue Stream | Default Value | Range | Source |
|---|---|---|---|
| Rooftop lease rate | $8/sq ft/year | $4–$18 | Atlanta commercial rooftop rates |
| Property value increase | 3.5% | 1–7% | Green roof studies (GSA, EPA) |
| Energy savings (cooling) | $0.45/sq ft/year | $0.20–$0.80 | Green roof insulation effect; savings calculated from Georgia Power commercial rate ($0.105/kWh) × estimated cooling reduction (~25% for green roof coverage) |
| Tax incentives | $2.50/sq ft (one-time) | $0–$5 | GA urban agriculture credits |

### Developer Revenue & Costs

| Item | Default Value | Range | Source / Rationale |
|---|---|---|---|
| **Revenue** | | | |
| Leafy greens yield | 8 lbs/sq ft/year | 5–12 | USDA greenhouse lettuce benchmarks |
| Herbs yield | 5 lbs/sq ft/year | 3–8 | Commercial herb greenhouse data |
| Microgreens yield | 12 lbs/sq ft/year | 8–20 | High-density tray growing |
| Leafy greens price | $4.50/lb | $3–$7 | Atlanta Farmers Market / wholesale |
| Herbs price | $18/lb | $12–$30 | Atlanta Farmers Market / retail |
| Microgreens price | $30/lb | $20–$50 | Atlanta restaurant wholesale |
| **Startup Costs** | | | |
| Greenhouse construction | $45/sq ft (one-time) | $25–$85 | Light commercial greenhouse |
| Structural reinforcement | $12/sq ft (one-time) | $5–$25 | Rooftop load-bearing upgrades |
| **Annual Operating Costs (Itemized)** | | | |
| ⚡ Electricity (HVAC, lighting) | $3.20/sq ft/year | $2–$5 | **Georgia Power** commercial rate: $0.105/kWh × ~30 kWh/sq ft/year for greenhouse climate control + supplemental lighting |
| 💧 Water (irrigation) | $1.80/sq ft/year | $1–$3 | **City of Atlanta Watershed** commercial rate: $10.77/CCF (~$0.0144/gal) × ~125 gal/sq ft/year for hydroponic systems |
| 🔥 Natural gas (heating) | $0.90/sq ft/year | $0.40–$1.50 | **Atlanta Gas Light** commercial rate: ~$1.05/therm × ~0.85 therms/sq ft/year (mild Atlanta winters reduce this significantly) |
| 👷 Labor | $5.50/sq ft/year | $3–$9 | 1 FTE per ~2,000 sq ft at Atlanta wages (~$18/hr) |
| 📦 Supplies & insurance | $2.60/sq ft/year | $1.50–$4 | Seeds, growing media, packaging, pest management, liability insurance |
| **Total operating costs** | **$14.00/sq ft/year** | **$7.90–$22.50** | **Sum of above** |
| Lease payment to owner | $8/sq ft/year | $4–$18 | Synced with Owner View lease rate |

### Crop Mix Presets

| Preset | Leafy Greens | Herbs | Microgreens | Avg Revenue/sq ft |
|--------|-------------|-------|-------------|-------------------|
| **Balanced** | 50% | 30% | 20% | ~$50/sq ft/year |
| **Premium** | 20% | 30% | 50% | ~$72/sq ft/year |
| **Volume** | 70% | 20% | 10% | ~$38/sq ft/year |
| **Custom** | User-defined | User-defined | User-defined | Calculated |

---

## Screen: Revenue Calculator (Inside Detail Panel)

Appears as a new section in the Detail Panel, below the score breakdown and above property/owner info. Can be expanded to a larger view.

### Tab Toggle

```
┌─────────────────────────────────────┐
│  [🏢 Owner View] [🌱 Developer View] │
└─────────────────────────────────────┘
```

- Two pill-shaped toggle buttons, side by side
- Active tab: filled with `--gradient-primary` (emerald→cyan), white text
- Inactive tab: transparent, `--text-secondary`, `1px solid rgba(255,255,255,0.08)` border
- Transition: 200ms ease, background color slides between tabs
- Default: Owner View (since we're showing this to building owners initially)

---

### Owner View Tab

```
┌─────────────────────────────────────┐
│  [🏢 Owner View] [🌱 Developer View] │
├─────────────────────────────────────┤
│                                     │
│  ESTIMATED ANNUAL REVENUE           │
│                                     │
│         $36,000                     │
│         ─────────                   │
│         per year                    │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Lease Income        $36,000   │  │
│  │ ███████████████████████████   │  │
│  │                               │  │
│  │ Energy Savings       $2,025   │  │
│  │ ██░░░░░░░░░░░░░░░░░░░░░░░   │  │
│  │                               │  │
│  │ Tax Incentives      $11,250   │  │
│  │ ████████░░░░░░░░░░░░░░░░░   │  │
│  │ (one-time)                    │  │
│  └───────────────────────────────┘  │
│                                     │
│  10-YEAR PROJECTION                 │
│  ┌───────────────────────────────┐  │
│  │     $                         │  │
│  │  400k ┤              ╱──      │  │
│  │  300k ┤          ╱──╱         │  │
│  │  200k ┤      ╱──╱             │  │
│  │  100k ┤  ╱──╱                 │  │
│  │     0 ┤──                     │  │
│  │       └──┬──┬──┬──┬──┬──     │  │
│  │       Y1  Y3  Y5  Y7  Y10    │  │
│  └───────────────────────────────┘  │
│                                     │
│  PROPERTY VALUE IMPACT              │
│  Current Est. Value    $850,000     │
│  Green Roof Premium      +3.5%     │
│  New Est. Value        $879,750     │
│  Value Increase        +$29,750     │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  ADJUST ASSUMPTIONS                 │
│                                     │
│  Lease Rate ($/sq ft/yr)            │
│  [════════●══════════] $8.00        │
│                                     │
│  Property Value ($)                 │
│  [════●══════════════] $850,000     │
│                                     │
│  Value Increase (%)                 │
│  [══════●════════════] 3.5%         │
│                                     │
└─────────────────────────────────────┘
```

#### Hero Revenue Number
- **Size:** 36px, bold, `--text-primary`
- **Color:** `--accent-emerald` 
- **Animation:** Counts up from $0 on mount (800ms, ease-out)
- **"per year"** label: 14px, `--text-secondary`
- Recalculates live as sliders are adjusted (300ms debounce, smooth number transition)

#### Revenue Breakdown Bars
- Same visual style as score breakdown bars from the main detail panel
- Each bar shows the revenue stream name (left), dollar amount (right), and a proportional bar below
- Bars are colored emerald for recurring, cyan for one-time
- "one-time" tag: small pill badge, `--accent-cyan` at 15% opacity

#### 10-Year Projection Chart
- **Type:** Area chart with gradient fill
- **Line:** 2px, `--accent-emerald`
- **Area fill:** Gradient from `rgba(16, 185, 129, 0.3)` at top to `transparent` at bottom
- **Dots:** 6px circles at each year marker, emerald fill, white 2px border
- **Hover:** Tooltip shows exact value at that year
- **Axes:** `--text-muted`, thin lines, minimal
- **Includes:** Cumulative lease income + energy savings (compound line)
- **Animation:** Line draws from left to right on mount (1000ms, ease-out)

#### Property Value Impact
- 2×2 info grid with labels and values
- "Value Increase" number in `--accent-emerald`, bold
- Subtle `+` prefix on positive values

#### Assumption Sliders
- Expandable section (collapsed by default, "Adjust Assumptions ▾" toggle)
- Each slider:
  - Label above (12px, `--text-secondary`)
  - Value readout on the right (14px, `--text-primary`, tabular-nums)
  - Track: 4px tall, rounded, `rgba(255,255,255,0.08)` background
  - Fill: `--gradient-primary`
  - Thumb: 20px circle, white, `box-shadow: 0 2px 8px rgba(0,0,0,0.3)`
  - Thumb hover: scale(1.15), glow
- Changes recalculate all numbers in real-time (no submit button)

---

### Developer View Tab

```
┌─────────────────────────────────────┐
│  [🏢 Owner View] [🌱 Developer View] │
├─────────────────────────────────────┤
│                                     │
│  PROJECTED ANNUAL PROFIT            │
│                                     │
│        $118,800                     │
│        ──────────                   │
│        per year (after Year 1)      │
│                                     │
│  ROI: 24 months                     │
│  [████████████░░░░░░░░░░░░] 24mo    │
│  Break-even in 2 years              │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  CROP MIX                           │
│  [Balanced ▾]  or customize:        │
│                                     │
│  🥬 Leafy Greens    50%             │
│  [══════════●════════════]          │
│  2,250 sq ft · $81,000 rev          │
│                                     │
│  🌿 Herbs            30%            │
│  [══════●════════════════]          │
│  1,350 sq ft · $121,500 rev         │
│                                     │
│  🌱 Microgreens      20%            │
│  [════●══════════════════]          │
│  900 sq ft · $324,000 rev           │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  P&L BREAKDOWN                      │
│                                     │
│  Revenue                            │
│  ┌─────────────────────────────┐    │
│  │ Leafy Greens      $81,000  ░│    │
│  │ Herbs            $121,500  ░│    │
│  │ Microgreens      $324,000  ░│    │
│  │ ─────────────────────────── │    │
│  │ Total Revenue    $526,500   │    │
│  └─────────────────────────────┘    │
│                                     │
│  Annual Costs                       │
│  ┌─────────────────────────────┐    │
│  │ Lease to Owner    -$36,000  ░│   │
│  │ ⚡ Electricity     -$14,400  ░│   │
│  │ 💧 Water            -$8,100  ░│   │
│  │ 🔥 Natural Gas      -$4,050  ░│   │
│  │ 👷 Labor           -$24,750  ░│   │
│  │ 📦 Supplies/Ins    -$11,700  ░│   │
│  │ ─────────────────────────── │    │
│  │ Total Costs       -$99,000  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ NET ANNUAL PROFIT           │    │
│  │ $427,500                    │    │
│  │ Margin: 81%                 │    │
│  └─────────────────────────────┘    │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  STARTUP COSTS                      │
│  Greenhouse Build     $202,500      │
│  Structural Work       $54,000      │
│  ──────────────────────────         │
│  Total Upfront        $256,500      │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  5-YEAR CASH FLOW                   │
│  ┌───────────────────────────────┐  │
│  │        ▓▓▓  ▓▓▓  ▓▓▓  ▓▓▓   │  │
│  │        ▓▓▓  ▓▓▓  ▓▓▓  ▓▓▓   │  │
│  │   ░░░  ▓▓▓  ▓▓▓  ▓▓▓  ▓▓▓   │  │
│  │───░░░──▓▓▓──▓▓▓──▓▓▓──▓▓▓──  │  │
│  │   ░░░                         │  │
│  │   Y1    Y2   Y3   Y4   Y5    │  │
│  │   ▬ Revenue  ▬ Costs  ▬ Net  │  │
│  └───────────────────────────────┘  │
│                                     │
│  ADJUST ASSUMPTIONS ▾               │
│  (Construction $/sqft, operating    │
│   costs, crop prices, lease rate)   │
│                                     │
└─────────────────────────────────────┘
```

#### Hero Profit Number
- Same styling as Owner View hero number
- Shows annual net profit after year 1 (post-startup)
- Color: `--accent-emerald` if positive, `--score-poor` (red) if negative
- Animates on mount and on slider changes

#### ROI Progress Bar
- Full-width bar showing months to break-even
- Track: `rgba(255,255,255,0.06)`
- Fill: gradient from `--score-poor` (red) → `--score-moderate` (amber) → `--accent-emerald` (green)
- The fill stops at the break-even point
- Animated fill on mount (600ms)
- Label: "Break-even in X years" — prominent if < 3 years (green badge), cautionary if > 5 years (amber badge)

#### Crop Mix Section
- **Preset dropdown:** "Balanced", "Premium", "Volume", "Custom" — styled as a glassmorphic dropdown with score-colored borders
- **Three crop sliders:** Each shows crop emoji, name, percentage
  - Sliders are interlocked: adjusting one redistributes the others proportionally (always sum to 100%)
  - Below each slider: calculated area (sq ft) and revenue contribution
  - Revenue numbers update in real-time
- **Visual proportions:** A small stacked horizontal bar shows the crop mix split visually (green / teal / lime segments)

#### P&L Breakdown
- **Revenue section:** Light green-tinted card (`rgba(16, 185, 129, 0.05)` background)
  - Each line item: name left, amount right, small proportional bar
  - Total row: bold, separated by divider
- **Costs section:** Light red-tinted card (`rgba(239, 68, 68, 0.05)` background)
  - Negative amounts in `--score-poor` color
  - Total row: bold
- **Net Profit box:** Highlighted card with `--border-glow` border
  - Large profit number in `--accent-emerald`
  - "Margin: X%" badge — green if > 50%, amber if 20-50%, red if < 20%

#### Startup Costs
- Simple list with labels left, amounts right
- Total highlighted with a top border divider
- All amounts in `--text-primary`

#### 5-Year Cash Flow Chart
- **Type:** Grouped bar chart (3 bars per year: revenue, costs, net)
- **Colors:** Revenue = `--accent-emerald` at 60% opacity, Costs = `--score-poor` at 60% opacity, Net = `--accent-cyan`
- **Year 1** shows net below zero line (red bar going down — startup costs eat profit)
- **Years 2–5** show growing positive net
- **Hover:** Tooltip with exact numbers
- **Animation:** Bars grow upward from baseline on mount, staggered by 80ms per bar

#### Assumption Sliders (Expandable)
Same visual style as Owner View, but with grouped slider sections:

**Startup Costs**
- Construction cost ($/sq ft): $25–$85, default $45
- Structural reinforcement ($/sq ft): $5–$25, default $12

**Utility & Operating Costs** — each with source label in `--text-muted`
- ⚡ Electricity ($/sq ft/yr): $2–$5, default $3.20 — _"Georgia Power commercial rate"_
- 💧 Water ($/sq ft/yr): $1–$3, default $1.80 — _"Atlanta Watershed commercial rate"_
- 🔥 Natural gas ($/sq ft/yr): $0.40–$1.50, default $0.90 — _"Atlanta Gas Light commercial rate"_
- 👷 Labor ($/sq ft/yr): $3–$9, default $5.50
- 📦 Supplies & insurance ($/sq ft/yr): $1.50–$4, default $2.60
- Running total shown below sliders: `"Total operating: $14.00/sq ft/yr"` — updates live

**Crop Prices**
- Leafy greens price ($/lb): $3–$7, default $4.50
- Herbs price ($/lb): $12–$30, default $18
- Microgreens price ($/lb): $20–$50, default $30

**Lease**
- Lease rate ($/sq ft/yr): $4–$18, default $8 (synced with Owner View)

---

## Expanded Financial View (Full-Screen)

An "Expand ↗" button in the top-right of the calculator section opens a full-screen modal with richer financial analysis.

### Layout (Desktop — full viewport, dark overlay)

```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Map          Revenue Calculator         ✕     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  523 Auburn Ave NE · 4,500 sq ft · Score: 78/100        │
│                                                          │
│ ┌────────────────────────┐  ┌──────────────────────────┐│
│ │    OWNER PERSPECTIVE   │  │  DEVELOPER PERSPECTIVE   ││
│ │                        │  │                          ││
│ │  Annual Revenue        │  │  Annual Profit           ││
│ │  $38,025               │  │  $427,500                ││
│ │                        │  │                          ││
│ │  10-Year Total         │  │  5-Year ROI              ││
│ │  $391,500              │  │  832%                    ││
│ │                        │  │                          ││
│ │  [Revenue chart]       │  │  [P&L stacked chart]     ││
│ │                        │  │                          ││
│ │  [Property value       │  │  [Crop mix donut chart]  ││
│ │   comparison]          │  │                          ││
│ │                        │  │  [Cash flow waterfall]   ││
│ └────────────────────────┘  └──────────────────────────┘│
│                                                          │
│ ┌──────────────────────────────────────────────────────┐ │
│ │  SENSITIVITY ANALYSIS                                │ │
│ │                                                      │ │
│ │  What if lease rates change?                         │ │
│ │  $4/sqft → $24,300 profit  |  $12/sqft → $18,300    │ │
│ │  ─────●──────────────────── (current: $8)            │ │
│ │                                                      │ │
│ │  What if crop prices drop 20%?                       │ │
│ │  Profit: $342,000 (still 66% margin)                 │ │
│ │  Break-even: 28 months (vs. 24 baseline)             │ │
│ └──────────────────────────────────────────────────────┘ │
│                                                          │
│          [📄 Download Report (PDF)]                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Key Elements

#### Side-by-Side Comparison
- Owner and Developer perspectives shown as two equal-width cards
- Each has their hero metrics and charts
- Visually demonstrates the win-win nature of the deal

#### Sensitivity Analysis Section
- Shows how profit changes under different assumptions
- Interactive slider lets users explore "what if" scenarios
- Color-coded outcomes: green = still profitable, amber = tight margins, red = loss

#### Crop Mix Donut Chart (Developer Side)
- SVG donut chart showing percentage allocation by crop
- Segments colored: Leafy greens = `#84CC16`, Herbs = `#10B981`, Microgreens = `#06B6D4`
- Center text: total revenue/sq ft
- Hover on segment: shows that crop's revenue contribution

#### Download Report Button
- Secondary style: outlined, `--accent-cyan` border and text
- Generates a simple PDF summary (stretch goal)
- Icon: document icon from Lucide

---

## Mobile Adaptation

### In-Panel Calculator (Mobile)
- Tab toggle stays at full width
- Charts shrink but remain readable (min-height: 160px)
- Sliders get larger touch targets (thumb: 28px)
- P&L breakdown stacks revenue and costs vertically instead of side-by-side

### Full-Screen View (Mobile)
- Owner and Developer cards stack vertically (no side-by-side)
- Charts are full-width
- Sensitivity sliders are full-width
- Scroll to navigate between sections

---

## Animations & Micro-Interactions

| Element | Animation | Duration | Trigger |
|---------|-----------|----------|---------|
| Hero number count-up | Numeric interpolation from $0 | 800ms ease-out | On mount / slider change |
| Revenue bars fill | Width grows from 0% | 500ms ease-out, 80ms stagger | On mount |
| ROI progress bar | Fill from left | 600ms ease-out | On mount |
| Area chart draw | SVG path draws left to right | 1000ms ease-out | On mount |
| Bar chart bars | Grow from baseline | 500ms ease-out, 80ms stagger | On mount |
| Donut chart | Segments grow from 0° | 800ms ease-out | On mount |
| Slider value change | Number smoothly transitions | 200ms ease | On drag |
| Tab switch | Content cross-fades | 250ms ease | On click |
| Expand to full-screen | Scale + fade transition | 300ms ease-out | On click |
| Crop slider interlock | Other sliders smoothly adjust | 200ms ease | On drag |

---

## Figma AI Prompt Suggestions

### Prompt: Owner Revenue Calculator
> "A dark glassmorphic sidebar panel showing a financial calculator for building owners. At the top is a tab toggle between '🏢 Owner View' (active, emerald gradient) and '🌱 Developer View' (inactive). Below is a large emerald-green number '$36,000 per year'. Then three horizontal bars showing revenue breakdown: Lease Income $36,000 (long emerald bar), Energy Savings $2,025 (short bar), Tax Incentives $11,250 (medium cyan bar, tagged 'one-time'). Below is a 10-year projection area chart with emerald gradient fill. Then a Property Value Impact section showing +$29,750 increase. At the bottom are adjustment sliders for lease rate and property value. Dark mode, glassmorphism, Inter font, premium fintech aesthetic."

### Prompt: Developer Profit Calculator
> "A dark glassmorphic sidebar panel showing a profit calculator for urban agriculture developers. Tab toggle shows '🌱 Developer View' active. Hero number shows '$427,500 per year' in emerald green. Below is an ROI progress bar showing '24 months to break-even'. Then a crop mix section with three interlocked sliders for Leafy Greens (50%), Herbs (30%), Microgreens (20%), each showing allocated square footage and revenue. Below is a P&L breakdown: Revenue card (green tint) listing three crop revenues totaling $526,500, Costs card (red tint) showing lease and operating costs of $99,000, and a highlighted Net Profit card showing $427,500 with 81% margin badge. A 5-year grouped bar chart shows cash flow with Year 1 negative (startup costs). Dark mode, premium fintech look."

### Prompt: Full-Screen Financial Comparison
> "A full-screen dark modal showing a side-by-side financial comparison. Left card: 'Owner Perspective' with $38,025 annual revenue, 10-year projection line chart, and property value comparison. Right card: 'Developer Perspective' with $427,500 annual profit, 832% 5-year ROI, crop mix donut chart, and cash flow waterfall chart. Below both cards is a 'Sensitivity Analysis' section with interactive sliders showing how profit changes under different assumptions. Address bar at top shows '523 Auburn Ave NE · 4,500 sq ft · Score: 78/100'. A 'Download Report' button at bottom. Dark mode, glassmorphism, emerald/cyan accents, premium dashboard aesthetic."
