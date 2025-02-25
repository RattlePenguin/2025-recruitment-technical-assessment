use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};

use serde_json::Value;

pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
    // Calculate sums and return response

    let mut string_len = 0;
    let mut int_sum = 0;

    // for string in json response calculate strlen and add to string_len
    // if int, add to int_sum
    for elem in request.data.iter() {
        match elem {
            Value::String(s) => string_len += s.len(),
            Value::Number(n) => {
                if n.is_i64() {
                    int_sum += n.as_i64().unwrap();
                }
            }
            _ => {}
        }
    }    

    let response = DataResponse {
        string_len: string_len.try_into().unwrap(),
        int_sum: int_sum.try_into().unwrap(),
    };

    (StatusCode::OK, Json(response))
}

#[derive(Deserialize)]
pub struct DataRequest {
    data:       Vec<serde_json::Value>,
}

#[derive(Serialize)]
pub struct DataResponse {
    string_len: i32,
    int_sum:    i32,
}
