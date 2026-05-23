from flask import Flask, render_template

app = Flask(__name__)

PROJECTS = [
    {
        'name': 'Personal Website',
        'description': 'Website to host personal content and projects.',
    },
    {
        'name': 'Music Generating Neural Network',
        'description': 'Generative Adversarial Network and Recurrent Neural Network that'
                       ' produced music after learning on MIDI data.',
    },
]


@app.route('/')
def home():
    return render_template('index.html', projects=PROJECTS)


if __name__ == '__main__':
    app.run(debug=True)
