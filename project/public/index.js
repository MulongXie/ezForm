$(document).ready(function () {

    $('#btn-start').on('click', function () {
    })
    $('#btn-fill').on('click', function () {
        let page = document.getElementById('page-fill').contentWindow.document
        let inputs = page.getElementsByTagName('input')
        let data = {}
        for (let i = 0; i < inputs.length; i++){
            data[inputs[i].id] = inputs[i].value
        }
        $.ajax({
                url: '/submitData',
                type: 'post',
                data:{
                    inputs: data
                },
                success: function (resp) {
                    if (resp.code === 1){
                        $('#img-filled-res').attr('src', resp.filled_form_img)
                        $('#img-filled-res').show()
                    }
                    else {
                        alert('Filling form failed')
                    }
                }
            }
        )
    })
    // $('.btn-upload').on('click', function () {
    //     $('#cover-page').slideToggle()
    //     $('#main-contents').slideToggle()
    //     $('.footer').css('position', 'inherit')
    // })
    $('#btn-process').on('click', function () {
        $.ajax({
            url: '/process',
            type: 'get',
            success: function(resp){
                if (resp.code === 1){
                    $('#img-detection-res').attr('src', resp.result_img)
                    $('#img-detection-res').show()
                    $('#page-fill').attr('src', resp.result_page)
                    $('#page-fill').show()
                    $('#btn-fill').show()
                }
                else {
                    alert('Processing form failed')
                }
            }
        })
    })
})