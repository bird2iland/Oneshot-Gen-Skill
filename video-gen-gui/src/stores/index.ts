import { create } from "zustand";
import { Preset, SavedPreset, Credential, Config } from "../types";

interface AppState {
  presets: Preset[];
  savedPresets: SavedPreset[];
  credentials: Credential[];
  config: Config | null;
  loading: boolean;
  error: string | null;
  
  setPresets: (presets: Preset[]) => void;
  setSavedPresets: (presets: SavedPreset[]) => void;
  setCredentials: (credentials: Credential[]) => void;
  setConfig: (config: Config) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStore = create<AppState>((set) => ({
  presets: [],
  savedPresets: [],
  credentials: [],
  config: null,
  loading: false,
  error: null,
  
  setPresets: (presets) => set({ presets }),
  setSavedPresets: (savedPresets) => set({ savedPresets }),
  setCredentials: (credentials) => set({ credentials }),
  setConfig: (config) => set({ config }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));

interface ComposerState {
  presetName: string;
  selectedVisual: string | null;
  selectedTime: string | null;
  selectedCamera: string | null;
  customDescription: string;
  generatedPrompt: string;
  conflictWarning: string | null;
  isSaving: boolean;
  
  setPresetName: (name: string) => void;
  setSelectedVisual: (visual: string | null) => void;
  setSelectedTime: (time: string | null) => void;
  setSelectedCamera: (camera: string | null) => void;
  setCustomDescription: (desc: string) => void;
  setGeneratedPrompt: (prompt: string) => void;
  setConflictWarning: (warning: string | null) => void;
  setIsSaving: (saving: boolean) => void;
  reset: () => void;
}

export const useComposerStore = create<ComposerState>((set) => ({
  presetName: "",
  selectedVisual: null,
  selectedTime: null,
  selectedCamera: null,
  customDescription: "",
  generatedPrompt: "",
  conflictWarning: null,
  isSaving: false,
  
  setPresetName: (name) => set({ presetName: name }),
  setSelectedVisual: (visual) => set({ selectedVisual: visual }),
  setSelectedTime: (time) => set({ selectedTime: time }),
  setSelectedCamera: (camera) => set({ selectedCamera: camera }),
  setCustomDescription: (desc) => set({ customDescription: desc }),
  setGeneratedPrompt: (prompt) => set({ generatedPrompt: prompt }),
  setConflictWarning: (warning) => set({ conflictWarning: warning }),
  setIsSaving: (saving) => set({ isSaving: saving }),
  reset: () => set({
    presetName: "",
    selectedVisual: null,
    selectedTime: null,
    selectedCamera: null,
    customDescription: "",
    generatedPrompt: "",
    conflictWarning: null,
    isSaving: false,
  }),
}));

interface ExportState {
  selectedPresets: string[];
  exportFormat: "txt" | "json";
  exportDir: string;
  namingRule: string;
  isExporting: boolean;
  exportProgress: number;
  exportedFiles: string[];
  
  setSelectedPresets: (presets: string[]) => void;
  setExportFormat: (format: "txt" | "json") => void;
  setExportDir: (dir: string) => void;
  setNamingRule: (rule: string) => void;
  setIsExporting: (exporting: boolean) => void;
  setExportProgress: (progress: number) => void;
  setExportedFiles: (files: string[]) => void;
  reset: () => void;
}

export const useExportStore = create<ExportState>((set) => ({
  selectedPresets: [],
  exportFormat: "json",
  exportDir: "~/Desktop/video-gen-export",
  namingRule: "{preset_name}_{date}",
  isExporting: false,
  exportProgress: 0,
  exportedFiles: [],
  
  setSelectedPresets: (presets) => set({ selectedPresets: presets }),
  setExportFormat: (format) => set({ exportFormat: format }),
  setExportDir: (dir) => set({ exportDir: dir }),
  setNamingRule: (rule) => set({ namingRule: rule }),
  setIsExporting: (exporting) => set({ isExporting: exporting }),
  setExportProgress: (progress) => set({ exportProgress: progress }),
  setExportedFiles: (files) => set({ exportedFiles: files }),
  reset: () => set({
    selectedPresets: [],
    exportFormat: "json",
    exportDir: "~/Desktop/video-gen-export",
    namingRule: "{preset_name}_{date}",
    isExporting: false,
    exportProgress: 0,
    exportedFiles: [],
  }),
}));