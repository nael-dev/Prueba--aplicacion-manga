"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, redirect
from api.models import db, User, Libro
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import select, exc
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError



ph = PasswordHasher()
api = Blueprint('api', __name__)


# Allow CORS requests to this API
CORS(api)


@api.route('/signup', methods=['POST'])
def create_user():
    body = request.get_json()

    required_fields = ['email', 'password']
    if not all(field in body for field in required_fields):
        return jsonify({'err': 'Bad request, missing fields'}), 400

    search_exist = select(User).where(User.email == body['email'])
    already_exist = db.session.execute(search_exist).scalar_one_or_none()

    if (already_exist):
        return jsonify({"error": "User already exist"}), 401

    try:
        hashed_password = ph.hash(body['password'])
    except Exception as e:
        return jsonify({'error': 'Failed to hash password'}), 500

    user = User()
    user.email = body['email']
    user.password = hashed_password
    db.session.add(user)
    db.session.commit()

    return jsonify({'Ok': "User created"}), 200


@api.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    if 'email' not in body or 'password' not in body:
        return jsonify({'err': 'Bad request'}), 400

    email = body['email']
    password = body['password']
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"err": " User not exist"}), 404

    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        return jsonify({'err': 'Invalid password'}), 401
    except Exception:
        return jsonify({'err': 'Error verifying password'}), 500

    token = create_access_token(identity=str(user.id))
    is_admin = user.email == 'admin@admin.com'

    return jsonify({'token': token,
                    'is_admin': is_admin
                    }), 200


@api.route('/create_manga', methods=['POST'])
def create_manga():
    body = request.get_json()
    required_fields = ['title','pages','isbn','img','author_id','editorial_id']
    if not all(field in body for field in required_fields):
        return jsonify({'err': 'Bad request, missing fields'}), 400
    
    search_exist = select(Libro).where(Libro.title == body['title'])
    already_exist = db.session.execute(search_exist).scalar_one_or_none()

    if (already_exist):
        return jsonify({"error": "User already exist"}), 401
    
    manga = Libro()
    manga.title = body['title']
    manga.pages = body['pages']
    manga.author_id= body['author_id']
    manga.editorial_id= body['editorial_id']
    manga.img = body['img']
    manga.isbn= body['isbn']
    db.session.add(manga)
    db.session.commit()

    return jsonify({'Ok': "Manga created"}), 200

    
