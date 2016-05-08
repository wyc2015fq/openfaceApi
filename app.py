'''
    Face detection and localization
    ---------------------------

    Accepts a flattened image and returns bounding boxes for faces:

    Run ./test-api.py to test API

'''

from __future__ import division
import argparse
import logging
from flask import Flask, make_response, jsonify
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.restful.representations.json import output_json
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import sys
sys.path.append('/src/source_files')
from face_detect import face_detector

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser(description='LangAgnosticAge')
    parser._optionals.title = "Options"
    parser.add_argument('-p', '--port', help='Specify port for API to listen on.',  type=str, required=False, default=5000)
    return parser.parse_args()


class ClassifierAPI(Resource):
    def __init__(self):

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('image', type=list, location='json')
        self.reqparse.add_argument('dim', type=list, location='json')
        self.fd = face_detector()

        super(ClassifierAPI, self).__init__()

    def post(self):
        args    = self.reqparse.parse_args()
        img = args['image']
        dim = args['dim']
        return make_response(jsonify(self.fd.score_img(img, dim)), 200)


class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    logger.info('Starting service.')
    args = parse_arguments()

    api.add_resource(ClassifierAPI, '/api/score')
    api.add_resource(HealthCheck, '/api/health')

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(args.port)
    IOLoop.instance().start()
