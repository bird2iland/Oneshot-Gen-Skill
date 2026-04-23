import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { Layout, List, Settings, Key } from "lucide-react";
import PresetList from "./pages/PresetList";
import Composer from "./pages/Composer";
import Credentials from "./pages/Credentials";
import Config from "./pages/Config";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <nav className="sidebar">
          <div className="sidebar-header">
            <h1>Video-Gen</h1>
          </div>
          <ul className="nav-links">
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>
                <List size={20} />
                <span>预设列表</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/composer" className={({ isActive }) => isActive ? "active" : ""}>
                <Layout size={20} />
                <span>组合编辑</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/credentials" className={({ isActive }) => isActive ? "active" : ""}>
                <Key size={20} />
                <span>凭证管理</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/config" className={({ isActive }) => isActive ? "active" : ""}>
                <Settings size={20} />
                <span>配置编辑</span>
              </NavLink>
            </li>
          </ul>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PresetList />} />
            <Route path="/composer" element={<Composer />} />
            <Route path="/composer/:presetName" element={<Composer />} />
            <Route path="/credentials" element={<Credentials />} />
            <Route path="/config" element={<Config />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}