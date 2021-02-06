from blog import create_app  #, db  #, manager
'''from blog.models import (User, Post, Comment, Message, PostLike, CommentLike,
                         Notification, Group)'''

app = create_app()


'''@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post, Comment=Comment, Message=Message,
                Follow=Follow, PostLike=PostLike, CommentLike=CommentLike,
                Notification=Notification)'''


if __name__ == '__main__':
    app.run(debug=True)
