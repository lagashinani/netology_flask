from flask import Flask, jsonify, request, abort, g
from flask_httpauth import HTTPBasicAuth

from sqlalchemy.orm import sessionmaker

from database_setup import Post, Base, engine, UserNetology as User
from validators import validate, POST

app = Flask(__name__)
auth = HTTPBasicAuth()


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def post_alchemy_serializer(obj):
    return {
        'id': obj.id,
        'title': str(obj.title),
        'description': str(obj.description),
        'author': db_session.query(User).get(obj.user_id).email,
        'datetime_creation': str(obj.datetime_creation)
    }


@auth.verify_password
def verify_password(email, password):
    user = db_session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/api/v1/users', methods=['POST'])
def new_user():
    data = request.json
    email = data.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400)
    if db_session.query(User).filter_by(email=email).first() is not None:
        abort(400)
    user = User(email=email)
    user.hash_password(password)
    db_session.add(user)
    db_session.commit()
    return jsonify({'username': user.email}), 201,


@app.route('/api/v1/posts', methods=['GET', ])
def get_posts():
    return jsonify([post_alchemy_serializer(post) for post in db_session.query(Post).all()])


@app.route('/api/v1/posts/<int:post_id>', methods=['GET', ])
def get_post(post_id):
    post_obj = db_session.query(Post).get(post_id)
    if post_obj is None:
        return jsonify({'error': 'no such post'}), 404
    return jsonify(post_alchemy_serializer(post_obj))


@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE', ])
@auth.login_required
def delete_post(post_id):
    post_obj = db_session.query(Post).get(post_id)
    if post_obj is None:
        return jsonify({'error': 'no such post'}), 404
    db_session.delete(post_obj)
    db_session.commit()
    return jsonify({'status': 'ok'})


@app.route('/api/v1/posts', methods=['POST', ])
@auth.login_required
@validate(POST)
def add_post():
    data = request.get_json()
    post = Post(title=data['title'], description=data['description'], user_id=g.user.id)
    db_session.add(post)
    db_session.commit()
    return jsonify({'status': 'ok'})

