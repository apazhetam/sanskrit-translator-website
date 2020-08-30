#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
path_to_packages = os.path.abspath(os.path.join("venv/lib/site-packages"))
sys.path.insert(0, path_to_packages)

from flask import Flask, render_template, jsonify, request
from flask_wtf import FlaskForm
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
import requests
import json
import re
from flask import Flask, jsonify, request
from waitress import serve
from onmt.translate import TranslationServer, ServerModelError
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
pagedown = PageDown(app)
STATUS_OK = "ok"
STATUS_ERROR = "error"
config_file = "available_models/conf.json"
translation_server = TranslationServer()
translation_server.start(config_file)

class PageDownFormExample(FlaskForm):
    pagedown = PageDownField('')
    submit = SubmitField('Translate')

def translate(inputs):
    # inputs = request.get_json(force=True)
    debug = False
    out = {}
    try:
        trans, scores, n_best, _, aligns = translation_server.run(inputs)
        assert len(trans) == len(inputs) * n_best
        assert len(scores) == len(inputs) * n_best
        assert len(aligns) == len(inputs) * n_best

        out = [[] for _ in range(n_best)]
        for i in range(len(trans)):
            response = {"src": inputs[i // n_best]['src'], "tgt": trans[i],
                        "n_best": n_best, "pred_score": scores[i]}
            if len(aligns[i]) > 0 and aligns[i][0] is not None:
                response["align"] = aligns[i]
            out[i % n_best].append(response)
    except ServerModelError as e:
        model_id = inputs[0].get("id")
        translation_server.models[model_id].unload()
        out['error'] = str(e)
        out['status'] = STATUS_ERROR
    return out

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PageDownFormExample()
    text = None
    language = "en-fr" #Default
    if form.validate_on_submit():
        source = form.pagedown.data
        source = re.sub(r"([?.!,:;¿])", r" \1 ", source)
        source = re.sub(r'[" "]+', " ", source)
        source = re.sub(r"m ", "M ", source)        #changes "aham" to "ahaM"

        language = str(request.form.get('lang'))
        data = [{"src": source, "id": 100}]
        response = translate(data)
        t = type(response)
        text = response[0][0]['tgt']
        text = re.sub(r" ([?.!,:،؛؟¿])", r"\1", text)
    else:
        form.pagedown.data = ('namaste.')
    return render_template('index.html', form=form, language=language, text=text)




if __name__ == '__main__':
    app.run(debug=True)
