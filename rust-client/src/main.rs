use std::{env, fs, process};
use tq_classic_client_foundation::ClientSettings;
fn main() {
    let args: Vec<String> = env::args().collect();
    let default_path = "client-settings.conf";
    match args.get(1).map(String::as_str) {
        Some("init") => {
            let path = args.get(2).map(String::as_str).unwrap_or(default_path);
            if std::path::Path::new(path).exists() { eprintln!("Refusing to overwrite: {path}"); process::exit(2); }
            if let Err(e) = fs::write(path, ClientSettings::default().serialize()) { eprintln!("{e}"); process::exit(1); }
            println!("Created settings at {path}");
        }
        Some("check") => {
            let path = args.get(2).map(String::as_str).unwrap_or(default_path);
            match fs::read_to_string(path).ok().and_then(|x| ClientSettings::parse(&x).ok()) {
                Some(s) => println!("Settings valid: {s:?}; no game client implemented"),
                None => { eprintln!("Invalid or unreadable settings: {path}"); process::exit(2); }
            }
        }
        _ => println!("Usage: tq-classic-client-foundation [init|check] [path]\nNot a game client or launcher yet."),
    }
}
