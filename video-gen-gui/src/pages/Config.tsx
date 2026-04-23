import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, RotateCcw, Save, FolderOpen, AlertCircle, CheckCircle } from "lucide-react";
import { useStore } from "../stores";
import { loadConfig, saveConfig } from "../utils/api";
import type { Config as ConfigType } from "../types";
import ConfirmDialog from "../components/ConfirmDialog";

export default function Config() {
  const navigate = useNavigate();
  const { setConfig, loading, setLoading, error, setError } = useStore();
  const [formData, setFormData] = useState<ConfigType | null>(null);
  const [yamlContent, setYamlContent] = useState("");
  const [showYaml, setShowYaml] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadConfigData();
  }, []);

  async function loadConfigData() {
    setLoading(true);
    setError(null);
    try {
      const data = await loadConfig();
      setConfig(data);
      setFormData(data);
      setYamlContent(JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load config");
    }
    setLoading(false);
  }

  function updateField(field: keyof ConfigType, value: unknown) {
    if (!formData) return;
    setFormData({ ...formData, [field]: value });
  }

  async function handleSave() {
    if (!formData) return;
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await saveConfig(formData);
      setConfig(formData);
      setSuccess("配置已保存");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    }
    setIsSaving(false);
  }

  async function handleReset() {
    const defaultConfig: ConfigType = {
      output_dir: "~/Videos/video-gen-output",
      default_resolution: "1080p",
      default_fps: 30,
      default_preset: undefined,
      max_concurrent: 2,
      auto_save_history: true,
      enable_notifications: true,
      debug_mode: false,
      prompt_template: "High quality video, {preset_keywords}, {description}, 4K resolution",
    };
    setFormData(defaultConfig);
    setShowResetConfirm(false);
  }

  if (loading || !formData) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <button className="btn btn-secondary" onClick={() => navigate("/")}>
          <ArrowLeft size={16} />
          返回
        </button>
        <h2 className="page-title">配置编辑</h2>
        <div style={{ display: "flex", gap: "8px" }}>
          <button className="btn btn-secondary" onClick={() => setShowResetConfirm(true)}>
            <RotateCcw size={16} />
            重置
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
            <Save size={16} />
            {isSaving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <CheckCircle size={16} />
          {success}
        </div>
      )}

      <p style={{ marginBottom: "20px", fontSize: "14px", color: "#64748b" }}>
        📄 配置文件: ~/.video-gen/config.yaml
      </p>

      <div className="config-section">
        <h3 className="config-section-title">基本设置</h3>

        <div className="form-group">
          <label className="form-label">默认输出目录</label>
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              type="text"
              className="form-input"
              value={formData.output_dir}
              onChange={(e) => updateField("output_dir", e.target.value)}
            />
            <button className="btn btn-secondary">
              <FolderOpen size={16} />
              浏览
            </button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">默认视频分辨率</label>
          <select
            className="form-select"
            value={formData.default_resolution}
            onChange={(e) => updateField("default_resolution", e.target.value)}
          >
            <option value="720p">720p (1280x720)</option>
            <option value="1080p">1080p (1920x1080)</option>
            <option value="4k">4K (3840x2160)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">默认帧率</label>
          <select
            className="form-select"
            value={formData.default_fps}
            onChange={(e) => updateField("default_fps", Number(e.target.value))}
          >
            <option value="24">24 fps</option>
            <option value="30">30 fps</option>
            <option value="60">60 fps</option>
          </select>
        </div>
      </div>

      <div className="config-section">
        <h3 className="config-section-title">高级设置</h3>

        <div className="form-group">
          <label className="form-label">并发生成数量</label>
          <input
            type="number"
            className="form-input"
            value={formData.max_concurrent}
            onChange={(e) => updateField("max_concurrent", Math.max(1, Math.min(5, Number(e.target.value))))}
            min={1}
            max={5}
          />
          <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>
            ⚠️ 建议不超过 3
          </p>
        </div>

        <div className="checkbox-group">
          <div className="checkbox-item">
            <input
              type="checkbox"
              checked={formData.auto_save_history}
              onChange={(e) => updateField("auto_save_history", e.target.checked)}
            />
            <label>自动保存提示词历史</label>
          </div>
          <div className="checkbox-item">
            <input
              type="checkbox"
              checked={formData.enable_notifications}
              onChange={(e) => updateField("enable_notifications", e.target.checked)}
            />
            <label>启用通知提醒</label>
          </div>
          <div className="checkbox-item">
            <input
              type="checkbox"
              checked={formData.debug_mode}
              onChange={(e) => updateField("debug_mode", e.target.checked)}
            />
            <label>调试模式</label>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">提示词模板</label>
          <textarea
            className="form-input"
            style={{ minHeight: "80px", resize: "vertical" }}
            value={formData.prompt_template || ""}
            onChange={(e) => updateField("prompt_template", e.target.value)}
          />
          <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>
            变量说明: {`{preset_keywords}`} - 预设关键词, {`{description}`} - 用户描述, {`{resolution}`} - 分辨率
          </p>
        </div>
      </div>

      <div className="config-section">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <h3 className="config-section-title" style={{ marginBottom: 0 }}>YAML 编辑器（高级）</h3>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowYaml(!showYaml)}>
            {showYaml ? "收起" : "展开"}
          </button>
        </div>
        {showYaml && (
          <textarea
            className="yaml-editor"
            value={yamlContent}
            onChange={(e) => setYamlContent(e.target.value)}
          />
        )}
      </div>

      {showResetConfirm && (
        <ConfirmDialog
          title="确认重置"
          message="确定要重置所有配置为默认值吗？"
          onConfirm={handleReset}
          onCancel={() => setShowResetConfirm(false)}
        />
      )}
    </div>
  );
}