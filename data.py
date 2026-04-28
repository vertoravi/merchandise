"""
Zigly Margin Intelligence — Real Catalog
Sourced from zigly.com (April 2026 scrape).
Costs are MODELED based on Indian pet retail benchmarks:
  - Premium imported branded (Royal Canin, Acana, Orijen): 18-25% gross margin
  - Mass branded (Pedigree, Whiskas, Sheba): 22-30% gross margin
  - Mid-brand (Trixie, FOFOS, Kong): 30-40% gross margin
  - Private label (Applod, Zigly, Zigly Lifestyle): 45-65% gross margin
Competitor prices are MODELED off realistic Amazon/Flipkart positioning patterns.
"""
from dataclasses import dataclass, asdict
from typing import Optional
import random

random.seed(42)  # reproducible competitor noise


@dataclass
class SKU:
    sku_id: str
    name: str
    brand: str
    category: str           # food, treats, toys, grooming, accessories
    sub_category: str
    pet: str                # dog, cat, both
    is_private_label: bool
    mrp: float              # rupees
    cost: float             # landed cost
    current_d2c_price: float
    current_amazon_price: float
    current_flipkart_price: float
    competitor_amazon_lowest: float   # lowest competing seller on Amazon
    competitor_flipkart_lowest: float
    stock: int
    buy_box_eligible: bool
    is_buy_box_winner: bool
    pl_equivalent_id: Optional[str] = None   # for branded SKUs, the PL alternative
    bundle_affinity: Optional[list] = None   # SKUs that co-purchase well


# ------------------------------------------------------------------
# Real Zigly SKUs (verified via scrape Apr 2026)
# ------------------------------------------------------------------
CATALOG = [
    # ---------- DOG FOOD: PRIVATE LABEL (Applod) ----------
    SKU("ZIG-APL-001",
        "Applod Chicken & Vegetables Dry Dog Food (Adult) - 2kg",
        "Applod", "food", "dry-food", "dog", True,
        mrp=1499, cost=720,
        current_d2c_price=1199, current_amazon_price=1249, current_flipkart_price=1229,
        competitor_amazon_lowest=1199, competitor_flipkart_lowest=1219,
        stock=420, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-005", "ZIG-APL-007", "ZIG-ZL-001"]),

    SKU("ZIG-APL-002",
        "Applod Chicken & Vegetables Dry Dog Food (Adult) - 4kg",
        "Applod", "food", "dry-food", "dog", True,
        mrp=2799, cost=1280,
        current_d2c_price=2239, current_amazon_price=2349, current_flipkart_price=2299,
        competitor_amazon_lowest=2299, competitor_flipkart_lowest=2289,
        stock=180, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-005", "ZIG-APL-008"]),

    SKU("ZIG-APL-003",
        "Applod Chicken & Vegetables Dry Dog Food (Puppy) - 2kg",
        "Applod", "food", "puppy-food", "dog", True,
        mrp=1599, cost=780,
        current_d2c_price=1280, current_amazon_price=1329, current_flipkart_price=1299,
        competitor_amazon_lowest=1299, competitor_flipkart_lowest=1289,
        stock=210, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-006", "ZIG-APL-007"]),

    SKU("ZIG-APL-004",
        "Applod Chicken Pilaf Fresh Dog Food - 300g",
        "Applod", "food", "fresh-food", "dog", True,
        mrp=299, cost=125,
        current_d2c_price=254, current_amazon_price=275, current_flipkart_price=269,
        competitor_amazon_lowest=265, competitor_flipkart_lowest=259,
        stock=95, buy_box_eligible=True, is_buy_box_winner=False,
        bundle_affinity=["ZIG-APL-001", "ZIG-APL-008"]),

    SKU("ZIG-APL-005",
        "Applod Chicken & Veggies Wet Dog Food - 85g",
        "Applod", "food", "wet-food", "dog", True,
        mrp=99, cost=38,
        current_d2c_price=84, current_amazon_price=89, current_flipkart_price=87,
        competitor_amazon_lowest=85, competitor_flipkart_lowest=85,
        stock=1100, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-001", "ZIG-APL-002"]),

    SKU("ZIG-APL-006",
        "Applod Chicken Paste Wet Puppy Food - 85g",
        "Applod", "food", "wet-food", "dog", True,
        mrp=99, cost=42,
        current_d2c_price=89, current_amazon_price=95, current_flipkart_price=92,
        competitor_amazon_lowest=89, competitor_flipkart_lowest=89,
        stock=540, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-003"]),

    SKU("ZIG-APL-007",
        "Applod Chicken Bone Broth - 150ml",
        "Applod", "food", "supplements", "both", True,
        mrp=199, cost=68,
        current_d2c_price=199, current_amazon_price=215, current_flipkart_price=209,
        competitor_amazon_lowest=199, competitor_flipkart_lowest=199,
        stock=720, buy_box_eligible=True, is_buy_box_winner=False,
        bundle_affinity=["ZIG-APL-001", "ZIG-APL-002", "ZIG-APL-003"]),

    SKU("ZIG-APL-008",
        "Applod Dental Stix Chicken - 220g",
        "Applod", "treats", "dental", "dog", True,
        mrp=349, cost=125,
        current_d2c_price=296, current_amazon_price=315, current_flipkart_price=305,
        competitor_amazon_lowest=299, competitor_flipkart_lowest=295,
        stock=380, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-001", "ZIG-APL-002", "ZIG-APL-009"]),

    SKU("ZIG-APL-009",
        "Applod Crunch-a-Licious Chicken & Peanut Butter Biscuits - 800g",
        "Applod", "treats", "biscuits", "dog", True,
        mrp=599, cost=215,
        current_d2c_price=509, current_amazon_price=549, current_flipkart_price=529,
        competitor_amazon_lowest=519, competitor_flipkart_lowest=515,
        stock=210, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-008"]),

    SKU("ZIG-APL-010",
        "Applod Real Chicken Dog Biscuit - 500g",
        "Applod", "treats", "biscuits", "dog", True,
        mrp=399, cost=140,
        current_d2c_price=339, current_amazon_price=365, current_flipkart_price=355,
        competitor_amazon_lowest=349, competitor_flipkart_lowest=345,
        stock=290, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-001"]),

    # ---------- DOG FOOD: BRANDED ----------
    SKU("ZIG-RC-001",
        "Royal Canin Maxi Adult Dry Dog Food - 4kg",
        "Royal Canin", "food", "dry-food", "dog", False,
        mrp=4290, cost=3290,
        current_d2c_price=3650, current_amazon_price=3690, current_flipkart_price=3699,
        competitor_amazon_lowest=3590, competitor_flipkart_lowest=3650,
        stock=85, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-002",
        bundle_affinity=["ZIG-RC-002", "ZIG-APL-008"]),

    SKU("ZIG-RC-002",
        "Royal Canin Maxi Adult Wet Dog Food - 140g",
        "Royal Canin", "food", "wet-food", "dog", False,
        mrp=359, cost=235,
        current_d2c_price=305, current_amazon_price=315, current_flipkart_price=312,
        competitor_amazon_lowest=299, competitor_flipkart_lowest=305,
        stock=240, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-005",
        bundle_affinity=["ZIG-RC-001"]),

    SKU("ZIG-RC-003",
        "Royal Canin Maxi Adult 5+ Dry Dog Food - 4kg",
        "Royal Canin", "food", "dry-food", "dog", False,
        mrp=4490, cost=3450,
        current_d2c_price=3815, current_amazon_price=3849, current_flipkart_price=3859,
        competitor_amazon_lowest=3759, competitor_flipkart_lowest=3815,
        stock=42, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-002",
        bundle_affinity=["ZIG-RC-002"]),

    SKU("ZIG-PED-001",
        "Pedigree Adult Dry Dog Food Chicken & Veg - 3kg",
        "Pedigree", "food", "dry-food", "dog", False,
        mrp=899, cost=625,
        current_d2c_price=791, current_amazon_price=799, current_flipkart_price=789,
        competitor_amazon_lowest=765, competitor_flipkart_lowest=775,
        stock=520, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-001",
        bundle_affinity=["ZIG-PED-002", "ZIG-APL-008"]),

    SKU("ZIG-PED-002",
        "Pedigree Adult Wet Dog Food - 80g",
        "Pedigree", "food", "wet-food", "dog", False,
        mrp=49, cost=33,
        current_d2c_price=43, current_amazon_price=44, current_flipkart_price=43,
        competitor_amazon_lowest=42, competitor_flipkart_lowest=42,
        stock=2400, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-005",
        bundle_affinity=["ZIG-PED-001"]),

    SKU("ZIG-FAR-001",
        "Farmina N&D Pumpkin Chicken Dry Dog Food - 2.5kg",
        "Farmina", "food", "dry-food", "dog", False,
        mrp=3690, cost=2780,
        current_d2c_price=3140, current_amazon_price=3199, current_flipkart_price=3175,
        competitor_amazon_lowest=3099, competitor_flipkart_lowest=3149,
        stock=58, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-APL-002",
        bundle_affinity=["ZIG-APL-007"]),

    # ---------- DOG TREATS: BRANDED ----------
    SKU("ZIG-FB-001",
        "First Bark Mango & Chicken Wraps Dog Treat - 70g",
        "First Bark", "treats", "meaty", "dog", False,
        mrp=199, cost=95,
        current_d2c_price=179, current_amazon_price=189, current_flipkart_price=185,
        competitor_amazon_lowest=175, competitor_flipkart_lowest=179,
        stock=180, buy_box_eligible=True, is_buy_box_winner=True,
        pl_equivalent_id="ZIG-APL-010",
        bundle_affinity=["ZIG-APL-001"]),

    SKU("ZIG-IMG-001",
        "Imaginelles Pup Ice Rocket Lollies - 90g",
        "Imaginelles", "treats", "frozen", "dog", False,
        mrp=399, cost=190,
        current_d2c_price=359, current_amazon_price=379, current_flipkart_price=375,
        competitor_amazon_lowest=355, competitor_flipkart_lowest=365,
        stock=120, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-002"]),

    # ---------- DOG TOYS ----------
    SKU("ZIG-TRX-001",
        "Trixie Cooling Dumbbell Dog Toy - 18cm",
        "Trixie", "toys", "chew", "dog", False,
        mrp=845, cost=485,
        current_d2c_price=744, current_amazon_price=789, current_flipkart_price=775,
        competitor_amazon_lowest=735, competitor_flipkart_lowest=755,
        stock=140, buy_box_eligible=True, is_buy_box_winner=False,
        bundle_affinity=["ZIG-APL-001", "ZIG-APL-008"]),

    SKU("ZIG-TRX-002",
        "Trixie Dog Pool Light Blue/Blue (5.25ft x 1ft)",
        "Trixie", "toys", "outdoor", "dog", False,
        mrp=8500, cost=5850,
        current_d2c_price=7650, current_amazon_price=7899, current_flipkart_price=7799,
        competitor_amazon_lowest=7549, competitor_flipkart_lowest=7699,
        stock=22, buy_box_eligible=True, is_buy_box_winner=False,
        bundle_affinity=["ZIG-MP-001", "ZIG-ZL-002"]),

    SKU("ZIG-FF-001",
        "FOFOS Summer Cat Toy Watermelon with Popsicle",
        "FOFOS", "toys", "plush", "cat", False,
        mrp=349, cost=175,
        current_d2c_price=307, current_amazon_price=325, current_flipkart_price=319,
        competitor_amazon_lowest=299, competitor_flipkart_lowest=309,
        stock=210, buy_box_eligible=True, is_buy_box_winner=False,
        bundle_affinity=[]),

    # ---------- ZIGLY LIFESTYLE (PL) ----------
    SKU("ZIG-ZL-001",
        "Zigly Lifestyle Tropical Farm Pumpkin Dog Shirt - M",
        "Zigly Lifestyle", "accessories", "clothing", "dog", True,
        mrp=1099, cost=410,
        current_d2c_price=1099, current_amazon_price=1149, current_flipkart_price=1119,
        competitor_amazon_lowest=1099, competitor_flipkart_lowest=1099,
        stock=48, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-ZL-002"]),

    SKU("ZIG-ZL-002",
        "Zigly Lifestyle Portable Water Bottle for Pets - 500ml",
        "Zigly Lifestyle", "accessories", "travel", "both", True,
        mrp=999, cost=345,
        current_d2c_price=899, current_amazon_price=949, current_flipkart_price=929,
        competitor_amazon_lowest=899, competitor_flipkart_lowest=899,
        stock=160, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-ZL-001", "ZIG-TRX-002"]),

    SKU("ZIG-ZL-003",
        "ZL Ultimate Double Walled Dog Bowl - Red - M",
        "Zigly Lifestyle", "accessories", "bowls", "dog", True,
        mrp=799, cost=275,
        current_d2c_price=639, current_amazon_price=679, current_flipkart_price=659,
        competitor_amazon_lowest=635, competitor_flipkart_lowest=649,
        stock=95, buy_box_eligible=True, is_buy_box_winner=True,
        bundle_affinity=["ZIG-APL-001", "ZIG-ZL-002"]),

    # ---------- DISPENSER ----------
    SKU("ZIG-MP-001",
        "M-Pets Nile Dog/Cat Water Dispenser - 3000ml",
        "M-Pets", "accessories", "feeders", "both", False,
        mrp=1550, cost=950,
        current_d2c_price=1395, current_amazon_price=1449, current_flipkart_price=1425,
        competitor_amazon_lowest=1379, competitor_flipkart_lowest=1399,
        stock=68, buy_box_eligible=True, is_buy_box_winner=False,
        pl_equivalent_id="ZIG-ZL-002",
        bundle_affinity=[]),
]


def get_catalog():
    """Return catalog as list of dicts for easy DataFrame use."""
    return [asdict(sku) for sku in CATALOG]


def get_sku(sku_id: str):
    for s in CATALOG:
        if s.sku_id == sku_id:
            return s
    return None


def get_pl_equivalent(sku_id: str):
    sku = get_sku(sku_id)
    if not sku or not sku.pl_equivalent_id:
        return None
    return get_sku(sku.pl_equivalent_id)


# ------------------------------------------------------------------
# Channel economics (for margin math)
# ------------------------------------------------------------------
CHANNEL_ECONOMICS = {
    "d2c":      {"commission_pct": 0.00, "fulfillment_cost_pct": 0.06, "label": "D2C (zigly.com)"},
    "amazon":   {"commission_pct": 0.15, "fulfillment_cost_pct": 0.04, "label": "Amazon India"},
    "flipkart": {"commission_pct": 0.13, "fulfillment_cost_pct": 0.04, "label": "Flipkart"},
    "chewy":    {"commission_pct": 0.15, "fulfillment_cost_pct": 0.08, "label": "Chewy (US)"},
}


def channel_margin(price: float, cost: float, channel: str) -> dict:
    """Return absolute and % margin for a sale at `price` on `channel`."""
    e = CHANNEL_ECONOMICS[channel]
    fees = price * (e["commission_pct"] + e["fulfillment_cost_pct"])
    margin_abs = price - cost - fees
    margin_pct = (margin_abs / price) if price > 0 else 0.0
    return {
        "price": price,
        "cost": cost,
        "fees": fees,
        "margin_abs": margin_abs,
        "margin_pct": margin_pct,
    }


# ------------------------------------------------------------------
# Policy / guardrails (shared across all agents)
# ------------------------------------------------------------------
POLICY = {
    "min_margin_pct_pl":         0.30,   # private label floor
    "min_margin_pct_branded":    0.08,   # branded floor (after marketplace fees)
    "max_daily_change_pct":      0.05,   # max 5% price swing per day
    "low_stock_threshold":       50,     # units; trigger price-up
    "buy_box_undercut_paise":    1.0,    # rupee undercut to win box
    "parity_d2c_to_amazon_pct":  0.00,   # D2C must be <= Amazon (no public undercut)
    "max_pl_nudges_per_session": 1,      # UX restraint
    "bundle_min_discount_pct":   0.05,   # bundle discount floor
    "bundle_max_discount_pct":   0.12,   # bundle discount ceiling
}
