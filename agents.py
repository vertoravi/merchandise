"""
Three agents, one shared policy. Rule-based, fully transparent reasoning.
Every recommendation returns a `trace` so the dashboard can show WHY.
"""
from data import (
    CHANNEL_ECONOMICS, POLICY, channel_margin,
    get_sku, get_pl_equivalent, CATALOG,
)


# =========================================================================
# 1) PRICING AGENT
# =========================================================================
def pricing_recommendation(sku, mode: str = "balanced"):
    """
    Returns recommended prices per channel + reasoning trace.
    mode: 'defensive' (margin-first), 'balanced', 'aggressive' (volume-first)
    """
    trace = []
    floor_pct = POLICY["min_margin_pct_pl"] if sku.is_private_label else POLICY["min_margin_pct_branded"]

    # ---- Step 1: Compute canonical anchor price ----
    competitor_min = min(sku.competitor_amazon_lowest, sku.competitor_flipkart_lowest)
    if mode == "defensive":
        anchor = max(sku.current_d2c_price, competitor_min * 1.02)
        trace.append(f"Defensive mode: anchor = max(current, competitor×1.02) = ₹{anchor:,.0f}")
    elif mode == "aggressive":
        anchor = competitor_min - POLICY["buy_box_undercut_paise"]
        trace.append(f"Aggressive mode: undercut competitor lowest (₹{competitor_min:,.0f}) by ₹1 → ₹{anchor:,.0f}")
    else:  # balanced
        anchor = (competitor_min + sku.current_d2c_price) / 2
        trace.append(f"Balanced mode: anchor = midpoint of competitor & current → ₹{anchor:,.0f}")

    # ---- Step 2: Channel-specific recommendations ----
    recs = {}

    # AMAZON: Buy Box optimizer
    amz_rec, amz_trace = _amazon_buy_box(sku, anchor, floor_pct, mode)
    recs["amazon"] = amz_rec
    trace.extend(amz_trace)

    # FLIPKART: similar Buy Box logic
    flp_rec, flp_trace = _flipkart_logic(sku, anchor, floor_pct, mode)
    recs["flipkart"] = flp_rec
    trace.extend(flp_trace)

    # D2C: must be <= Amazon (parity), but loyalty-priced for members
    d2c_public = recs["amazon"]["price"]   # public price = same as Amazon
    d2c_member = d2c_public * 0.95           # 5% loyalty discount allowed (private)
    d2c_margin = channel_margin(d2c_public, sku.cost, "d2c")
    recs["d2c"] = {
        "price": d2c_public,
        "member_price": d2c_member,
        "margin_pct": d2c_margin["margin_pct"],
        "margin_abs": d2c_margin["margin_abs"],
        "current": sku.current_d2c_price,
        "delta": d2c_public - sku.current_d2c_price,
    }
    trace.append(f"D2C public = Amazon price (parity rule) = ₹{d2c_public:,.0f}; "
                 f"member price (logged-in only) = ₹{d2c_member:,.0f}")

    # ---- Step 3: Guardrail checks ----
    violations = []
    for ch, r in recs.items():
        if ch == "d2c":
            continue
        if r["price"] < sku.cost:
            violations.append(f"{ch.upper()}: price ₹{r['price']:,.0f} below cost ₹{sku.cost:,.0f}")
        if r["margin_pct"] < floor_pct:
            violations.append(
                f"{ch.upper()}: margin {r['margin_pct']*100:.1f}% below floor {floor_pct*100:.0f}%"
            )

    # Stock-driven adjustment
    if sku.stock < POLICY["low_stock_threshold"]:
        trace.append(f"⚠ Low stock ({sku.stock} units): hold prices firm; do not chase competitor down")

    # Daily change cap
    max_swing = sku.current_amazon_price * POLICY["max_daily_change_pct"]
    if abs(recs["amazon"]["price"] - sku.current_amazon_price) > max_swing:
        trace.append(
            f"⚠ Recommended Amazon swing exceeds {POLICY['max_daily_change_pct']*100:.0f}% daily cap; "
            f"will be staged across {2}–{3} days"
        )

    return {
        "sku_id": sku.sku_id,
        "mode": mode,
        "recommendations": recs,
        "trace": trace,
        "violations": violations,
        "anchor": anchor,
    }


def _amazon_buy_box(sku, anchor, floor_pct, mode):
    trace = []
    bb_low = sku.competitor_amazon_lowest

    if not sku.buy_box_eligible:
        trace.append("Amazon: NOT Buy Box eligible — fix fulfillment health before pricing")
        price = sku.current_amazon_price
    elif sku.is_buy_box_winner:
        # Probe up if we already win
        probe = sku.current_amazon_price * 1.015
        if probe < bb_low * 0.98:
            price = probe
            trace.append(f"Amazon: we own Buy Box; probe price up by 1.5% → ₹{price:,.0f}")
        else:
            price = sku.current_amazon_price
            trace.append("Amazon: we own Buy Box; hold (no headroom to probe)")
    else:
        # We don't own the box. Try to win it within margin floor.
        target = bb_low - POLICY["buy_box_undercut_paise"]
        margin = channel_margin(target, sku.cost, "amazon")
        if margin["margin_pct"] >= floor_pct:
            price = target
            trace.append(
                f"Amazon: undercut Buy Box winner by ₹1 → ₹{price:,.0f} "
                f"(margin {margin['margin_pct']*100:.1f}% ≥ floor {floor_pct*100:.0f}%) ✓"
            )
        else:
            # Cannot win profitably — hold at floor
            min_price = sku.cost / (1 - floor_pct - CHANNEL_ECONOMICS["amazon"]["commission_pct"]
                                       - CHANNEL_ECONOMICS["amazon"]["fulfillment_cost_pct"])
            price = max(min_price, sku.current_amazon_price)
            trace.append(
                f"Amazon: cannot win Buy Box without breaking margin floor; "
                f"hold at floor-aware price ₹{price:,.0f} (lose box consciously)"
            )

    margin = channel_margin(price, sku.cost, "amazon")
    return {
        "price": round(price, 0),
        "margin_pct": margin["margin_pct"],
        "margin_abs": margin["margin_abs"],
        "current": sku.current_amazon_price,
        "delta": round(price - sku.current_amazon_price, 0),
        "buy_box_target": bb_low,
        "wins_buy_box": sku.is_buy_box_winner or (price < bb_low),
    }, trace


def _flipkart_logic(sku, anchor, floor_pct, mode):
    trace = []
    fp_low = sku.competitor_flipkart_lowest
    target = max(fp_low - 1, anchor)
    margin = channel_margin(target, sku.cost, "flipkart")
    if margin["margin_pct"] < floor_pct:
        target = sku.current_flipkart_price
        trace.append(f"Flipkart: floor would be breached; hold at current ₹{target:,.0f}")
    else:
        trace.append(f"Flipkart: target ₹{target:,.0f} (margin {margin['margin_pct']*100:.1f}%)")

    margin = channel_margin(target, sku.cost, "flipkart")
    return {
        "price": round(target, 0),
        "margin_pct": margin["margin_pct"],
        "margin_abs": margin["margin_abs"],
        "current": sku.current_flipkart_price,
        "delta": round(target - sku.current_flipkart_price, 0),
    }, trace


# =========================================================================
# 2) PRIVATE LABEL RECOMMENDATION AGENT  (D2C only)
# =========================================================================
def pl_recommendation(branded_sku):
    """
    Given a branded SKU on a D2C PDP/cart, return PL nudge recommendation.
    Returns None if no viable PL alternative.
    """
    if branded_sku.is_private_label:
        return None
    pl = get_pl_equivalent(branded_sku.sku_id)
    if not pl:
        return None

    # Margin uplift if customer switches
    branded_margin = channel_margin(branded_sku.current_d2c_price, branded_sku.cost, "d2c")
    pl_margin = channel_margin(pl.current_d2c_price, pl.cost, "d2c")
    margin_uplift_abs = pl_margin["margin_abs"] - branded_margin["margin_abs"]
    margin_uplift_pct = pl_margin["margin_pct"] - branded_margin["margin_pct"]

    # Customer savings
    customer_saves = branded_sku.current_d2c_price - pl.current_d2c_price
    savings_pct = customer_saves / branded_sku.current_d2c_price

    # Parity score (heuristic): same category + same sub_category = 0.85; same pet adds 0.10
    parity = 0.0
    if branded_sku.category == pl.category:
        parity += 0.45
    if branded_sku.sub_category == pl.sub_category:
        parity += 0.40
    if branded_sku.pet == pl.pet or pl.pet == "both":
        parity += 0.15
    parity = min(parity, 1.0)

    # Nudge intensity decision
    if pl.stock < POLICY["low_stock_threshold"]:
        intensity = "none"
        reason = "PL stock low — do not surface alternative"
    elif parity < 0.70:
        intensity = "passive"
        reason = "Low parity — passive mention only ('Try Applod for similar nutrition')"
    elif savings_pct < 0.15:
        intensity = "passive"
        reason = "Savings <15% — not enough switch incentive for active nudge"
    elif margin_uplift_pct > 0.20:
        intensity = "active"
        reason = "High margin uplift + decent savings — full comparison widget at PDP+Cart"
    else:
        intensity = "moderate"
        reason = "PDP comparison widget; skip cart nudge"

    # Forecast switch rate (industry heuristic by intensity)
    switch_rate_forecast = {
        "none": 0.0,
        "passive": 0.04,
        "moderate": 0.18,
        "active": 0.30,
    }[intensity]

    return {
        "branded_sku": branded_sku.sku_id,
        "branded_name": branded_sku.name,
        "branded_price": branded_sku.current_d2c_price,
        "branded_margin_pct": branded_margin["margin_pct"],
        "pl_sku": pl.sku_id,
        "pl_name": pl.name,
        "pl_price": pl.current_d2c_price,
        "pl_margin_pct": pl_margin["margin_pct"],
        "customer_saves": customer_saves,
        "savings_pct": savings_pct,
        "margin_uplift_abs": margin_uplift_abs,
        "margin_uplift_pct": margin_uplift_pct,
        "parity_score": parity,
        "intensity": intensity,
        "reason": reason,
        "switch_rate_forecast": switch_rate_forecast,
        "expected_margin_lift_per_view": switch_rate_forecast * margin_uplift_abs,
    }


# =========================================================================
# 3) BUNDLE AGENT
# =========================================================================
def bundle_recommendation(cart_sku_ids: list, max_addons: int = 2):
    """
    Given current cart contents, generate bundle suggestions.
    Returns ranked list of bundle candidates with margin economics.
    """
    cart_skus = [get_sku(sid) for sid in cart_sku_ids if get_sku(sid)]
    if not cart_skus:
        return {"bundles": [], "trace": ["Empty cart"]}

    trace = [f"Cart: {len(cart_skus)} items, value ₹{sum(s.current_d2c_price for s in cart_skus):,.0f}"]

    # Aggregate co-purchase candidates from all cart items' bundle_affinity
    candidates = {}  # sku_id -> count of mentions
    for s in cart_skus:
        for aff in (s.bundle_affinity or []):
            if aff in cart_sku_ids:
                continue  # already in cart
            candidates[aff] = candidates.get(aff, 0) + 1

    if not candidates:
        return {"bundles": [], "trace": trace + ["No bundle candidates from co-purchase graph"]}

    # Score each candidate: affinity_count × margin × (1 if PL else 0.6) × stock_health
    scored = []
    for sku_id, freq in candidates.items():
        sku = get_sku(sku_id)
        if not sku or sku.stock < 10:
            continue
        margin_d2c = channel_margin(sku.current_d2c_price, sku.cost, "d2c")
        pl_boost = 1.4 if sku.is_private_label else 1.0
        stock_health = min(sku.stock / 200, 1.0)
        score = freq * margin_d2c["margin_abs"] * pl_boost * stock_health
        scored.append((sku, freq, margin_d2c, score))

    scored.sort(key=lambda x: -x[3])
    selected = scored[:max_addons]

    if not selected:
        return {"bundles": [], "trace": trace + ["No candidates passed stock/margin filters"]}

    # Build the bundle
    bundle_items = [s for s, _, _, _ in selected]
    bundle_subtotal = sum(s.current_d2c_price for s in bundle_items)
    cart_subtotal = sum(s.current_d2c_price for s in cart_skus)
    full_total = cart_subtotal + bundle_subtotal

    # Discount sized so it doesn't violate margin floor
    bundle_margin_abs = sum(channel_margin(s.current_d2c_price, s.cost, "d2c")["margin_abs"]
                            for s in bundle_items)
    max_discount_abs = bundle_margin_abs * 0.40   # cap discount at 40% of marginal margin
    discount_pct = min(POLICY["bundle_max_discount_pct"],
                       max(POLICY["bundle_min_discount_pct"],
                           max_discount_abs / bundle_subtotal))
    discount_abs = bundle_subtotal * discount_pct

    # Recompute net margin after discount
    net_addon_margin = bundle_margin_abs - discount_abs

    trace.append(f"Selected {len(bundle_items)} add-ons; bundle subtotal ₹{bundle_subtotal:,.0f}")
    trace.append(f"Discount: {discount_pct*100:.1f}% (₹{discount_abs:,.0f}) — within margin-safe band")
    trace.append(f"Net margin from add-ons: ₹{net_addon_margin:,.0f}")

    # Bundle reason / framing
    pet_types = set(s.pet for s in cart_skus + bundle_items)
    if "food" in [s.category for s in cart_skus] and any(s.category == "treats" for s in bundle_items):
        framing = "Complete the meal — food + treats"
    elif any(s.is_private_label for s in bundle_items):
        framing = "Save more with Applod & Zigly Lifestyle add-ons"
    else:
        framing = "Frequently bought together"

    return {
        "bundles": [{
            "addons": [{"sku_id": s.sku_id, "name": s.name, "price": s.current_d2c_price,
                        "is_pl": s.is_private_label} for s in bundle_items],
            "cart_subtotal": cart_subtotal,
            "addon_subtotal": bundle_subtotal,
            "discount_pct": discount_pct,
            "discount_abs": discount_abs,
            "bundle_total": full_total - discount_abs,
            "net_addon_margin": net_addon_margin,
            "framing": framing,
            "aov_lift_pct": (bundle_subtotal - discount_abs) / cart_subtotal,
        }],
        "trace": trace,
    }
