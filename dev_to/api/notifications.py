
#   sender: { type: Schema.Types.ObjectId, ref: "User" },
#   receiver: { type: Schema.Types.ObjectId, ref: "User" },
#   date: { type: Date, default: Date.now },
#   post: { type: Schema.Types.ObjectId, ref: "Post" },
#   comment: { type: Schema.Types.ObjectId, ref: "Comment" },
#   notificationType: {
#     type: String,
#     enum: ["like", "comment", "follow"],
#   },
#   read: {
#     type: Boolean,
#     default: false,
#   },
from datetime import datetime
from flask import Blueprint, request
from . import db
from bson.objectid import ObjectId

# Blueprint
notification_api_v1  = Blueprint('notification_api_v1', __name__)

@notification_api_v1.route('/')
def index():
    return 'api/v1 routes notification'

@notification_api_v1.route('/likeNotification', methods=['POST'])
def likeNotification():
    # Receive request from a type json
    post_data = request.get_json()

    createdNotification = {
       'notificationType': 'like',
       'sender': ObjectId(post_data.get('senderId')),
       'receiver': ObjectId(post_data.get('receiverId')),
       'post': ObjectId(post_data.get('postId')),
       'date': datetime.now()
    }

    notificationId = db.Notification.insert(createdNotification)
    return str(notificationId)