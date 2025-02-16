from flask import Flask, request, jsonify, send_file, render_template
import requests
import os

app = Flask(__name__)

API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return render_template("index1.html")

@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    if not user_prompt:
        return jsonify({"error": "No description provided"}), 400

    payload = {"inputs": user_prompt}

    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        image_path = "static/generated_image.png"
        with open(image_path, "wb") as file:
            file.write(response.content)
        
        return jsonify({"image_url": "/" + image_path})
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)
