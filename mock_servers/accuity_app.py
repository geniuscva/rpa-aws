from flask import Flask, render_template, request, redirect, url_for, send_file
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('search'))
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        entity_type = request.form.get('entityType')
        name = request.form.get('name')
        return redirect(url_for('result', name=name, entity_type=entity_type))
    return render_template('search.html')

@app.route('/result')
def result():
    name = request.args.get('name', 'Unknown')
    entity_type = request.args.get('entity_type', 'Unknown')
    return render_template('result.html', name=name, entity_type=entity_type)

@app.route('/record')
def record():
    name = request.args.get('name', 'Unknown')
    return render_template('record.html', name=name)

@app.route('/export')
def export():
    # Return a dummy PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Mock PDF File) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000222 00000 n \n0000000309 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n404\n%%EOF"
    return send_file(
        io.BytesIO(pdf_content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Tra_cuu_Accuity.pdf'
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)
