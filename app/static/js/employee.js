$(document).ready(function(){
    $('.update_form').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            type: 'post',
            data: $(this).serialize(),
            url: 'update_employee',
            success: function(response){
                if(response.errors == null)
                    location.reload()
                if(response.errors.first_name)
                    $('.error-first_name').html(response.errors.first_name)
                else
                    $('.error-first_name').html('')
                if(response.errors.last_name)
                    $('.error-last_name').html(response.errors.last_name)
                else
                    $('.error-last_name').html('')
                if(response.errors.email)
                    $('.error-email').html(response.errors.email)
                else
                    $('.error-email').html('')
            }
        })
    })
})