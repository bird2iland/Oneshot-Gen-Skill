import { invoke } from "@tauri-apps/api/core";
import { Preset, SavedPreset, Credential, Config, ExportOptions } from "../types";

export async function getPresetList(dimension?: string): Promise<Preset[]> {
  return invoke<Preset[]>("get_preset_list", { dimension });
}

export async function saveCredential(provider: string, apiKey: string): Promise<boolean> {
  return invoke<boolean>("save_credential", { provider, apiKey });
}

export async function loadCredentials(): Promise<Credential[]> {
  return invoke<Credential[]>("load_credentials");
}

export async function deleteCredential(provider: string): Promise<boolean> {
  return invoke<boolean>("delete_credential", { provider });
}

export async function testConnection(provider: string): Promise<boolean> {
  return invoke<boolean>("test_connection", { provider });
}

export async function loadConfig(): Promise<Config> {
  return invoke<Config>("load_config");
}

export async function saveConfig(config: Config): Promise<boolean> {
  return invoke<boolean>("save_config", { config });
}

export async function exportPrompts(presets: SavedPreset[], options: ExportOptions): Promise<string[]> {
  return invoke<string[]>("export_prompts", { presets, options });
}

export async function savePreset(
  name: string,
  visual?: string,
  time?: string,
  camera?: string
): Promise<boolean> {
  return invoke<boolean>("save_preset", { name, visual, time, camera });
}

export async function deletePreset(name: string): Promise<boolean> {
  return invoke<boolean>("delete_preset", { name });
}

export async function getSavedPresets(): Promise<SavedPreset[]> {
  return invoke<SavedPreset[]>("get_saved_presets");
}

export async function exportPrompt(prompt: string, filename?: string): Promise<string> {
  return invoke<string>("export_prompt", { prompt, filename });
}

export async function saveSinglePreset(
  dimension: string,
  presetId: string,
  name: string,
  description: string,
  keywords: string[]
): Promise<boolean> {
  return invoke<boolean>("save_single_preset", { dimension, presetId, name, description, keywords });
}

export async function deleteSinglePreset(
  dimension: string,
  presetId: string
): Promise<boolean> {
  return invoke<boolean>("delete_single_preset", { dimension, presetId });
}