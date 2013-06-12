var fs = require('fs');

var express = require('express');
var app = express();

// Initially the app was based on json but brython's deserializer
// is broken for now so we concatenate manually comments
//var comments = [{author: 'Pete Hunt', text: 'Hey there!'}];
var comments = 'Hello Web5! — Edward Snowden';

app.use('/', express.static(__dirname));
app.use(express.bodyParser());

app.get('/comments', function(req, res) {
  res.setHeader('Content-Type', 'application/json');
  res.send(comments);
});

app.post('/comments', function(req, res) {
  comments = comments + '@@@' + req.body['comment'];
  res.setHeader('Content-Type', 'application/json');
  res.send(comments);
});

app.listen(3000);
