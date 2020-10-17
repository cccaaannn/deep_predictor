
// generate prediction_id
const id = generate_id(12)
document.getElementById("prediction_id").value = id;
console.log("prediction_id: " + id);


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