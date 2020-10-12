
function on_error(){
    const result_div = document.getElementById('result_div');

    const error_html = `
    <h1 class="display-4">Prediction failed</h1>
    `;

    result_div.innerHTML = error_html;
}

function on_success(data){

    const result_div = document.getElementById('result_div');
    
    const confidence1 = Number.parseFloat(data.predictions["1"].confidence*100).toPrecision(4)
    const confidence2 = Number.parseFloat(data.predictions["2"].confidence*100).toPrecision(4)
    const confidence3 = Number.parseFloat(data.predictions["3"].confidence*100).toPrecision(4)

    result_div.innerHTML = `
        <h1 class="display-4">Prediction results</h1>
            
        <h2>class: ${data.predictions["1"].class_name}</h2>
        <div class="progress">
            <div class="progress-bar" style="width:${confidence1}%">
            ${confidence1}%
            </div>
        </div>
        
        </br>
        <h2>class: ${data.predictions["2"].class_name}</h2>
        <div class="progress">
            <div class="progress-bar bg-warning" role="progressbar" aria-valuenow="${confidence2}"
            aria-valuemin="0" aria-valuemax="100" style="width:${confidence2}%">
            ${confidence2}%
            </div>
        </div>

        </br>
        <h2>class: ${data.predictions["3"].class_name}</h2>
        <div class="progress">
            <div class="progress-bar bg-danger" role="progressbar" aria-valuenow="${confidence3}"
            aria-valuemin="0" aria-valuemax="100" style="width:${confidence3}%">
            ${confidence3}%
            </div>
        </div>
    `;
}





function fetch_api(){
    fetch("/api?prediction_id=" + prediction_id)
    .then((resp) => resp.json())
    .then(function(data) {
        if(data.prediction_status === 200){
            console.log(data)
            // var jsonPretty = JSON.stringify(data,null,2);


            on_success(data);

            clearInterval(interval)
            clearTimeout(timeout)
            clearTimeout(timeout2)
        }

    })
    .catch(function() {
        console.log("error");

        on_error();

    });


}





let interval = setInterval(fetch_api, 1000);


function timeout_function(){
    clearInterval(interval)
}

let timeout = setTimeout(timeout_function, 10000);



function timeout_function2(){
    on_error()
}

let timeout2 = setTimeout(timeout_function2, 11000);

