from flask import Flask, render_template, request, send_file
from PIL import Image
from rembg import remove
from pillow_heif import register_heif_opener
import rawpy
import io

register_heif_opener()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        quality = int(request.form.get('quality', 30))
        width = request.form.get('width', type=int)
        height = request.form.get('height', type=int)
        format = request.form.get('format', 'JPEG')
        remove_bg = 'remove_bg' in request.form
        bg_color = request.form.get('bg_color', '#FFFFFF')

        try:
            filename = file.filename.lower()
            if filename.endswith(('.cr2', '.nef', '.arw', '.dng')):
                raw = rawpy.imread(file)
                rgb = raw.postprocess()
                img = Image.fromarray(rgb).convert("RGBA")
            else:
                img = Image.open(file).convert("RGBA")
        except Exception as e:
            return f"Error processing image: {e}"

        if remove_bg:
            img = remove(img)
            bg = Image.new("RGBA", img.size, bg_color)
            bg.paste(img, mask=img.split()[3])
            img = bg.convert("RGB" if format != "PNG" else "RGBA")

        if width and height:
            img = img.resize((width, height))

        buffer = io.BytesIO()
        img.save(buffer, format=format.upper(), quality=quality)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"compressed.{format.lower()}",
                         mimetype=f"image/{format.lower()}")
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/faq')
def editor():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render will set PORT
    app.run(host='0.0.0.0', port=port)

