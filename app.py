# --- Aptus AI Back-End Server (The FINAL Real Version with Live Keys) ---
# This server is ready for deployment and uses real AI API Keys.

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

# --- THE REAL BRAIN: LIVE API KEYS INSERTED ---
# WARNING: Storing keys directly in code is not recommended for a public project.
# For this final version, I am inserting them as you requested.
GOOGLE_VISION_API_KEY = "AIzaSyCPFY5V6UFT8Tso3FmX4PjdjMI4iuHQ3Xo"
GEMINI_API_KEY = "AIzaSyDXKY_zATbhTzNtUlxntuKcamSUuT40o_s"

VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"


# --- The Smart Fashion Library (Phase 1 Database) ---
db = {
    'Men': {
        'outfits': {
            'Date': [
                {'tone_profile': 'Warm', 'items': [{'name': 'Maroon Casual Shirt', 'img': 'https://placehold.co/400x500/800000/FFFFFF?text=Shirt', 'search_query': 'maroon casual shirt'}, {'name': 'Beige Chinos', 'img': 'https://placehold.co/400x500/F5F5DC/000000?text=Pants', 'search_query': 'beige chinos'}, {'name': 'Brown Loafers', 'img': 'https://placehold.co/400x500/964B00/FFFFFF?text=Shoes', 'search_query': 'brown loafers'}]},
                {'tone_profile': 'Cool', 'items': [{'name': 'Navy Blue Polo', 'img': 'https://placehold.co/400x500/000080/FFFFFF?text=Polo', 'search_query': 'navy blue polo shirt'}, {'name': 'Grey Trousers', 'img': 'https://placehold.co/400x500/808080/FFFFFF?text=Pants', 'search_query': 'grey formal trousers'}, {'name': 'White Sneakers', 'img': 'https://placehold.co/400x500/FFFFFF/000000?text=Shoes', 'search_query': 'white sneakers'}]},
            ],
            'Marriage': [
                 {'tone_profile': 'Warm', 'items': [{'name': 'Gold Kurta', 'img': 'https://placehold.co/400x500/FFD700/000000?text=Kurta', 'search_query': 'gold kurta for men'}, {'name': 'Cream Pajama', 'img': 'https://placehold.co/400x500/FFFDD0/000000?text=Pajama', 'search_query': 'cream pajama set'}, {'name': 'Brown Mojaris', 'img': 'https://placehold.co/400x500/964B00/FFFFFF?text=Mojaris', 'search_query': 'brown mojaris'}]}
            ]
        }
    },
    'Women': {'outfits': {} }
}

@app.route('/get-outfit', methods=['POST'])
def get_outfit():
    data = request.get_json()
    gender, skin_tone, occasion = data.get('gender'), data.get('skinTone'), data.get('occasion')
    try:
        all_outfits = db.get(gender, {}).get('outfits', {}).get(occasion, [])
        if not all_outfits: return jsonify([])
        
        perfect_matches = [o for o in all_outfits if o.get('tone_profile') == skin_tone]
        neutral_matches = [o for o in all_outfits if o.get('tone_profile') == 'Neutral']
        recommendations = perfect_matches + [o for o in neutral_matches if o not in perfect_matches]
        
        final_outfits_raw = recommendations[:3]
        final_outfits_with_links = []
        for outfit in final_outfits_raw:
            new_items = []
            for item in outfit['items']:
                query = urllib.parse.quote(item['search_query'])
                item['link'] = f"https://www.myntra.com/{query}"
                new_items.append(item)
            new_outfit = outfit.copy()
            new_outfit['items'] = new_items
            final_outfits_with_links.append(new_outfit)
        return jsonify(final_outfits_with_links)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze-skin', methods=['POST'])
def analyze_skin():
    data = request.get_json()
    if not (data and data.get('image')): return jsonify({"success": False, "error": "No image provided"}), 400
    
    request_body = { "requests": [{"image": {"content": data['image']}, "features": [{"type": "FACE_DETECTION", "maxResults": 1}, {"type": "IMAGE_PROPERTIES", "maxResults": 1}] }] }
    try:
        response = requests.post(VISION_API_URL, json=request_body)
        response.raise_for_status()
        vision_data = response.json()
        face = vision_data['responses'][0].get('faceAnnotations')
        colors = vision_data['responses'][0].get('imagePropertiesAnnotation', {}).get('dominantColors', {}).get('colors')
        if not face or not colors: return jsonify({"success": False, "tone": "Detection failed."})
        
        dominant_color = colors[0]['color']
        red, green, blue = dominant_color.get('red', 0), dominant_color.get('green', 0), dominant_color.get('blue', 0)
        tone = 'Neutral'
        if red > blue and green > blue: tone = 'Warm'
        elif blue > red and blue > green: tone = 'Cool'
        return jsonify({"success": True, "tone": tone})
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to connect to AI service."}), 500

@app.route('/get-ai-coach-tip', methods=['POST'])
def get_ai_coach_tip():
    data = request.get_json()
    if not (data and data.get('prompt')): return jsonify({"success": False, "error": "No prompt provided"}), 400
    
    request_body = {"contents": [{"parts": [{"text": data['prompt']}]}]}
    try:
        response = requests.post(GEMINI_API_URL, json=request_body)
        response.raise_for_status()
        gemini_data = response.json()
        tip = gemini_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"success": True, "tip": tip})
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to connect to AI Coach."}), 500

if __name__ == '__main__':
    print("🚀 Starting Aptus AI REAL BRAIN Server...")
    app.run(debug=True, port=5000)

