
# Roofus — Research Brief: Demand Response, Data Centers & the Georgia Grid

> Prepared as background reading for the Cox urban-agriculture hackathon. Everything here is sourced; **[VERIFIED]** = pulled from a primary/news source, **[ANALYSIS]** = our own reasoning connecting facts to the project. Use it to write your own pitch — don't read it verbatim.
> Last updated: 2026-06-16.

---

## TL;DR (the story in five sentences)
1. Georgia Power just got approval to add **~8,500 MW** of new capacity over six years — roughly a **50% increase** — and says **~80% of that growth is from data centers**. [VERIFIED]
2. Building that much generation is slow, costs **$16.3B to build** (and an estimated **$50–60B to customers** over decades), and is politically contested. [VERIFIED]
3. The fastest, cheapest alternative to building power plants is **demand response** — paying customers to cut or shift load at peak — which acts like a "virtual power plant" (VPP). [VERIFIED]
4. Georgia Power's commercial demand-response tariff is **CL-1 (Curtailable Load)**: ≥200 kW reduction, 75% of capacity value paid as bill credits, 30-min event notice. It opened for enrollment **Jan 1, 2025**. [VERIFIED]
5. Roofus turns idle apartment rooftops into flexible, controllable load (greenhouse lighting/HVAC + AC cycling) — exactly the kind of distributed capacity the grid needs as data centers boom. [ANALYSIS]

---

## 1. Georgia's data-center load crisis (the "why now")

- Georgia Power's **2025 Integrated Resource Plan (IRP)**, approved by the Public Service Commission on **July 15, 2025**, projects **~8,500 MW of load growth over six years** — up from a 6,600 MW estimate in 2023 and just **400 MW estimated in 2022**. The forecast has exploded in three years. [VERIFIED]
- Company officials estimate **~80% of the projected increase over the next decade is tied to new data centers**. [VERIFIED]
- The buildout is described as **one of the biggest in the U.S. to meet AI-driven electricity demand** — roughly a **50% capacity increase**. Construction cost **~$16.3B**; PSC staff estimate customers pay **$50–60B** over coming decades (interest + guaranteed utility profit). [VERIFIED]
- **Georgia is the #4 AI data-center hub globally**; metro Atlanta is one of the hottest data-center markets in the country. [VERIFIED]
- Side effect: people living near data centers have seen power bills rise sharply (a 2025 Bloomberg analysis cited up to **267% higher** over five years in some areas). [VERIFIED]

> **Your hook:** the energy problem behind your project isn't hypothetical — it's the single biggest issue in Georgia's utility planning right now, and the utility itself is saying so out loud.

## 2. Why demand response = capacity (the concept that makes your project matter)

- **Core idea [VERIFIED concept]:** every kW a utility can get a customer to *not* draw during a peak is a kW it doesn't have to *build*. Reducing/shifting demand at the right moment is, to the grid, equivalent to adding a power plant — but faster and cheaper.
- A coordinated fleet of these flexible loads is a **Virtual Power Plant (VPP)**.
- **Scale, nationally (so you can say "this is proven, not sci-fi"):** [VERIFIED]
  - U.S. DOE estimates current VPP capacity at **30–60 GW**.
  - **California** leads with **42+ GW** of VPP capacity enrolled (as of March 2026); its Demand-Side Grid Support program alone hit **~1,145 MW** by Oct 2025.
  - **Massachusetts** (National Grid "ConnectedSolutions"): **227 MW** from thermostats, batteries, and C&I demand response.
  - **Texas** (ERCOT ADER pilot): expanding from **80 MW to 160 MW**.
  - **38 states + DC** took **105 policy actions** on VPPs / DER aggregation in 2024 — a "pivotal year."
- RMI has explicitly framed VPPs as a way for the U.S. to **"win the AI race"** by absorbing data-center load growth without building everything new. [VERIFIED]

## 3. Georgia Power's CL-1 tariff — exact mechanics [VERIFIED, from the tariff itself]

| Feature | Detail |
|---|---|
| Program | **Curtailable Load Rider "CL-1"**, effective Jan 2025 |
| Who | Qualifying **Commercial & Industrial** customers |
| **Minimum** | Customer agrees to provide **at least 200 kW of demand reduction** |
| How it works | Customer sets a **Firm Demand Level (FDL)**; during a Demand Response Event their measured demand can't exceed the FDL |
| Notice | Company gives **at least 30 minutes** before each event |
| Payment | Monthly bill credits = **75% of the capacity value** provided over the contract |
| Admin charge | **$120/month** (plus any extra metering the customer must fund) |
| Term | **6-year** agreement, auto-renewing |
| Penalties | Compliance incentive + termination fees if you fail to curtail when called |
| Not eligible | FPA, Electric Arc Furnace, DPEC, DER-DRC, and TOU-Supplier Choice customers |

### ⚠️ The critical finding for your thesis [VERIFIED + ANALYSIS]
The CL-1 tariff is written **per customer**: one customer, one Firm Demand Level, one agreement, **≥200 kW**. **The tariff contains no language about aggregating multiple separate accounts/owners** to reach the 200 kW minimum. That has two big implications:

- **Big single sites qualify directly.** A large complex like **532 Cleveland Ave SW** — whose greenhouse load alone is ~1,700 kW — easily clears 200 kW on its own and could sign a CL-1 agreement directly. ✅
- **Small scattered complexes (different owners) do NOT obviously qualify under CL-1 as written.** Pooling ten small buildings into one 200 kW bundle would require a **third-party aggregator / VPP arrangement that CL-1 itself doesn't describe.** ❗

### Why aggregation isn't automatic in Georgia [ANALYSIS — verify on a call]
The federal rule that forces utilities to let third parties aggregate small resources into wholesale markets (**FERC Order 2222**) applies to organized wholesale markets (RTOs/ISOs). **Georgia is NOT in an organized market** — Georgia Power is a vertically integrated, regulated monopoly in the Southeast. So aggregation of small sites would depend on **Georgia Power's own programs**, not an automatic federal right. This is the single most important thing to confirm with them.

## 4. How Roofus fits — two honest paths [ANALYSIS]

| Path | Who | CL-1 fit | Risk |
|---|---|---|---|
| **A. Anchor sites** | Big complexes (e.g., 532 Cleveland) whose flexible greenhouse + HVAC load alone clears 200 kW | Direct CL-1 enrollment | Low — works under the tariff as written |
| **B. Aggregated fleet** | Many small complexes pooled to reach 200 kW | Needs an aggregator/VPP structure GA Power must allow | Higher — depends on a program that may not exist yet |

- **The flexible-load insight:** a greenhouse *adds* load (~1,700 kW at 532 Cleveland — bigger than the building itself), but if the lights run **off-peak (overnight)** and can **shed on 30-min notice**, that load *helps* the grid instead of straining it. The grid's problem is the **peak**, not total energy. [ANALYSIS]
- **The "add-on" confirmation:** demand response stacks **on top of** the complex's existing commercial (PLM) rate — it's extra revenue, not a replacement. [VERIFIED via your call]

## 5. Honest caveats (so you don't get caught)
- **Don't claim you solve the 8,500 MW gap.** You're a **scalable model** for distributed demand response — "a small but replicable drop." [ANALYSIS]
- **Aggregation across owners is unproven under current GA tariffs** — present Path A (anchor sites) as the solid case and Path B (fleet) as the growth vision. [ANALYSIS]
- **The greenhouse must be operated as a flexible load** for the grid benefit to be real; a dumb always-on greenhouse would just make the peak worse. [ANALYSIS]
- **CL-1 has teeth:** 6-year term, $120/mo admin, penalties for failing to curtail. It's a real commercial commitment, not free money. [VERIFIED]

---

## Sources
- [Georgia utility projects 'extraordinary' load growth — Renewable Energy World](https://www.renewableenergyworld.com/news/georgia-utility-projects-extraordinary-load-growth-in-newest-plan-to-satisfy-data-centers/)
- [Georgia Power Integrated Resource Plan (official)](https://www.georgiapower.com/about/company/filings/irp.html)
- [Georgia Power 2025 IRP (PDF)](https://www.georgiapower.com/content/dam/georgia-power/pdfs/company-pdfs/2025-Integrated-Resource-Plan.pdf)
- [PSC approves major generation expansion for data centers — Perkins Coie](https://perkinscoie.com/insights/blog/georgia-public-service-commission-approves-georgia-powers-major-generation-expansion)
- [Georgia regulators approve massive grid expansion — Georgia Recorder](https://georgiarecorder.com/2025/12/19/georgia-regulators-approve-massive-power-grid-expansion-to-serve-data-centers/)
- [Georgia utility regulators boost capacity for AI data centers — Fortune](https://fortune.com/2025/12/20/georgia-utility-regulators-power-capacity-boost-ai-data-center-demand/)
- [How the Atlanta area became a hot data center market — GovTech](https://www.govtech.com/products/how-the-atlanta-area-became-the-hot-data-center-market)
- [CL-1 Curtailable Load Rider tariff (PDF)](https://www.georgiapower.com/content/dam/georgia-power/pdfs/business-pdfs/cl-1_final.pdf)
- [Real Time Pricing Day-Ahead tariff RTP-DA-12 (PDF)](https://www.georgiapower.com/content/dam/georgia-power/pdfs/business-pdfs/tariffs/2025/rtp-da-12.pdf)
- [Demand Response in Georgia toolkit — Drawdown Georgia](https://info.drawdownga.org/demand-response-georgia-toolkit)
- [Grid-scale VPPs are here — RMI](https://rmi.org/grid-scale-virtual-power-plants-are-here-have-utilities-noticed/)
- [How VPPs can help the US win the AI race — RMI](https://rmi.org/how-virtual-power-plants-can-help-the-united-states-win-the-ai-race/)
- [2024 a pivotal year for VPP policy — Utility Dive](https://www.utilitydive.com/news/virtual-power-plants-policy-der-aggregations/739970/)
- [As energy demand rises, states turn to VPPs — Inside Climate News](https://insideclimatenews.org/news/04062026/inside-clean-energy-virtual-power-plants-role-in-transition-away-from-fossil-fuels/)
- [AI data center boom and rising energy bills — CBS News](https://www.cbsnews.com/news/how-ai-driven-data-center-boom-leading-to-skyrocketing-energy-bills/)
