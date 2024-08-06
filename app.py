from flask import Flask, request, render_template, jsonify
import threading
import uuid

app = Flask(__name__)

# In-memory cache for results
results_cache = {}

# Dummy AI71 class for simulation
class AI71:
    def __init__(self, api_key):
        self.api_key = api_key

    class chat:
        @staticmethod
        def completions_create(model, messages, stream):
            # Simulate a streaming response for the sake of example
            responses = [
                {"choices": [{"delta": {"content": "Hint: Use trigonometric identities.\n\n"}}]},
                {"choices": [{"delta": {"content": "Real-world example: Engineers use trigonometry in building designs.\n\n"}}]},
                {"choices": [{"delta": {"content": "For beginners: Review basic trigonometric identities.\n\n"}}]},
                {"choices": [{"delta": {"content": "Code solution: sin(x)cos(x) = 1/2 sin(2x)\n\n"}}]},
                {"choices": [{"delta": {"content": "Topic: Trigonometry"}}]}
            ]
            for response in responses:
                yield response

def process_ai_request(input_text, job_id):
    AI71_API_KEY = "api71-api-2fcb29da-a589-4632-9e26-47a71786cd25"
    response = ""
    prompt = (
        input_text + ''' First, judge whether the person is a beginner or advanced based on the way they ask questions. 
        If the person is a beginner, give more detailed hints, and if advanced, give less concise hints. The answer 
        you give must have the following sections: 1. Give hints to solve the question but do not give the coding 
        solution. After it, give a two-line space. 2. Provide some real-world examples. Give only one example to explain 
        it. Don't give the code. After it, give a two-line space. 3. If the question is of beginner level, then give some 
        more hints that enhance the self-learning of the user, and if the question is advanced, then ignore this line. 
        After it, give a two-line space. 4. Provide the code solution to the question. After it, give a two-line space. 
        5. Mention the topic name to study to understand the question. After it, give a two-line space.'''
    )
    for chunk in AI71(AI71_API_KEY).chat.completions_create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for coding problems."},
            {"role": "user", "content": prompt}
        ],
        stream=True,
    ):
        if chunk['choices'][0]['delta']['content']:
            response += chunk['choices'][0]['delta']['content']
    
    x = response.split("\n\n")
    results_cache[job_id] = x

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form['answer']
    job_id = str(uuid.uuid4())
    threading.Thread(target=process_ai_request, args=(answer, job_id)).start()
    return jsonify({"job_id": job_id})

@app.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    if job_id in results_cache:
        result = results_cache[job_id]
        del results_cache[job_id]  # Clean up the cache
        hint1, hint2, hint3, hint4, hint5 = result[:5]
        return jsonify({
            "status": "complete",
            "hint1": hint1,
            "hint2": hint2,
            "hint3": hint3,
            "hint4": hint4,
            "hint5": hint5
        })
    else:
        return jsonify({"status": "processing"})

if __name__ == '__main__':
    app.run(debug=True)
