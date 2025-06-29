from flask import Flask, render_template, request, redirect, session, url_for
import json, random, os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# ------------------------ Helper Functions ------------------------

def load_questions():
    with open('questions.json') as f:
        return json.load(f)

def load_leaderboard():
    if not os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'w') as f:
            json.dump([], f)
    with open('leaderboard.json') as f:
        return json.load(f)

def save_leaderboard(data):
    with open('leaderboard.json', 'w') as f:
        json.dump(data, f)

# ------------------------ Routes ------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect('/home')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('/')
    return render_template('home.html')

@app.route('/quiz/<category>')
def quiz(category):
    if 'username' not in session:
        return redirect('/')
    num_questions = int(request.args.get('num', 5))
    all_questions = load_questions().get(category, [])
    selected = random.sample(all_questions, min(num_questions, len(all_questions)))
    return render_template('quiz.html', questions=selected, category=category)

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect('/')
    
    # Load original questions
    questions = json.loads(request.form['questions'])
    score = 0

    for q in questions:
        q_text = q['question']
        user_ans = request.form.get(q_text)
        correct_ans = q['answer']
        if user_ans == correct_ans:
            score += 1

    username = session.get('username', 'Guest')

    # Update leaderboard
    leaderboard = load_leaderboard()
    leaderboard.append({
        "user": username,
        "score": score,
        "total": len(questions)
    })
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]
    save_leaderboard(leaderboard)

    return render_template('result.html', score=score, total=len(questions))

@app.route('/leaderboard')
def leaderboard():
    if 'username' not in session:
        return redirect('/')
    data = load_leaderboard()
    return render_template('leaderboard.html', leaderboard=data)

# ------------------------ Run ------------------------

if __name__ == '__main__':
    app.run(debug=True)





