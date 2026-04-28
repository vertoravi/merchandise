"""
Zigly Margin Intelligence — Internal Demo Dashboard
Built by BTL for Zigly leadership review.

Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from data import (
    CATALOG, get_catalog, get_sku, CHANNEL_ECONOMICS, POLICY, channel_margin,
)
from agents import pricing_recommendation, pl_recommendation, bundle_recommendation


# =========================================================================
# PAGE CONFIG + GLOBAL STYLES
# =========================================================================
st.set_page_config(
    page_title="Zigly Margin Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0a0a0a;
    color: #e8e6e0;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1400px;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #f4f1ea !important;
}

h1 { font-size: 2.4rem !important; }
h2 { font-size: 1.6rem !important; margin-top: 2rem !important; }
h3 { font-size: 1.15rem !important; color: #d4b97a !important; }

.mono, code, pre {
    font-family: 'DM Mono', monospace !important;
}

/* Sidebar / Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #2a2a2a;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #888 !important;
    padding: 12px 28px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #d4b97a !important;
    border-bottom: 2px solid #d4b97a !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #141414;
    border: 1px solid #222;
    padding: 18px 20px;
    border-radius: 2px;
}
[data-testid="stMetricLabel"] {
    color: #888 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="stMetricValue"] {
    color: #f4f1ea !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.7rem !important;
}

/* Buttons */
.stButton > button {
    background: #d4b97a;
    color: #0a0a0a;
    border: none;
    border-radius: 2px;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.78rem;
    padding: 10px 20px;
}
.stButton > button:hover {
    background: #e8cc8a;
    color: #0a0a0a;
}

/* Selectbox / inputs */
.stSelectbox label, .stRadio label, .stMultiSelect label {
    color: #888 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* Custom card */
.bt-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    padding: 24px;
    border-radius: 2px;
    margin-bottom: 16px;
}
.bt-card-accent {
    background: linear-gradient(135deg, #1a1610 0%, #141414 100%);
    border: 1px solid #d4b97a40;
}
.bt-tag {
    display: inline-block;
    padding: 3px 10px;
    background: #d4b97a20;
    color: #d4b97a;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-radius: 2px;
    margin-right: 6px;
}
.bt-tag-pl {
    background: #4a8a6520;
    color: #6dbf94;
}
.bt-tag-warn {
    background: #d44d3320;
    color: #e8745c;
}
.bt-trace {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #aaa;
    line-height: 1.7;
    background: #0e0e0e;
    border-left: 2px solid #d4b97a;
    padding: 12px 16px;
    margin: 8px 0;
}
.bt-divider {
    height: 1px;
    background: linear-gradient(90deg, #d4b97a 0%, transparent 60%);
    margin: 32px 0 16px 0;
}
.bt-stat-row {
    display: flex;
    gap: 32px;
    padding: 16px 0;
    border-bottom: 1px solid #1f1f1f;
}
.bt-stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.bt-stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    color: #f4f1ea;
    font-weight: 700;
}

/* Dataframe styling */
.stDataFrame {
    background: #141414;
}

/* Radio horizontal */
div[role="radiogroup"] {
    gap: 8px;
}
div[role="radiogroup"] label {
    background: #141414;
    border: 1px solid #2a2a2a;
    padding: 8px 16px;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================================
# HEADER
# =========================================================================
col_h1, col_h2 = st.columns([3, 2])
with col_h1:
    st.markdown(
        "<div style='font-family: DM Mono; font-size: 0.72rem; color: #d4b97a; "
        "letter-spacing: 0.15em; text-transform: uppercase;'>BTL × ZIGLY · INTERNAL DEMO</div>",
        unsafe_allow_html=True
    )
    st.markdown("# Margin Intelligence")
    st.markdown(
        "<div style='color:#888; font-size: 0.95rem; margin-top: -8px;'>"
        "Three coordinated agents. One shared policy layer. "
        "Real catalog (Applod, Zigly Lifestyle, Royal Canin, Pedigree, Trixie).</div>",
        unsafe_allow_html=True
    )
with col_h2:
    st.markdown(
        "<div style='text-align: right; font-family: DM Mono; font-size: 0.75rem; "
        "color: #666; letter-spacing: 0.08em; padding-top: 24px;'>"
        f"CATALOG: {len(CATALOG)} SKUs · CHANNELS: 3<br>"
        "MODE: DEMO · DATA: ZIGLY.COM (APR 2026)"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("<div class='bt-divider'></div>", unsafe_allow_html=True)


# =========================================================================
# TABS
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Margin Sentinel",
    "Pricing Agent",
    "Private Label Recommender",
    "Bundle Agent",
])


# -------------------------------------------------------------------------
# TAB 1: MARGIN SENTINEL (overview dashboard)
# -------------------------------------------------------------------------
with tab1:
    df = pd.DataFrame(get_catalog())

    # Channel-level margin overview
    st.markdown("### Channel margin overview")

    rows = []
    for ch in ["d2c", "amazon", "flipkart"]:
        price_col = f"current_{ch}_price" if ch != "d2c" else "current_d2c_price"
        margins = []
        revenue = 0
        for sku in CATALOG:
            p = getattr(sku, price_col)
            m = channel_margin(p, sku.cost, ch)
            margins.append(m["margin_pct"])
            revenue += p
        rows.append({
            "Channel": CHANNEL_ECONOMICS[ch]["label"],
            "Avg margin %": f"{sum(margins)/len(margins)*100:.1f}%",
            "Revenue (catalog snapshot)": f"₹{revenue:,.0f}",
            "Min margin SKU %": f"{min(margins)*100:.1f}%",
        })

    cmargin_df = pd.DataFrame(rows)
    st.dataframe(
        cmargin_df, use_container_width=True, hide_index=True,
        column_config={col: st.column_config.TextColumn(col) for col in cmargin_df.columns}
    )

    st.markdown("<div class='bt-divider'></div>", unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    pl_count = sum(1 for s in CATALOG if s.is_private_label)
    bb_wins = sum(1 for s in CATALOG if s.is_buy_box_winner)
    low_stock = sum(1 for s in CATALOG if s.stock < POLICY["low_stock_threshold"])
    avg_pl_margin = sum(channel_margin(s.current_d2c_price, s.cost, "d2c")["margin_pct"]
                        for s in CATALOG if s.is_private_label) / max(pl_count, 1)

    with k1: st.metric("PL SKUs", f"{pl_count} / {len(CATALOG)}")
    with k2: st.metric("Buy Box wins (Amazon)", f"{bb_wins} / {len(CATALOG)}")
    with k3: st.metric("Low-stock SKUs", low_stock)
    with k4: st.metric("Avg PL margin (D2C)", f"{avg_pl_margin*100:.1f}%")

    # Margin opportunity bar chart
    st.markdown("### Top 10 margin opportunities (Amazon Buy Box)")

    opps = []
    for sku in CATALOG:
        if sku.is_buy_box_winner:
            continue
        rec = pricing_recommendation(sku, mode="balanced")
        cur_m = channel_margin(sku.current_amazon_price, sku.cost, "amazon")["margin_abs"]
        new_m = rec["recommendations"]["amazon"]["margin_abs"]
        delta = new_m - cur_m
        opps.append({
            "sku": sku.sku_id,
            "name": sku.name[:40] + ("…" if len(sku.name) > 40 else ""),
            "delta_per_unit": delta,
            "margin_pct_now": cur_m / sku.current_amazon_price * 100,
            "margin_pct_new": new_m / rec["recommendations"]["amazon"]["price"] * 100,
            "wins_box": rec["recommendations"]["amazon"]["wins_buy_box"],
        })

    opps.sort(key=lambda x: -x["delta_per_unit"])
    top_opps = opps[:10]

    if top_opps:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[o["delta_per_unit"] for o in top_opps],
            y=[o["name"] for o in top_opps],
            orientation="h",
            marker=dict(color="#d4b97a", line=dict(color="#a08855", width=0)),
            text=[f"₹{o['delta_per_unit']:+.0f}" for o in top_opps],
            textposition="outside",
            hovertemplate="%{y}<br>Δ margin/unit: %{x:.0f}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
            font=dict(family="DM Mono", color="#aaa", size=11),
            height=400, margin=dict(l=10, r=40, t=20, b=20),
            xaxis=dict(gridcolor="#1f1f1f", zeroline=False, title=""),
            yaxis=dict(autorange="reversed", title=""),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No improvement opportunities flagged — every SKU already winning Buy Box.")

    # Guardrail violations panel
    st.markdown("### Guardrail status")
    violations = []
    for sku in CATALOG:
        rec = pricing_recommendation(sku, mode="balanced")
        if rec["violations"]:
            for v in rec["violations"]:
                violations.append({"SKU": sku.sku_id, "Name": sku.name[:50], "Violation": v})

    if violations:
        st.dataframe(pd.DataFrame(violations), use_container_width=True, hide_index=True)
    else:
        st.markdown(
            "<div class='bt-card bt-card-accent'><span class='bt-tag'>OK</span> "
            "No guardrail violations across catalog. All recommendations within margin floors and parity rules.</div>",
            unsafe_allow_html=True
        )


# -------------------------------------------------------------------------
# TAB 2: PRICING AGENT
# -------------------------------------------------------------------------
with tab2:
    st.markdown("### Pricing recommendations")

    cmode1, cmode2 = st.columns([2, 3])
    with cmode1:
        mode = st.radio("Mode", ["defensive", "balanced", "aggressive"],
                        index=1, horizontal=True, key="price_mode",
                        help="Defensive: protect margin. Aggressive: chase Buy Box / volume.")
    with cmode2:
        st.markdown(
            "<div style='color:#888; font-family:DM Mono; font-size:0.78rem; padding-top:24px;'>"
            "All recommendations respect parity (D2C ≤ Amazon), margin floors, and stock health."
            "</div>", unsafe_allow_html=True
        )

    # Build rec table
    rows = []
    for sku in CATALOG:
        rec = pricing_recommendation(sku, mode=mode)
        amz = rec["recommendations"]["amazon"]
        flp = rec["recommendations"]["flipkart"]
        d2c = rec["recommendations"]["d2c"]
        rows.append({
            "_sku_obj": sku,
            "_rec": rec,
            "SKU": sku.sku_id,
            "Name": sku.name[:55],
            "PL": "✓" if sku.is_private_label else "",
            "Stock": sku.stock,
            "D2C now": f"₹{sku.current_d2c_price:,.0f}",
            "D2C rec": f"₹{d2c['price']:,.0f}",
            "Amz now": f"₹{sku.current_amazon_price:,.0f}",
            "Amz rec": f"₹{amz['price']:,.0f}",
            "Amz Δ": f"₹{amz['delta']:+.0f}",
            "Amz margin": f"{amz['margin_pct']*100:.1f}%",
            "Buy Box": "WIN" if amz["wins_buy_box"] else "—",
            "Flp rec": f"₹{flp['price']:,.0f}",
            "Issues": "⚠" if rec["violations"] else "",
        })

    display_df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])

    st.dataframe(
        display_df, use_container_width=True, hide_index=True, height=420
    )

    st.markdown("### Drill-down: reasoning trace")
    sku_choice = st.selectbox(
        "Select SKU",
        options=[s.sku_id for s in CATALOG],
        format_func=lambda x: f"{x} — {get_sku(x).name[:60]}",
    )

    if sku_choice:
        sku = get_sku(sku_choice)
        rec = pricing_recommendation(sku, mode=mode)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("D2C → recommended", f"₹{rec['recommendations']['d2c']['price']:,.0f}",
                      delta=f"₹{rec['recommendations']['d2c']['delta']:+.0f} vs current")
        with c2:
            amz = rec["recommendations"]["amazon"]
            st.metric("Amazon → recommended", f"₹{amz['price']:,.0f}",
                      delta=f"₹{amz['delta']:+.0f} vs current")
        with c3:
            flp = rec["recommendations"]["flipkart"]
            st.metric("Flipkart → recommended", f"₹{flp['price']:,.0f}",
                      delta=f"₹{flp['delta']:+.0f} vs current")

        st.markdown("**Reasoning trace**")
        trace_html = "<div class='bt-trace'>"
        for i, t in enumerate(rec["trace"], 1):
            trace_html += f"[{i:02d}] {t}<br>"
        trace_html += "</div>"
        st.markdown(trace_html, unsafe_allow_html=True)

        if rec["violations"]:
            st.markdown("**Guardrail violations**")
            for v in rec["violations"]:
                st.markdown(f"<span class='bt-tag bt-tag-warn'>⚠ {v}</span>", unsafe_allow_html=True)


# -------------------------------------------------------------------------
# TAB 3: PRIVATE LABEL RECOMMENDER
# -------------------------------------------------------------------------
with tab3:
    st.markdown("### Customer journey simulator")
    st.markdown(
        "<div style='color:#888; font-size:0.9rem;'>"
        "Pick a branded SKU. The agent decides whether — and how aggressively — to nudge "
        "toward the Applod or Zigly Lifestyle equivalent on the D2C surface."
        "</div>", unsafe_allow_html=True
    )

    branded_skus = [s for s in CATALOG if not s.is_private_label and s.pl_equivalent_id]

    cpl1, cpl2 = st.columns([1, 1])
    with cpl1:
        chosen = st.selectbox(
            "Branded SKU on PDP",
            options=[s.sku_id for s in branded_skus],
            format_func=lambda x: f"{x} — {get_sku(x).name[:55]}",
        )

    if chosen:
        branded = get_sku(chosen)
        pl_rec = pl_recommendation(branded)

        if not pl_rec:
            st.warning("No PL recommendation for this SKU.")
        else:
            # Side-by-side comparison
            st.markdown("<div class='bt-divider'></div>", unsafe_allow_html=True)

            colb, colpl = st.columns(2)
            with colb:
                st.markdown(f"<div class='bt-card'><span class='bt-tag'>BRANDED</span> "
                            f"<h3 style='margin-top:8px;'>{branded.name}</h3>"
                            f"<div class='bt-stat-row'><div><div class='bt-stat-label'>Price</div>"
                            f"<div class='bt-stat-value'>₹{branded.current_d2c_price:,.0f}</div></div>"
                            f"<div><div class='bt-stat-label'>Margin</div>"
                            f"<div class='bt-stat-value'>{pl_rec['branded_margin_pct']*100:.1f}%</div></div></div>"
                            f"</div>", unsafe_allow_html=True)
            with colpl:
                pl = get_sku(pl_rec["pl_sku"])
                st.markdown(f"<div class='bt-card bt-card-accent'><span class='bt-tag bt-tag-pl'>PRIVATE LABEL</span> "
                            f"<h3 style='margin-top:8px;'>{pl.name}</h3>"
                            f"<div class='bt-stat-row'><div><div class='bt-stat-label'>Price</div>"
                            f"<div class='bt-stat-value'>₹{pl.current_d2c_price:,.0f}</div></div>"
                            f"<div><div class='bt-stat-label'>Margin</div>"
                            f"<div class='bt-stat-value'>{pl_rec['pl_margin_pct']*100:.1f}%</div></div></div>"
                            f"</div>", unsafe_allow_html=True)

            # Decision metrics
            dm1, dm2, dm3, dm4 = st.columns(4)
            with dm1:
                st.metric("Customer saves", f"₹{pl_rec['customer_saves']:,.0f}",
                          delta=f"{pl_rec['savings_pct']*100:.0f}%")
            with dm2:
                st.metric("Margin uplift", f"+{pl_rec['margin_uplift_pct']*100:.0f} pp",
                          delta=f"₹{pl_rec['margin_uplift_abs']:.0f}/unit")
            with dm3:
                st.metric("Parity score", f"{pl_rec['parity_score']:.2f}")
            with dm4:
                st.metric("Forecast switch rate", f"{pl_rec['switch_rate_forecast']*100:.0f}%")

            # Agent decision
            intensity_color = {
                "none": "bt-tag-warn", "passive": "bt-tag",
                "moderate": "bt-tag", "active": "bt-tag-pl"
            }
            st.markdown(
                f"<div class='bt-card'><span class='bt-tag {intensity_color.get(pl_rec['intensity'], '')}'>"
                f"NUDGE: {pl_rec['intensity'].upper()}</span><br><br>"
                f"<div style='color:#ccc; font-size:0.95rem;'>{pl_rec['reason']}</div></div>",
                unsafe_allow_html=True
            )

            # What the customer sees (mock surface)
            if pl_rec["intensity"] in ("moderate", "active"):
                st.markdown("**Customer-facing nudge (PDP surface preview)**")
                st.markdown(
                    f"<div class='bt-card bt-card-accent'>"
                    f"<div style='color:#d4b97a; font-family:DM Mono; font-size:0.78rem; "
                    f"letter-spacing:0.08em; text-transform:uppercase;'>"
                    f"Save ₹{pl_rec['customer_saves']:,.0f} with {pl.brand}</div>"
                    f"<h3 style='margin:6px 0 8px 0;'>{pl.name}</h3>"
                    f"<div style='color:#aaa; font-size:0.9rem;'>"
                    f"Same {branded.sub_category} for your {branded.pet}. "
                    f"Made in India. Available in stock.</div>"
                    f"<div style='margin-top:14px;'>"
                    f"<span style='color:#888; text-decoration:line-through; font-size:0.95rem;'>₹{branded.current_d2c_price:,.0f}</span> "
                    f"<span style='color:#f4f1ea; font-size:1.4rem; font-weight:700; "
                    f"font-family:Syne; margin-left:8px;'>₹{pl.current_d2c_price:,.0f}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

            # Aggregate impact (if applied across all branded views)
            st.markdown("<div class='bt-divider'></div>", unsafe_allow_html=True)
            st.markdown("### Portfolio-level forecast")

            agg_rows = []
            total_lift = 0
            for b in branded_skus:
                r = pl_recommendation(b)
                if r:
                    agg_rows.append({
                        "Branded SKU": b.sku_id,
                        "Name": b.name[:45],
                        "Intensity": r["intensity"],
                        "Switch rate": f"{r['switch_rate_forecast']*100:.0f}%",
                        "₹ margin lift / view": f"₹{r['expected_margin_lift_per_view']:.0f}",
                    })
                    total_lift += r["expected_margin_lift_per_view"]
            if agg_rows:
                st.dataframe(pd.DataFrame(agg_rows), use_container_width=True, hide_index=True)
                st.markdown(
                    f"<div style='color:#d4b97a; font-family:DM Mono; font-size:0.85rem;'>"
                    f"Sum of expected margin lift per branded PDP view: ₹{total_lift:,.1f}<br>"
                    f"At ~10,000 monthly branded PDP views, monthly margin uplift potential ≈ ₹{total_lift*10000:,.0f}"
                    f"</div>", unsafe_allow_html=True
                )


# -------------------------------------------------------------------------
# TAB 4: BUNDLE AGENT
# -------------------------------------------------------------------------
with tab4:
    st.markdown("### Cart simulator")
    st.markdown(
        "<div style='color:#888; font-size:0.9rem;'>"
        "Add items to cart. Bundle agent generates contextually relevant add-ons "
        "from the SKU co-purchase graph, ranked by margin × PL preference × stock health."
        "</div>", unsafe_allow_html=True
    )

    cart_choice = st.multiselect(
        "Build a cart",
        options=[s.sku_id for s in CATALOG],
        default=["ZIG-APL-001"],   # default to a popular Applod food
        format_func=lambda x: f"{x} — {get_sku(x).name[:55]}",
    )

    if cart_choice:
        # Cart summary
        cart_skus = [get_sku(s) for s in cart_choice]
        cart_total = sum(s.current_d2c_price for s in cart_skus)
        cart_margin = sum(channel_margin(s.current_d2c_price, s.cost, "d2c")["margin_abs"]
                          for s in cart_skus)

        cb1, cb2, cb3 = st.columns(3)
        with cb1: st.metric("Cart items", len(cart_skus))
        with cb2: st.metric("Cart subtotal", f"₹{cart_total:,.0f}")
        with cb3: st.metric("Cart margin", f"₹{cart_margin:,.0f}",
                            delta=f"{cart_margin/cart_total*100:.1f}%")

        result = bundle_recommendation(cart_choice, max_addons=2)

        st.markdown("<div class='bt-divider'></div>", unsafe_allow_html=True)

        if not result["bundles"]:
            st.warning("No bundle recommendations for this cart.")
            st.markdown("<div class='bt-trace'>" + "<br>".join(result["trace"]) + "</div>",
                        unsafe_allow_html=True)
        else:
            for bundle in result["bundles"]:
                st.markdown(f"### {bundle['framing']}")

                # Render addons
                for addon in bundle["addons"]:
                    pl_tag = "<span class='bt-tag bt-tag-pl'>PL</span>" if addon["is_pl"] else "<span class='bt-tag'>BRANDED</span>"
                    st.markdown(
                        f"<div class='bt-card'>{pl_tag} "
                        f"<span style='color:#f4f1ea; font-weight:600;'>{addon['name']}</span> "
                        f"<span style='color:#d4b97a; float:right; font-family:DM Mono;'>"
                        f"₹{addon['price']:,.0f}</span></div>",
                        unsafe_allow_html=True
                    )

                # Bundle math
                st.markdown(
                    f"<div class='bt-card bt-card-accent'>"
                    f"<div class='bt-stat-row' style='border:none;'>"
                    f"<div><div class='bt-stat-label'>Cart + add-ons</div>"
                    f"<div class='bt-stat-value'>₹{bundle['cart_subtotal'] + bundle['addon_subtotal']:,.0f}</div></div>"
                    f"<div><div class='bt-stat-label'>Bundle discount</div>"
                    f"<div class='bt-stat-value' style='color:#6dbf94;'>−₹{bundle['discount_abs']:,.0f}</div></div>"
                    f"<div><div class='bt-stat-label'>Customer pays</div>"
                    f"<div class='bt-stat-value'>₹{bundle['bundle_total']:,.0f}</div></div>"
                    f"<div><div class='bt-stat-label'>Net add-on margin</div>"
                    f"<div class='bt-stat-value' style='color:#d4b97a;'>₹{bundle['net_addon_margin']:,.0f}</div></div>"
                    f"<div><div class='bt-stat-label'>AOV lift</div>"
                    f"<div class='bt-stat-value'>+{bundle['aov_lift_pct']*100:.0f}%</div></div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

                # Reasoning
                st.markdown("**Reasoning trace**")
                trace_html = "<div class='bt-trace'>"
                for i, t in enumerate(result["trace"], 1):
                    trace_html += f"[{i:02d}] {t}<br>"
                trace_html += "</div>"
                st.markdown(trace_html, unsafe_allow_html=True)


# =========================================================================
# FOOTER
# =========================================================================
st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='color:#444; font-family:DM Mono; font-size:0.7rem; "
    "letter-spacing:0.1em; text-transform:uppercase; text-align:center; "
    "border-top:1px solid #1a1a1a; padding-top:24px;'>"
    "BTL × ZIGLY · Margin Intelligence Prototype · "
    "Demo-grade · Real catalog, modeled costs &amp; competitor data"
    "</div>",
    unsafe_allow_html=True
)
