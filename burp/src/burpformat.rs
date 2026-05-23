use crate::representation;
use crate::representation::{BodyContent, Exchange, Mode, Url};
use serde::{Deserialize, Serialize};
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Items {
    #[serde(rename = "$value")]
    pub items: Vec<Item>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Item {
    time: String,
    url: String,
    port: i32,
    host: Host,
    protocol: String,
    method: String,
    path: String,
    extension: String,
    pub request: Request,
    status: i32,
    responselength: i32,
    mimetype: String,
    pub response: Response,
}

impl Item {
    pub fn to_exchange(&self, id: usize, mode: Mode) -> Exchange {
        let request = self.try_into_request(mode).unwrap();
        let response = self.try_into_response(mode).unwrap();
        Exchange {
            id,
            request,
            response,
        }
    }

    fn try_into_request(&self, mode: Mode) -> Result<representation::Request, &'static str> {
        let url = self.url.clone();
        let method = self.method.clone();
        let body = self.request.body()?;
        Ok(representation::Request {
            url: Url::from_str(&url),
            method,
            body: body.digest(mode),
        })
    }

    fn try_into_response(&self, mode: Mode) -> Result<representation::Response, &'static str> {
        let status = self.status;
        let body = self.response.body()?;
        Ok(representation::Response {
            status,
            body: body.digest(mode),
        })
    }
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct Host {
    #[serde(rename = "$value")]
    value: String,
    ip: String,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Request {
    #[serde(rename = "$value")]
    value: String,
    base64: bool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Response {
    #[serde(rename = "$value")]
    pub value: String,
    base64: bool,
}

pub trait HttpMessage {
    fn value(&self) -> &str;

    fn headers(&self) -> Vec<String> {
        self.value()
            .lines()
            .take_while(|line| !line.is_empty())
            .map(ToString::to_string)
            .collect()
    }

    fn body(&self) -> Result<Body, &'static str> {
        let body_str = self
            .value()
            .lines()
            .skip_while(|line| !line.is_empty())
            .skip(1) // Skip the empty line itself
            .collect::<Vec<&str>>()
            .join("\n"); // Rejoin the lines if necessary

        Body::from_str(&body_str)
    }
}

impl HttpMessage for Request {
    fn value(&self) -> &str {
        &self.value
    }
}

impl HttpMessage for Response {
    fn value(&self) -> &str {
        &self.value
    }
}

type Key = String;
type Value = String;

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub enum Body {
    QueryString(Vec<(Key, Value)>),
    Htlm(String),
    Empty,
}

impl FromStr for Body {
    type Err = &'static str;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.is_empty() {
            return Ok(Body::Empty);
        }

        if s.contains("<html>") && s.contains("</html>") {
            return Ok(Body::Htlm(s.to_owned()));
        }

        let query_string = s
            .split('&')
            .map(|pair| {
                let mut parts = pair.splitn(2, '=');
                match (parts.next(), parts.next()) {
                    (Some(key), Some(value)) => Ok((key.to_string(), value.to_string())),
                    _ => Err("Invalid query string"),
                }
            })
            .collect::<Result<Vec<(Key, Value)>, &'static str>>()?;

        Ok(Body::QueryString(query_string))
    }
}

impl Body {
    fn digest(self, mode: Mode) -> representation::Body {
        let content = match self {
            Body::QueryString(query_string) => {
                let mut body = Vec::<(Key, Value)>::new();

                for (key, value) in query_string {
                    body.push((key, value));
                }

                BodyContent::QueryString(body)
            }
            Body::Htlm(s) => BodyContent::Htlm(s),
            Body::Empty => BodyContent::Empty,
        };

        representation::Body { content, mode }
    }
}
