# Local Tweetcast

### Team Members

Shawn Caeiro, Sam Cohen, Athif Wulandana

### What if Twitter decided this election?

Local Tweetcast is a data-heavy application that predicts the outcome of political elections based solely on the local's twitter sentiment.
 
### How it Works

Users will enter a location their are intersted in seeing the politic preferences of. The application will take a sample of tweeters located in that local. From those tweeters, our system scours their most recent tweets, and looks for candidate leaning terms. From this, a city political composition is created. This dashboard of information is then displayed to the user.

## How to Run App

### Through Heroku Service

Go to https://localtweetcast.herokuapp.com

### Locally

1) Clone repository locally.
2) Setup virtual environment with the command
```
pip install -r requirements.txt
```
3) Run application using command
```python
python application.py
```
4) Go to address given in terminal.

## Files of Interest

### application.py

Contains code for the creating the flask application and url directs.

### twitter.py

Contains all the code for interacting with the Twitter API

### searching.py

Contains the meat of the ML algorithms used for matching.

## Tech Architecture

* Python
* Flask
* gensim
* Tweepy

## Next Steps

#### Long Term

* Create more detailed views for the location's politic's dashboard
* Fine tune our algoirhtm for determining politcal preference
* Matching Places to voting districts
* Trying to predict local elections.
