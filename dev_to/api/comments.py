from datetime import datetime
from http import HTTPStatus
import os
import json
import re
import nltk
import emoji
from pyvi import ViTokenizer
from flask import Blueprint, jsonify, make_response, request
from bson import json_util
from . import db, get_comment, get_comments, update_comment, delete_comment
from bson.objectid import ObjectId
from .utils.obj_dict import obj_dict

comment_api_v1  = Blueprint('comments_api_v1', __name__)

def remove_special_text(tweet):
    tokens = re.sub(r'(http\S+)|(@\S+)|RT|\#|!|:|\.|,', ' ', tweet)
    
    return tokens

def load_dictionary(filename):
    vndict = {}
    dict_file = open(filename, 'r', encoding="utf-8").read().split('\n')
    for line in dict_file:
        if line == "":
            continue
        line = line.split('\t')
        score = [int(line[1]), int(line[2])]
        vndict[line[0].strip()] = score
    return vndict

def load_boost_word(filename):
    boost_word = {}
    boost_file = open(filename, 'r', encoding="utf-8").read().split('\n')
    for line in boost_file:
        if line == "":
            continue
        word, score = line.partition("\t")[::2]
        # print(word, score)
        boost_word[word.strip()] = int(score)
    return boost_word

def boost_word_score(i, tokens):
    
    listword = []

    if i < len(tokens)-1:
        after_word = tokens[i+1]
        listword.append(after_word)
        if i< len(tokens) -2:
            after_word2 = tokens[i+2]
            listword.append(after_word2)
    if i>0:
        prev_word = tokens[i-1]
        listword.append(prev_word)
        if i>1:
            prev_word2 = tokens[i-2]
            listword.append(prev_word2)
    
    list_score = []
    for word in listword:
        if word in boost_dict:
            list_score.append(boost_dict[word])
    score = sum(list_score)
    if score == 0:
        score = 1 
    
    return score

def evalue_score(tokens):
    pos_score = 0
    neg_score = 0
    for i,word in enumerate(tokens):
        if word in vndict:
            pos_score += (vndict[word][0] * boost_word_score(i, tokens) )
            neg_score += (vndict[word][1] * boost_word_score(i, tokens))
            # print(word, boost_word_score(i, tokens), "Pos: ", pos_score, "Neg: ", neg_score)
    
    return pos_score , neg_score

def pre_process(tweet):
    
    tweet = ViTokenizer.tokenize(tweet)             # Tokenizer Vietnamese
    tokens = remove_special_text(tweet)             # Remove special text
    tokens = emoji.demojize(tokens)                 # Convert emojition to text
    tokens = tokens.lower()                         # To lowercase
    tokens = tokens.split()                         # Tokenize tweet
    
    return tokens

#Load file:
vndict = load_dictionary(os.path.abspath(os.path.join('dev_to/dictionary/vndict.txt')))               # Main dictinary
print('VNDICT', vndict)
emoji_dict = load_dictionary(os.path.abspath(os.path.join('dev_to/dictionary/emoji-dict.txt')))   # Emoji dictionary
boost_dict = load_boost_word(os.path.abspath(os.path.join('dev_to/dictionary/boost-words.txt')))  # Boost dictionary

# Update dictionary with emoji score:
# vndict.update(emoji_dict)

@comment_api_v1.route('/')
def index():
    return 'api/v1 routes comments'

@comment_api_v1.route('/createComment', methods=['POST'])
def api_comments():
    """
    - Posts a comment about a article.
    - This endpoint allows the client to retrieve all comments belonging 
    to an article or podcast episode as threaded conversations.
    - It will return the all top level comments with their nested comments 
    as threads. See the format specification for further details.
    """

    # Receive request from a type json
    post_data = request.get_json()
    # Article match id pipeline
    pipeline = [
        {
            "$match": { 
                "_id": ObjectId(post_data.get('_idPost'))
             }
        }
    ]

    tokens = pre_process(post_data.get('body'))
    pos, neg = evalue_score(tokens)
    isPositive = True

    if (pos - neg <= 0):
        isPositive = bool(neg)
    elif (pos - neg > 0): isPositive = bool(pos)

    # Schema comment
    comments_schema = {
        'date': datetime.now(),
        'body': post_data.get('body'),
        'parent_post': ObjectId(post_data.get('_idPost')),
        'parent_id': ObjectId(post_data.get('_idParent')) if post_data.get('_idParent') != "" else "",
        'author': ObjectId(post_data.get('userId')),
        'isPositive': isPositive,
        'likes': [],
        'replies': []
    }

    # Insert comments_schema to MongoDB
    commentId = db.comment.insert_one(comments_schema)

    if (post_data.get('_idParent') != ""):
        db.comment.find_one_and_update(
            { "_id": ObjectId(post_data.get('_idParent')) },
            { "$addToSet": { "replies": ObjectId(commentId.inserted_id) } },
            { "new": True }
        )

    return {
        'state': 'Done'
    }

@comment_api_v1.route('/getCommentById/<id>', methods=['GET'])
def getCommentById(id):
    comment = get_comment(id)
    if comment is None:
        return jsonify({
            'error': 'Not found'
        }), 400
    elif comment == {}:
        return jsonify({
            'error': 'Uncaught general exception'
        }), 400
    else: 
        return jsonify(json.loads(json_util.dumps({
            'comment': comment
        })))

@comment_api_v1.route('/getAllComment', methods=['POST'])
def get_all_comments():
    try:
        # Receive request from a type json
        post_data = request.get_json()
        # Article match id pipeline

        if post_data.get('_idParent') != "":
            comment = db.comment.aggregate([
                {
                    "$match": { 
                        "parent_post": ObjectId(post_data.get('_idPost')), 
                        "parent_id": ObjectId(post_data.get('_idParent')) 
                    }
                },
                {
                    "$lookup": {
                        'from': 'users',
                        'localField': 'author',
                        'foreignField': '_id',
                        'as': 'author'
                    }
                }
            ])
        else:
            comment = db.comment.aggregate([
                {
                    "$match": { "parent_post": ObjectId(post_data.get('_idPost')), "parent_id": "" }
                },
                {
                    "$lookup": {
                        'from': 'users',
                        'localField': 'author',
                        'foreignField': '_id',
                        'as': 'author'
                    }
                }
            ])

        return jsonify(json.loads(json_util.dumps({
            'comment': comment
        })))

    except (StopIteration) as _:
        return None
    except Exception as e:
        return {}

@comment_api_v1.route('/updateComment/<id>', methods=['PUT'])
def api_update_comment(id):
    # Receive request from a type json
    post_data = request.get_json()

    update_comment(id, post_data.get('body'))
    return {
        'status': 'successfull'
    }

@comment_api_v1.route('/deleteComment/<id>', methods=['DELETE'])
def api_delete_comment(id):
    delete_comment(id)
    return {
        'status': 'successfull'
    }
