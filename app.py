# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["RESTX_JSON"] = {'ensure_ascii': False, 'indent': 2}
app.url_map.strict_slashes = False
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


@movies_ns.route("/", methods=["GET", "POST", "DELETE"])
class MoviesViews(Resource):
    def get(self):
        all_movies = Movie.query.all()
        result = movies_schema.dump(all_movies)

        if request.args.get("director_id"):
            result = all_movies.filter(Movie.director_id == request.args.get("director_id"))
        if request.args.get("genre_id"):
            result = all_movies.filter(Movie.genre_id == request.args.get("genre_id"))

        return result, 200

    def post(self):
        movie_json = request.json
        new_movie = Movie(**movie_json)

        with db.session.begin():
            db.session.add(new_movie)
            db.session.commit()
        return "фильм добавлен в базу", 201

    def delete(self):
        movies = Movie.query.all()
        db.session.delete(movies)
        db.session.commit()
        return "фильмы удалены", 204


@movies_ns.route("/<int:pk>", methods=["GET", "PUT", "PATCH", "DELETE"])
class MovieViews(Resource):
    def get(self, pk):
        movie = Movie.query.get(pk)
        if movie is None:
            return "Такой фильм не найден", 404
        return movie_schema.dump(movie), 200

    def put(self, pk):
        movie = Movie.query.get(pk)
        if movie is None:
            return "Такой фильм не найден", 404
        req_movie = request.json
        movie.title = req_movie.get("title")
        movie.description = req_movie.get("description")
        movie.trailer = req_movie.get("trailer")
        movie.year = req_movie.get("year")
        movie.rating = req_movie.get("rating")
        movie.genre_id = req_movie.get("genre_id")
        movie.director_id = req_movie.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return f"Фильм {movie.title} обновлен", 204

    def patch(self, pk):
        movie = Movie.query.get(pk)
        if movie is None:
            return "Такой фильм не найден", 404
        req_movie = request.json
        if "title" in req_movie:
            movie.title = req_movie.get("title")
        if "description" in req_movie:
            movie.description = req_movie.get("description")
        if "trailer" in req_movie:
            movie.trailer = req_movie.get("trailer")
        if "year" in req_movie:
            movie.year = req_movie.get("year")
        if "rating" in req_movie:
            movie.rating = req_movie.get("rating")
        if "genre_id" in req_movie:
            movie.genre_id = req_movie.get("genre_id")
        if "director_id" in req_movie:
            movie.director_id = req_movie.get("director_id")

        db.session.add(movie)
        db.session.commit()

        return f"фильм {movie} обновлен", 204

    def delete(self, pk):
        movie = Movie.query.get(pk)
        if movie is None:
            return "Такой фильм не найден", 404
        db.session.delete(movie)
        db.session.commit()

        return f"Фильм с id {pk} удален", 204


if __name__ == '__main__':
    app.run(debug=True)
