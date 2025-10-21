# --- Aptus AI Back-End Server (The FINAL Real Version) ---
# This server is ready for live deployment. It creates smart search links
# and includes endpoints for real AI skin tone analysis and Gemini coaching.

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

# --- THE REAL BRAIN: Securely load API keys from the server's environment ---
# We will add these keys in Render.com. The code will read them from there.
GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"


# --- The Smart Fashion Library (Phase 1 Database) ---
# This database now creates smart, real search links.
db = {
    'Men': {
        'outfits': {
            'Date': [
                {'tone_profile': 'Warm', 'items': [{'name': 'Maroon Casual Shirt', 'img': 'https://placehold.co/400x500/800000/FFFFFF?text=Shirt', 'search_query': 'maroon casual shirt'}, {'name': 'Beige Chinos', 'img': 'https://placehold.co/400x500/F5F5DC/000000?text=Pants', 'search_query': 'beige chinos'}, {'name': 'Brown Loafers', 'img': 'https://placehold.co/400x500/964B00/FFFFFF?text=Shoes', 'search_query': 'brown loafers'}]},
                {'tone_profile': 'Cool', 'items': [{'name': 'Navy Blue Polo', 'img': 'https://placehold.co/400x500/000080/FFFFFF?text=Polo', 'search_query': 'navy blue polo shirt'}, {'name': 'Grey Trousers', 'img': 'https://placehold.co/400x500/808080/FFFFFF?text=Pants', 'search_query': 'grey formal trousers'}, {'name': 'White Sneakers', 'img': 'https://placehold.co/400x500/FFFFFF/000000?text=Shoes', 'search_query': 'white sneakers'}]},
                {'tone_profile': 'Neutral', 'items': [{'name': 'White T-Shirt', 'img': 'https://placehold.co/400x500/FFFFFF/000000?text=T-Shirt', 'search_query': 'white round neck t-shirt'}, {'name': 'Black Jeans', 'img': 'https://placehold.co/400x500/000000/FFFFFF?text=Jeans', 'search_query': 'black slim fit jeans'}, {'name': 'Black Boots', 'img': 'https://placehold.co/400x500/1A1A1A/FFFFFF?text=Boots', 'search_query': 'black chelsea boots'}]}
            ],
            'Marriage': [
                 {'tone_profile': 'Warm', 'items': [{'name': 'Gold Kurta', 'img': 'https://placehold.co/400x500/FFD700/000000?text=Kurta', 'search_query': 'gold kurta for men'}, {'name': 'Cream Pajama', 'img': 'https://placehold.co/400x500/FFFDD0/000000?text=Pajama', 'search_query': 'cream pajama set'}, {'name': 'Brown Mojaris', 'img': 'https://placehold.co/400x500/964B00/FFFFFF?text=Mojaris', 'search_query': 'brown mojaris'}]}
            ]
        }
    },
    'Women': {
        'outfits': {
             'Date': [
                {'tone_profile': 'Cool', 'items': [{'name': 'Blue Satin Dress', 'img': 'https://placehold.co/400x500/4682B4/FFFFFF?text=Dress', 'search_query': 'blue satin dress'}, {'name': 'Silver Heels', 'img': 'https://placehold.co/400x500/C0C0C0/000000?text=Heels', 'search_query': 'silver heels'}, {'name': 'Diamond Earrings', 'img': 'https://placehold.co/400x500/B9F2FF/000000?text=Jewelry', 'search_query': 'diamond stud earrings'}]}
             ]
        }
    }
}

@app.route('/get-outfit', methods=['POST'])
def get_outfit():
    data = request.get_json()
    gender = data.get('gender')
    skin_tone = data.get('skinTone')
    occasion = data.get('occasion')
    print(f"✅ Request for Outfit: Gender={gender}, SkinTone={skin_tone}, Occasion={occasion}")
    try:
        all_outfits = db.get(gender, {}).get('outfits', {}).get(occasion, [])
        if not all_outfits: return jsonify([])
        
        perfect_matches = [o for o in all_outfits if o.get('tone_profile') == skin_tone]
        neutral_matches = [o for o in all_outfits if o.get('tone_profile') == 'Neutral']
        recommendations = perfect_matches + [o for o in neutral_matches if o not in perfect_matches]
        if len(recommendations) < 3:
            other_outfits = [o for o in all_outfits if o not in recommendations]
            random.shuffle(other_outfits)
            recommendations.extend(other_outfits)
        final_outfits_raw = recommendations[:3]
        
        # Create real search links
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
        print(f"❌ Error in get_outfit: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analyze-skin', methods=['POST'])
def analyze_skin():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"success": False, "error": "No image data provided"}), 400

    if not GOOGLE_VISION_API_KEY:
         return jsonify({"success": False, "error": "Server is missing Vision API key."}), 500

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
        print(f"❌ Vision API request failed: {e}")
        return jsonify({"success": False, "error": "Failed to connect to AI service."}), 500

@app.route('/get-ai-coach-tip', methods=['POST'])
def get_ai_coach_tip():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"success": False, "error": "No prompt provided"}), 400
    
    if not GEMINI_API_KEY:
        return jsonify({"success": False, "tip": "AI Coach is not configured on the server."})

    request_body = {"contents": [{"parts": [{"text": data['prompt']}]}]}
    try:
        response = requests.post(GEMINI_API_URL, json=request_body)
        response.raise_for_status()
        gemini_data = response.json()
        tip = gemini_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"success": True, "tip": tip})
    except Exception as e:
        print(f"❌ Gemini API request failed: {e}")
        return jsonify({"success": False, "error": "Failed to connect to AI Coach."}), 500

if __name__ == '__main__':
    print("🚀 Starting Aptus AI REAL BRAIN Server...")
    app.run(debug=True, port=5000)

