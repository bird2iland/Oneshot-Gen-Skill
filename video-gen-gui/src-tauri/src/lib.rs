mod commands;
mod types;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let _ = app;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_preset_list,
            commands::save_credential,
            commands::load_credentials,
            commands::delete_credential,
            commands::test_connection,
            commands::load_config,
            commands::save_config,
            commands::export_prompts,
            commands::save_preset,
            commands::delete_preset,
            commands::get_saved_presets,
            commands::export_prompt,
            commands::save_single_preset,
            commands::delete_single_preset,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}