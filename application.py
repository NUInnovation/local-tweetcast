from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, copy_current_request_context
from geopy.geocoders import Nominatim
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import tweepy
import twitter as tw
import searching as srch
import threading

app = Flask(__name__)
app.config.from_object('config')

auth = tweepy.OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
auth.set_access_token(app.config['ACCESS_TOKEN_KEY'], app.config['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)


class ReusableForm(Form):
    name = TextField('Location: ', validators=[validators.required()])

@app.route('/', methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        if form.validate():
            # Save the comment here.
            loc= request.form['name']
            if loc is not None:
                return redirect(url_for('results', location=loc))
            else:
                flash('Please enter a valid location.')
        else:
            flash('Error: All the form fields are required. ')
    return render_template('hello.html', form=form)

@app.route('/results/<location>', methods=['GET', 'POST'])
def results(location):
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        if form.validate():
            # Save the comment here.
            loc= request.form['name']
            if loc is not None:
                return redirect(url_for('results', location=loc))
            else:
                flash('Please enter a valid location.')
        else:
            flash('Error: All the form fields are required. ')

    cache = srch.get_area_candidate_counts_from_cache(location)
    app.logger.debug(cache)
    if cache is not None:
        res = cache
        return render_template('results.html', res=res, city=location, form=form)
    else:
        threading.Thread(target=lambda: srch.cache_area_results(location, 10, 5)).start()
        return redirect(url_for('waiter', location=location))
    return render_template('results.html', res=res, city=location, form=form)

@app.route('/waiter/<location>')
def waiter(location):
    return render_template('waiter.html', city=location)

@app.route('/checkincache/<location>')
def checker(location):
    cache = srch.get_area_candidate_counts_from_cache(location)
    if cache is not None:
        return 'Yes'
    else:
        return 'No'

if __name__ == '__main__':
    app.debug = True
    # uncomment this line for heroku
    # app.run(host="0.0.0.0", port=80)
    app.run()
