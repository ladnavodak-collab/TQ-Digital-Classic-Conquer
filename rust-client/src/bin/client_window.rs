//! A pixel-based graphical *shell*, NOT the Conquer client.
//! Run: cargo run --features graphics --bin tq-classic-window -- client-settings.conf
//! Graphics dependency: minifb 0.27, downloaded by Cargo on the user's PC.
use minifb::{Key, MouseMode, Window, WindowOptions};
use std::{env, fs, process, thread, time::{Duration, Instant}};
use tq_classic_client_foundation::{ClientSettings, DisplayMode, FrameLimit};

const BACK: u32 = 0x101827;
const PANEL: u32 = 0x19263a;
const ACCENT: u32 = 0x55c8bb;
const LIGHT: u32 = 0xe2eef5;

fn rectangle(pixels: &mut [u32], width: usize, height: usize, x: usize, y: usize,
             w: usize, h: usize, color: u32) {
    let end_y = y.saturating_add(h).min(height);
    let end_x = x.saturating_add(w).min(width);
    for py in y.min(height)..end_y {
        let row = py * width;
        for px in x.min(width)..end_x { pixels[row + px] = color; }
    }
}

// Tiny hardcoded glyphs keep this demo asset-free and render without extra font libraries.
fn glyph(c: char) -> [u8; 7] {
    match c.to_ascii_uppercase() {
        'A' => [14,17,17,31,17,17,17], 'B' => [30,17,17,30,17,17,30],
        'C' => [14,17,16,16,16,17,14], 'D' => [30,17,17,17,17,17,30],
        'E' => [31,16,16,30,16,16,31], 'F' => [31,16,16,30,16,16,16],
        'G' => [14,17,16,23,17,17,14], 'H' => [17,17,17,31,17,17,17],
        'I' => [31,4,4,4,4,4,31], 'J' => [7,2,2,2,18,18,12],
        'K' => [17,18,20,24,20,18,17], 'L' => [16,16,16,16,16,16,31],
        'M' => [17,27,21,21,17,17,17], 'N' => [17,25,21,19,17,17,17],
        'O' => [14,17,17,17,17,17,14], 'P' => [30,17,17,30,16,16,16],
        'Q' => [14,17,17,17,21,18,13], 'R' => [30,17,17,30,20,18,17],
        'S' => [15,16,16,14,1,1,30], 'T' => [31,4,4,4,4,4,4],
        'U' => [17,17,17,17,17,17,14], 'V' => [17,17,17,17,17,10,4],
        'W' => [17,17,17,21,21,21,10], 'X' => [17,17,10,4,10,17,17],
        'Y' => [17,17,10,4,4,4,4], 'Z' => [31,1,2,4,8,16,31],
        '0' => [14,17,19,21,25,17,14], '1' => [4,12,4,4,4,4,14],
        '2' => [14,17,1,2,4,8,31], '3' => [30,1,1,14,1,1,30],
        '4' => [2,6,10,18,31,2,2], '5' => [31,16,16,30,1,1,30],
        '6' => [14,16,16,30,17,17,14], '7' => [31,1,2,4,8,8,8],
        '8' => [14,17,17,14,17,17,14], '9' => [14,17,17,15,1,1,14],
        ':' => [0,4,4,0,4,4,0], '.' => [0,0,0,0,0,12,12],
        '-' => [0,0,0,31,0,0,0], '/' => [1,1,2,4,8,16,16],
        _ => [0; 7],
    }
}
fn write_text(buf: &mut [u32], w: usize, h: usize, x: usize, y: usize,
              msg: &str, scale: usize, color: u32) {
    for (i, ch) in msg.chars().take(90).enumerate() {
        for (gy, bits) in glyph(ch).iter().enumerate() {
            for gx in 0..5 {
                if bits & (1 << (4 - gx)) != 0 {
                    rectangle(buf, w, h, x + i * 6 * scale + gx * scale,
                              y + gy * scale, scale, scale, color);
                }
            }
        }
    }
}
fn main() {
    let path = env::args().nth(1).unwrap_or_else(|| "client-settings.conf".into());
    let raw = match fs::read_to_string(&path) {
        Ok(x) => x,
        Err(err) => { eprintln!("Cannot read {path}: {err}. Run cargo run -- init first."); process::exit(2); }
    };
    let config = match ClientSettings::parse(&raw) {
        Ok(c) => c,
        Err(e) => { eprintln!("Invalid settings: {e}"); process::exit(2); }
    };
    let (w, h) = (usize::from(config.width), usize::from(config.height));
    // Deliberately no network traffic, no client asset patching, no auto-clicking.
    let mut window = Window::new("TQ Digital | Classic Client Shell (NOT GAME)", w, h,
        WindowOptions { resize: false, borderless: matches!(config.mode, DisplayMode::Borderless), ..WindowOptions::default() })
        .unwrap_or_else(|e| { eprintln!("Cannot create window: {e}"); process::exit(1) });
    let mut buffer = vec![BACK; w * h];
    let mut frames: u32 = 0;
    let mut shown_fps = 0;
    let mut last_second = Instant::now();
    let frame_budget = config.fps.target_frame_ns().map(Duration::from_nanos);
    while window.is_open() && !window.is_key_down(Key::Escape) {
        let start = Instant::now();
        buffer.fill(BACK);
        let margin = (w / 18).max(20);
        let panel_width = w.saturating_sub(margin * 2);
        rectangle(&mut buffer, w, h, margin, h/7, panel_width, h/2, PANEL);
        rectangle(&mut buffer, w, h, margin, h/7, panel_width, 9, ACCENT);
        let font_scale = (w / 480).clamp(1, 4);
        write_text(&mut buffer, w, h, margin + 25, h/7 + 28, "TQ DIGITAL CLASSIC", font_scale, LIGHT);
        write_text(&mut buffer, w, h, margin + 25, h/7 + 110, "RUST GRAPHICS SHELL", font_scale, ACCENT);
        write_text(&mut buffer, w, h, margin + 25, h/7 + 180, "NO SERVER CONNECTION YET", font_scale, LIGHT);
        let label = format!("{} X {}  FPS {}", w, h, shown_fps);
        write_text(&mut buffer, w, h, margin + 25, h/7 + 240, &label, font_scale, LIGHT);
        let mode = match config.fps { FrameLimit::Uncapped => "FPS LIMIT NONE", FrameLimit::Capped(_) => "FPS LIMIT ENABLED" };
        write_text(&mut buffer, w, h, margin + 25, h/7 + 290, mode, font_scale, ACCENT);
        if let Some((mx, my)) = window.get_mouse_pos(MouseMode::Clamp) {
            let x = (mx as usize).min(w.saturating_sub(1));
            let y = (my as usize).min(h.saturating_sub(1));
            rectangle(&mut buffer, w, h, x.saturating_sub(5), y, 11, 1, 0xffd36a);
            rectangle(&mut buffer, w, h, x, y.saturating_sub(5), 1, 11, 0xffd36a);
        }
        window.update_with_buffer(&buffer, w, h).unwrap_or_else(|e| { eprintln!("Display error: {e}"); process::exit(1) });
        frames = frames.saturating_add(1);
        if last_second.elapsed() >= Duration::from_secs(1) {
            shown_fps = frames;
            frames = 0;
            last_second = Instant::now();
        }
        if let Some(budget) = frame_budget {
            if let Some(remain) = budget.checked_sub(start.elapsed()) { thread::sleep(remain); }
        }
    }
}
