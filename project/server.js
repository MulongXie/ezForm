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
    res.sendfile("public/test.html");
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
                processImg(uploadPath, res, 'image')
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
                processImg(uploadPath, res, 'pdf')
            }
            else {
                uploadedImgId --;
                console.log(err);
                res.json({code: 0})
            }
        })
    }
    else if (req.body.inputType === 'path'){
        processImg(req.body.img, res, 'image')
    }
})

function processImg(inputImgPath, res, type){
    console.log('Processing img:', inputImgPath)
    let imgName = inputImgPath.split('/')
    imgName = imgName[imgName.length - 1].split('.')[0]
    if (type === 'image'){
        let resultDir = 'data/output/' + imgName;
        let detectionResultImg = resultDir + '/detection.jpg'
        let generationPage = resultDir + '/xml.html'
        let compoLocFile = resultDir + '/input_loc.json'
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
                    console.log('Processing successfully');
                    res.json({code:1, resultImg:detectionResultImg, resultPage:generationPage, inputImg: inputImgPath, compoLocFile: compoLocFile})
                }
            });
        processer.on('exit', function () {
            // console.log('Program Completed');
        });
    }

    else if (type === 'pdf'){
        let resultDir = 'data/output/pdf-' + imgName;
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
                    // console.log(stdout);
                    console.log(JSON.parse(stdout.replace(/'/g, '"')))
                    let detectionResultImg = resultDir + '/detection.jpg'
                    let generationPage = resultDir + '/xml.html'
                    let compoLocFile = resultDir + '/input_loc.json'
                    console.log('Processing successfully');
                    // res.json({code:1, resultImg:detectionResultImg, resultPage:generationPage, inputImg: inputImgPath, compoLocFile: compoLocFile})
                    res.json({code:0});
                }
            });
        processer.on('exit', function () {
            // console.log('Program Completed');
        });
    }
}

app.post('/fillForm', function (req, res) {
    let data = req.body

    let formImgFile = req.body.orgImg
    let inputPathSplit = formImgFile.split('/');
    let resultDir = './data/output/' + inputPathSplit[inputPathSplit.length - 1].split('.')[0];
    let filledDataFile = resultDir + '/input_data.json'
    let filledFormImg = resultDir + '/filled.jpg'

    // store input data
    fs.writeFile(filledDataFile, JSON.stringify(data, null, '\t'), function (err) {
        if (! err){
            console.log('data store')
            // fill the data on the form img
            let processer = child_process.exec('python generation/fill.py ' + formImgFile,
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
                        res.json({code:1, stdout:stdout, filledFormImg:filledFormImg})
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