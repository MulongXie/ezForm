$(document).ready(function () {
    /*--------------------------------------------------------------
    # Upload New Image
    --------------------------------------------------------------*/
    /* Upload */
    var canvas_loaded = false;
    $('#avatarInput').on('change', function () {
        this.$avatarModal = $("body").find('#modal-new-img');

        this.$avatarForm = this.$avatarModal.find('.avatar-form');
        this.$avatarUpload = this.$avatarForm.find('.avatar-upload');
        this.$avatarSrc = this.$avatarForm.find('.avatar-src');
        this.$avatarData = this.$avatarForm.find('.avatar-data');
        this.$avatarInput = this.$avatarForm.find('.avatar-input');
        this.$avatarSave = this.$avatarForm.find('.avatar-save');
        this.$avatarBtns = this.$avatarForm.find('.avatar-btns');

        this.$avatarWrapper = this.$avatarModal.find('.avatar-wrapper');
        this.$avatarPreview = this.$avatarModal.find('.avatar-preview');

        var canvas = $(".avatar-wrapper")
        var context = canvas.get(0).getContext("2d")
        var img = new Image();

        var files = this.$avatarInput.prop('files');
        console.log(files);
        if (files.length > 0) {
            $('#btn-upload-process').prop('disabled', false);
            file = files[0];
            this.url = URL.createObjectURL(file);

            img.src = this.url;
            if (canvas_loaded) {
                canvas.cropper('replace', this.url);
            } else {
                img.onload = function () {
                    context.clearRect(0, 0, img.width, img.height);
                    context.canvas.height = img.height;
                    context.canvas.width = img.width;
                    context.drawImage(img, 0, 0);

                    var cropper = canvas.cropper({
                        autoCropArea: 1,
                        preview: ".avatar-preview"
                    });
                };
                canvas_loaded = true;
            }
        }

        this.$avatarBtns.click(function (e) {
            var data = $(e.target).data();
            if (data.method) {
                canvas.cropper(data.method, data.option);
            }
        });

        this.$avatarSave.click(function () {
            var croppedImageDataURL = canvas.cropper('getCroppedCanvas').toDataURL("image/png");
            $(".display-pic").attr('src', croppedImageDataURL);
            $("#display-content").removeClass("hide");
            $("#display-content").attr('data-type', 'base64');
            // $(".display-content").fadeIn(1000);
        });
    });

    /* Button for processing new image rather than new model for the same img*/
    $('#btn-upload-process').click(function () {
        // Switch processing button
        $('#modal_proc_btn_new_model').hide();
        $('#modal_proc_btn_new_img').show();
    });

    /* Go back when cancel */
    $('#modal-new-model').on('hide.bs.modal', function () {
        console.log('hidden');
        $('#modal_proc_btn_new_img').hide();
        $('#modal_proc_btn_new_model').show();
    });


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
})