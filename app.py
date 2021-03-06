# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["RESTX_JSON"] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()


@movies_ns.route("/", methods=["GET"])
class MoviesViews(Resource):
    def get(self):
        all_movies = Movie.query.all()
        result = movies_schema.dump(all_movies)
        return result, 200


@movies_ns.route("/<int:pk>", methods=["GET"])
class MovieViews(Resource):
    def get(self, pk):
        movie = Movie.query.get(pk)
        if movie is None:
            return "Такой фильм не найден", 404
        return movie_schema.dump(movie), 200


if __name__ == '__main__':
    app.run(debug=True)
