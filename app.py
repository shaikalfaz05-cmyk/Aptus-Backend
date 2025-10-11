# app.py
"""
Aptus backend - Phase 1 (fake brain) with Phase 2 (real brain) adapter-ready skeleton.

How it works:
- POST /get-outfit expects JSON: { "gender": "Boy"|"Girl", "skinTone": "Warm"|"Cool"|"Neutral", "occasion": "Date"|"Marriage"|... }
- Returns: { "success": True, "outfits": [ { title, description, tone_profile, items: [ {name,image,link} ] } ] }

Phase-2:
- Set USE_REAL_BRAIN=true (in .env) and provide API keys (OPENAI_API_KEY, AFFILIATE_API_KEY etc.)
- Implement the get_outfits_from_real(...) function or integrate with a real module.
- The wrapper will try real brain first, and fall back to fake brain on errors.
"""

import os
import time
import random
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from backend/.env if present
load_dotenv()

# Configuration
USE_REAL_BRAIN = os.getenv("USE_REAL_BRAIN", "false").lower() in ("1", "true", "yes")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        # example placeholder
AFFILIATE_API_KEY = os.getenv("AFFILIATE_API_KEY")  # example placeholder
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

# Initialize
app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

# --------------------------
# Fake brain dataset (Phase1)
# --------------------------
# Designed to return consistent structured responses.
# Images use placehold.co or stable placeholder links; replace with real images later.
fake_brain = {
    "Boy": {
        "Date": [
            {
                "title": "Maroon Shirt + Beige Chinos",
                "description": "A warm maroon shirt paired with beige chinos — classic, approachable date-night look.",
                "tone_profile": "Warm",
                "items": [
                    {"name": "Maroon Shirt", "image": "https://placehold.co/400x400/7c2aab/ffffff?text=Maroon+Shirt", "link": "https://example.com/maroon-shirt"},
                    {"name": "Beige Chinos", "image": "https://placehold.co/400x400/d8c99b/050505?text=Beige+Chinos", "link": "https://example.com/beige-chinos"},
                    {"name": "Brown Loafers", "image": "https://placehold.co/400x400/8b5e3c/ffffff?text=Brown+Loafers", "link": "https://example.com/brown-loafers"},
                ]
            },
            {
                "title": "Navy Shirt + Slim Jeans",
                "description": "Smart-casual navy shirt with slim jeans — clean and modern.",
                "tone_profile": "Cool",
                "items": [
                    {"name": "Navy Shirt", "image": "https://placehold.co/400x400/0f172a/ffffff?text=Navy+Shirt", "link": "https://example.com/navy-shirt"},
                    {"name": "Slim Jeans", "image": "https://placehold.co/400x400/4b5563/ffffff?text=Slim+Jeans", "link": "https://example.com/slim-jeans"},
                    {"name": "White Sneakers", "image": "https://placehold.co/400x400/ffffff/050505?text=White+Sneakers", "link": "https://example.com/sneakers"},
                ]
            },
            {
                "title": "Casual Denim Jacket Look",
                "description": "Layered denim jacket + tee — relaxed yet stylish.",
                "tone_profile": "Neutral",
                "items": [
                    {"name": "Denim Jacket", "image": "https://placehold.co/400x400/1e3a8a/ffffff?text=Denim+Jacket", "link": "https://example.com/denim-jacket"},
                    {"name": "White Tee", "image": "https://placehold.co/400x400/ffffff/050505?text=White+Tee", "link": "https://example.com/white-tee"},
                    {"name": "Casual Shoes", "image": "https://placehold.co/400x400/94a3b8/050505?text=Casual+Shoes", "link": "https://example.com/casual-shoes"},
                ]
            },
        ],
        "Marriage": [
            {
                "title": "Cream Sherwani with Embroidery",
                "description": "Traditional cream sherwani with delicate embroidery — festive & elegant.",
                "tone_profile": "Warm",
                "items": [
                    {"name": "Cream Sherwani", "image": "https://placehold.co/400x400/E6B980/050505?text=Sherwani", "link": "https://example.com/sherwani"},
                    {"name": "Embroidered Mojris", "image": "https://placehold.co/400x400/8b5e3c/ffffff?text=Mojris", "link": "https://example.com/mojris"},
                    {"name": "Golden Shawl", "image": "https://placehold.co/400x400/EACDA3/050505?text=Shawl", "link": "https://example.com/shawl"},
                ]
            },
            {
                "title": "Navy Indo-Western Suit",
                "description": "Modern Indo-western suit — perfect balance of tradition and modernity.",
                "tone_profile": "Cool",
                "items": [
                    {"name": "Indo-Western Jacket", "image": "https://placehold.co/400x400/1e3a8a/ffffff?text=Indo+Jacket", "link": "https://example.com/indo-jacket"},
                    {"name": "Tailored Trousers", "image": "https://placehold.co/400x400/94a3b8/050505?text=Trousers", "link": "https://example.com/trousers"},
                    {"name": "Loafers", "image": "https://placehold.co/400x400/8b5e3c/ffffff?text=Loafers", "link": "https://example.com/loafers"},
                ]
            },
        ],
        "Party": [
            {
                "title": "Velvet Blazer Combo",
                "description": "A plush velvet blazer that stands out under party lights.",
                "tone_profile": "Neutral",
                "items": [
                    {"name":"Velvet Blazer","image":"https://placehold.co/400x400/6d28d9/ffffff?text=Velvet+Blazer","link":"https://example.com/velvet-blazer"},
                    {"name":"Black Shirt","image":"https://placehold.co/400x400/0b1020/ffffff?text=Black+Shirt","link":"https://example.com/black-shirt"},
                    {"name":"Chelsea Boots","image":"https://placehold.co/400x400/3f3f46/ffffff?text=Boots","link":"https://example.com/boots"},
                ]
            }
        ],
        "Office": [
            {
                "title": "Smart Grey Suit",
                "description": "Minimal grey suit with crisp shirt — professional & refined.",
                "tone_profile": "Neutral",
                "items": [
                    {"name":"Grey Suit","image":"https://placehold.co/400x400/9ca3af/050505?text=Grey+Suit","link":"https://example.com/grey-suit"},
                    {"name":"White Shirt","image":"https://placehold.co/400x400/ffffff/050505?text=White+Shirt","link":"https://example.com/white-shirt"},
                    {"name":"Oxford Shoes","image":"https://placehold.co/400x400/6b7280/ffffff?text=Oxfords","link":"https://example.com/oxfords"},
                ]
            }
        ],
        "College": [
            {
                "title": "Hoodie & Jeans",
                "description": "Comfy hoodie with relaxed jeans — campus casual.",
                "tone_profile": "Neutral",
                "items": [
                    {"name":"Hoodie","image":"https://placehold.co/400x400/111827/ffffff?text=Hoodie","link":"https://example.com/hoodie"},
                    {"name":"Jeans","image":"https://placehold.co/400x400/1f2937/ffffff?text=Jeans","link":"https://example.com/jeans"},
                    {"name":"Sneakers","image":"https://placehold.co/400x400/ffffff/050505?text=Sneakers","link":"https://example.com/sneakers"},
                ]
            }
        ]
    },
    "Girl": {
        "Date": [
            {
                "title": "Red Dress + Nude Heels",
                "description": "A classic red dress paired with nude heels — romantic and confident.",
                "tone_profile": "Cool",
                "items": [
                    {"name":"Red Dress","image":"https://placehold.co/400x400/ef4444/ffffff?text=Red+Dress","link":"https://example.com/red-dress"},
                    {"name":"Nude Heels","image":"https://placehold.co/400x400/f5d0a9/050505?text=Nude+Heels","link":"https://example.com/nude-heels"},
                    {"name":"Gold Clutch","image":"https://placehold.co/400x400/E6B980/050505?text=Clutch","link":"https://example.com/clutch"},
                ]
            }
        ],
        "Marriage": [
            {
                "title": "Designer Saree (Golden-Pink)",
                "description": "Elegant saree in golden-pink tones with matching bangles and sandals.",
                "tone_profile": "Warm",
                "items": [
                    {"name":"Golden-Pink Saree","image":"https://placehold.co/400x400/EACDA3/050505?text=Saree","link":"https://example.com/saree"},
                    {"name":"Matching Bangles","image":"https://placehold.co/400x400/8b5e3c/ffffff?text=Bangles","link":"https://example.com/bangles"},
                    {"name":"Traditional Sandals","image":"https://placehold.co/400x400/8b5e3c/ffffff?text=Sandals","link":"https://example.com/sandals"},
                ]
            },
            {
                "title": "Lehenga with Mirror Work",
                "description": "Festive lehenga with fine mirror work — statement-making and bright.",
                "tone_profile": "Neutral",
                "items": [
                    {"name":"Mirror Lehenga","image":"https://placehold.co/400x400/fbcfe8/050505?text=Lehenga","link":"https://example.com/lehenga"},
                    {"name":"Designer Earrings","image":"https://placehold.co/400x400/fab1c9/050505?text=Earrings","link":"https://example.com/earrings"},
                    {"name":"Heels","image":"https://placehold.co/400x400/fea4b4/050505?text=Heels","link":"https://example.com/heels"},
                ]
            }
        ],
        "Party": [
            {
                "title":"Sequin Party Dress",
                "description":"Shimmery sequin dress to stand out at night events.",
                "tone_profile":"Neutral",
                "items":[
                    {"name":"Sequin Dress","image":"https://placehold.co/400x400/f59e0b/050505?text=Sequin","link":"https://example.com/sequin"},
                    {"name":"Heels","image":"https://placehold.co/400x400/f97316/050505?text=Heels","link":"https://example.com/heels"},
                    {"name":"Clutch","image":"https://placehold.co/400x400/6d28d9/ffffff?text=Clutch","link":"https://example.com/clutch"},
                ]
            }
        ],
        "Office": [
            {
                "title":"Blazer & Trousers",
                "description":"Tailored blazer with trousers — polished professional look.",
                "tone_profile":"Cool",
                "items":[
                    {"name":"Blazer","image":"https://placehold.co/400x400/0f172a/ffffff?text=Blazer","link":"https://example.com/blazer"},
                    {"name":"Trousers","image":"https://placehold.co/400x400/94a3b8/050505?text=Trousers","link":"https://example.com/trousers"},
                    {"name":"Loafers","image":"https://placehold.co/400x400/6b7280/ffffff?text=Loafers","link":"https://example.com/loafers"},
                ]
            }
        ],
        "College": [
            {
                "title":"Kurti with Jeans",
                "description":"Cute kurti paired with jeans — comfortable and trendy for campus.",
                "tone_profile":"Neutral",
                "items":[
                    {"name":"Kurti","image":"https://placehold.co/400x400/fecaca/050505?text=Kurti","link":"https://example.com/kurti"},
                    {"name":"Jeans","image":"https://placehold.co/400x400/1f2937/ffffff?text=Jeans","link":"https://example.com/jeans"},
                    {"name":"Casual Shoes","image":"https://placehold.co/400x400/ffffff/050505?text=Shoes","link":"https://example.com/shoes"},
                ]
            }
        ]
    }
}

# --------------------------
# Simple in-memory cache
# --------------------------
_cache = {}
def cache_get(key):
    rec = _cache.get(key)
    if not rec: return None
    ts, value = rec
    if time.time() - ts > CACHE_TTL_SECONDS:
        del _cache[key]
        return None
    return value

def cache_set(key, value):
    _cache[key] = (time.time(), value)

# --------------------------
# Phase-1: fake brain function
# --------------------------
def get_outfits_from_fake(gender, skin_tone, occasion, count=3):
    """
    Return prioritized list: exact tone first, then neutral, then others.
    Keeps structure stable for frontend.
    """
    gender_key = gender if gender in fake_brain else ("Boy" if gender.lower().startswith("b") else "Girl")
    pool = fake_brain.get(gender_key, {}).get(occasion, [])
    if not pool:
        # fallback across gender or occasion
        pool = []
        for g in fake_brain:
            pool.extend(fake_brain[g].get(occasion, []))

    # prioritize
    exact = [o for o in pool if (o.get("tone_profile") or "").lower() == (skin_tone or "").lower()]
    neutral = [o for o in pool if (o.get("tone_profile") or "").lower() == "neutral"]
    other = [o for o in pool if o not in exact and o not in neutral]
    selected = (exact + neutral + other)[:count]

    # ensure copy and consistent keys
    results = []
    for s in selected:
        # deep-ish copy to avoid mutation
        copy = {
            "title": s.get("title"),
            "description": s.get("description"),
            "tone_profile": s.get("tone_profile", "Neutral"),
            "items": s.get("items", []),
            "_source": "fake"
        }
        results.append(copy)
    return results

# --------------------------
# Phase-2: real brain stub
# --------------------------
def get_outfits_from_real(gender, skin_tone, occasion, count=3):
    """
    IMPLEMENT THIS for Phase-2.

    Suggested flow:
    1) Form a prompt for your AI (OpenAI/Gemini) asking for structured JSON with outfits.
       Example response structure expected:
       [
         { "title": "...", "description": "...", "tone_profile":"Warm", "items":[ {"name":"", "search":"..."} ] },
         ...
       ]
    2) Parse AI JSON response safely.
    3) For each item.search, call affiliate/product search API (using AFFILIATE_API_KEY)
       to get actual image URL and affiliate link for the product.
    4) Normalize the results into same schema as fake_brain (title, description, tone_profile, items with name,image,link).
    5) Return the list (max 'count').

    This stub intentionally raises NotImplementedError so you don't accidentally call an unimplemented real brain.
    """
    # You can replace the raise with actual code when you add keys.
    raise NotImplementedError("Real brain not implemented. Set USE_REAL_BRAIN=false or implement get_outfits_from_real().")

# --------------------------
# Wrapper: pick real or fake, with fallback and caching
# --------------------------
def get_outfits(gender, skin_tone, occasion, count=3):
    cache_key = f"{gender}|{skin_tone}|{occasion}|{count}"
    cached = cache_get(cache_key)
    if cached:
        app.logger.debug("CACHE HIT: %s", cache_key)
        return cached

    if USE_REAL_BRAIN:
        app.logger.info("Using REAL brain for: %s %s %s", gender, skin_tone, occasion)
        try:
            outfits = get_outfits_from_real(gender, skin_tone, occasion, count=count)
            # annotate
            for o in outfits:
                o["_source"] = "real"
            cache_set(cache_key, outfits)
            return outfits
        except Exception as e:
            app.logger.error("Real brain failed: %s. Falling back to fake brain.", str(e))

    # fallback (or default)
    app.logger.info("Using FAKE brain for: %s %s %s", gender, skin_tone, occasion)
    outfits = get_outfits_from_fake(gender, skin_tone, occasion, count=count)
    cache_set(cache_key, outfits)
    return outfits

# --------------------------
# API endpoints
# --------------------------
@app.route("/get-outfit", methods=["POST"])
def api_get_outfit():
    try:
        data = request.get_json(force=True)
        gender = data.get("gender", "Boy")
        skin_tone = data.get("skinTone") or data.get("skin_tone") or "Neutral"
        occasion = data.get("occasion", "Date")
        count = int(data.get("count", 3))

        app.logger.info("Request: gender=%s skin_tone=%s occasion=%s count=%s", gender, skin_tone, occasion, count)
        outfits = get_outfits(gender, skin_tone, occasion, count=count)
        return jsonify({"success": True, "outfits": outfits})
    except Exception as e:
        app.logger.exception("Failed to handle /get-outfit")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "use_real_brain": USE_REAL_BRAIN,
        "time": datetime.utcnow().isoformat()
    })

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    # Helpful startup message
    app.logger.info("Starting Aptus backend (USE_REAL_BRAIN=%s).", USE_REAL_BRAIN)
    app.run(host="127.0.0.1", port=5000, debug=True)
