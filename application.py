from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
app = Flask(__name__)

class ReusableForm(Form):
    name = TextField('Location: ', validators=[validators.required()])

@app.route('/main', methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        location=request.form['location']
        print(location)
        if form.validate():
            # Save the comment here.
            flash('Hello ' + location)
        else:
            flash('Error: All the form fields are required. ')

    return render_template('hello.html', form=form)

if __name__ == '__main__':
    app.run()