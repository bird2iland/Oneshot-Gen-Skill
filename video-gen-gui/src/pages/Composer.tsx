import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Save, AlertTriangle, Download, CheckCircle } from "lucide-react";
import { useStore, useComposerStore } from "../stores";
import { getPresetList, savePreset, getSavedPresets, exportPrompt } from "../utils/api";
import { Preset } from "../types";
import ConfirmDialog from "../components/ConfirmDialog";

export default function Composer() {
  const navigate = useNavigate();
  const { presetName } = useParams();
  const { presets, setPresets, savedPresets, setSavedPresets, loading, setLoading, error, setError } = useStore();
  const {
    presetName: currentName,
    selectedVisual,
    selectedTime,
    selectedCamera,
    customDescription,
    generatedPrompt,
    conflictWarning,
    isSaving,
    setPresetName,
    setSelectedVisual,
    setSelectedTime,
    setSelectedCamera,
    setCustomDescription,
    setGeneratedPrompt,
    setConflictWarning,
    setIsSaving,
    reset,
  } = useComposerStore();
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  const conflicts: Record<string, string[]> = {
    timelapse: ["slow_motion"],
    slow_motion: ["timelapse"],
    gimbal: ["handheld"],
    handheld: ["gimbal"],
  };

  useEffect(() => {
    loadData();
    if (presetName) {
      const existing = savedPresets.find((p) => p.name === presetName);
      if (existing) {
        setPresetName(existing.name);
        setSelectedVisual(existing.visual || null);
        setSelectedTime(existing.time || null);
        setSelectedCamera(existing.camera || null);
      }
    }
  }, [presetName]);

  // 监听选中状态变化，自动更新提示词预览
  useEffect(() => {
    generatePromptFromSelection();
  }, [selectedVisual, selectedTime, selectedCamera, customDescription, presets]);

  function generatePromptFromSelection() {
    const parts: string[] = [];
    
    // 只添加当前选中模块的关键词
    if (selectedVisual) {
      const visual = presets.find((p) => p.id === selectedVisual && p.dimension === "visual");
      if (visual) parts.push(...visual.keywords);
    }
    if (selectedTime) {
      const time = presets.find((p) => p.id === selectedTime && p.dimension === "time");
      if (time) parts.push(...time.keywords);
    }
    if (selectedCamera) {
      const camera = presets.find((p) => p.id === selectedCamera && p.dimension === "camera");
      if (camera) parts.push(...camera.keywords);
    }
    if (customDescription) parts.push(customDescription);
    
    // 只有在有选中模块或有描述时才添加默认关键词
    if (parts.length > 0) {
      parts.push("4K resolution", "high quality");
    }
    
    setGeneratedPrompt(parts.join(", "));
  }

  async function loadData() {
    setLoading(true);
    try {
      const data = await getPresetList();
      setPresets(data.filter((p: Preset & { error?: string }) => !p.error));
      const saved = await getSavedPresets();
      setSavedPresets(saved);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    }
    setLoading(false);
  }

  function checkConflict(dimension: string, newPreset: string): boolean {
    const conflicting = conflicts[newPreset];
    if (!conflicting) return false;

    if (dimension === "time" && selectedVisual) {
      return false;
    }
    if (dimension === "camera" && (selectedVisual || selectedTime)) {
      return false;
    }

    return false;
  }

  function handleSelect(dimension: string, presetId: string) {
    setConflictWarning(null);

    // 如果点击的是已选中的预设，则取消选中
    if (dimension === "visual" && selectedVisual === presetId) {
      setSelectedVisual(null);
    } else if (dimension === "time" && selectedTime === presetId) {
      setSelectedTime(null);
    } else if (dimension === "camera" && selectedCamera === presetId) {
      setSelectedCamera(null);
    } else {
      // 否则选中该预设
      const hasConflict = checkConflict(dimension, presetId);
      if (hasConflict) {
        setConflictWarning(`${presetId} 与当前选择冲突`);
        return;
      }
      
      if (dimension === "visual") setSelectedVisual(presetId);
      else if (dimension === "time") setSelectedTime(presetId);
      else if (dimension === "camera") setSelectedCamera(presetId);
    }
    // 不需要手动调用 generatePrompt，useEffect 会自动处理
  }

  async function handleSave() {
    if (!currentName.trim()) {
      setError("请输入预设名称");
      return;
    }

    setIsSaving(true);
    try {
      await savePreset(
        currentName,
        selectedVisual ?? undefined,
        selectedTime ?? undefined,
        selectedCamera ?? undefined
      );
      const saved = await getSavedPresets();
      setSavedPresets(saved);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    }
    setIsSaving(false);
  }

  async function handleExportPrompt() {
    if (!generatedPrompt) {
      setError("没有可导出的提示词");
      return;
    }

    setIsExporting(true);
    setError(null);
    setExportSuccess(null);
    try {
      const filePath = await exportPrompt(generatedPrompt);
      setExportSuccess(`提示词已导出至: ${filePath}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    }
    setIsExporting(false);
  }

  function handleCancel() {
    if (currentName || selectedVisual || selectedTime || selectedCamera) {
      setShowCancelConfirm(true);
    } else {
      navigate("/");
    }
  }

  const visualPresets = presets.filter((p) => p.dimension === "visual");
  const timePresets = presets.filter((p) => p.dimension === "time");
  const cameraPresets = presets.filter((p) => p.dimension === "camera");

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <button className="btn btn-secondary" onClick={handleCancel}>
          <ArrowLeft size={16} />
          返回
        </button>
        <h2 className="page-title">{presetName ? `编辑预设: ${presetName}` : "新建预设"}</h2>
        <div style={{ display: "flex", gap: "8px" }}>
          <button 
            className="btn btn-secondary" 
            onClick={handleExportPrompt} 
            disabled={isExporting || !generatedPrompt}
          >
            <Download size={16} />
            {isExporting ? "导出中..." : "导出提示词"}
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
            <Save size={16} />
            {isSaving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      {exportSuccess && (
        <div className="alert alert-success">
          <CheckCircle size={16} />
          {exportSuccess}
        </div>
      )}

      {conflictWarning && (
        <div className="alert alert-warning">
          <AlertTriangle size={16} />
          冲突警告: {conflictWarning}
        </div>
      )}

      <div className="form-group">
        <label className="form-label">预设名称</label>
        <input
          type="text"
          className="form-input"
          value={currentName}
          onChange={(e) => setPresetName(e.target.value)}
          placeholder="输入预设名称..."
        />
      </div>

      <div className="config-section">
        <h3 className="config-section-title">视觉风格</h3>
        <div className="preset-selector">
          {visualPresets.map((preset) => (
            <div
              key={preset.id}
              className={`preset-option ${selectedVisual === preset.id ? "selected" : ""}`}
              onClick={() => handleSelect("visual", preset.id)}
            >
              <div className="preset-option-name">{preset.name}</div>
              <div className="preset-option-id">{preset.id}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="config-section">
        <h3 className="config-section-title">时间采样</h3>
        <div className="preset-selector">
          {timePresets.map((preset) => (
            <div
              key={preset.id}
              className={`preset-option ${selectedTime === preset.id ? "selected" : ""}`}
              onClick={() => handleSelect("time", preset.id)}
            >
              <div className="preset-option-name">{preset.name}</div>
              <div className="preset-option-id">{preset.id}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="config-section">
        <h3 className="config-section-title">运镜风格</h3>
        <div className="preset-selector">
          {cameraPresets.map((preset) => (
            <div
              key={preset.id}
              className={`preset-option ${selectedCamera === preset.id ? "selected" : ""}`}
              onClick={() => handleSelect("camera", preset.id)}
            >
              <div className="preset-option-name">{preset.name}</div>
              <div className="preset-option-id">{preset.id}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="config-section">
        <h3 className="config-section-title">提示词预览</h3>
        <div className="prompt-preview">
          {generatedPrompt || "选择预设后生成提示词"}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">描述补充（可选）</label>
        <textarea
          className="form-input"
          style={{ minHeight: "80px", resize: "vertical" }}
          value={customDescription}
          onChange={(e) => setCustomDescription(e.target.value)}
          placeholder="添加额外描述..."
        />
      </div>

      {showCancelConfirm && (
        <ConfirmDialog
          title="确认取消"
          message="当前有未保存的更改，确定要离开吗？"
          onConfirm={() => {
            reset();
            navigate("/");
          }}
          onCancel={() => setShowCancelConfirm(false)}
        />
      )}
    </div>
  );
}