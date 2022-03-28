from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
from flask_pymongo import pymongo
import app.dbConfig as database
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

post_series_args = reqparse.RequestParser()

post_series_args.add_argument("id", type=int, help="ERROR id value needs to be an integer", required=True)
post_series_args.add_argument( "series_name", type=str, help="ERROR first_name is required", required=True)
post_series_args.add_argument( "series_description", type=str, help="ERROR last_name is required", required=True)
post_series_args.add_argument("logo", type=str, help="ERROR you need to add the image url", required=True)

patch_series_args = reqparse.RequestParser()

patch_series_args.add_argument("id", type=int, help="ERROR id value needs to be an integer", required=True)
patch_series_args.add_argument( "series_name", type=str, help="ERROR first_name is required", required=True)
patch_series_args.add_argument( "series_description", type=str, help="ERROR last_name is required", required=True)
patch_series_args.add_argument("logo", type=str, help="ERROR you need to add the image url", required=True)


class Test(Resource):

    def get(self):
        return jsonify({"message":"You are connected"})


class Series(Resource):

    def get(self):
        response = list(database.db.series.find())
        series = []
        for serie in response:
            del serie['_id']
            series.append(serie)
        return jsonify({'results':series})


class Serie(Resource):

    def get(self, id):
        response = database.db.series.find_one({'id':id})
        del response['_id']
        return jsonify(response)

    def post(self):
        args = post_series_args.parse_args()
        self.abort_if_id_exist(args['id'])
        database.db.series.insert_one({
            'id': args['id'],
            'series_name': args['series_name'],
            'series_description': args['series_description'],
            'logo': args['logo'],
        })
        return jsonify(args)

    def put(self, id):
        args = post_series_args.parse_args()
        self.abort_if_not_exist(id)
        database.db.series.update_one(
            {'id':id},
            {'$set':{
                'id': args['id'],
                'series_name': args['series_name'],
                'series_description': args['series_description'],
                'logo': args['logo'],
            }}
        )
        return jsonify(args)

    def patch(self, id):
        serie = self.abort_if_not_exist(id)
        args = patch_series_args.parse_args()

        database.db.series.update_one(
            {'id':id},
            {'$set':{
                'id': args['id'] or serie['id'],
                'series_name': args['series_name'] or serie['series_name'],
                'series_details': args['series_details'] or serie['series_details'],
                'logo': args['logo'] or serie['logo'],
            }
        })

        serie = self.abort_if_not_exist(id)
        del serie['_id']
        return jsonify(serie)
    
    def delete(self, id):
        serie = self.abort_if_not_exist(id)
        database.db.series.delete_one({'id':id})
        del serie['_id']
        return jsonify({'deleted serie': serie})

    def abort_if_id_exist(self, id):
        if database.db.series.find_one({'id':id}):
            abort(
                jsonify({'error':{'406': f"The serie with the id: {id} already exist"}}))

    def abort_if_not_exist(self, id):
        serie = database.db.series.find_one({'id':id})
        if not serie:
            abort(
                jsonify({'error':{'404': f"The serie with the id: {id} not found"}}))
        else:
            return serie



api.add_resource(Test,'/test/')
api.add_resource(Series,'/series/')
api.add_resource(Serie, '/serie/', '/serie/<int:id>/')