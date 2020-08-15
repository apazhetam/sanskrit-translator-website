#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath("c:/users/foliage/downloads/opennmt-gui-master/venv/lib/site-packages"))

from flask import Flask, render_template, jsonify, request
from flask_wtf import FlaskForm
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
import requests
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
pagedown = PageDown(app)


class PageDownFormExample(FlaskForm):
    pagedown = PageDownField('Type the text you want to translate and click "Translate".')
    submit = SubmitField('Translate')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = PageDownFormExample()
    text = None
    output = None
    language = "en-fr" #Default
    if form.validate_on_submit():
        source = form.pagedown.data
        # source = re.sub(r"([?.!,:;¿])", r" \1 ", source)
        # source = re.sub(r'[" "]+', " ", source)

        print(source)

        # arglength = len(sys.argv)

        # if arglength <= 2:
        ruleid = str(100)
        # else:
        #     ruleid = sys.argv[2]

        # req = sys.argv[1]

        url = "http://127.0.0.1:5000/translator/translate"
        data='[{"src": "' + source +'", "id": ' + ruleid +'}]'
        # data = [{"src": source, "id": 100}]
        output = requests.post(url, data=data).text

        myjson = json.loads(output)

        # with open(output, "r") as read_file:
        #    myjson = json.load(read_file)

        input = myjson[0][0]['src']
        output = myjson[0][0]['tgt']

        print(input)
        print(output)


        text = jsn[0][0]['tgt']
        # text = "hi"
        text = re.sub(r" ([?.!,:،؛؟¿])", r"\1", text)
    else:
        form.pagedown.data = ('This is a very simple test.')
    return render_template('index.html', form=form, language=language, text=output)




if __name__ == '__main__':
    app.run(debug=True)
