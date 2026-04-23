use std::path::PathBuf;
use std::process::Command;

use crate::types::{SavedPreset, Credential, Config, ExportOptions};

pub fn get_python_path() -> String {
    // 尝试 1: 从环境变量获取
    if let Ok(path) = std::env::var("VIDEO_GEN_PYTHON") {
        return path;
    }
    
    // 尝试 2: 使用 video-gen-cli 的 venv
    let root_path = get_root_path();
    let cli_path = root_path.join("video-gen-cli");
    let venv_python = cli_path.join("venv").join("bin").join("python");
    if venv_python.exists() {
        eprintln!("DEBUG: Using venv python: {:?}", venv_python);
        return venv_python.display().to_string();
    }
    
    // 尝试 3: 回退到系统 python3
    eprintln!("DEBUG: Falling back to system python3");
    if let Ok(output) = Command::new("which").arg("python3").output() {
        String::from_utf8_lossy(&output.stdout).trim().to_string()
    } else {
        "python3".to_string()
    }
}

pub fn get_root_path() -> PathBuf {
    // 尝试从环境变量获取路径，或使用默认路径
    if let Ok(path) = std::env::var("VIDEO_GEN_ROOT_PATH") {
        eprintln!("DEBUG: Using env VIDEO_GEN_ROOT_PATH: {:?}", path);
        PathBuf::from(path)
    } else {
        // 默认路径：相对于 GUI 目录的父目录（即项目根目录）
        // GUI 从 video-gen-gui 目录启动，current_dir() 就是 video-gen-gui
        // 所以 parent() 才是项目根目录
        let gui_dir = std::env::current_dir()
            .unwrap_or_else(|_| PathBuf::from("."));
        eprintln!("DEBUG: GUI dir: {:?}", gui_dir);
        let root = gui_dir.parent()
            .unwrap_or(&PathBuf::from("."))
            .to_path_buf();
        eprintln!("DEBUG: Root path: {:?}", root);
        root
    }
}

pub fn get_video_gen_path() -> PathBuf {
    // 返回项目根目录
    get_root_path()
}

pub fn get_cli_path() -> PathBuf {
    // CLI 脚本路径：根目录/video-gen-cli/scripts/datastore_cli.py
    get_root_path().join("video-gen-cli").join("scripts").join("datastore_cli.py")
}

pub fn get_data_dir() -> PathBuf {
    // 尝试从环境变量获取数据目录
    if let Ok(path) = std::env::var("VIDEO_GEN_DATA_DIR") {
        PathBuf::from(path)
    } else {
        // 默认使用项目根目录的 data/
        get_root_path().join("data")
    }
}

fn call_cli(args: Vec<String>) -> Result<serde_json::Value, String> {
    let python_path = get_python_path();
    let cli_path = get_cli_path();
    let video_gen_path = get_video_gen_path();
    
    eprintln!("DEBUG call_cli:");
    eprintln!("  python_path: {:?}", python_path);
    eprintln!("  cli_path: {:?}", cli_path);
    eprintln!("  video_gen_path: {:?}", video_gen_path);
    eprintln!("  args: {:?}", args);
    
    let output = Command::new(&python_path)
        .arg(&cli_path)
        .args(&args)
        .current_dir(&video_gen_path)
        .output()
        .map_err(|e| format!("Failed to execute Python CLI: {}", e))?;
    
    eprintln!("  status: {}", output.status);
    eprintln!("  stdout: {}", String::from_utf8_lossy(&output.stdout));
    eprintln!("  stderr: {}", String::from_utf8_lossy(&output.stderr));
    
    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let trimmed = stdout.trim();
        
        if trimmed.is_empty() {
            return Err("Python CLI returned empty output".to_string());
        }
        
        let result: serde_json::Value = serde_json::from_str(trimmed)
            .map_err(|e| format!("Failed to parse JSON '{}': {}", trimmed, e))?;
        
        if let Some(error) = result.get("error") {
            return Err(error.as_str().unwrap_or("Unknown error").to_string());
        }
        
        Ok(result)
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python CLI error ({}): {}", output.status, stderr))
    }
}

#[tauri::command]
pub async fn get_preset_list(dimension: Option<String>) -> Result<Vec<serde_json::Value>, String> {
    let mut args = vec!["get_presets".to_string()];
    if let Some(dim) = dimension {
        args.push(dim);
    }
    
    let result = call_cli(args)?;
    
    if let Some(presets) = result.as_array() {
        Ok(presets.clone())
    } else {
        Err("Invalid response format".to_string())
    }
}

#[tauri::command]
pub async fn save_credential(provider: String, api_key: String) -> Result<bool, String> {
    let args = vec!["save_credential".to_string(), provider, api_key];
    let result = call_cli(args)?;
    
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn load_credentials() -> Result<Vec<Credential>, String> {
    let result = call_cli(vec!["get_credentials".to_string()])?;
    
    if let Some(credentials) = result.as_array() {
        let creds: Result<Vec<Credential>, _> = credentials
            .iter()
            .map(|c| {
                Ok(Credential {
                    provider: c.get("provider").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    api_key: c.get("api_key").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    configured: c.get("configured").and_then(|v| v.as_bool()).unwrap_or(false),
                })
            })
            .collect();
        creds
    } else {
        Err("Invalid response format".to_string())
    }
}

#[tauri::command]
pub async fn delete_credential(provider: String) -> Result<bool, String> {
    let args = vec!["delete_credential".to_string(), provider];
    let result = call_cli(args)?;
    
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn test_connection(_provider: String) -> Result<bool, String> {
    let python_path = get_python_path();
    let video_gen_path = get_video_gen_path();
    
    let script = format!(
        "import sys; sys.path.insert(0, '{}'); \
         from video_gen.agent_tools import AgentTools; \
         import asyncio; \
         tools = AgentTools(); \
         result = asyncio.run(tools.check_status()); \
         print(json.dumps(result))",
        video_gen_path.display()
    );
    
    let output = Command::new(&python_path)
        .arg("-c")
        .arg(&script)
        .current_dir(&video_gen_path)
        .output()
        .map_err(|e| format!("Failed to execute Python: {}", e))?;
    
    if output.status.success() {
        Ok(true)
    } else {
        Err(format!("Connection test failed"))
    }
}

#[tauri::command]
pub async fn load_config() -> Result<Config, String> {
    let result = call_cli(vec!["get_config".to_string()])?;
    
    let config: Config = serde_json::from_value(result)
        .map_err(|e| format!("Failed to parse config: {}", e))?;
    
    Ok(config)
}

#[tauri::command]
pub async fn save_config(config: Config) -> Result<bool, String> {
    let config_json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize config: {}", e))?;
    
    let args = vec!["save_config".to_string(), config_json];
    let result = call_cli(args)?;
    
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn export_prompts(
    presets: Vec<SavedPreset>,
    options: ExportOptions,
) -> Result<Vec<String>, String> {
    let output_dir = PathBuf::from(&options.output_dir);
    std::fs::create_dir_all(&output_dir)
        .map_err(|e| format!("Failed to create output dir: {}", e))?;
    
    let mut exported_files = Vec::new();
    
    for preset in presets {
        let filename = options.naming_rule
            .replace("{preset_name}", &preset.name)
            .replace("{date}", &chrono::Local::now().format("%Y%m%d").to_string());
        
        let file_path = if options.format == "json" {
            output_dir.join(format!("{}.json", filename))
        } else {
            output_dir.join(format!("{}.txt", filename))
        };
        
        if options.format == "json" {
            let json_content = serde_json::to_string_pretty(&preset)
                .map_err(|e| format!("Failed to serialize preset: {}", e))?;
            std::fs::write(&file_path, json_content)
                .map_err(|e| format!("Failed to write file: {}", e))?;
        } else {
            let content = format!(
                "Name: {}\nVisual: {}\nTime: {}\nCamera: {}\nCreated: {}",
                preset.name,
                preset.visual.unwrap_or_default(),
                preset.time.unwrap_or_default(),
                preset.camera.unwrap_or_default(),
                preset.created_at
            );
            std::fs::write(&file_path, content)
                .map_err(|e| format!("Failed to write file: {}", e))?;
        }
        
        exported_files.push(file_path.display().to_string());
    }
    
    Ok(exported_files)
}

#[tauri::command]
pub async fn save_preset(
    name: String,
    visual: Option<String>,
    time: Option<String>,
    camera: Option<String>,
) -> Result<bool, String> {
    let args = vec![
        "save_preset_combo".to_string(),
        name,
        visual.unwrap_or_default(),
        time.unwrap_or_default(),
        camera.unwrap_or_default(),
    ];
    let result = call_cli(args)?;
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn delete_preset(name: String) -> Result<bool, String> {
    let args = vec!["delete_preset_combo".to_string(), name];
    let result = call_cli(args)?;
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn get_saved_presets() -> Result<Vec<SavedPreset>, String> {
    let result = call_cli(vec!["get_preset_combos".to_string()])?;
    
    if let Some(combos) = result.as_array() {
        let saved: Vec<SavedPreset> = combos
            .iter()
            .map(|c| {
                SavedPreset {
                    name: c.get("name").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    visual: c.get("visual").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    time: c.get("time").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    camera: c.get("camera").and_then(|v| v.as_str()).map(|s| s.to_string()),
                    created_at: c.get("created_at").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                }
            })
            .collect();
        Ok(saved)
    } else {
        Err("Invalid response format".to_string())
    }
}

#[tauri::command]
pub async fn export_prompt(
    prompt: String,
    filename: Option<String>,
) -> Result<String, String> {
    let output_dir = PathBuf::from("output/prompts");
    std::fs::create_dir_all(&output_dir)
        .map_err(|e| format!("Failed to create output dir: {}", e))?;
    
    let timestamp = chrono::Local::now().format("%Y%m%d_%H%M%S").to_string();
    let name = filename.unwrap_or_else(|| format!("prompt_{}", timestamp));
    
    let file_path = output_dir.join(format!("{}.txt", name));
    
    std::fs::write(&file_path, prompt)
        .map_err(|e| format!("Failed to write prompt file: {}", e))?;
    
    Ok(file_path.display().to_string())
}

#[tauri::command]
pub async fn save_single_preset(
    dimension: String,
    preset_id: String,
    name: String,
    description: String,
    keywords: Vec<String>,
) -> Result<bool, String> {
    let keywords_json = serde_json::to_string(&keywords)
        .map_err(|e| format!("Failed to serialize keywords: {}", e))?;
    
    let args = vec![
        "save_preset".to_string(),
        dimension,
        preset_id,
        name,
        description,
        keywords_json,
        "".to_string(),
        "{}".to_string(),
    ];
    let result = call_cli(args)?;
    Ok(result.as_bool().unwrap_or(false))
}

#[tauri::command]
pub async fn delete_single_preset(
    dimension: String,
    preset_id: String,
) -> Result<bool, String> {
    let args = vec![
        "delete_preset".to_string(),
        dimension,
        preset_id,
    ];
    let result = call_cli(args)?;
    Ok(result.as_bool().unwrap_or(false))
}