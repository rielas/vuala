use serde::{ser::SerializeMap, Deserialize, Serialize};
use url;

#[derive(Debug, Deserialize, PartialEq, Clone, Copy)]
pub enum Mode {
    Compact,
    Full,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Exchange {
    pub id: usize,
    pub request: Request,
    pub response: Response,
}

#[derive(Debug, Deserialize, PartialEq)]
pub struct Url(String);

impl Url {
    pub fn from_str(url: &str) -> Self {
        Url(url.to_string())
    }
}

impl Serialize for Url {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::ser::Serializer,
    {
        let url = url::Url::parse(&self.0).expect("Failed to parse URL");
        let path = url.path();
        let query = url.query().map_or("".to_owned(), |q| format!("?{}", q));
        serializer.serialize_str(format!("{path}{query}").as_str())
    }
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Request {
    pub url: Url,
    pub method: String,
    pub body: Body,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Response {
    pub status: i32,
    pub body: Body,
}

#[derive(Debug, Deserialize, PartialEq)]
pub enum BodyContent {
    QueryString(Vec<(Key, Value)>),
    Htlm(String),
    Empty,
}

#[derive(Debug, Deserialize, PartialEq)]
pub struct Body {
    pub content: BodyContent,
    pub mode: Mode,
}

impl Serialize for Body {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::ser::Serializer,
    {
        match &self.content {
            BodyContent::QueryString(ref query_string) => {
                let mut map = serializer.serialize_map(Some(query_string.len()))?;

                for (key, value) in query_string {
                    map.serialize_entry(key, value)?;
                }

                map.end()
            }
            BodyContent::Htlm(s) => match self.mode {
                Mode::Compact => serializer.serialize_str("<<html>>"),
                Mode::Full => serializer.serialize_str(s),
            },
            BodyContent::Empty => serializer.serialize_str("<<empty>>"),
        }
    }
}

pub type Key = String;
pub type Value = String;
