//! Original client configuration and frame-pacing foundation.
//! No imported Preservation source, graphics, login, or Conquer packet support.
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DisplayMode { Windowed, Borderless }

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FrameLimit { Capped(u16), Uncapped }

impl FrameLimit {
    pub fn target_frame_ns(self) -> Option<u64> {
        match self {
            FrameLimit::Uncapped => None,
            FrameLimit::Capped(fps) if fps > 0 => Some(1_000_000_000 / u64::from(fps)),
            _ => None,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ClientSettings {
    pub width: u16,
    pub height: u16,
    pub mode: DisplayMode,
    pub fps: FrameLimit,
    pub auto_clicker_enabled: bool,
}

#[derive(Debug, PartialEq, Eq)]
pub enum ConfigError { InvalidResolution, InvalidFrameLimit, InvalidLine, DuplicateKey, MissingKey, InvalidValue }
impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "{self:?}") }
}
impl std::error::Error for ConfigError {}

impl Default for ClientSettings {
    fn default() -> Self {
        Self { width: 1920, height: 1080, mode: DisplayMode::Windowed,
            fps: FrameLimit::Capped(144), auto_clicker_enabled: false }
    }
}
impl ClientSettings {
    pub fn validate(&self) -> Result<(), ConfigError> {
        if !(800..=7680).contains(&self.width) || !(600..=4320).contains(&self.height) {
            return Err(ConfigError::InvalidResolution);
        }
        if let FrameLimit::Capped(value) = self.fps {
            if !matches!(value, 30 | 60 | 120 | 144 | 165 | 240) {
                return Err(ConfigError::InvalidFrameLimit);
            }
        }
        Ok(())
    }
    pub fn serialize(&self) -> String {
        format!("width={}\nheight={}\nmode={}\nfps={}\nauto_clicker_enabled={}\n",
            self.width, self.height,
            match self.mode { DisplayMode::Windowed => "windowed", DisplayMode::Borderless => "borderless" },
            match self.fps { FrameLimit::Capped(x) => x.to_string(), FrameLimit::Uncapped => "uncapped".into() },
            self.auto_clicker_enabled)
    }
    pub fn parse(input: &str) -> Result<Self, ConfigError> {
        let mut width = None; let mut height = None; let mut mode = None;
        let mut fps = None; let mut auto_clicker_enabled = None;
        for line in input.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') { continue; }
            let (key, value) = line.split_once('=').ok_or(ConfigError::InvalidLine)?;
            let value = value.trim();
            let slot = match key.trim() {
                "width" => { if width.replace(value.parse().map_err(|_| ConfigError::InvalidValue)?).is_some() { return Err(ConfigError::DuplicateKey); } continue; },
                "height" => { if height.replace(value.parse().map_err(|_| ConfigError::InvalidValue)?).is_some() { return Err(ConfigError::DuplicateKey); } continue; },
                "mode" => &mut mode,
                "fps" => { let val = if value == "uncapped" { FrameLimit::Uncapped }
                    else { FrameLimit::Capped(value.parse().map_err(|_| ConfigError::InvalidValue)?) };
                    if fps.replace(val).is_some() { return Err(ConfigError::DuplicateKey); } continue; },
                "auto_clicker_enabled" => { let val = value.parse().map_err(|_| ConfigError::InvalidValue)?;
                    if auto_clicker_enabled.replace(val).is_some() { return Err(ConfigError::DuplicateKey); } continue; },
                _ => return Err(ConfigError::InvalidLine),
            };
            let val = match value { "windowed" => DisplayMode::Windowed, "borderless" => DisplayMode::Borderless,
                _ => return Err(ConfigError::InvalidValue) };
            if slot.replace(val).is_some() { return Err(ConfigError::DuplicateKey); }
        }
        let output = Self { width: width.ok_or(ConfigError::MissingKey)?,
            height: height.ok_or(ConfigError::MissingKey)?, mode: mode.ok_or(ConfigError::MissingKey)?,
            fps: fps.ok_or(ConfigError::MissingKey)?,
            auto_clicker_enabled: auto_clicker_enabled.ok_or(ConfigError::MissingKey)? };
        output.validate()?;
        Ok(output)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn round_trip_defaults() { let s = ClientSettings::default(); assert_eq!(ClientSettings::parse(&s.serialize()), Ok(s)); }
    #[test]
    fn widescreen_and_uncapped() {
        let s = ClientSettings { fps: FrameLimit::Uncapped, mode: DisplayMode::Borderless, ..ClientSettings::default() };
        assert_eq!(s.fps.target_frame_ns(), None);
        assert_eq!(ClientSettings::parse(&s.serialize()), Ok(s));
    }
    #[test]
    fn reject_zero_fps() { let mut s = ClientSettings::default(); s.fps = FrameLimit::Capped(0); assert_eq!(s.validate(), Err(ConfigError::InvalidFrameLimit)); }
    #[test]
    fn reject_duplicate_and_unknown() {
        let s = ClientSettings::default().serialize();
        assert_eq!(ClientSettings::parse(&(s.clone() + "width=1024\n")), Err(ConfigError::DuplicateKey));
        assert_eq!(ClientSettings::parse(&(s + "unknown=1\n")), Err(ConfigError::InvalidLine));
    }
    #[test]
    fn reject_invalid_resolution() { let mut s = ClientSettings::default(); s.width = 0; assert_eq!(s.validate(), Err(ConfigError::InvalidResolution)); }
}
