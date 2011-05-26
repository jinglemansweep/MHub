from flask import Flask


def generate_app(controller):

    """ Generate Flask web application """

    app = Flask(__name__)

    return app