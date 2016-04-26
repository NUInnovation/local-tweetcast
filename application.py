from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
app = Flask(__name__)
app.config['SECRET_KEY'] = '<the super secret key comes here>'

class ReusableForm(Form):
    name = TextField('Location: ', validators=[validators.required()])

@app.route('/main', methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        loc=request.form['name']
        print(loc)
        if form.validate():
            # Save the comment here.
            flash('Hello ' + loc)
        else:
            flash('Error: All the form fields are required. ')
        return redirect(url_for('results', location=loc))
    return render_template('hello.html', form=form)

@app.route('/results/<location>')
def results(location):
    return location
if __name__ == '__main__':
    app.debug = True
    app.run()