"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, redirect
from api.models import db, User, Libro, Editorial, Author, MyComics
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


@api.route('/get_all_users', methods=['GET'])
def get_all_users():
    all_users = db.session.execute(select(User)).scalars().all()
    all_users = list(map(lambda user: user.serialize(), all_users))
    response_body = {
        "Users": all_users
    }
    return jsonify(response_body), 200


@api.route('/get_user_byId/<int:user_id>', methods=['GET'])
def get_user_byId(user_id):
     user = db.session.get(User, user_id)
     if user is None:
        return jsonify({'err': "User not found"}), 404

     response_body = {
        "User": user.serialize()
    }
     return jsonify(response_body), 200


@api.route('/create_manga', methods=['POST'])
def create_manga():
    body = request.get_json()
    required_fields = ['title', 'pages', 'isbn',
        'img', 'author_id', 'editorial_id']
    if not all(field in body for field in required_fields):
        return jsonify({'err': 'Bad request, missing fields'}), 400

    search_exist = select(Libro).where(Libro.title == body['title'])
    already_exist = db.session.execute(search_exist).scalar_one_or_none()

    if (already_exist):
        return jsonify({"error": "User already exist"}), 401

    manga = Libro()
    manga.title = body['title']
    manga.pages = body['pages']
    manga.author_id = body['author_id']
    manga.editorial_id = body['editorial_id']
    manga.img = body['img']
    manga.isbn = body['isbn']
    db.session.add(manga)
    db.session.commit()

    return jsonify({'Ok': "Manga created"}), 200


@api.route('/get_all_manga', methods=['GET'])
def get_all_manga():
    all_manga = db.session.execute(select(Libro)).scalars().all()
    all_manga = list(map(lambda manga: manga.serialize(), all_manga))

    response_body = {
        "Libro": all_manga
    }
    return jsonify(response_body), 200


@api.route('/get_manga_by_id/<int:libro_id>')
def get_manga_by_id(libro_id):
    manga = db.session.get(Libro, libro_id)

    if manga is None:
        return jsonify({'err': "Manga not found"}), 404

    response_body = {
        "User": manga.serialize()
    }
    return jsonify(response_body), 200



@api.route('/create_editorial', methods = ['POST'])
def create_editorial():
    body = request.get_json()

    if 'name' not in body:
        return jsonify({'err':'Bad request, missing fields'}),400
    
    search_exists = select(Editorial).where(Editorial.name == body['name'])
    already_exits = db.session.execute(search_exists).scalar_one_or_none()

    if(already_exits):
        return jsonify({'err':'Editorial already exists'}),401
    
    editorial = Editorial()
    editorial.name = body['name']
    db.session.add(editorial)
    db.session.commit()

    return jsonify({'Ok': "Editorial created"}), 200

@api.route('/get_all_editorials', methods = ['GET'])
def get_all_editorial():
    all_editorial = db.session.execute(select(Editorial)).scalars().all()
    all_editorial = list(map(lambda editorial : editorial.serialize(), all_editorial))

    response_body = {
        "Editorial": all_editorial
    }

    return jsonify(response_body), 200

@api.route('/get_editorial_by_id/<int:editorial_id>')
def get_editorial_by_id(editorial_id):

    edit = db.session.get(Editorial, editorial_id)

    if (edit is None):
        return jsonify({'err': 'Editorial not found'}),404
    
    response_body = {
        "Editorial" : edit.serialize()
    }

    return jsonify(response_body), 200




@api.route('/create_author', methods= ['POST'])
def create_author():
    body = request.get_json()

    if 'name' not in body:
        return jsonify({'err':'Bad request, missing fields'}),400
    
    search_exits = select(Author).where(Author.name == body['name'])
    already_exits = db.session.execute(search_exits).scalar_one_or_none()

    if (already_exits):
        return jsonify({'err': 'Author already exists'}),401
    
    author = Author()
    author.name = body['name']
    db.session.add(author)
    db.session.commit()

    return jsonify({'ok': 'Author created'}), 201

@api.route('/get_all_author', methods = ['GET'])
def get_all_author():
    all_author = db.session.execute(select(Author)).scalars().all()
    all_author = list(map(lambda author: author.serialize(), all_author))

    response_body = {
        "Author" : all_author
    }
    return jsonify(response_body), 201

@api.route('/get_author_byId/<int:author_id>', methods = ['GET'])
def get_author_byId(author_id):
    author = db.session.get(Author, author_id)

    if (author is None):
        return jsonify({'err': 'Author not exists'}),404
    
    response_body = {
        "Author" : author.serialize()
    }
    return jsonify(response_body), 200

@api.route('/create_My_manga', methods = ['POST'])
def create_my_manga():
    body  = request.get_json()

    if ('libro_id' not in body or 'user_id' not in body):
        return jsonify({'err': 'Bad request'}), 401
    
    myManga = MyComics()
    myManga.libro_id = body['libro_id']
    myManga.user_id = body['user_id']
    db.session.add(myManga)
    db.session.commit()

    return jsonify({'ok': 'MyManga created'}), 201

@api.route('/get_all_myManga', methods = ['GET'])
def get_all_myManga():
    all_myManga = db.session.execute(select(MyComics)).scalars().all()
    all_myManga = list(map(lambda mymanga : mymanga.serialize(), all_myManga))

    response_body = {
        "myManga" : all_myManga
    }

    return jsonify(response_body), 201

