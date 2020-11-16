window.onload = function() {
    // make capctcha required
    var $recaptcha = document.querySelector('#g-recaptcha-response');
    if($recaptcha) {
        $recaptcha.setAttribute("required", "required");
    }

    // listen submit form
    const form = document.getElementById("image-form");
    form.addEventListener("submit", post_form);
};

// generate prediction_id
function generate_id(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
 }

// on form post
function post_form(e){
    const id = generate_id(32)
    document.getElementById("prediction_id").value = id;
    // console.log("prediction_id: " + id);
    // document.getElementById("api_key").value = "";

    // change elements when upload started
    document.getElementById("file_chooser").style.display = "none";
    document.getElementById("dropdown").style.display = "none";
    document.getElementById("submit_button").style.display = "none";
    // form.submit_button.disabled = true;
    document.getElementById("recaptcha").style.display = "none";

    // show Uploading with progress bar
    document.getElementById('header_div').innerHTML = `
        <h1>Uploading</h1>
        </br>
        <div id='bar' class='indeterminate-progress-box'>
            <div class='indeterminate-progress-block'>
            </div>
        </div>
    `
}

// --- dropdown functions --- //

// on dom load
$('document ').ready(function(){    
    $('.dropdown-toggle').html($('.dropdown-menu a').html());
    $('#model_name').val($('.dropdown-menu a').html());
})

// file input text change
$(".custom-file-input").on("change", function() {
var fileName = $(this).val().split("\\").pop();
$(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});

// on dropdown change
$('.dropdown-menu a').on('click', function(){    
    $('.dropdown-toggle').html($(this).html());
    $('#model_name').val($(this).html());
})
