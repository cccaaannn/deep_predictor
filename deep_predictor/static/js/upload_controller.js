const form = document.getElementById("image-form");

form.addEventListener("submit", post_form);


// generate prediction_id
function generate_id(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
 }

// generate the id when form is sent
function post_form(e){
    const id = generate_id(32)
    document.getElementById("prediction_id").value = id;
    console.log("prediction_id: " + id);
}

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

// on dom load
$('document ').ready(function(){    
    $('.dropdown-toggle').html($('.dropdown-menu a').html());
    $('#model_name').val($('.dropdown-menu a').html());
})

//   $('.dropdown').on('hidden.bs.dropdown', function () {
    
//     })

//   $('.dropdown').click(function(){

// $('.dropdown-menu').toggleClass('show');
// console.log($(this).value);
// });