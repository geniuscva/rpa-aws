import os
# pyrefly: ignore [missing-import]
from flask import Flask, send_file
import io

app = Flask(__name__)

# HTML mimicking the Accuity search and detail flow using the selectors PlaywrightAccuityPort expects
PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Accuity Mock Server</title></head>
<body>
    <div id="login-section">
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button id="loginBtn" onclick="document.getElementById('login-section').style.display='none'; document.getElementById('search-section').style.display='block';">Login</button>
    </div>
    
    <div id="search-section" style="display:none;">
        <select id="entityType"><option value="Individual">Individual</option><option value="Organization">Organization</option></select>
        <input type="text" id="name" placeholder="Name">
        <input type="checkbox" id="singleCheck">
        <button id="searchBtn" onclick="document.getElementById('search-section').style.display='none'; document.getElementById('result-section').style.display='block';">Search</button>
    </div>

    <div id="result-section" style="display:none;">
        <div class="matchScore">100</div>
        <a id="exportPdfBtn" href="/export">Export PDF</a>
        <button id="openRecordBtn" onclick="document.getElementById('result-section').style.display='none'; document.getElementById('detail-section').style.display='block';">Open Record</button>
    </div>

    <div id="detail-section" style="display:none;">
        <h1>Detail Page</h1>
        <a id="exportRecordPdfBtn" href="/export">Export Record PDF</a>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    return PAGE_HTML

@app.route('/export')
def export_pdf():
    # Return a dummy PDF file
    dummy_pdf = io.BytesIO(b"%PDF-1.4\\n1 0 obj\\n<< /Type /Catalog /Pages 2 0 R >>\\nendobj\\n2 0 obj\\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\\nendobj\\n3 0 obj\\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\\nendobj\\nxref\\n0 4\\n0000000000 65535 f \\n0000000009 00000 n \\n0000000058 00000 n \\n0000000115 00000 n \\ntrailer\\n<< /Size 4 /Root 1 0 R >>\\nstartxref\\n188\\n%%EOF")
    return send_file(
        dummy_pdf,
        as_attachment=True,
        download_name='Tra_cuu.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(port=5005, debug=True)

