from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('dictionary.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/flashcards')
def flashcards():
    return render_template('flashcards.html')

@app.route('/diary')
def diary():
    return render_template('diary.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not query:
        cursor.execute("SELECT * FROM words LIMIT 20")
    else:
        sql = """
            SELECT * FROM words 
            WHERE word_kanji LIKE ? OR 
                  word_kana LIKE ? OR 
                  word_romaji LIKE ? OR 
                  meaning LIKE ? OR
                  tags LIKE ?
            LIMIT 50
        """
        p = f"%{query}%"
        cursor.execute(sql, (p, p, p, p, p))
        
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(results)

@app.route('/api/words')
def get_all_words():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words")
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run()