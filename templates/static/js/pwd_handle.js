$(function () {

    var error_name = false;
    var error_email = false;
    var error_check = false;


    $('#user_name').blur(function () {
        /*        $.get('/json2/', function (data) {
         $('#user_name').next().html(data)
         });*/
        check_user_name();
    });


    $('#email').blur(function () {
        check_email();
    });

    $('#allow').click(function () {
        if ($(this).is(':checked')) {
            error_check = false;
            $(this).siblings('span').hide();
        }
        else {
            error_check = true;
            $(this).siblings('span').html('请勾选同意');
            $(this).siblings('span').show();
        }
    });


    function check_user_name() {
        var len = $('#user_name').val().length;
        if (len < 5 || len > 20) {
            $('#user_name').next().html('请输入5-20个字符的用户名');
            $('#user_name').next().show();
            error_name = true;
        }
        else {
            $.get('/user/register_uname/', {'user_name': $('#user_name').val()}, function (data) {
                if (data.count >= 1) {
                    $('#user_name').next().hide();
                    error_name = false;
                } else {
                    $('#user_name').next().html('用户名不存在').show();
                    error_name = true;
                }
            });

        }
    }


    function check_email() {
        var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

        if (re.test($('#email').val())) {
            $('#email').next().hide();
            error_email = false;
        }
        else {
            $('#email').next().html('你输入的邮箱格式不正确')
            $('#email').next().show();
            error_check_password = true;
        }

    }


    $('#reg_form').submit(function () {
        check_user_name();
        check_email();

        if (error_name == false&&error_check == false) {
            return true;
        }
        else {
            return false;
        }

    });

})