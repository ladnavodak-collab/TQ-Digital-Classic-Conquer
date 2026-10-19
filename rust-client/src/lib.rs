#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FpsLimit { Cap(u16), Uncapped }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ClientSettings { pub width: u32, pub height: u32, pub fps: FpsLimit }
impl ClientSettings {
    pub fn validate(self) -> Result<(), &'static str> {
        if !(800..=7680).contains(&self.width) || !(600..=4320).contains(&self.height) {
            return Err("invalid resolution");
        }
        if let FpsLimit::Cap(n) = self.fps {
            if !(30..=360).contains(&n) { return Err("invalid fps cap"); }
        }
        Ok(())
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn widescreen() { assert!(ClientSettings{width:1920,height:1080,fps:FpsLimit::Cap(144)}.validate().is_ok()); }
    #[test] fn uncapped() { assert!(ClientSettings{width:1920,height:1080,fps:FpsLimit::Uncapped}.validate().is_ok()); }
    #[test] fn rejects_bad_cap() { assert!(ClientSettings{width:1920,height:1080,fps:FpsLimit::Cap(0)}.validate().is_err()); }
    #[test] fn rejects_bad_resolution() { assert!(ClientSettings{width:0,height:1080,fps:FpsLimit::Cap(60)}.validate().is_err()); }
}
