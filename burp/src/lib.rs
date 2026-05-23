// rustimport:pyo3

use pyo3::prelude::*;
use std::{fs::File, io::Read};

mod burpformat;
mod representation;

#[pyfunction]
fn get_digest(filename: &str) -> String {
    let mut src = String::new();
    File::open(filename)
        .expect(&format!("Failed to open file: {}", filename))
        .read_to_string(&mut src)
        .expect("Failed to read file to string");
    let items: burpformat::Items = serde_xml_rs::from_str(&src).expect("Failed to parse XML");
    let items: Vec<representation::Exchange> = items
        .items
        .iter()
        .enumerate()
        .map(|(num, item)| item.to_exchange(num, representation::Mode::Compact))
        .collect();
    serde_json::to_string(&items).unwrap()
}

#[pyfunction]
fn get_json(filename: &str) -> String {
    let mut src = String::new();
    File::open(filename)
        .expect(&format!("Failed to open file: {}", filename))
        .read_to_string(&mut src)
        .expect("Failed to read file to string");
    let items: burpformat::Items = serde_xml_rs::from_str(&src).expect("Failed to parse XML");
    let items: Vec<representation::Exchange> = items
        .items
        .iter()
        .enumerate()
        .map(|(num, item)| item.to_exchange(num, representation::Mode::Full))
        .collect();
    serde_json::to_string(&items).unwrap()
}

#[pyfunction]
fn get_yaml(filename: &str) -> String {
    let mut src = String::new();
    File::open(filename)
        .expect(&format!("Failed to open file: {}", filename))
        .read_to_string(&mut src)
        .expect("Failed to read file to string");
    let items: burpformat::Items = serde_xml_rs::from_str(&src).expect("Failed to parse XML");
    let items: Vec<representation::Exchange> = items
        .items
        .iter()
        .enumerate()
        .map(|(num, item)| item.to_exchange(num, representation::Mode::Full))
        .collect();
    serde_json::to_string(&items).unwrap()
}


#[pymodule]
fn burp(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_digest, m)?)?;
    m.add_function(wrap_pyfunction!(get_json, m)?)?;
    m.add_function(wrap_pyfunction!(get_yaml, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_digest() {
        let f = get_digest("/Users/anatol/Projects/Neuralegion/business-logic-analysis/history.xml");
        print!("{}", f)
    }
}
