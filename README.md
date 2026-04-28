# Zigly Margin Intelligence — Working Prototype

**BTL × Zigly · Internal Demo · v0.1**

A working prototype of three coordinated agents — Dynamic Pricing, Private Label Recommender, and Bundle Agent — operating on real Zigly catalog data.

---

## What this is

A demo-grade prototype that proves the agent stack architecture works end-to-end on real-shaped data. Built in one session.

- **Real catalog**: 25 SKUs scraped from zigly.com (Applod, Zigly Lifestyle, Royal Canin, Pedigree, Farmina, Trixie, FOFOS, First Bark, Imaginelles, M-Pets)
- **Modeled costs**: Indian pet retail margin benchmarks applied per category (PL: 45–65%, premium imported: 18–25%, mass branded: 22–30%, mid-brand: 30–40%)
- **Modeled competitor data**: Realistic Amazon/Flipkart positioning patterns (not live scrapes — that's Phase 1)
- **Three agents, one shared policy layer**: pricing, PL recommender, bundle agent all read from the same data and respect the same guardrails

## What this is NOT

- Not a production system. No live API integrations. No ML models. No real scrapers.
- Not a finished product. This is a 1-day prototype to validate logic and demo the architecture.
- The cost numbers are educated estimates, not BTL/Zigly actuals. Replace with real cost master before any production decision.

---

## How to run

```bash
cd zigly_prototype
pip install streamlit pandas plotly
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## What's inside

| File | Purpose |
|---|---|
| `data.py` | Real Zigly SKU catalog (25 items), channel economics, shared policy layer |
| `agents.py` | Three agent implementations with full reasoning traces |
| `app.py` | Streamlit dashboard, 4 tabs, BTL dark editorial aesthetic |

---

## Demo script (15 min walkthrough)

### Tab 1 — Margin Sentinel
- "This is what merchandising would see every morning."
- Channel margin overview shows D2C is highest-margin (~45%), Amazon eaten by 15% commission.
- KPI row: 13/25 SKUs are private label, 13/25 win Amazon Buy Box.
- Top 10 margin opportunities chart shows where we're losing — almost all are branded SKUs where we don't own Buy Box.
- Guardrail status confirms no SKU is being recommended below the margin floor.

### Tab 2 — Pricing Agent
- Show the full table in **balanced** mode.
- Switch to **defensive** → prices nudge up, fewer Buy Box wins, margin protected.
- Switch to **aggressive** → undercut competitors, more Buy Box wins, some margin compression.
- **Drill into Royal Canin Maxi 4kg**: agent correctly identifies we cannot win Buy Box without breaking margin floor — refuses to chase. This is the "discipline" point: most automated repricers race to zero. Ours doesn't.
- **Drill into Applod 2kg**: agent already wins Buy Box — probes price up by 1.5% to find ceiling.
- Explain the parity logic: D2C public price = Amazon price (Amazon parity rule), but member price (logged-in only) is 5% lower — the legal workaround most DTC brands use.

### Tab 3 — Private Label Recommender
- Pick **Royal Canin Maxi 4kg**.
- Side-by-side card: Royal Canin ₹3,650 (low margin) vs Applod ₹2,239 (high margin).
- Customer saves ₹1,411 (39%). Margin uplift +33pp.
- Parity score 1.0 (same category, same sub-category, same pet).
- Agent recommends **active nudge** — full comparison widget at PDP + cart.
- Show the customer-facing nudge mock — what the user actually sees on the PDP.
- Portfolio view: forecast monthly margin uplift across all branded SKUs at 10K monthly PDP views.

### Tab 4 — Bundle Agent
- Default cart: Applod Chicken & Veg 4kg dry food.
- Bundle agent suggests Applod Dental Stix + Applod Wet Food (both PL — boosts margin).
- Framing: "Complete the meal — food + treats" (auto-detected from cart category).
- Discount math: 12% bundle discount, but net margin still ₹149 because PL margin is fat enough to absorb.
- AOV lift: +15%.
- Try adding **ZIG-RC-001** (Royal Canin) to cart — bundle agent now suggests Pedigree wet + Applod treats. Shows category-aware logic.

---

## Key design decisions (talk through these)

1. **One shared policy layer.** Every agent reads from the same margin floors, parity rules, and stock thresholds. Without this, the three agents would conflict (e.g., pricing drops a SKU's price, weakening the PL agent's pitch).

2. **Buy Box optimizer ≠ race to bottom.** When margin floor is breached, the agent consciously loses Buy Box. Most automated repricers don't have this discipline — they bleed margin until manual override.

3. **D2C ≤ Amazon (parity).** Hard-coded into the canonical pricing logic to avoid Amazon Buy Box suppression. Member-only loyalty discount on D2C is the legal workaround.

4. **PL agent only on D2C.** On Amazon you can't inject a "switch to Applod" widget — Amazon owns the surface. PL strategy on marketplaces becomes a sponsored ads + A+ content problem, not an agent decision.

5. **Reasoning traces on every decision.** Every recommendation shows why it fired. Critical for trust during rollout — merchandising won't approve agent decisions they can't audit.

---

## Honest gaps

What this prototype doesn't yet do (and what Phase 1 would add):

- ❌ Real Amazon SP-API / Flipkart Seller API integrations (read & write)
- ❌ Real competitor scrapers
- ❌ Real cost master ingestion (currently modeled)
- ❌ ML elasticity models (currently rule-based)
- ❌ Persistence layer (no DB — state resets each session)
- ❌ Multi-user / authentication
- ❌ Historical performance tracking
- ❌ Inventory allocation across channels
- ❌ A/B test infrastructure

These are deliberately out of scope for the prototype. The point is to validate the **shape** of the system before investing in production infra.

---

## Suggested next steps after demo

1. **Get real costs.** Ingest the actual Zigly cost master. Validate that the prototype's margin floors are right.
2. **Pick one agent to deepen.** Pricing has the highest leverage; PL has the easiest visual demo; bundle has the cleanest A/B test path. Pick one.
3. **Build the Margin Sentinel as v1 production.** Read-only dashboard, no automation. Get merchandising looking at it daily before you let any agent make decisions.
4. **Then automate one agent in shadow mode.** Logs decisions, doesn't execute. Measure agreement rate with human pricers.
5. **Then go live, on top 50 SKUs only.** Hard guardrails, kill switch, daily monitoring.

Total path to first agent live with real money behind it: ~6–8 weeks from green light.
