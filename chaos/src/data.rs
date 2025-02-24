use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};

pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
    // Calculate sums and return response

    let mut string_len = 0;
    let mut int_sum = 0;

    // for string in json response calculate strlen and add to string_len
    // if int, add to int_sum
    for elem in request.data.iter() {
        match elem {
            serde_json::Value::String(s) => string_len += s.len(),
            serde_json::Value::Number(n) => int_sum += n,
            _ => {}
        }
    }    

    let response = DataResponse {
        string_len,
        int_sum
    };

    (StatusCode::OK, Json(response))
}

#[derive(Deserialize)]
pub struct DataRequest {
    data:       Vec<i32>,
}

#[derive(Serialize)]
pub struct DataResponse {
    string_len: i32,
    int_sum:    i32,
}
