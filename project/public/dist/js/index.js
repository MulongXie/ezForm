var resultPaths = null;

//*********************
//***** Modification *****
//*********************
$('video').bind('play', function (e) {
    var videoid = $(this).attr('id');
    document.getElementById(videoid).addEventListener('playing', function(){
        $(this).removeClass("hero-media-image")
    });
    // document.getElementById(videoid).addEventListener('pause', function(){
    //     $(this).addClass("hero-media-image")
    // });
    document.getElementById(videoid).addEventListener('ended', function(){
        $(this).addClass("hero-media-image")
    });
});

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


//*************************
//****** Upload Form ******
//*************************
$('.file-upload-input').on('change', function () {
    // show the detection result tab
    $('#preview-filled-res').removeClass('active in')
    $('#li-tab-filled-res').removeClass('active')
    $('#preview-detect-res').addClass('active in')
    $('#li-tab-detect-res').addClass('active')
    // hide note
    // $('.note').hide()

    if (this.files && this.files[0]){
        if (this.files[0].type.includes('image')){
            $(this).attr('data-type', 'image')
            let reader = new FileReader()
            reader.readAsDataURL(this.files[0])
            reader.onload = function (e) {
                $('#img-form-uploaded').attr('src', e.target.result)
                $('#img-form-uploaded').show()
                $('#btn-process').prop('disabled', false)
                process(e.target.result, 'image')
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
                process(e.target.result, 'pdf')
            }
        }
        else {
            alert('Only support image (.PNG & .JPG) and PDF formats')
        }
    }
})

// use examples
$('.img-exp-form').on('click', function () {
    process($(this).attr('src'), 'path')
})

//************************
//***** Process Form *****
//************************
function goToPage(pageID){
    let pageBtnID = '#page-btn-' + pageID
    $('.page-btn-active').removeClass('page-btn-active')
    $(pageBtnID).addClass('page-btn-active')

    let iframePageID = '#iframe-page-fill-' + pageID
    let detectionResPageID = '#detection-img-wrapper-' + pageID
    let filledResPageID = '#fill-img-wrapper-' + pageID
    $('.page-active').removeClass('page-active')
    $(iframePageID).addClass('page-active')
    $(detectionResPageID).addClass('page-active')
    $(filledResPageID).addClass('page-active')
}

function presentResultPage(pageID, resultFiles){
    // 1. pagination
    $('.pagination').append('<li><a id="page-btn-' + pageID + '" class="page-btn">'+ pageID +'</a></li>')
    // 2. page iframe
    $('#viewer-iframe').append('<iframe id="iframe-page-fill-' + pageID + '" class="iframe-viewer page" src="' + resultFiles.resultPage + '"></iframe>\n')
    // 3. page detection result
    let wrapper = '<div id="detection-img-wrapper-'+ pageID +'" class="overlay-container page">\n' +
        '    <img id="img-detection-res-'+ pageID +'" class="img-viewer img-viewer-insert" src="'+ resultFiles.inputImg +'" data-toggle="tooltip" title="Click the image to insert input box">\n' +
        '</div>'
    $('#preview-detect-res').append(wrapper)
    // 4. page filled result
    wrapper = '<div id="fill-img-wrapper-' + pageID + '" class="text-center page filled-img-viewer">\n' +
        '     <img id="img-filled-res-' + pageID + '" class="img-viewer img-viewer-preview" src="'+ resultFiles.inputImg +'" data-toggle="tooltip" title="Click the image to edit">\n' +
        '</div>'
    $('#preview-filled-res').append(wrapper)

    if (pageID === 1){
        $('.page-btn').addClass('page-btn-active')
        $('#iframe-page-fill-1').addClass('page-active')
        $('#detection-img-wrapper-1').addClass('page-active')
        $('#fill-img-wrapper-1').addClass('page-active')
    }

    $('.page-btn').on('click', function () {
        goToPage($(this).text())
    })

    // Trace input inner the iframe page
    $('#iframe-page-fill-' + pageID).on('load', function () {
        let frame = $('#iframe-page-fill-' + pageID)[0].contentWindow.document
        // Trace overlay
        $(frame).find('input').click(function () {
            // remove active compo
            let activeCompo = frame.getElementsByClassName('input-active')
            if (activeCompo.length > 0) {activeCompo[0].classList.remove('input-active')}
            $(this).addClass('input-active')

            let inputId = this.id
            let overlay =  $('#overlay-' + inputId + '-' + pageID)
            $('.overlay-active').removeClass('overlay-active')
            overlay.addClass('overlay-active')

            let imgWrapper = $('.img-wrapper')
            let offset = overlay.offset().top - imgWrapper.offset().top + imgWrapper.scrollTop() - 35
            imgWrapper.animate({scrollTop: offset},'slow')

            // show the detection result tab
            $('#preview-filled-res').removeClass('active in')
            $('#li-tab-filled-res').removeClass('active')
            $('#preview-detect-res').addClass('active in')
            $('#li-tab-detect-res').addClass('active')
        })
        // realtime type in on overlay
        $(frame).find('input').on('input', function () {
            let inputId = this.id
            let overlay =  $('#overlay-' + inputId + '-' + pageID)
            overlay.text($(this).val())

            // resize font to fit the box
            while ($(overlay)[0].scrollHeight > $(overlay).innerHeight() && parseInt($(overlay).css('font-size')) > 7){
                // console.log($(overlay)[0].scrollHeight, $(overlay).innerHeight())
                $(overlay).css('font-size', (parseInt($(overlay).css('font-size')) - 1) + 'px')
            }

            // enable font adjustment
            $('#nav-font-adjust').show("slide", { direction: "left" }, 300)
            $('.overlay-editing').removeClass('overlay-editing')
            $(overlay).addClass('overlay-editing')
        })

        // Trace input compo
        $('.overlay').on('click', function (e) {
            e.stopPropagation()
            cleanInsertedInput()

            // hide signature
            $('#signature').hide()
            $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')

            // show side font adjustment bar
            $('#nav-font-adjust').show("slide", { direction: "left" }, 300)

            // remove active compo
            let activeCompo = frame.getElementsByClassName('input-active')
            if (activeCompo.length > 0) {activeCompo[0].classList.remove('input-active')}

            // remove active overlay
            $('.overlay-active').removeClass('overlay-active')

            // add editing overlay
            $('.overlay-editing').removeClass('overlay-editing')
            $(this).addClass('overlay-editing')

            // activate the input compo
            let inputCompo = frame.getElementById($(this).attr('data-target'))
            if (inputCompo){
                inputCompo.scrollIntoView(false)
                inputCompo.classList.add('input-active')
            }
        })
        // realtime type in on input compo
        $('.overlay').on('input', function () {
            let inputCompo = frame.getElementById($(this).attr('data-target'))
            if (inputCompo){
                inputCompo.value = $(this).text()
            }
            // resize font to fit the box
            while ($(this)[0].scrollHeight > $(this).innerHeight() && parseInt($(this).css('font-size')) > 7){
                console.log($(this)[0].scrollHeight, $(this).innerHeight())
                $(this).css('font-size', (parseInt($(this).css('font-size')) - 1) + 'px')
            }
        })
    })

    // add overlay
    $.getJSON(resultFiles.compoLocFile, function (result) {
        let overlays = ''
        $.each(result, function (i, field) {
            field = field[0]
            // console.log(i, field)
            overlays += '<div id="overlay-' + i + '-' + pageID +'" contenteditable="true" ' + 'data-target="' + i + '"' +
                ' data-toggle="tooltip" title="Click to edit" class="overlay" style="top: ' + field['top'] + 'px; left: ' + field['left'] +
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
    if ($('#modal-upload').hasClass('in')){
        $('#modal-image-upload-wrap').slideUp()
        $('#modal-waiting-processing').slideDown()
        $('#modal-waiting-processing h5').text('Processing')
        $('#modal-waiting-processing .loader').slideDown()
    }else{
        $('#wrapper-exps').slideUp()
        $('#waiting-processing').slideDown()
        $('#waiting-processing h5').text('Processing')
        $('#waiting-processing .loader').slideDown()
        $("body, html").animate({
            scrollTop: $("#cover-page").offset().top
        }, 50);
    }

    $.ajax({
        url: '/process',
        type: 'post',
        data: {img: img, inputType:inputType},
        success: function(resp){
            if (resp.code === 1){
                // alert('success')
                $('.hero').slideUp()
                $('.cta').slideUp()
                $('#cover-page').slideUp()
                $('#main-contents').slideDown()
                $('#navbar-btn').slideDown()
                $('#modal-upload').modal('hide');
                $('#modal-image-upload-wrap').slideDown()
                $('#modal-waiting-processing').slideUp()
                $('#modal-waiting-processing .loader').slideUp()

                // clean viewers
                $('.page-btn').remove()
                $('.iframe-viewer').remove()
                $('.overlay-container').remove()
                $('.filled-img-viewer').remove()

                $("body, html").animate({
                    scrollTop: $("#header").offset().top
                }, 50);

                // Add viewers to present results of each page (if many)
                resultPaths = resp.resultPaths
                console.log(resp.resultPaths)
                for(let i = 0; i < resp.resultPaths.length; i ++){
                    // console.log(i, resp.resultPaths[i])
                    presentResultPage(i + 1, resp.resultPaths[i])
                }
                if (resp.resultPaths.length === 1){
                    $('#wrapper-pagination').hide()
                }
                else {
                    $('#wrapper-pagination').show()
                }

                // reset the container's size according to the form image
                setTimeout(function () {
                    let imgWidth = $('#img-detection-res-1').width()
                    $('.overlay-container').width(imgWidth)
                    $('.filled-img-viewer').width(imgWidth)
                    for (let i = 0; i < $('.page-btn').length; i ++) {
                        $('#img-filled-res-' + (i+1)).width(imgWidth)
                    }
                }, 1000)

                insertInputBox()

                // click the preview image and jump back to editing
                $('.img-viewer-preview').on('click', function () {
                    // show the detection result tab
                    $('#preview-filled-res').removeClass('active in')
                    $('#li-tab-filled-res').removeClass('active')
                    $('#preview-detect-res').addClass('active in')
                    $('#li-tab-detect-res').addClass('active')
                })
            }
            else {
                alert('Processing form failed. Probably try image of .PNG or .JPG')
                $('#waiting-processing').slideUp()
                $('#wrapper-exps').slideDown()
                $('#modal-image-upload-wrap').slideDown()
                $('#modal-waiting-processing').slideUp()
                $('#modal-waiting-processing .loader').slideUp()
            }
        },
        error: function (resp) {
            alert('Processing form failed for' + resp.statusText)
            $('#waiting-processing').slideUp()
            $('#wrapper-exps').slideDown()
            $('#modal-image-upload-wrap').slideDown()
            $('#modal-waiting-processing').slideUp()
            $('#modal-waiting-processing .loader').slideUp()
        }
    })
}


//*********************
//***** Fill Form *****
//*********************
$('#btn-show-filled').on('click', function () {
    // show preview tab
    $('#preview-detect-res').removeClass('active')
    $('#preview-detect-res').removeClass('in')
    $('#li-tab-detect-res').removeClass('active')
    $('#preview-filled-res').addClass('active')
    $('#preview-filled-res').addClass('in')
    $('#li-tab-filled-res').addClass('active')
    // jump to the position
    $('html,body').animate({scrollTop: $('#li-tab-filled-res').offset().top},'slow');
})


//****************************
//***** Insert Input Box *****
//****************************
function insertInputBox() {
    // insert input box while clicking the image
    $('.img-viewer-insert').on('click', function (e) {
        e.stopPropagation();
        // hide font bar
        $('#nav-font-adjust').show("slide", { direction: "left" }, 300)
        // hide signature
        $('#signature').hide()
        $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')

        // stop editing overlay
        $('.overlay-editing').removeClass('overlay-editing')

        let id = $(this).attr('id').split('-')
        let pageID = id[id.length - 1]
        let pageContainer = $('#detection-img-wrapper-' + pageID)
        // pageContainer.width($(this).width())
        // pageContainer.css('margin', '20px auto')

        // clean empty inserted inputs
        cleanInsertedInput()

        // insert new input box
        let inputBox = '<div class="insert-input insert-input-active text-left"' +
            ' style="left: ' + (e.pageX - pageContainer.offset().left) + 'px; top: ' + (e.pageY  - pageContainer.offset().top - 10) + 'px; ' +
            'position: absolute; min-width: 100px; min-height: 20px; font-size: 15px" contenteditable="true"' +
            ' data-toggle="tooltip" title="Drag to move & Click to edit"></div>'
        pageContainer.append(inputBox)

        // activate the input box while clicking
        $('.insert-input').on('click', function (e) {
            e.stopPropagation()
            // hide signature
            $('#signature').hide()
            $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
            // activate the input
            $('.insert-input-active').removeClass('insert-input-active')
            $(this).addClass('insert-input-active')
            // show side font adjustment bar
            $('#nav-font-adjust').show("slide", { direction: "left" }, 300)
            // remove overlay-editing
            $('.overlay-editing').remove()
        })

        // make the input box draggable
        $('.insert-input').draggable()
            .click(function() {
                $(this).draggable({ disabled: false });
            }).dblclick(function() {
            $(this).draggable({ disabled: true });
        })
    })

}

$('.btn-input-font').click(function (e) {
    e.stopPropagation()
    // hide signature
    $('#signature').hide()
    $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
})

fontAdjustment()

function fontAdjustment() {
    $('#font-up').click(function () {
        let activeInput = $('.insert-input-active, .overlay-editing')
        let fontSize = activeInput.css('font-size')
        activeInput.css('font-size', parseInt(fontSize) + 1 + 'px')
    })
    $('#font-down').click(function () {
        let activeInput = $('.insert-input-active, .overlay-editing')
        let fontSize = activeInput.css('font-size')
        activeInput.css('font-size', parseInt(fontSize) - 1 + 'px')
    })
    $('#font-bold').click(function () {
        let activeInput = $('.insert-input-active, .overlay-editing')
        if (activeInput.css('font-weight') === 'bold' || activeInput.css('font-weight') === '700'){
            activeInput.css('font-weight', 'normal')
        }
        else {
            activeInput.css('font-weight', 'bold')
        }
    })
    $('#font-italic').click(function () {
        let activeInput = $('.insert-input-active, .overlay-editing')
        if (activeInput.css('font-style') === 'italic'){
            activeInput.css('font-style', 'normal')
        }
        else {
            activeInput.css('font-style', 'italic')
        }
    })
    $('#input-del').click(function () {
        // clean overlay and corresponding input compo
        if ($('.overlay-editing').length > 0){
            $('.overlay-editing').text('')
            let pageID = $('.page-btn-active').text()
            $('#iframe-page-fill-' + pageID).contents().find(".input-active")[0].value = ''
        }
        // remove inserted input box
        else if($('.insert-input-active').length > 0){
            $('.insert-input-active').remove()
        }
    })
}

function cleanInsertedInput(){
    let inputs = $('.insert-input')
    for (let i = 0; i < inputs.length; i ++){
        if ($(inputs[i]).text() === ''){
            $(inputs[i]).remove()
        }
    }
    $('.insert-input-active').removeClass('insert-input-active')
}

// hide the active input while clicking outside
$(document).click(function () {
    $('#nav-font-adjust').hide("slide", { direction: "left" }, 300)

    // hide or delete the previous box
    let previousBox = $('.insert-input-active')
    if (previousBox.text() === ''){
        previousBox.remove()
    }
    else{
        previousBox.removeClass('insert-input-active')
    }

    // hide signature
    $('#signature').hide()
    $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
})


//*********************
//***** Signature *****
//*********************
$(function () {
    var canvas = document.getElementById("signature-pad");
    var signaturePad = new SignaturePad(canvas);
    $('#btn-sig-clear').on('click', function(){
        signaturePad.clear();
    });

    $('#btn-sig-use').on('click', function (e) {
        e.stopPropagation()
        $('.insert-input-active').removeClass('insert-input-active')

        // show the detection result tab
        $('#preview-filled-res').removeClass('active in')
        $('#li-tab-filled-res').removeClass('active')
        $('#preview-detect-res').addClass('active in')
        $('#li-tab-detect-res').addClass('active')

        let signature = canvas.toDataURL("image/png")
        let pageContainer = $('.overlay-container.page-active')
        let img = '<div class="inserted-signature-img inserted-signature-img-active" style="top:200px; left: 200px; position: absolute; width: 100px; height: 50px">' +
            '   <img src="' + signature + '" style="width: 100%; height: 100%">' +
            '   <a class="btn del-sig" style="display: none">x</a>' +
            '</div>'
        pageContainer.append(img)

        // activate the div while clicking
        let insertedSig = $('.inserted-signature-img')
        insertedSig.on('click', function (e) {
            e.stopPropagation()
            $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
            $('.insert-input-active').removeClass('insert-input-active')
            $(this).addClass('inserted-signature-img-active')
        })

        // make the div draggable and resizable
        insertedSig.draggable()
        insertedSig.resizable()

        // delete button
        $('.del-sig').on('click', function () {
            $(this).parent().remove()
        })
    })
})

$('#btn-signature').click(function (e) {
    e.stopPropagation()
    $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
    $('.insert-input-active').removeClass('insert-input-active')

    $('.signature-element').click(function (e) {
        e.stopPropagation()
        // $('.inserted-signature-img-active').removeClass('inserted-signature-img-active')
        $('.insert-input-active').removeClass('insert-input-active')
    })
    $('#signature').toggle()
})


// *********************
// ***** Fill Data *****
// *********************
function cloneInput(node){
    let clone = node.cloneNode(true)
    clone.removeAttribute('id')
    clone.removeAttribute('contenteditable')
    clone.removeAttribute('class')
    clone.removeAttribute('data-target')
    clone.classList.add('filled-input')
    clone.style.position = "absolute"
    clone.style.textAlign = "left"
    return clone
}

function fillData(callback){
    let fillingData = []

    // show preview tab
    $('#preview-detect-res').removeClass('active in')
    $('#li-tab-detect-res').removeClass('active')
    $('#preview-filled-res').addClass('active in')
    $('#li-tab-filled-res').addClass('active')

    let pageBtn = $('.page-btn')
    for (let i = 0; i < pageBtn.length; i++){
        // reset wrapper to fit
        let pageID = $(pageBtn[i]).text()
        let filledWrapper = $('#fill-img-wrapper-' + pageID)

        // add overlay on filled result image
        $('#fill-img-wrapper-' + pageID + '>.filled-input').remove()
        let overlays = $('#detection-img-wrapper-' + pageID + '>.overlay')
        for (let i = 0; i < overlays.length; i ++){
            if (overlays[i].textContent !== ''){
                let clone = cloneInput(overlays[i])
                filledWrapper.append(clone)

                let data = overlays[i]
                let jsonData = {'type':'text', 'top': data.style.top, 'left': data.style.left,
                    'fontWeight': data.style.fontWeight, 'fontSize': data.style.fontSize, 'fontStyle':data.style.fontStyle,
                    'fontFamily':data.style.fontFamily, 'fontColor': data.style.color}
                fillingData.push(jsonData)
            }
        }
        let insertedInputs = $('#detection-img-wrapper-' + pageID + '>.insert-input')
        for (let i = 0; i < insertedInputs.length; i ++){
            if (insertedInputs[i].textContent !== ''){
                let clone = cloneInput(insertedInputs[i])
                filledWrapper.append(clone)

                let data = insertedInputs[i]
                let jsonData = {'type':'text', 'top': data.style.top, 'left': data.style.left,
                    'fontWeight': data.style.fontWeight, 'fontSize': data.style.fontSize, 'fontStyle':data.style.fontStyle,
                    'fontFamily':data.style.fontFamily, 'fontColor': data.style.color}
                fillingData.push(jsonData)
            }
        }
        let sigImg = $('#detection-img-wrapper-' + pageID + '>.inserted-signature-img')
        for (let i = 0; i < sigImg.length; i ++){
            let clone = sigImg[i].cloneNode(true)
            filledWrapper.append(clone)

            let data = sigImg[i]
            let jsonData = {'id':i, 'type':'img', 'top': data.style.top, 'left': data.style.left,
                'width':data.style.width, 'height':data.style.height}
            fillingData.push(jsonData)
        }
    }
    if(typeof callback === 'function'){
        callback(fillingData)
    }
}

$('.btn-fill').on('click', function (){
    fillData()
})


//***********************
//***** Export Form *****
//***********************
function screenshotHTMLPage(zip, pageID){
    if (pageID <= $('.page-btn').length){
        console.log('Page ID:', pageID)
        // show the page
        $('.page-btn-active').removeClass('page-btn-active')
        $('#page-btn-' + pageID).addClass('page-btn-active')
        $('.page-active').removeClass('page-active')
        $('#iframe-page-fill-' + pageID).addClass('page-active')
        $('#detection-img-wrapper-' + pageID).addClass('page-active')
        $('#fill-img-wrapper-' + pageID).addClass('page-active')

        // convert html to image
        let filledImgWrapper = $('#fill-img-wrapper-' + pageID)
        console.log(filledImgWrapper)
        html2canvas(filledImgWrapper,{
            onrendered: function (canvas) {
                let imgData = canvas.toDataURL('image/png')
                $('#filling-rest').attr('src', imgData)
                imgData = imgData.replace(/^data:image.*;base64,/, "")
                // zip and download
                zip.file("filledForm-" + pageID +".jpg", imgData, {base64: true});

                screenshotHTMLPage(zip, pageID + 1)
            }
        })
    }
    else {
        // hide full image overflow
        $('.content-wrapper').css('overflow', 'auto')
        $('.img-wrapper').css('overflow', 'auto')
        let imgViewer = $('.img-viewer')
        imgViewer.css('border', '1px solid')
        imgViewer.css('box-shadow', '5px 10px lightgrey')

        goToPage(1)

        zip.generateAsync({type: "blob"})
            .then(function (content) {
                // see FileSaver.js
                saveAs(content, "form.zip");
            })
    }
}

$('#btn-export').on('click', function () {
    // let pageID = $('.page-btn-active').text()
    // getDivImage(pageID)

    // show the detection result tab
    $('#preview-detect-res').removeClass('active in')
    $('#li-tab-detect-res').removeClass('active')
    $('#preview-filled-res').addClass('active in')
    $('#li-tab-filled-res').addClass('active')

    // show the full image
    $('.content-wrapper').css('overflow', 'unset')
    $('.img-wrapper').css('overflow', 'unset')
    let imgViewer = $('.img-viewer')
    imgViewer.css('border', 'none')
    imgViewer.css('box-shadow', 'none')

    var zip = new JSZip();
    screenshotHTMLPage(zip, 1)

    // for (let i = 0; i < $('.page-btn').length; i ++) {
    //     console.log(i)
    //     let pageID = i + 1
    //     // show the full image
    //     $('.content-wrapper').css('overflow', 'unset')
    //     $('.img-wrapper').css('overflow', 'unset')
    //     let imgViewer = $('.img-viewer')
    //     imgViewer.css('border', 'none')
    //     imgViewer.css('box-shadow', 'none')
    //
    // }
    // setTimeout(function () {
    //     goToPage(curPage)
    //     zip.generateAsync({type: "blob"})
    //         .then(function (content) {
    //             // see FileSaver.js
    //             saveAs(content, "form.zip");
    //         })
    // }, 1000)
})
