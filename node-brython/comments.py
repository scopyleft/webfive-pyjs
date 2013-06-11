import html
import json

# Hacking editor
doc = doc
log = log
ajax = ajax
alert = alert
timeout = 4  # seconds
url = "comments.json"


def on_complete(req):
    if req.status == 200 or req.status == 0:
        comments = doc["comments"]
        for comment_data in json.parse(req.text):
            log(comment_data)
            # Bug: comment_data.author doesn't work...
            author = req.text
            text = req.text
            comment = html.DIV(Class="comment")
            comment <= html.H2(author, Class="commentAuthor")
            comment <= html.SPAN(text)
            comments <= comment
        doc["comments"].html = comments.html
    else:
        doc["comments"].html = "error " + req.text


def err_msg():
    doc["comments"].html = "server didn't reply after %s seconds" % timeout


def load_comments():
    req = ajax()
    req.on_complete = on_complete
    req.set_timeout(timeout, err_msg)
    req.open('GET', url, True)  # Check why True!
    req.send()


def post_comment(event):
    req = ajax()
    req.on_complete = on_complete
    req.set_timeout(timeout, err_msg)
    req.open('POST', url, True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    req.send({
        'author': doc["author"].value,
        'text': doc["text"].value})
    alert('Manual event.preventDefault(). Press esc twice to stay here.')


load_comments()
doc["submitButton"].onclick = post_comment
