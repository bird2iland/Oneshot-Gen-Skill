use serde::{Deserialize, Serialize};

#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Preset {
    pub id: String,
    pub name: String,
    pub dimension: String,
    pub description: String,
    pub keywords: Vec<String>,
    pub template: String,
    pub metadata: Option<serde_json::Value>,
    pub is_custom: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SavedPreset {
    pub name: String,
    pub visual: Option<String>,
    pub time: Option<String>,
    pub camera: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Credential {
    pub provider: String,
    pub api_key: String,
    pub configured: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub output_dir: String,
    pub default_provider: String,
    pub default_model: String,
    pub default_visual_preset: Option<String>,
    pub default_time_preset: Option<String>,
    pub default_camera_preset: Option<String>,
    pub default_duration: u32,
    pub default_ratio: String,
    pub default_mode: String,
    pub poll_interval: f64,
    pub poll_max_wait: f64,
    pub poll_retry_count: u32,
    pub verbose: bool,
}

#[allow(dead_code)]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DefaultPreset {
    pub visual: String,
    pub time: String,
    pub camera: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportOptions {
    pub format: String,
    pub output_dir: String,
    pub naming_rule: String,
}
