from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"
DB = "kardex.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS persona (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        fecha_nac TEXT
    );
    """)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    personas = conn.execute("SELECT * FROM persona ORDER BY id ASC").fetchall()
    conn.close()
    return render_template('index.html', personas=personas)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefono = request.form['telefono'].strip()
        fecha_nac = request.form['fecha_nac'].strip()

        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            return render_template('create.html')

        conn = get_db_connection()
        conn.execute("INSERT INTO persona (nombre, telefono, fecha_nac) VALUES (?, ?, ?)",
                    (nombre, telefono, fecha_nac))
        conn.commit()
        conn.close()
        flash('Persona registrada correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    persona = conn.execute("SELECT * FROM persona WHERE id = ?", (id,)).fetchone()

    if not persona:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        telefono = request.form['telefono'].strip()
        fecha_nac = request.form['fecha_nac'].strip()

        conn.execute("UPDATE persona SET nombre=?, telefono=?, fecha_nac=? WHERE id=?",
                     (nombre, telefono, fecha_nac, id))
        conn.commit()
        conn.close()
        flash('Registro actualizado correctamente', 'success')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', persona=persona)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM persona WHERE id = ?", (id,))
    conn.commit()

    # Reordenar IDs después de eliminar
    personas = conn.execute("SELECT * FROM persona ORDER BY id ASC").fetchall()
    conn.execute("DELETE FROM sqlite_sequence WHERE name='persona'")  # reinicia el contador AUTOINCREMENT

    nuevo_id = 1
    for p in personas:
        conn.execute("UPDATE persona SET id = ? WHERE rowid = ?", (nuevo_id, p['id']))
        nuevo_id += 1

    conn.commit()
    conn.close()
    flash('Persona eliminada y IDs reordenados', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
