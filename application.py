from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from geopy.geocoders import Nominatim
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import tweepy

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
            loc=request.form['name']
            geolocator = Nominatim()
            loc_geo = geolocator.geocode(loc)
            if loc_geo is not None:
                return redirect(url_for('results', location=loc_geo))
            else:
                flash('Please enter a valid location.')
        else:
            flash('Error: All the form fields are required. ') 
    return render_template('hello.html', form=form)

@app.route('/results/<location>')
def results(location):
    geolocator = Nominatim()
            loc_geo = geolocator.geocode(loc)
            if loc_geo is not None:
    places = api.reverse_geocode(location.latitude, long= location.longitude)
    a = api.search(q="",geocode="{0},{1},{2}".format(location.latitude,location.latitude,5))

    return a

if __name__ == '__main__':
    app.debug = True
    app.run()


