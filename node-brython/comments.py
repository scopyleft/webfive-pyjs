import html

# Hacking editor
doc = doc
log = log
ajax = ajax
alert = alert

timeout = 4  # seconds


def on_complete(req):
    if req.status == 200 or req.status == 0:
        doc["comments"].html = ''
        comments = doc["comments"]
        for comment_data in req.text.split('@@@'):
            comment = html.DIV(Class="comment")
            comment <= html.H3(comment_data, Class="commentAuthor")
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
    req.open('GET', "comments", True)  # Check why True!
    req.send()


def post_comment(event):
    req = ajax()
    req.on_complete = on_complete
    req.set_timeout(timeout, err_msg)
    req.open('POST', event.target.form.action, True)
    req.set_header('content-type', 'application/x-www-form-urlencoded')
    comment = doc["text"].value + ' — ' + doc["author"].value
    req.send({'comment': comment})
    event.preventDefault()


load_comments()
doc["submitButton"].onclick = post_comment
