export interface Preset {
  id: string;
  name: string;
  dimension: string;
  description: string;
  keywords: string[];
  template: string;
  metadata?: Record<string, unknown>;
  is_custom: boolean;
}

export interface SavedPreset {
  name: string;
  visual?: string;
  time?: string;
  camera?: string;
  created_at: string;
}

export interface Credential {
  provider: string;
  api_key: string;
  configured: boolean;
}

export interface Config {
  output_dir: string;
  default_resolution: string;
  default_fps: number;
  default_preset?: {
    visual: string;
    time: string;
    camera: string;
  };
  max_concurrent: number;
  auto_save_history: boolean;
  enable_notifications: boolean;
  debug_mode: boolean;
  prompt_template?: string;
}

export interface ExportOptions {
  format: string;
  output_dir: string;
  naming_rule: string;
}

export interface PresetConflict {
  dimension: string;
  preset1: string;
  preset2: string;
  reason: string;
}