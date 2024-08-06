from flask import Flask, request, render_template
from rq import Queue
from rq.job import Job
from worker import conn
import time
from ai71 import AI71

app = Flask(__name__)
q = Queue(connection=conn)

def process_ai_request(Input):
    AI71_API_KEY = "api71-api-2fcb29da-a589-4632-9e26-47a71786cd25"
    response = ""
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {
                "role": "system",
                "content": '''You are a helpful assistant for coding problems.'''
            },
            {
                "role": "user",
                "content": Input + ''' First, judge whether the person is a beginner or advanced based on the way they ask questions. If the person is a beginner, give more detailed hints, and if advanced, give less concise hints. The answer you give must have the following sections:
    1. Give hints to solve the question but do not give the coding solution. After it, give a two-line space.
    2. Provide some real-world examples. Give only one example to explain it. Don't give the code. After it, give a two-line space.
    3. If the question is of beginner level, then give some more hints that enhance the self-learning of the user, and if the question is advanced, then ignore this line. After it, give a two-line space.
    4. Provide the code solution to the question. After it, give a two-line space.
    5. Mention the topic name to study to understand the question. After it, give a two-line space.
    Do not use the word "beginner" directly.'''
            },
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
    
    x = response.split("\n\n")
    return x

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form['answer']
    job = q.enqueue(process_ai_request, answer)
    return render_template('processing.html', job_id=job.id)

@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        result = job.result
        hint1, hint2, hint3, *hint4, hint5 = result
        hint4 = "\n\n".join(hint4)
        return render_template('main.html', hint1=hint1, hint2=hint2, hint3=hint3, hint4=hint4, hint5=hint5, Input=job.args[0])
    else:
        return "Nay!", 202

if __name__ == '__main__':
    app.run(debug=True)
