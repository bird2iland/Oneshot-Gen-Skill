import { useEffect, useState } from "react";
import { Plus, Edit, Trash2, AlertCircle, Save, X, CheckCircle, Settings } from "lucide-react";
import { useStore } from "../stores";
import { getPresetList, getSavedPresets, deletePreset, saveSinglePreset, deleteSinglePreset } from "../utils/api";
import { Preset } from "../types";
import ConfirmDialog from "../components/ConfirmDialog";

interface EditPresetForm {
  id: string;
  dimension: string;
  name: string;
  description: string;
  keywords: string;
}

export default function PresetList() {
  const { presets, savedPresets, setPresets, setSavedPresets, loading, setLoading, error, setError } = useStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDimension, setFilterDimension] = useState<string>("all");
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string; dimension: string } | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // 新建预设表单状态
  const [showNewPresetForm, setShowNewPresetForm] = useState(false);
  const [newPreset, setNewPreset] = useState({
    name: "",
    dimension: "visual",
    description: "",
    keywords: "",
  });
  const [isSavingNew, setIsSavingNew] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  
  // 管理模式状态
  const [isManageMode, setIsManageMode] = useState(false);
  
  // 编辑预设表单状态
  const [showEditPresetForm, setShowEditPresetForm] = useState(false);
  const [editPreset, setEditPreset] = useState<EditPresetForm>({
    id: "",
    dimension: "",
    name: "",
    description: "",
    keywords: "",
  });
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const presetData = await getPresetList();
      setPresets(presetData.filter((p: Preset & { error?: string }) => !p.error));
      const savedData = await getSavedPresets();
      setSavedPresets(savedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load presets");
    }
    setLoading(false);
  }

  function handleDelete(preset: { id: string; name: string; dimension: string }) {
    // 所有预设都可以删除
    setDeleteTarget(preset);
    setShowDeleteConfirm(true);
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      let result = false;
      if (deleteTarget.dimension === "combo") {
        // combo 预设使用 deletePreset（使用 name）
        result = await deletePreset(deleteTarget.name);
      } else {
        // 单个预设使用 deleteSinglePreset（使用 ID）
        result = await deleteSinglePreset(deleteTarget.dimension, deleteTarget.id);
      }
      
      // 检查删除结果
      if (!result) {
        throw new Error('删除失败：Python CLI 返回 false');
      }
      
      await loadData();
      setSaveSuccess(`预设 "${deleteTarget.name}" 已删除`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete preset");
      setSaveSuccess(null);  // 删除失败时清除成功提示
    }
    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  }

  function handleEdit(preset: Preset) {
    // 所有预设都可以编辑
    if (preset.dimension === "combo") {
      // combo 预设跳转到组合编辑页面
      window.location.href = `/composer/${preset.name}`;
    } else {
      // 单个预设显示编辑表单
      setEditPreset({
        id: preset.id,
        dimension: preset.dimension,
        name: preset.name,
        description: preset.description,
        keywords: preset.keywords.join(", "),
      });
      setShowEditPresetForm(true);
      setShowNewPresetForm(false);
      setError(null);
      setSaveSuccess(null);
    }
  }

  async function handleSaveEditPreset() {
    if (!editPreset.name.trim()) {
      setError("请输入预设名称");
      return;
    }
    if (!editPreset.description.trim() && !editPreset.keywords.trim()) {
      setError("请输入描述或关键词");
      return;
    }

    setIsSavingEdit(true);
    setError(null);
    try {
      const keywordsList = editPreset.keywords
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      // 直接保存，后端会自动覆盖
      await saveSinglePreset(
        editPreset.dimension,
        editPreset.id,
        editPreset.name,
        editPreset.description,
        keywordsList
      );

      setSaveSuccess(`预设 "${editPreset.name}" 已更新`);
      setShowEditPresetForm(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save preset");
    }
    setIsSavingEdit(false);
  }

  function handleCancelEditPreset() {
    setShowEditPresetForm(false);
    setEditPreset({
      id: "",
      dimension: "",
      name: "",
      description: "",
      keywords: "",
    });
    setError(null);
  }

  function handleNewPreset() {
    setShowNewPresetForm(true);
    setShowEditPresetForm(false);
    setNewPreset({
      name: "",
      dimension: "visual",
      description: "",
      keywords: "",
    });
    setError(null);
    setSaveSuccess(null);
  }

  async function handleSaveNewPreset() {
    if (!newPreset.name.trim()) {
      setError("请输入预设名称");
      return;
    }
    if (!newPreset.description.trim() && !newPreset.keywords.trim()) {
      setError("请输入描述或关键词");
      return;
    }

    setIsSavingNew(true);
    setError(null);
    try {
      const keywordsList = newPreset.keywords
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      const presetId = newPreset.name.toLowerCase().replace(/\s+/g, "_");

      await saveSinglePreset(
        newPreset.dimension,
        presetId,
        newPreset.name,
        newPreset.description,
        keywordsList
      );

      setSaveSuccess(`预设 "${newPreset.name}" 已保存`);
      setShowNewPresetForm(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save preset");
    }
    setIsSavingNew(false);
  }

  function handleCancelNewPreset() {
    setShowNewPresetForm(false);
    setNewPreset({
      name: "",
      dimension: "visual",
      description: "",
      keywords: "",
    });
    setError(null);
  }

  function handleEnterManageMode() {
    setIsManageMode(true);
  }

  function handleExitManageMode() {
    setIsManageMode(false);
    setShowEditPresetForm(false);
  }

  const filteredPresets = presets.filter((preset) => {
    const matchesSearch = preset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      preset.keywords.some((k) => k.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = filterDimension === "all" || preset.dimension === filterDimension;
    return matchesSearch && matchesFilter;
  });

  // 合并预设列表：普通预设 + combo 预设
  const allPresets = [...filteredPresets, ...savedPresets.map((sp) => ({
    id: sp.name,
    name: sp.name,
    dimension: "combo",
    description: `Visual: ${sp.visual || "none"}, Time: ${sp.time || "none"}, Camera: ${sp.camera || "none"}`,
    keywords: [sp.visual || "", sp.time || "", sp.camera || ""].filter(Boolean),
    template: "",
  } as Preset))];

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
        <h2 className="page-title">预设列表</h2>
        <div style={{ display: "flex", gap: "8px" }}>
          {isManageMode ? (
            <button className="btn btn-secondary" onClick={handleExitManageMode}>
              <X size={16} />
              退出管理
            </button>
          ) : (
            <>
              <button className="btn btn-secondary" onClick={handleEnterManageMode}>
                <Settings size={16} />
                管理预设
              </button>
              <button className="btn btn-primary" onClick={handleNewPreset}>
                <Plus size={16} />
                新建预设
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {saveSuccess && (
        <div className="alert alert-success">
          <CheckCircle size={16} />
          {saveSuccess}
        </div>
      )}

      {/* 编辑预设表单 */}
      {showEditPresetForm && (
        <div className="card" style={{ marginBottom: "20px", border: "2px solid #f59e0b" }}>
          <div className="card-header">
            <h3 className="card-title">编辑预设：{editPreset.name}</h3>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={handleCancelEditPreset}
              style={{ padding: "4px 8px" }}
            >
              <X size={14} />
              取消
            </button>
          </div>
          <div className="card-body">
            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">预设 ID（不可修改）</label>
              <input
                type="text"
                className="form-input"
                value={editPreset.id}
                disabled
                style={{ backgroundColor: "#f1f5f9" }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">所属维度（不可修改）</label>
              <input
                type="text"
                className="form-input"
                value={editPreset.dimension === "visual" ? "视觉风格" : 
                       editPreset.dimension === "time" ? "时间采样" : 
                       editPreset.dimension === "camera" ? "运镜风格" : editPreset.dimension}
                disabled
                style={{ backgroundColor: "#f1f5f9" }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">预设名称</label>
              <input
                type="text"
                className="form-input"
                value={editPreset.name}
                onChange={(e) => setEditPreset({ ...editPreset, name: e.target.value })}
                placeholder="预设名称"
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">描述</label>
              <input
                type="text"
                className="form-input"
                value={editPreset.description}
                onChange={(e) => setEditPreset({ ...editPreset, description: e.target.value })}
                placeholder="预设描述"
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">关键词（用逗号分隔）</label>
              <input
                type="text"
                className="form-input"
                value={editPreset.keywords}
                onChange={(e) => setEditPreset({ ...editPreset, keywords: e.target.value })}
                placeholder="关键词 1, 关键词 2, ..."
              />
            </div>

            <button 
              className="btn btn-primary" 
              onClick={handleSaveEditPreset}
              disabled={isSavingEdit}
            >
              <Save size={16} />
              {isSavingEdit ? "保存中..." : "保存修改"}
            </button>
          </div>
        </div>
      )}

      {/* 新建预设表单 */}
      {showNewPresetForm && (
        <div className="card new-preset-card" style={{ marginBottom: "20px", border: "2px solid #3b82f6" }}>
          <div className="card-header">
            <h3 className="card-title">新建预设</h3>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={handleCancelNewPreset}
              style={{ padding: "4px 8px" }}
            >
              <X size={14} />
              取消
            </button>
          </div>
          <div className="card-body">
            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">预设名称</label>
              <input
                type="text"
                className="form-input"
                value={newPreset.name}
                onChange={(e) => setNewPreset({ ...newPreset, name: e.target.value })}
                placeholder="例如：realistic, cinematic, vintage..."
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">所属维度</label>
              <div className="filter-group" style={{ marginTop: "8px" }}>
                <button
                  className={`filter-btn ${newPreset.dimension === "visual" ? "active" : ""}`}
                  onClick={() => setNewPreset({ ...newPreset, dimension: "visual" })}
                >
                  视觉风格
                </button>
                <button
                  className={`filter-btn ${newPreset.dimension === "time" ? "active" : ""}`}
                  onClick={() => setNewPreset({ ...newPreset, dimension: "time" })}
                >
                  时间采样
                </button>
                <button
                  className={`filter-btn ${newPreset.dimension === "camera" ? "active" : ""}`}
                  onClick={() => setNewPreset({ ...newPreset, dimension: "camera" })}
                >
                  运镜风格
                </button>
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">描述</label>
              <input
                type="text"
                className="form-input"
                value={newPreset.description}
                onChange={(e) => setNewPreset({ ...newPreset, description: e.target.value })}
                placeholder="例如：写实风格，真实感强，细节丰富"
              />
            </div>

            <div className="form-group" style={{ marginBottom: "12px" }}>
              <label className="form-label">关键词（用逗号分隔）</label>
              <input
                type="text"
                className="form-input"
                value={newPreset.keywords}
                onChange={(e) => setNewPreset({ ...newPreset, keywords: e.target.value })}
                placeholder="例如：photorealistic, detailed, natural lighting"
              />
            </div>

            <button 
              className="btn btn-primary" 
              onClick={handleSaveNewPreset}
              disabled={isSavingNew}
            >
              <Save size={16} />
              {isSavingNew ? "保存中..." : "保存预设"}
            </button>
          </div>
        </div>
      )}

      <div className="search-box">
        <input
          type="text"
          className="search-input"
          placeholder="搜索预设..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <div className="filter-group">
          <button
            className={`filter-btn ${filterDimension === "all" ? "active" : ""}`}
            onClick={() => setFilterDimension("all")}
          >
            全部
          </button>
          <button
            className={`filter-btn ${filterDimension === "visual" ? "active" : ""}`}
            onClick={() => setFilterDimension("visual")}
          >
            视觉风格
          </button>
          <button
            className={`filter-btn ${filterDimension === "time" ? "active" : ""}`}
            onClick={() => setFilterDimension("time")}
          >
            时间采样
          </button>
          <button
            className={`filter-btn ${filterDimension === "camera" ? "active" : ""}`}
            onClick={() => setFilterDimension("camera")}
          >
            运镜风格
          </button>
          {savedPresets.length > 0 && (
            <button
              className={`filter-btn ${filterDimension === "combo" ? "active" : ""}`}
              onClick={() => setFilterDimension("combo")}
            >
              组合预设
            </button>
          )}
        </div>
      </div>

      {allPresets.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p className="empty-text">暂无预设，点击上方按钮创建</p>
        </div>
      ) : (
        <div className="card-grid">
          {allPresets.map((preset) => (
            <div key={`${preset.dimension}-${preset.id}`} className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">{preset.name}</h3>
                  <p className="card-subtitle">
                    {preset.dimension === "visual" ? "视觉风格" : 
                     preset.dimension === "time" ? "时间采样" : 
                     preset.dimension === "camera" ? "运镜风格" : 
                     preset.dimension === "combo" ? "组合预设" : preset.dimension}
                  </p>
                </div>
              </div>
              <div className="card-body">
                <p style={{ fontSize: "14px", color: "#64748b" }}>{preset.description}</p>
              </div>
              <div className="card-tags">
                {preset.keywords.slice(0, 3).map((keyword) => (
                  keyword && <span key={keyword} className="tag">{keyword}</span>
                ))}
              </div>
              {/* 只有在管理模式下才显示编辑和删除按钮 */}
              {isManageMode && (
                <div className="card-actions" style={{ marginTop: "12px" }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleEdit(preset)}
                  >
                    <Edit size={14} />
                    编辑
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete({ 
                      id: preset.id,
                      name: preset.name, 
                      dimension: preset.dimension
                    })}
                  >
                    <Trash2 size={14} />
                    删除
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showDeleteConfirm && deleteTarget && (
        <ConfirmDialog
          title="确认删除"
          message={`确定要删除预设 "${deleteTarget.name}" 吗？此操作无法撤销。`}
          onConfirm={confirmDelete}
          onCancel={() => {
            setShowDeleteConfirm(false);
            setDeleteTarget(null);
          }}
        />
      )}
    </div>
  );
}
