from flask import current_app, g, Flask
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy
from bson.objectid import ObjectId
from flask_pymongo import PyMongo

def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    current_app.config['MONGO_URI'] = "mongodb+srv://devto:YOI7852j4JgvQmS9@cluster0.w8qa7p4.mongodb.net/devto?retryWrites=true&w=majority"
    
    if db is None:
        db = g._database = PyMongo(current_app).cx['devto']
    return db

db = LocalProxy(get_db)


# $match: Chọn document mong muốn (_id) để truy vấn
# aggregate: truy vấn nâng cao đưa vào pipeline
# pipeline: $match -> $group -> . . . -> tuần tự theo đường ống
def get_user(id):
    try:
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(id)
                }
            }
        ]

        user = db.user.aggregate(pipeline).next()
        return user
    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}

def get_users():
    users = db.user.find({})
    return users

def update_user(id, username):
    response = db.user.update_one(
        { "_id": ObjectId(id) },
        { "$set": { "username": username } }
    )

    return response
  
def delete_user(id):
    response = db.user.delete_one({ "_id": ObjectId(id) })
    return response

def get_acticles():
    # articles = db.article.find({})
    try:
        pipeline = [
            {
                "$lookup": {
                    'from': 'users',
                    'localField': 'user',
                    'foreignField': '_id',
                    'as': 'user'
                }
            }
        ]

        article = db.article.aggregate(pipeline)
        return article
    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}

def get_article(id):
    try:
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(id)
                }
            },
            {
                "$lookup": {
                    'from': 'users',
                    'localField': 'user',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
        ]

        article = db.article.aggregate(pipeline).next()
        return article
    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}

def get_articles_user_id(id):
    try:
        pipeline = [
            {
                "$match": {
                    "user": ObjectId(id),
                }
            },
            {
                "$lookup": {
                    'from': 'users',
                    'localField': 'user',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
        ]

        article = db.article.aggregate(pipeline)
        return article
    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}


def update_article(id, title, body_markdown, cover_image, edited_at):
    response = db.article.update_one(
        { "_id": ObjectId(id) },
        { "$set": { 
                "title": title, 
                "body": body_markdown ,
                "cover_image": cover_image,
                "edited_at": edited_at
            } 
        }
    )

    return response
  
def delete_article(id):
    response = db.article.delete_one({ "_id": ObjectId(id) })
    return response

def get_comment(id):
    try:
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(id)
                }
            }
        ]

        comment = db.comment.aggregate(pipeline).next()
        return comment
    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}

def get_comments():
    comments = db.comment.find({})
    return comments

def update_comment(id, body):
    response = db.comment.update_one(
        { "_id": ObjectId(id) },
        { "$set": { "body": body } }
    )

    return response
  
def delete_comment(id):
    response = db.comment.delete_one({ "_id": ObjectId(id) })
    return response