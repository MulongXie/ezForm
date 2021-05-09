var resultPaths = null;

$('#input-upload-form').on('change', function () {
    if (this.files && this.files[0]){
        if (this.files[0].type.includes('image')){
            $(this).attr('data-type', 'image')
            let reader = new FileReader()
            reader.readAsDataURL(this.files[0])
            reader.onload = function (e) {
                $('#img-form-uploaded').attr('src', e.target.result)
                $('#img-form-uploaded').show()
                $('#btn-process').prop('disabled', false)
            }
        }
        else if(this.files[0].type.includes('pdf')){
            $(this).attr('data-type', 'pdf')
            $('#img-form-uploaded').hide()
            let reader = new FileReader()
            reader.readAsDataURL(this.files[0])
            reader.onload = function (e) {
                $('#img-form-uploaded').attr('src', e.target.result)
                $('#btn-process').prop('disabled', false)
            }
        }
        else {
            alert('Only support image (.PNG & .JPG) and PDF formats')
        }
    }
})

function presentResultPage(pageID, resultFiles){
    // 1. pagination
    $('.pagination').append('<li><a class="page-btn">'+ pageID +'</a></li>')
    // 2. page iframe
    $('#viewer-iframe').append('<iframe id="iframe-page-fill-' + pageID + '" class="iframe-viewer page" src="' + resultFiles.resultPage + '"></iframe>\n')
    // 3. page detection result
    let wrapper = '<div id="detection-img-wrapper-'+ pageID +'" class="overlay-container page">\n' +
        '    <img id="img-detection-res-'+ pageID +'" class="img-viewer" src="'+ resultFiles.resultImg +'">\n' +
        '</div>'
    $('#previewer-detect-res').append(wrapper)
    // 4. page filled result
    wrapper = '<div id="fill-img-wrapper-' + pageID + '" class="text-center page filled-img-viewer">\n' +
        '     <img id="img-filled-res-' + pageID + '" class="img-viewer" src="'+ resultFiles.inputImg +'">\n' +
        '</div>'
    $('#preview-filled-res').append(wrapper)

    if (pageID === 1){
        $('.page-btn').addClass('page-btn-active')
        $('#iframe-page-fill-1').addClass('page-active')
        $('#detection-img-wrapper-1').addClass('page-active')
        $('#fill-img-wrapper-1').addClass('page-active')
    }

    $('.page-btn').on('click', function () {
        $('.page-btn-active').removeClass('page-btn-active')
        $(this).addClass('page-btn-active')

        let id = $(this).text()
        let iframePageID = '#iframe-page-fill-' + id
        let detectionResPageID = '#detection-img-wrapper-' + id
        let filledResPageID = '#fill-img-wrapper-' + id
        $('.page-active').removeClass('page-active')
        $(iframePageID).addClass('page-active')
        $(detectionResPageID).addClass('page-active')
        $(filledResPageID).addClass('page-active')
    })

    // Trace input inner the iframe page
    setTimeout(function () {
        let frame = $('#iframe-page-fill-' + pageID)[0].contentWindow.document
        // console.log($(frame))
        $(frame).find('input').click(function () {
            let inputId = this.id
            let overlay =  $('#overlay-' + inputId + '-' + pageID)
            $('.overlay-active').removeClass('overlay-active')
            overlay.addClass('overlay-active')

            let imgWrapper = $('.img-wrapper')
            let offset = overlay.offset().top - imgWrapper.offset().top + imgWrapper.scrollTop()
            imgWrapper.animate({scrollTop: offset},'slow')

        })
    }, 1000)

    // add overlay
    $.getJSON(resultFiles.compoLocFile, function (result) {
        let overlays = ''
        $.each(result, function (i, field) {
            field = field[0]
            // console.log(i, field)
            overlays += '<div id="overlay-' + i + '-' + pageID +'" class="overlay" style="top: ' + field['top'] + 'px; left: ' + field['left'] +
                'px; width: ' + (field['right'] - field['left']) + 'px; height: ' + (field['bottom'] - field['top']) + 'px;"></div>\n'
        })
        $('#detection-img-wrapper-'+ pageID).append(overlays)
    })
}

function process(img, inputType){
    // show cover page and hide main content
    if (! $('#cover-page').is(':visible') && $('#main-contents').is(':visible')){
        $('#cover-page').slideToggle()
        $('#main-contents').slideToggle()
        $('.footer').css('position', 'fixed')
    }
    $('.overlay').remove()
    // show processing loader
    $('#wrapper-exps').slideUp()
    $('#waiting-processing').slideDown()
    $('#waiting-processing h5').text('Processing')
    $('#waiting-processing .loader').slideDown()
    $('.btn-upload').prop('disabled', true)

    $.ajax({
        url: '/process',
        type: 'post',
        data: {img: img, inputType:inputType},
        success: function(resp){
            if (resp.code === 1){
                // alert('success')
                $('.btn-upload').prop('disabled', false)
                $('#cover-page').slideToggle()
                $('#main-contents').slideToggle()
                $('.footer').css('position', 'inherit')

                // clean viewers
                $('.page-btn').remove()
                $('.iframe-viewer').remove()
                $('.overlay-container').remove()
                $('.filled-img-viewer').remove()

                // Add viewers to present results of each page (if many)
                resultPaths = resp.resultPaths
                console.log(resp.resultPaths)
                for(let i = 0; i < resp.resultPaths.length; i ++){
                    // console.log(i, resp.resultPaths[i])
                    presentResultPage(i + 1, resp.resultPaths[i])
                }

                // reset the container's size according to the form image
                setTimeout(function () {
                    let imgWidth = $('#img-detection-res-1').width()
                    $('.overlay-container').width(imgWidth)
                    for (let i = 0; i < $('.page-btn').length; i ++) {
                        $('#img-filled-res-' + (i+1)).width(imgWidth)
                    }
                }, 1000)
            }
            else {
                alert('Processing form failed. Probably try image of .PNG or .JPG')
                $('#waiting-processing h5').text('Processing form failed. Probably try image of .PNG or .JPG')
                $('#waiting-processing .loader').slideUp()
                $('.btn-upload').prop('disabled', false)
            }
        },
        error: function (resp) {
            alert('Processing form failed for' + resp.statusText)
            $('#waiting-processing h5').text('Processing form failed for ' + resp.statusText)
            $('#waiting-processing .loader').slideUp()
            $('.btn-upload').prop('disabled', false)
        }
    })
}

$('#btn-process').on('click', function () {
    process($('#img-form-uploaded').attr('src'), $('#input-upload-form').attr('data-type'))
})

$('.img-exp-form').on('click', function () {
    process($(this).attr('src'), 'path')
})

$('.btn-fill').on('click', function () {
    // show waiting loading
    $('#waiting-filling h4').text('Filling Form ...')
    $('#waiting-filling .loader').slideDown()
    $('#btn-show-filled').hide()

    let data_pages = []
    for (let i = 0; i < $('.page-btn').length; i ++){
        let page = document.getElementById('iframe-page-fill-' + (i+1)).contentWindow.document
        let inputs = page.getElementsByTagName('input')
        let data = {}
        for (let i = 0; i < inputs.length; i++){
            if (inputs[i].type === 'checkbox'){
                if (inputs[i].checked){
                    data[inputs[i].id] = 'Y'
                }
                else{
                    data[inputs[i].id] = ''
                }
            }
            else if (inputs[i].type === 'date'){
                data[inputs[i].id] = inputs[i].value.replace(/-/g, '/')
            }
            else{
                data[inputs[i].id] = inputs[i].value
            }
        }
        if (Object.keys(data).length === 0){
            data_pages.push(null)
        }
        else{
            data_pages.push(data)
        }
    }
    console.log(data_pages)

    $.ajax({
            url: '/fillForm',
            type: 'post',
            data:{
                inputData: data_pages,
                resultPaths: resultPaths
            },
            success: function (resp) {
                if (resp.code === 1){
                    for (let i = 0; i < resp.filledFormImages.length; i++){
                        let imgFilledRes = $('#img-filled-res-' + (i+1))
                        imgFilledRes.prop('src', resp.filledFormImages[i] + '?' + new Date().getTime())
                    }

                    $('#waiting-filling h4').text('Form Filled')
                    $('#waiting-filling .loader').slideUp()

                    $('#btn-show-filled').slideDown()
                    $('#btn-export').slideDown()
                }
                else {
                    alert('Filling form failed')
                    $('#waiting-filling h4').text('Filling form failed')
                    $('#waiting-filling .loader').slideUp()
                }
            }
        }
    )
})

$('.btn-flip').on('click', function () {
    let wrappers = $('.content-wrapper')
    if (wrappers.hasClass('col-md-6')){
        wrappers.removeClass('col-md-6')
        wrappers.addClass('col-md-12')
    }
    else if(wrappers.hasClass('col-md-12')){
        wrappers.removeClass('col-md-12')
        wrappers.addClass('col-md-6')
    }
})

$('#btn-reload').on('click', function () {
    let page = $('#iframe-page-fill')
    page.prop('src', page.prop('src') + '?' + new Date().getTime())
})

$('#btn-show-filled').on('click', function () {
    // show preview tab
    $('#previewer-detect-res').removeClass('active')
    $('#previewer-detect-res').removeClass('in')
    $('#li-tab-detect-res').removeClass('active')
    $('#preview-filled-res').addClass('active')
    $('#preview-filled-res').addClass('in')
    $('#li-tab-filled-res').addClass('active')
    // jump to the position
    $('html,body').animate({scrollTop: $('#li-tab-filled-res').offset().top},'slow');
})

$('#btn-export').on('click', function () {
    var zip = new JSZip();
    for (let i = 0; i < $('.page-btn').length; i ++) {
        // read the img as base64
        let img = document.getElementById("img-filled-res-" + (i+1))
        let canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth
        canvas.height = img.naturalHeight
        let ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        let imgBase = canvas.toDataURL("image/png");
        imgBase = imgBase.replace(/^data:image.*;base64,/, "")

        // zip and download
        zip.file("filledForm-" + (i+1) +".jpg", imgBase, {base64: true});
    }
    zip.generateAsync({type: "blob"})
        .then(function (content) {
            // see FileSaver.js
            saveAs(content, "form.zip");
        })
})

var insertedInputID = 0
$('#btn-insert').on('click', function () {
    // show preview tab
    $('#previewer-detect-res').removeClass('active in')
    $('#li-tab-detect-res').removeClass('active')
    $('#preview-filled-res').addClass('active in')
    $('#li-tab-filled-res').addClass('active')

    // show the note
    let note = $('.note')
    if (! note.is(':visible') ){
        note.slideToggle()
        $('.filled-img-viewer').css('margin-top', '20px')
        $('.img-viewer').addClass('img-viewer-insert')
    }
    else {
        note.slideToggle()
        $('.filled-img-viewer').css('margin-top', '')
        $('.img-viewer').removeClass('img-viewer-insert')
    }

    // insert input box while clicking the image
    $('.img-viewer-insert').on('click', function (e) {
        e.stopPropagation();

        let id = $(this).attr('id').split('-')
        let pageID = id[id.length - 1]
        let pageContainer = $('#fill-img-wrapper-' + pageID)
        pageContainer.width($(this).width())
        pageContainer.css('margin', '20px auto')

        // insert input box
        let inputs = $('.insert-input')
        for (let i = 0; i < inputs.length; i ++){
            if (inputs[i].textContent === ''){
                $(inputs[i]).parent().remove()
            }
        }
        $('.insert-input-active').removeClass('insert-input-active')
        let inputBox = '<div id="insert-input-' + insertedInputID + '" style="left: ' + (e.pageX - pageContainer.offset().left) + 'px; top: ' + (e.pageY  - pageContainer.offset().top - 10) + 'px; ' +
            'position: absolute; min-width: 100px; min-height: 20px; font-size: 15px">' +
            '    <div class="insert-input insert-input-active" contenteditable="true" style="width: calc(100% - 40px); height: 100%; float: left"></div>' +
            '    <div class="btn-group btn-group-font" style="float: right">\n' +
            '            <a id="btn-front-up-' + insertedInputID + '" class="btn btn-danger btn-input-font btn-input-font-up">+</a>\n' +
            '            <a id="btn-front-down-' + insertedInputID + '" class="btn btn-danger btn-input-font btn-input-font-down">-</a>\n' +
            '    </div>' +
            '</div>'
        pageContainer.append(inputBox)

        // Resizable with mouse
        let insertedBox = $('.insert-input-active')
        insertedBox.on('click', function (e) {
            e.stopPropagation();
        })

        // change the font size
        $('.btn-input-font-up').on('click', function () {
            let id = $(this).attr('id').split('-')
            id = id[id.length - 1]
            let inputBox =  $('#insert-input-' + id)
            let fontSize = inputBox.css('font-size')
            console.log('#insert-input-' + id, parseInt(fontSize))
            inputBox.css('font-size', parseInt(fontSize) + 1 + 'px')
        })
        $('.btn-input-font-down').on('click', function () {
            let id = $(this).attr('id').split('-')
            id = id[id.length - 1]
            let inputBox =  $('#insert-input-' + id)
            let fontSize = inputBox.css('font-size')
            inputBox.css('font-size', parseInt(fontSize) - 1 + 'px')
        })
        insertedInputID ++
    })
})

// hide the active input while clicking outside
$(document).click(function () {
    // insert input box
    let previousBox = $('.insert-input-active')
    if (previousBox.text() === ''){
        previousBox.parent().remove()
    }
    else{
        previousBox.removeClass('insert-input-active')
    }
})