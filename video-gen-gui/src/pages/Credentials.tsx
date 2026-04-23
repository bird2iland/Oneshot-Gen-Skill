import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff, Copy, Trash2, RefreshCw, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { useStore } from "../stores";
import { saveCredential, deleteCredential, testConnection } from "../utils/api";
import { loadCredentials as loadCredentialsApi } from "../utils/api";
import { Credential } from "../types";
import ConfirmDialog from "../components/ConfirmDialog";

export default function Credentials() {
  const navigate = useNavigate();
  const { credentials, setCredentials, loading, setLoading, error, setError } = useStore();
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [editingKey, setEditingKey] = useState<Record<string, string>>({});
  const [testStatus, setTestStatus] = useState<Record<string, "idle" | "testing" | "success" | "failed">>({});
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchCredentials();
  }, []);

  async function fetchCredentials() {
    setLoading(true);
    setError(null);
    try {
      const data = await loadCredentialsApi();
      setCredentials(data);
      const keys: Record<string, string> = {};
      data.forEach((c: Credential) => {
        keys[c.provider] = c.api_key;
      });
      setEditingKey(keys);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load credentials");
    }
    setLoading(false);
  }

  async function handleSave(provider: string) {
    const apiKey = editingKey[provider];
    if (!apiKey) return;

    try {
      await saveCredential(provider, apiKey);
      await fetchCredentials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    }
  }

  async function handleTest(provider: string) {
    setTestStatus({ ...testStatus, [provider]: "testing" });
    try {
      const success = await testConnection(provider);
      setTestStatus({ ...testStatus, [provider]: success ? "success" : "failed" });
    } catch {
      setTestStatus({ ...testStatus, [provider]: "failed" });
    }
  }

  function handleDelete(provider: string) {
    setDeleteTarget(provider);
    setShowDeleteConfirm(true);
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      await deleteCredential(deleteTarget);
      await fetchCredentials();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  }

  function toggleShowKey(provider: string) {
    setShowKeys({ ...showKeys, [provider]: !showKeys[provider] });
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

const providers = [
    { id: "jimeng", name: "Jimeng" },
    { id: "kling", name: "Kling" },
    { id: "veo", name: "Veo" },
  ];

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
        <button className="btn btn-secondary" onClick={() => navigate("/")}>
          <ArrowLeft size={16} />
          返回
        </button>
        <h2 className="page-title">凭证管理</h2>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <p style={{ marginBottom: "20px", color: "#64748b" }}>
        视频生成服务供应商 API Key 管理
      </p>

      {providers.map((provider) => {
        const cred = credentials.find((c) => c.provider === provider.id);
        const isConfigured = cred?.configured || false;
        const apiKey = editingKey[provider.id] || "";
        const status = testStatus[provider.id] || "idle";

        return (
          <div key={provider.id} className="provider-card">
            <div className="provider-header">
              <h3 className="provider-name">{provider.name}</h3>
              <div className="provider-status">
                <div className={`status-dot ${isConfigured ? "" : "unconfigured"}`}></div>
                <span style={{ fontSize: "14px", color: "#64748b" }}>
                  {isConfigured ? "已配置" : "未配置"}
                </span>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">API Key</label>
              <div className="api-key-input">
                <input
                  type={showKeys[provider.id] ? "text" : "password"}
                  value={apiKey}
                  onChange={(e) => setEditingKey({ ...editingKey, [provider.id]: e.target.value })}
                  placeholder={`请输入 ${provider.name} API Key...`}
                />
                <button
                  className="toggle-btn"
                  onClick={() => toggleShowKey(provider.id)}
                >
                  {showKeys[provider.id] ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
                {isConfigured && (
                  <button
                    className="toggle-btn"
                    onClick={() => copyToClipboard(apiKey)}
                  >
                    <Copy size={16} />
                  </button>
                )}
              </div>
            </div>

            {isConfigured && status !== "idle" && (
              <div className={`alert ${status === "success" ? "alert-success" : status === "failed" ? "alert-error" : ""}`}>
                {status === "testing" && <RefreshCw size={16} className="spin" />}
                {status === "success" && <CheckCircle size={16} />}
                {status === "failed" && <XCircle size={16} />}
                {status === "testing" ? "测试中..." : status === "success" ? "连接成功" : "连接失败"}
              </div>
            )}

            <div style={{ display: "flex", gap: "8px" }}>
              {!isConfigured && (
                <button className="btn btn-primary" onClick={() => handleSave(provider.id)}>
                  保存
                </button>
              )}
              {isConfigured && (
                <>
                  <button className="btn btn-secondary" onClick={() => handleTest(provider.id)}>
                    <RefreshCw size={16} />
                    测试连接
                  </button>
                  <button className="btn btn-danger" onClick={() => handleDelete(provider.id)}>
                    <Trash2 size={16} />
                    清除凭证
                  </button>
                </>
              )}
            </div>
          </div>
        );
      })}

      <p style={{ fontSize: "12px", color: "#94a3b8" }}>
        💾 凭证存储位置: ~/.video-gen/credentials.enc
        <br />
        🔐 凭证已加密存储
      </p>

      {showDeleteConfirm && (
        <ConfirmDialog
          title="确认清除"
          message={`确定要清除 ${deleteTarget} 的凭证吗？`}
          onConfirm={confirmDelete}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </div>
  );
}