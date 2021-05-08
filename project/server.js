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
                res.json({code:1, resultPaths: resultPaths})
            }
        });
    processer.on('exit', function () {
        // console.log('Program Completed');
    });
}

app.post('/fillForm', function (req, res) {
    // console.log(req.body)
    let inputData = req.body.inputData
    let resultPaths = req.body.resultPaths

    let inputPathSplit = resultPaths[0].inputImg.split('/');
    let resultDir = './data/output/' + inputPathSplit[2].split('.')[0] + '/filled';
    let filledFormImages = []

    for (let i = 0; i < inputData.length; i ++){
        // console.log(resultPaths[i])

        let data = inputData[i]
        let filledDataFile = resultDir + '/input_data' + (i+1) + '.json'
        let filledFormImg = resultDir + '/filled' + (i+1) + '.jpg'

        // store input data
        fs.writeFile(filledDataFile, JSON.stringify(data, null, '\t'), function (err) {
            if (! err){
                // console.log('data store')
                // fill the data on the form img
                let processer = child_process.exec('python generation/fill.py ' + resultPaths[i].inputImg + ' ' + resultPaths[i].compoLocFile + ' ' + filledDataFile + ' ' + filledFormImg,
                    function (error, stdout, stderr) {
                        if (! error){
                            filledFormImages.push(filledFormImg)
                            console.log('Filling form successfully', filledFormImages.length);
                            if (filledFormImages.length === inputData.length){
                                filledFormImages.sort()
                                console.log(filledFormImages)
                                res.json({code:1, filledFormImages:filledFormImages})
                            }
                        }
                        else {
                            console.log(stdout)
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
    }
})

app.listen(3000,function(){
    console.log("Working on port 3000");
});