var fs = require('fs');
var bodyParser = require('body-parser');
var child_process = require('child_process');
var express	= require("express");
var app	= express();

app.use(express.static("."));
app.use(express.static("public"));

app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({limit: '50mb', extended: true}));

app.get('/',function(req,res){
    res.sendfile("public/index.html");
    let time = Date()
    console.log("Connecting at", time.toLocaleString())
});

var uploadedImgId = 0
app.post('/process', function (req, res) {
    console.log('\nStart processing')
    // Processing uploaded forms
    if (req.body.inputType === 'image'){
        uploadedImgId ++
        let imgBase64 = req.body.img.replace(/^data:image.*base64,/, "");
        let uploadPath = 'data/upload/upload' + uploadedImgId.toString() + '.jpg'
        // upload form image
        fs.writeFile(uploadPath, imgBase64, 'base64', function (err) {
            if (! err){
                console.log('Upload image to', uploadPath)
                processImg(uploadPath, res)
            }
            else {
                uploadedImgId --;
                console.log(err);
                res.json({code: 0})
            }
        })
    }
    else if (req.body.inputType === 'pdf'){
        uploadedImgId ++
        let pdf = req.body.img.replace(/^data:.*base64,/, "");
        let uploadPath = 'data/upload/upload' + uploadedImgId.toString() + '.pdf'
        // upload form image
        fs.writeFile(uploadPath, pdf, 'base64', function (err) {
            if (! err){
                console.log('Upload image to', uploadPath)
                processImg(uploadPath, res)
            }
            else {
                uploadedImgId --;
                console.log(err);
                res.json({code: 0})
            }
        })
    }
    else if (req.body.inputType === 'path'){
        processImg(req.body.img, res)
    }
})

function processImg(inputImgPath, res){
    console.log('Processing img:', inputImgPath)
    // processing form
    let processer = child_process.exec('python main-pdf.py ' + inputImgPath,
        function (error, stdout, stderr) {
            if (error){
                console.log(stdout);
                console.log(error.stack);
                console.log('Error code: '+error.code);
                console.log('Signal received: '+error.signal);
                res.json({code:0});
            }
            else {
                let resultPaths = JSON.parse(stdout.replace(/'/g, '"'))
                // console.log(resultPaths)
                console.log('Processing successfully');
                res.json({code:1, resultPaths: resultPaths, uploadFilePath:inputImgPath})
            }
        });
    processer.on('exit', function () {
        // console.log('Program Completed');
    });
}

app.post('/exportForm', function (req, res) {
    // console.log(req.body)
    let inputData = req.body.fillingData
    if (inputData === undefined){inputData = []}
    let uploadFilePath = req.body.uploadFilePath
    let filledResultDir = req.body.filledResultDir

    // store input data
    let filledDataFile = filledResultDir + 'input.json'
    fs.writeFile(filledDataFile, JSON.stringify(inputData, null, '\t'), function (err) {
        if (! err){
            console.log('Filling data stored to', filledDataFile)
            // fill the data on the form img
            let processer = child_process.exec('python generation/fill.py ' + filledDataFile + ' ' + uploadFilePath + ' ' + filledResultDir,
                function (error, stdout, stderr) {
                    if (! error){
                        console.log('Filling form successfully', filledResultDir + 'filled.pdf');
                        res.json({code:1, filledResultPDF:filledResultDir + 'filled.pdf'})
                    }
                    else {
                        console.log(error)
                        res.json({code:0})
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

app.listen(3000,function(){
    console.log("Working on port 3000");
});