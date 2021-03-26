var fs = require('fs');
var express	= require("express");
var app	= express();

app.use(express.static("."));

app.get('/',function(req,res){
    res.sendfile("xml.html");
    let time = Date()
    console.log("Connecting at", time.toLocaleString())
});

app.get('/test', function (req, res) {
    console.log(req.query)
})

app.listen(8000,function(){
    console.log("Working on port 8000");
});