from flask import Flask, request, render_template, jsonify
import ai71

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form.get('answer')
    option = request.form.get('option')
    ai_response = get_ai_response(answer, option)
    if ai_response:
        hints = ai_response.split("\n\n")
        hint_titles = ["Hints", "Example", "Self Learning", "Solution", "Topics"]
        response = {}
        for i, (title, hint) in enumerate(zip(hint_titles, hints), 1):
            response[f'hint{i}'] = hint
        return jsonify(response)
    else:
        return jsonify({'error': 'Failed to generate hints'})

def get_ai_response(prompt, option):
    try:
        response = ""
        for chunk in ai71.AI71("api71-api-2fcb29da-a589-4632-9e26-47a71786cd25").chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant for {option} problems.Dont give answer to the problems orther than  {option}Dont give teh exact answer first and  provide meaningful responses only to highly valid queries and dont give resoponse to non-sensical or irrelevant inputs just say sorry it is irreelvant question"
                },
                {
                    "role": "user",
                    "content": prompt + f'''Dont give the direct answer. The answer you give must have the following sections:

                    Give hints to solve the question but do not give the coding solution. After it, give a two-line space.

                    Provide some real-world examples. Give only one example to explain it. Don't give the code. After it, give a two-line space.

                    Give some more topics that enhance the self-learning of the user. After it, give a two-line space.

                    Provide the {option} solution to the question. After it, give a two-line space.

                    Mention the topic name to study to understand the question.
                    '''
                },
            ],
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        return response
    except Exception as e:
        print(f"An error occurred while fetching the AI response: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
