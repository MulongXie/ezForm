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

app.get('/process', function (req, res) {
    console.log('\nStart processing')

    let form_img_file = './data/input/3.jpg'
    let input_path_split = form_img_file.split('/');
    let result_dir = './data/output/' + input_path_split[input_path_split.length - 1].split('.')[0];
    let detection_result_img = result_dir + '/detection.jpg'
    let generation_page = result_dir + '/xml.html'

    let processer = child_process.exec('python main.py ' + form_img_file,
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
                res.json({code:1, stdout:stdout, result_img:detection_result_img, result_page:generation_page})
            }
        });
    processer.on('exit', function () {
        // console.log('Program Completed');
    });
})

app.post('/submitData', function (req, res) {
    let data = req.body

    let form_img_file = './data/input/3.jpg'
    let input_path_split = form_img_file.split('/');
    let result_dir = './data/output/' + input_path_split[input_path_split.length - 1].split('.')[0];
    let filled_data_file = result_dir + '/input_data.json'
    let filled_form_img = result_dir + '/filled.jpg'

    // store input data
    fs.writeFile(filled_data_file, JSON.stringify(data, null, '\t'), function (err) {
        if (! err){
            console.log('data store')
            // fill the data on the form img
            let processer = child_process.exec('python generation/fill.py ' + form_img_file,
                function (error, stdout, stderr) {
                    if (error){
                        console.log(stdout);
                        console.log(error.stack);
                        console.log('Error code: '+error.code);
                        console.log('Signal received: '+error.signal);
                        res.json({code:0});
                    }
                    else {
                        console.log('Filling form successfully');
                        res.json({code:1, stdout:stdout, filled_form_img:filled_form_img})
                    }
                });
            processer.on('exit', function () {
                // console.log('Program Completed');
            });
        }
        else{
            console.log(err)
            res.json({code:0})
        }
    });
})

app.listen(8000,function(){
    console.log("Working on port 8000");
});