
// divs
const header_div = document.getElementById('header_div');
const result_div = document.getElementById('result_div');


function on_success_keras(data){
    header_div.innerHTML = `<h1 class="display-4">Prediction results</h1>`;
    animate_bar_charts(data);
}


function on_success_darknet(data){

}


function on_error(){
    const error_html = `
    <h1 class="display-4">Prediction failed</h1>
    `;
    header_div.innerHTML = error_html;
}



function animate_bar_charts(data){
    /*animates charts                   because why not */

    let is_confident = "";
    if(data.predictions.is_confident === 1){
        is_confident = "confident";
    }
    else{
        is_confident = "not confident";
    }

    const confidence1 = Number.parseFloat(data.predictions["1"].confidence*100).toPrecision(4);
    const confidence2 = Number.parseFloat(data.predictions["2"].confidence*100).toPrecision(4);
    const confidence3 = Number.parseFloat(data.predictions["3"].confidence*100).toPrecision(4);

    let val1 = 0;
    let val2 = 0;
    let val3 = 0;

    const increment1 = confidence1 / 100;
    const increment2 = confidence2 / 100;
    const increment3 = confidence3 / 100;


    for (let i = 0; i < 100; i++) {
        setTimeout(function() {
            result_div.innerHTML = `
                <h2>${data.predictions["1"].class_name} (${is_confident})</h2>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width:${Number.parseFloat(val1).toPrecision(4)}%">
                        <div class="chart_text"> 
                            ${Number.parseFloat(val1).toPrecision(4)}%
                        </div>
                    </div>
                </div>
            `

            result_div.innerHTML += `
                <h2>${data.predictions["2"].class_name}</h2>
                <div class="progress">
                    <div class="progress-bar bg-warning progress-bar-striped progress-bar-animated" style="width:${Number.parseFloat(val2).toPrecision(4)}%">
                        <div class="chart_text"> 
                            ${Number.parseFloat(val2).toPrecision(4)}%
                        </div>
                    </div>
                </div>
            `

            result_div.innerHTML += `
                <h2>${data.predictions["3"].class_name}</h2>
                <div class="progress">
                    <div class="progress-bar bg-danger progress-bar-striped progress-bar-animated" style="width:${Number.parseFloat(val3).toPrecision(4)}%">
                        <div class="chart_text"> 
                            ${Number.parseFloat(val3).toPrecision(4)}%
                        </div>
                    </div>
                </div>
            `

            val1 += increment1;
            val2 += increment2;
            val3 += increment3;


            // show final results
            if(i === 99){
                result_div.innerHTML = `
                    <h2>${data.predictions["1"].class_name} (${is_confident})</h2>
                    <div class="progress">
                        <div class="progress-bar" style="width:${confidence1}%">
                            <div class="chart_text"> 
                                ${confidence1}%
                            </div>
                        </div>
                    </div>
                `

                result_div.innerHTML += `
                    <h2>${data.predictions["2"].class_name}</h2>
                    <div class="progress">
                        <div class="progress-bar bg-warning" style="width:${confidence2}%">
                            <div class="chart_text"> 
                                ${confidence2}%
                            </div>
                        </div>
                    </div>
                `

                result_div.innerHTML += `
                    <h2>${data.predictions["3"].class_name}</h2>
                    <div class="progress">
                        <div class="progress-bar bg-danger" style="width:${confidence3}%">
                            <div class="chart_text"> 
                                ${confidence3}%
                            </div>
                        </div>
                    </div>
                `

            }

        }, i*30);
    }
}





// request the api
function fetch_api(){
    fetch("/api?prediction_id=" + prediction_id)
    .then((resp) => resp.json())
    .then(function(data) {
        if(data.prediction_status === 200){
            console.log(data)
            // var jsonPretty = JSON.stringify(data,null,2);


            if(data.model_id === 1){
                on_success_keras(data);
            }
            else if(data.model_id === 2){
                on_success_darknet(data);
            }
            


            clearInterval(api_request_interval);
            clearTimeout(api_request_timeout);
        }

    })
    .catch(function() {
        console.log("error");
        clearInterval(api_request_interval);
        on_error();
    });
}








// request the api every 1 second for 10 seconds
function api_request_timeout_function(){
    clearInterval(api_request_interval);
    on_error();
}

let api_request_interval = setInterval(fetch_api, 1000);

let api_request_timeout = setTimeout(api_request_timeout_function, 10000);



// function timeout_function2(){
//     on_error()
// }

// let timeout2 = setTimeout(timeout_function2, 11000);

