from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from geopy.geocoders import Nominatim
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import tweepy
import twitter as tw
import searching as srch

app = Flask(__name__)
app.config.from_object('config')

auth = tweepy.OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
auth.set_access_token(app.config['ACCESS_TOKEN_KEY'], app.config['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)


class ReusableForm(Form):
    name = TextField('Location: ', validators=[validators.required()])

@app.route('/main', methods=['GET', 'POST'])
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

    tweets = tw.get_tweets_from_location(api, location)
    pref = {"Clinton":0, "Trump":0, "Sanders":0, "Cruz":0}
    if tweets:
        users = tw.get_users_from_tweets(api, tweets)
        if users:
            corpus = tw.get_tweets_from_users(api, users)
            for u in corpus:
                nxt = srch.get_candidate_pref(u)
                pref = { k: pref.get(k, 0) + nxt.get(k, 0) for k in set(pref) & set(nxt) }
            #guess, res = srch.predict_candidate(corpus, 10)
            #res = srch.get_area_percentages(corpus, 7, 4)
    print pref
    factor=1.0/(sum(pref.itervalues()) + 1)
    normalised_pref = {k: v*factor for k, v in pref.iteritems() }

    res = {"res_party": { "Clinton": normalised_pref["Clinton"], "Sanders": normalised_pref["Sanders"], "Trump": normalised_pref["Trump"] + normalised_pref["Cruz"] }, "res_dem":{ "Clinton": normalised_pref["Clinton"], "Sanders": normalised_pref["Sanders"]}, "res_rep":{ "Cruz": normalised_pref["Cruz"] , "Trump": normalised_pref["Trump"]}, "winners":{"party": "DEM", "dem": "Clinton", "rep": "Trump"}}
    return render_template('results.html', res=res, city=location, form=form)

if __name__ == '__main__':
    app.debug = True
    app.run()
