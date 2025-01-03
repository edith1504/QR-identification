import base64
from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
from pymongo import MongoClient

# MongoDB Connection String
MONGO_URI = "mongodb+srv://shloke1504:edith@cluster0.onbyg.mongodb.net/"

# Connect to the MongoDB cluster
client = MongoClient(MONGO_URI)
db = client["qr_system"]

# Collections
users_collection = db["users"]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_code_file = None  # File to be downloaded
    
    if request.method == 'POST':
        name = request.form['name']
        registration = request.form['registration']

        # Create QR data and save to the database
        qr_data = {"name": name, "registration": registration}
        users_collection.insert_one(qr_data)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save QR code as a file
        qr_code_file = BytesIO()
        img.save(qr_code_file, format="PNG")
        qr_code_file.seek(0)  # Reset file pointer for downloading

        # Render the QR code image
        qr_code_base64 = base64.b64encode(qr_code_file.getvalue()).decode()
        qr_code_file.seek(0)  # Reset again for serving

        return render_template('index.html', qr_code=qr_code_base64, downloadable=True)

    return render_template('index.html', qr_code=None, downloadable=False)

@app.route('/download', methods=['GET'])
def download_qr():
    """Download the generated QR code"""
    qr_code_file = BytesIO()
    img = qrcode.make(request.args.get("data", ""))
    img.save(qr_code_file, format="PNG")
    qr_code_file.seek(0)
    return send_file(qr_code_file, as_attachment=True, download_name="qr_code.png", mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True)
