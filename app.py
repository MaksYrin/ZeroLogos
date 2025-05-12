# -*- coding: utf-8 -*-
import os
import uuid
from flask import Flask, request, render_template
import logo_gen

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/generate_logo', methods=['POST'])
def generate_logo():
    forma = request.form['shape']
    style = request.form['style']
    description = request.form['description']
    result = logo_gen.generate_logo(forma, style, description)
    if "Ошибка" in result:
        print(result)
        return render_template('index.html', error=result)
    return render_template('index.html', logo_url=result)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.form['prompt']
    output_path = f"static/generated/image_{uuid.uuid4().hex}.jpg"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = logo_gen.generate_by_prompt(prompt, output_path)
    if "Ошибка" in result:
        return render_template('index.html', error=result)
    return render_template('index.html', image_url=output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
