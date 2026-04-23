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
