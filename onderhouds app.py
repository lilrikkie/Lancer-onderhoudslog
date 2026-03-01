import os
import pandas as pd
from flask import Flask, render_template, request, redirect, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuratie
basedir = os.path.abspath(os.path.dirname(__file__))
# Gebruikt een omgevingsvariabele op de server, of lokaal de onderhoud.db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'onderhoud.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Onderhoud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.DateTime, default=datetime.utcnow)
    km_stand = db.Column(db.Integer)
    olie = db.Column(db.Boolean)
    oliefilter = db.Column(db.Boolean)
    luchtfilter = db.Column(db.Boolean)
    interieurfilter = db.Column(db.Boolean)
    koelvloeistof = db.Column(db.Boolean)
    remvloeistof = db.Column(db.Boolean)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nieuw_item = Onderhoud(
            km_stand=request.form.get('km_stand'),
            olie='olie' in request.form,
            oliefilter='oliefilter' in request.form,
            luchtfilter='luchtfilter' in request.form,
            interieurfilter='interieurfilter' in request.form,
            koelvloeistof='koelvloeistof' in request.form,
            remvloeistof='remvloeistof' in request.form
        )
        db.session.add(nieuw_item)
        db.session.commit()
        return redirect(url_for('index'))
    
    logs = Onderhoud.query.order_by(Onderhoud.datum.desc()).all()
    return render_template('index.html', logs=logs)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    log = Onderhoud.query.get_or_404(id)
    if request.method == 'POST':
        log.km_stand = request.form.get('km_stand')
        log.olie = 'olie' in request.form
        log.oliefilter = 'oliefilter' in request.form
        log.luchtfilter = 'luchtfilter' in request.form
        log.interieurfilter = 'interieurfilter' in request.form
        log.koelvloeistof = 'koelvloeistof' in request.form
        log.remvloeistof = 'remvloeistof' in request.form
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', log=log)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    log = Onderhoud.query.get_or_404(id)
    db.session.delete(log)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_excel():
    data = Onderhoud.query.all()
    lijst = []
    for item in data:
        lijst.append({
            'Datum': item.datum.strftime('%d-%m-%Y'),
            'Kilometerstand': item.km_stand,
            'Olie': 'Ja' if item.olie else 'Nee',
            'Oliefilter': 'Ja' if item.oliefilter else 'Nee',
            'Luchtfilter': 'Ja' if item.luchtfilter else 'Nee',
            'Interieurfilter': 'Ja' if item.interieurfilter else 'Nee',
            'Koelvloeistof': 'Ja' if item.koelvloeistof else 'Nee',
            'Remvloeistof': 'Ja' if item.remvloeistof else 'Nee'
        })
    df = pd.DataFrame(lijst)
    excel_pad = os.path.join(basedir, 'Mitsubishi_Lancer_Onderhoud.xlsx')
    df.to_excel(excel_pad, index=False)
    return send_file(excel_pad, as_attachment=True)

if __name__ == '__main__':
    # host='0.0.0.0' maakt de site bereikbaar via WiFi op je telefoon
    # port=int(os.environ.get("PORT", 5000)) is nodig voor GitHub/Render
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
