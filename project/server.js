var fs = require('fs');
var bodyParser = require('body-parser');
var child_process = require('child_process');
var express	= require("express");
var app	= express();

app.use(express.static("."));
app.use(express.static("public"));
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/',function(req,res){
    res.sendfile("public/test.html");
    let time = Date()
    console.log("Connecting at", time.toLocaleString())
});

app.get('/start', function (req, res) {
    console.log('\nStart processing')

    let processer = child_process.exec('python main.py ',
        function (error, stdout, stderr) {
            if (error){
                console.log(stdout);
                console.log(error.stack);
                console.log('Error code: '+error.code);
                console.log('Signal received: '+error.signal);
                res.json({code:0});
            }
            else {
                console.log('Processing successfully');
                res.json({code:1, stdout:stdout})
            }
        });

    processer.on('exit', function () {
        console.log('Program Completed');
    });
})

app.post('/submitData', function (req, res) {
    let data = req.body
    console.log(data)
    fs.writeFile('data.json', JSON.stringify(data, null, '\t'), function (err) {
        if (! err){
            console.log('data store')
        }
        else{
            console.log(err)
        }
    });
})

app.listen(8000,function(){
    console.log("Working on port 8000");
});