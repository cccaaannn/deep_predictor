
// divs
const header_div = document.getElementById('header_div');
const result_div = document.getElementById('result_div');


function on_success_keras(data){
    if(data.predictions.length < 1){
        header_div.innerHTML = `<h1 class="display-4">Nothing detected</h1>`;
    }
    else{
        header_div.innerHTML = `<h1 class="display-4">Prediction results</h1>`;
        animate_bar_charts(data);
    }
}

function on_success_darknet(data){
    if(data.predictions.length < 1){
        header_div.innerHTML = `<h1 class="display-4">Nothing detected</h1>`;
    }
    else{
        header_div.innerHTML = `<h1 class="display-4">Detection results</h1><p>${data.predictions.length} unique object(s) found</p>`;
        // let predictions = data.predictions;
        // for (let index = 0; index < predictions.length; index++) {
        //     result_div.innerHTML += `
        //     <h2>${predictions[index].class_name}  (% ${predictions[index].confidence})</h2>
        //     `
        // }
        animate_bar_charts(data);
    }
}

function on_error(){
    const error_html = `
    <h1 class="display-4">Prediction failed</h1>
    `;
    header_div.innerHTML = error_html;
}





function animate_bar_charts(data){
    /*animates charts->                   because why not */

    colors = ["", "bg-warning", "bg-danger"]
    let confidences = [];
    let class_names = [];
    let vals = [];
    let increments = [];
    for (let index = 0; index < data.predictions.length; index++) {
        confidences.push(Number.parseFloat(data.predictions[index].confidence*100).toPrecision(4));
        class_names.push(data.predictions[index].class_name)
        vals.push(0);
        increments.push(confidences[index] / 100);
    }

    for (let i = 0; i < 100; i++) {
        setTimeout(function() {
            result_div.innerHTML = ``
            
            for (let index = 0; index < confidences.length; index++) {
                
                let percent = Number.parseFloat(vals[index]).toPrecision(4);
                
                // don't show below 1 percent
                if(percent < 1){
                    break;
                }

                let color_index = 0;
                if(percent < 80){
                    color_index = 1;    
                }
                if(percent < 40){
                    color_index = 2;    
                }

                result_div.innerHTML += `
                    <h2>${class_names[index]}</h2>
                    <div class="progress">
                        <div class="progress-bar ${colors[color_index]} progress-bar-striped progress-bar-animated" style="width:${percent}%">
                            <div class="chart_text"> 
                                <h5>${percent}%</h5>
                            </div>
                        </div>
                    </div>
                `
            }


            for (let index2 = 0; index2 < vals.length; index2++) {
                vals[index2] += increments[index2];
            }

            // final results for correct percentages
            if(i == 99){
                result_div.innerHTML = ``
                for (let index3 = 0; index3 < confidences.length; index3++) {

                    // don't show below 1 percent
                    if(confidences[index3] < 1){
                        break;
                    }
                    let color_index = 0;
                    if(confidences[index3] < 80){
                        color_index = 1;    
                    }
                    if(confidences[index3] < 40){
                        color_index = 2;    
                    }
                    result_div.innerHTML += `
                        <h2>${class_names[index3]}</h2>
                        <div class="progress">
                            <div class="progress-bar ${colors[color_index]} progress-bar-striped progress-bar-animated" style="width:${confidences[index3]}%">
                                <div class="chart_text"> 
                                <h5>${confidences[index3]}%</h5>
                                </div>
                            </div>
                        </div>
                    `
                }
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



            
            if(data.model_info.predictor_backend === "keras"){
                on_success_keras(data);
            }
            else if(data.model_info.predictor_backend === "darknet" || data.model_info.predictor_backend === "tf_yolo"){
                on_success_darknet(data);
            }
            else{
                clearInterval(api_request_interval);
                clearTimeout(api_request_timeout);
                on_error();
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

