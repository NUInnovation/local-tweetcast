from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

app = Flask(__name__)
app.config.from_object('config')
