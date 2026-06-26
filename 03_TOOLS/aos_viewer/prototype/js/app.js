/* ═══════════════════════════════════════════════════════
   AOS Viewer v0.4 — 交互逻辑
   含：Dock 鱼眼 / Spotlight / 右键菜单 / 数字滚动 / 通知
   v0.4 修复：交互全场景覆盖 / 动效跳过 / 浮层联动关闭
   ═══════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════
// 偏好设置（提前定义，供启动逻辑使用）
// ═══════════════════════════════════════════════════════
const PREFS_KEY = 'aos_viewer_prefs';
const DEFAULT_PREFS = {
  theme: 'dark',        // dark / light / minimal
  animations: true,     // true / false
  scale: 1,             // 0.8 - 1.4
  glass: 'normal',      // weak / normal / strong
  debug: false,         // 调试面板开关
  mdSearch: false,      // MD 正文搜索开关
  lang: 'zh-CN',        // 界面语言：zh-CN / en-US
};

// 调试面板状态（提前声明，供 bootDesktop 使用）
let debugEnabled = false;
const debugLogs = [];

function loadPrefs() {
  try {
    const saved = localStorage.getItem(PREFS_KEY);
    return saved ? { ...DEFAULT_PREFS, ...JSON.parse(saved) } : { ...DEFAULT_PREFS };
  } catch { return { ...DEFAULT_PREFS }; }
}

function savePrefs(prefs) {
  try { localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)); } catch {}
}

function applyPrefs(prefs) {
  const body = document.body;
  // 主题
  body.classList.remove('theme-light', 'theme-minimal');
  if (prefs.theme === 'light') body.classList.add('theme-light');
  else if (prefs.theme === 'minimal') body.classList.add('theme-minimal');
  // 动效
  body.classList.toggle('no-animations', !prefs.animations);
  // 缩放
  body.style.setProperty('--ui-scale', prefs.scale);
  // 玻璃强度
  body.classList.remove('glass-weak', 'glass-strong');
  if (prefs.glass === 'weak') body.classList.add('glass-weak');
  else if (prefs.glass === 'strong') body.classList.add('glass-strong');
}

// 预加载偏好，避免闪烁（在 DOMContentLoaded 之前执行）
(function preloadPrefs() {
  const prefs = loadPrefs();
  applyPrefs(prefs);
})();

// ═══════════════════════════════════════════════════════
// 数据加载：支持本地 data.js + 后端 API 两种模式
// ═══════════════════════════════════════════════════════
let dataLoadMode = 'local'; // 'local' 或 'api'

// 合并 data_content.js 的大文本字段到 AOS_DATA 和 SUBPROJECT_DATA
// 拆分后 data.js 仅含元数据，大文本字段（content/skillMd/gotchas/agentsContent 等）需在初始化时合并回来
function mergeDataContent() {
  if (typeof AOS_DATA_CONTENT === 'undefined') {
    debugLog('warn', 'AOS_DATA_CONTENT 未定义（data_content.js 可能未加载），详情/搜索功能将不可用');
    return;
  }
  const c = AOS_DATA_CONTENT;

  // 合并 memories 的 content
  if (c.memories && AOS_DATA.memories) {
    for (const cat in c.memories) {
      const items = c.memories[cat] || [];
      const target = AOS_DATA.memories[cat] || [];
      for (let i = 0; i < items.length && i < target.length; i++) {
        target[i].content = items[i].content || '';
      }
    }
  }

  // 合并 references 的 content + metadata
  if (c.references && AOS_DATA.references) {
    for (let i = 0; i < c.references.length && i < AOS_DATA.references.length; i++) {
      AOS_DATA.references[i].content = c.references[i].content || '';
      AOS_DATA.references[i].metadata = c.references[i].metadata || '';
    }
  }

  // 合并 skills 的 skillMd + gotchas
  if (c.skills && AOS_DATA.skills) {
    for (let i = 0; i < c.skills.length && i < AOS_DATA.skills.length; i++) {
      AOS_DATA.skills[i].skillMd = c.skills[i].skillMd || '';
      AOS_DATA.skills[i].gotchas = c.skills[i].gotchas || '';
    }
  }

  // 合并 projects 的 agentsContent + readmeContent + statusContent
  if (c.projects && AOS_DATA.projects) {
    for (let i = 0; i < c.projects.length && i < AOS_DATA.projects.length; i++) {
      AOS_DATA.projects[i].agentsContent = c.projects[i].agentsContent || '';
      AOS_DATA.projects[i].readmeContent = c.projects[i].readmeContent || '';
      AOS_DATA.projects[i].statusContent = c.projects[i].statusContent || '';
    }
  }

  // 合并 subprojects 的 metadata + readme
  if (c.subprojects && typeof SUBPROJECT_DATA !== 'undefined') {
    for (const name in c.subprojects) {
      if (SUBPROJECT_DATA[name]) {
        SUBPROJECT_DATA[name].metadata = c.subprojects[name].metadata || '';
        SUBPROJECT_DATA[name].readme = c.subprojects[name].readme || '';
      }
    }
  }

  debugLog('info', 'AOS_DATA_CONTENT 已合并到 AOS_DATA 和 SUBPROJECT_DATA');
}

// 更新数据源指示器 UI
function updateDataSourceIndicator() {
  const indicator = document.getElementById('datasource-indicator');
  if (!indicator) return;
  const icon = indicator.querySelector('.ds-icon');
  const text = indicator.querySelector('.ds-text');
  if (dataLoadMode === 'api') {
    indicator.classList.add('ds-api');
    indicator.classList.remove('ds-local');
    if (icon) icon.textContent = '🔌';
    if (text) text.textContent = t('datasource.api');
    indicator.title = t('datasource.api.title');
  } else {
    indicator.classList.add('ds-local');
    indicator.classList.remove('ds-api');
    if (icon) icon.textContent = '📁';
    if (text) text.textContent = t('datasource.local');
    indicator.title = t('datasource.local.title');
  }
}

async function tryLoadApiData() {
  try {
    const resp = await fetch('/api/data', { signal: AbortSignal.timeout(2000) });
    if (!resp.ok) return false;
    const json = await resp.json();
    if (json.aos_data) {
      // 覆盖全局变量（data.js 中定义的）
      Object.assign(AOS_DATA, json.aos_data);
      if (json.subproject_data) {
        Object.assign(SUBPROJECT_DATA, json.subproject_data);
      }
      dataLoadMode = 'api';
      updateDataSourceIndicator();
      debugLog('info', '数据已从后端 API 加载');
      return true;
    }
  } catch (e) {
    debugLog('info', '后端 API 不可用，使用本地 data.js');
  }
  return false;
}

async function refreshApiData() {
  if (dataLoadMode !== 'api') return false;
  try {
    const resp = await fetch('/api/refresh', { method: 'POST', signal: AbortSignal.timeout(5000) });
    if (!resp.ok) return false;
    const json = await resp.json();
    if (json.success) {
      // 刷新后重新拉取数据
      await tryLoadApiData();
      // 重新渲染所有模块
      renderDashboard();
      renderSkills();
      renderProjects();
      renderMemory();
      renderReference();
      showNotification(t('notif.refreshed'), t('notif.refreshedDesc', json.stats?.components || '?', json.stats?.projects || '?', json.stats?.references || '?'));
      return true;
    }
  } catch (e) {
    debugLog('error', '刷新数据失败:', e);
  }
  return false;
}

// ═══════════════════════════════════════════════════════
// 浮层管理（统一关闭逻辑）
// ═══════════════════════════════════════════════════════

// 标志位：防止 openXxx 的同一 click 事件冒泡到 document 触发立即关闭
let justOpenedOverlay = false;

function closeSpotlight() {
  document.getElementById('spotlight').classList.remove('visible');
}

function closeContextMenu() {
  document.getElementById('context-menu').classList.remove('visible');
}

function closeSettings() {
  document.getElementById('settings-panel').classList.remove('visible');
  document.getElementById('overlay').classList.remove('visible');
}

function closeNotification() {
  document.getElementById('notification').classList.remove('visible');
}

function closeAllOverlays() {
  closeSpotlight();
  closeContextMenu();
  closeSettings();
  closeNotification();
}

function openSettings() {
  closeSpotlight();
  closeContextMenu();
  document.getElementById('settings-panel').classList.add('visible');
  document.getElementById('overlay').classList.add('visible');
  justOpenedOverlay = true;
  setTimeout(() => { justOpenedOverlay = false; }, 0);
}

function openSpotlight(initialQuery) {
  closeSettings();
  closeContextMenu();
  const spotlight = document.getElementById('spotlight');
  const input = document.getElementById('spotlight-input');
  spotlight.classList.add('visible');
  // 支持传入初始搜索词（右键"搜索选中文字"用）
  input.value = initialQuery || '';
  document.getElementById('spotlight-results').innerHTML = '';
  // 更新 MD 搜索提示
  updateSpotlightHint();
  justOpenedOverlay = true;
  // 如果有初始搜索词，立即触发搜索
  if (initialQuery) {
    input.dispatchEvent(new Event('input'));
  }
  setTimeout(() => { justOpenedOverlay = false; }, 0);
  setTimeout(() => input.focus(), 100);
}

// 更新 Spotlight 底部提示文本
function updateSpotlightHint() {
  const hint = document.getElementById('spotlight-hint');
  if (!hint) return;
  const prefs = loadPrefs();
  if (prefs.mdSearch) {
    hint.textContent = t('spotlight.hint.mdOn');
    hint.classList.add('md-on');
  } else {
    hint.textContent = t('spotlight.hint.titleOnly');
    hint.classList.remove('md-on');
  }
}

// ═══════════════════════════════════════════════════════
// 启动动画 → 桌面
// ═══════════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded', () => {
  // 合并 data_content.js 的大文本字段到 AOS_DATA 和 SUBPROJECT_DATA
  // data.js 仅含元数据，data_content.js 含 content/skillMd/gotchas 等大文本
  mergeDataContent();

  const prefs = loadPrefs();
  // 动效关闭时跳过启动动画，直接显示桌面
  const bootDuration = prefs.animations ? 2600 : 0;

  if (!prefs.animations) {
    document.getElementById('boot-screen').style.display = 'none';
    document.getElementById('desktop').classList.remove('hidden');
    bootDesktop();
  } else {
    setTimeout(() => {
      const boot = document.getElementById('boot-screen');
      const desktop = document.getElementById('desktop');
      boot.classList.add('fade-out');
      desktop.classList.remove('hidden');
      setTimeout(() => boot.remove(), 600);
      bootDesktop();
    }, bootDuration);
  }
});

function bootDesktop() {
  const steps = [
    ['initI18n', () => initI18n()],
    ['renderDashboard', () => renderDashboard()],
    ['renderSkills', () => renderSkills()],
    ['renderProjects', () => renderProjects()],
    ['renderMemory', () => renderMemory()],
    ['renderReference', () => renderReference()],
    ['renderLoops', () => renderLoops()],
    ['renderAgents', () => renderAgents()],
    ['renderLogs', () => renderLogs()],
    ['startClock', () => startClock()],
    ['initDockFisheye', () => initDockFisheye()],
    ['initSpotlight', () => initSpotlight()],
    ['initContextMenu', () => initContextMenu()],
    ['initSettings', () => initSettings()],
    ['initMenuBar', () => initMenuBar()],
    ['initGlobalClick', () => initGlobalClick()],
    ['initMdReaderOutsideClick', () => initMdReaderOutsideClick()],
    ['initMdReaderResize', () => initMdReaderResize()],
    ['initMemoryTabs', () => initMemoryTabs()],
    ['initRefFilter', () => initRefFilter()],
    ['initProjectDetail', () => initProjectDetail()],
    ['initPanelResizer', () => initPanelResizer()],
    ['initDebugPanel', () => initDebugPanel()],
  ];
  for (const [name, fn] of steps) {
    try {
      fn();
    } catch (e) {
      console.error(`[bootDesktop] ERROR in ${name}:`, e);
    }
  }
  // 恢复调试面板状态（如果之前开启过）
  const savedPrefs = loadPrefs();
  if (savedPrefs.debug) {
    debugEnabled = true;
    const debugPanel = document.getElementById('debug-panel');
    const handle = document.getElementById('debug-toggle-handle');
    debugPanel.classList.add('visible');
    handle.classList.add('visible');
    handle.classList.remove('collapsed');
    handle.title = '收起调试面板';
    handle.querySelector('.debug-handle-arrow').textContent = '‹';
    updateDebugState();
    debugLog('info', 'AOS 系统已就绪，调试面板自动恢复开启');
  }
  // 启动后发送欢迎通知（动态读取数据，避免硬编码）
  setTimeout(() => {
    const version = AOS_DATA.version || '1.1.0';
    const skillCount = (AOS_DATA.skills || []).length;
    const memoryCount = Object.values(AOS_DATA.memories || {}).reduce((sum, arr) => sum + (arr.length || 0), 0);
    const refCount = (AOS_DATA.references || []).length;
    showNotification(t('notif.ready'), t('notif.readyDesc', version, skillCount, memoryCount, refCount));
  }, 1200);
  // 初始化数据源指示器（默认本地）
  updateDataSourceIndicator();
  // 异步尝试从后端 API 加载最新数据
  tryLoadApiData().then(loaded => {
    if (loaded) {
      // API 数据加载成功，重新渲染
      renderDashboard(); renderSkills(); renderProjects();
      renderMemory(); renderReference();
      debugLog('info', '后端 API 数据已覆盖本地数据，界面已刷新');
    }
  });
}

// ═══════════════════════════════════════════════════════
// 全局点击 — 点击外部关闭浮层
// ═══════════════════════════════════════════════════════
function initGlobalClick() {
  document.addEventListener('click', (e) => {
    // 如果是 openXxx 触发的同一事件，跳过本次关闭
    if (justOpenedOverlay) return;
    // 点击 Spotlight 外部 → 关闭 Spotlight
    const spotlight = document.getElementById('spotlight');
    if (spotlight.classList.contains('visible') && !spotlight.contains(e.target)) {
      closeSpotlight();
    }
    // 点击右键菜单外部 → 关闭右键菜单
    const ctxMenu = document.getElementById('context-menu');
    if (ctxMenu.classList.contains('visible') && !ctxMenu.contains(e.target)) {
      closeContextMenu();
    }
    // 点击设置面板外部 → 关闭设置
    const settings = document.getElementById('settings-panel');
    if (settings.classList.contains('visible') && !settings.contains(e.target) && !e.target.closest('#settings-btn')) {
      closeSettings();
    }
  });
}

// ═══════════════════════════════════════════════════════
// 实时时钟
// ═══════════════════════════════════════════════════════
function startClock() {
  const clock = document.getElementById('clock');
  const update = () => {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    clock.textContent = `${h}:${m}:${s}`;
  };
  update();
  setInterval(update, 1000);
}

// ═══════════════════════════════════════════════════════
// 渲染系统总览
// ═══════════════════════════════════════════════════════
function renderDashboard() {
  // 组件状态
  const compList = document.getElementById('component-list');
  compList.innerHTML = AOS_DATA.components.map(c => `
    <div class="component-row">
      <div class="component-left">
        <span class="status-dot ${c.status}"></span>
        <div>
          <div class="component-name">${c.name}</div>
          <div class="component-desc">${c.desc}</div>
        </div>
      </div>
      <span class="component-status ${c.status}">${c.status === 'active' ? t('common.active') : t('common.ready')}</span>
    </div>
  `).join('');

  // 运行时统计（数字滚动动画）
  const statGrid = document.getElementById('stat-grid');
  statGrid.innerHTML = AOS_DATA.stats.map((s, i) => `
    <div class="stat-item">
      <div class="stat-value" data-target="${s.value}" data-delay="${i * 80}">0</div>
      <div class="stat-label">${s.label}</div>
    </div>
  `).join('');
  // 触发数字滚动
  setTimeout(() => {
    document.querySelectorAll('.stat-value').forEach(el => animateNumber(el));
  }, 400);

  // 事件日志
  const timeline = document.getElementById('event-timeline');
  timeline.innerHTML = AOS_DATA.events.map(e => `
    <div class="event-row">
      <span class="event-time">${e.time}</span>
      <span class="event-type ${e.type}">${e.type}</span>
      <span class="event-desc">${e.desc}</span>
    </div>
  `).join('');
  document.getElementById('event-count').textContent = AOS_DATA.events.length;
}

// ═══════════════════════════════════════════════════════
// 模块②：Skill 管理
// ═══════════════════════════════════════════════════════
function renderSkills() {
  const list = document.getElementById('skill-list');
  list.innerHTML = AOS_DATA.skills.map((s, i) => `
    <div class="skill-card" onclick="toggleSkillDetail(${i})">
      <div class="skill-header">
        <div>
          <div class="skill-id">${s.id} · v${s.version}</div>
          <div class="skill-name">${s.name}</div>
        </div>
        <span class="status-tag ${s.status === 'ACTIVE' ? 'active' : 'ready'}">${s.status}</span>
      </div>
      <div class="skill-trigger">${s.trigger}</div>
      <div class="skill-meta">
        <span class="meta-item">📁 ${s.path}</span>
        <span class="meta-item">🔢 ${t('skill.callCount', s.callCount)}</span>
        <span class="meta-item">🕐 ${s.lastExec}</span>
      </div>
      <div class="skill-detail-toggle">${t('skill.viewDetail')}</div>
      <div class="skill-detail-collapse">
        <div class="skill-structure">
          ${s.structure.map(f => `<span class="structure-tag">${f}</span>`).join('')}
        </div>
        <div class="skill-evolution">
          <div class="evolution-title">${t('skill.evolution', s.evolution.length)}</div>
          ${s.evolution.map(e => `
            <div class="evolution-row">
              <span class="evolution-type ${e.type}">${e.type}</span>
              <span class="evolution-desc">${e.desc}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `).join('');
  document.getElementById('skill-count').textContent = AOS_DATA.skills.length;
}

function toggleSkillDetail(index) {
  const cards = document.querySelectorAll('.skill-card');
  const card = cards[index];
  if (!card) return;
  const isExpanded = card.classList.toggle('expanded');
  const toggle = card.querySelector('.skill-detail-toggle');
  if (toggle) {
    toggle.textContent = isExpanded ? t('skill.collapse') : t('skill.viewDetail');
  }
}

// ═══════════════════════════════════════════════════════
// 模块③：项目工作区
// ═══════════════════════════════════════════════════════
function renderProjects() {
  const grid = document.getElementById('project-grid');
  grid.innerHTML = AOS_DATA.projects.map((p, i) => `
    <div class="project-card" data-index="${i}" onclick="openProjectDetail(${i})">
      <div class="project-header">
        <div>
          <div class="project-name">${p.title}</div>
          <div class="project-dir">${p.name}/</div>
        </div>
        <span class="status-tag ${p.status === 'ACTIVE' ? 'active' : 'ready'}">${p.status}</span>
      </div>
      <div class="project-desc">${p.desc}</div>
      <div class="project-meta">
        <span class="meta-item">🏷 ${p.type}</span>
        <span class="meta-item">🕐 ${p.createdAt}</span>
      </div>
      <div class="project-tech">
        ${p.techStack.map(t => `<span class="tech-tag">${t}</span>`).join('')}
      </div>
      <div class="project-structure">
        ${p.structure.map(s => `<span class="structure-tag">${s}</span>`).join('')}
      </div>
      <div class="project-files">
        <span class="file-status ${p.hasAgents ? 'ok' : 'missing'}">${p.hasAgents ? '✓' : '✗'} AGENTS.md</span>
        <span class="file-status ${p.hasReadme ? 'ok' : 'missing'}">${p.hasReadme ? '✓' : '✗'} README.md</span>
        <span class="file-status ${p.hasStatus ? 'ok' : 'missing'}">${p.hasStatus ? '✓' : '✗'} STATUS.md</span>
      </div>
      <div class="project-card-hint">${t('project.cardHint')}</div>
    </div>
  `).join('');
  document.getElementById('project-count').textContent = AOS_DATA.projects.length;
}

// ═══════════════════════════════════════════════════════
// 项目详情页（侧滑面板 + 全屏模式）
// ───────────────────────────────────────────────────────
// 【已修复问题记录 — 请勿重复修复】
// 问题：项目集卡片点击后闪现全屏
// 修复版本：v=20260623u（已稳定，无已知 bug）
// 修复方案：本函数 openProjectDetail() 的"三重保险"逻辑（第3-7步）：
//   1. 禁用 panel/子元素 transition（第1步）
//   2. 重置 class + toggle dual-column（第2步）
//   3. 内联 transform=translateX(100%) 锁定 panel 在右侧外（第3-1步）
//   4. 内联 visibility:hidden 防止闪现（第3-2步）
//   5. 内联 fullscreenView.opacity=0 防止全屏内容闪现（第3-3步）
//   6. 强制重排 void panel.offsetWidth（第5步）
//   7. 添加 visible class + 清除内联 visibility（第6步）
//   8. 恢复 transition（第8步）
//   9. 下一帧清除内联 transform + opacity，触发滑入动画（第9步）
// 配合 CSS：#project-detail-panel { animation: none } 禁止 cardIn 动画
// ⚠ 警告：此问题已彻底解决。不要删除三重保险逻辑，不要改 dual-column 名称。
//        重复修复会引入新 bug（历史教训：v=20260623v 误改 is-collection 已回退）。
// ═══════════════════════════════════════════════════════
let currentProjectIndex = -1;
let detailIsFullscreen = false;

function openProjectDetail(index) {
  currentProjectIndex = index;
  detailIsFullscreen = false;
  const p = AOS_DATA.projects[index];
  const panel = document.getElementById('project-detail-panel');
  const sidebarView = document.getElementById('detail-body-sidebar');
  const fullscreenView = document.getElementById('detail-body-fullscreen');
  document.getElementById('detail-project-name').textContent = p.title;
  const statusEl = document.getElementById('detail-project-status');
  statusEl.textContent = p.status;
  statusEl.className = `status-tag ${p.status === 'ACTIVE' ? 'active' : 'ready'}`;

  debugLog('info', `▶ openProjectDetail(${index}) 项目: ${p.title}`);
  debugLog('debug', `  调用前 panel.classList = "${panel.className}"`);
  debugLog('debug', `  调用前 panel.transform(计算值) = ${getComputedStyle(panel).transform}`);
  debugLog('debug', `  调用前 panel.visibility(计算值) = ${getComputedStyle(panel).visibility}`);
  debugLog('debug', `  调用前 fullscreenView.opacity(计算值) = ${getComputedStyle(fullscreenView).opacity}`);

  // ═══ 关键修复（第8次迭代）：禁用 panel 本身的 transition ═══
  // 之前只禁用了子元素 transition，没有禁用 panel 本身的 transition。
  // 当从 expanded 状态关闭后重新打开时，设置内联 transform=translateX(100%) 会触发
  // panel 的 transform 过渡（0.28s），panel 从全屏位置 translateX(0) 滑向右侧外，
  // 造成闪现全屏。必须禁用 panel 本身的 transition。
  panel.style.transition = 'none';
  sidebarView.style.transition = 'none';
  fullscreenView.style.transition = 'none';

  // 第2步：重置所有状态 class
  panel.classList.remove('visible', 'fullscreen', 'expanded');
  const isCollection = p.projectType === '项目集' && p.plugins && p.plugins.length > 0;
  panel.classList.toggle('dual-column', isCollection);
  debugLog('debug', `  移除 class 后 panel.classList = "${panel.className}"`);

  // 第3步：三重保险锁定 panel 在右侧外 + 全屏视图不可见
  // 3-1: 内联 transform 锁定 panel 在右侧外（覆盖任何 CSS transform）
  panel.style.transform = 'translateX(100%)';
  // 3-2: 内联 visibility:hidden（防止 panel 在添加 visible class 前闪现）
  panel.style.visibility = 'hidden';
  // 3-3: 内联 fullscreenView.opacity=0（防止全屏视图内容闪现）
  fullscreenView.style.opacity = '0';

  // 第4步：渲染侧滑视图内容，清空全屏视图
  renderDetailSidebar(p);
  fullscreenView.innerHTML = '';

  // 第5步：强制重排，确保三重保险的内联样式已生效
  void panel.offsetWidth;
  debugLog('debug', `  强制重排后 panel.transform(计算值) = ${getComputedStyle(panel).transform}`);
  debugLog('debug', `  强制重排后 panel.visibility(计算值) = ${getComputedStyle(panel).visibility}`);
  debugLog('debug', `  强制重排后 fullscreenView.opacity(计算值) = ${getComputedStyle(fullscreenView).opacity}`);

  // 第6步：添加 visible class，清除内联 visibility（让 CSS visibility:visible 生效）
  // 此时内联 transform=translateX(100%) 仍覆盖 CSS transform，panel 仍在右侧外
  panel.classList.add('visible');
  panel.style.visibility = '';
  debugLog('debug', `  添加 visible 后 panel.classList = "${panel.className}"`);

  // 第7步：强制重排，确保 visible class 已生效
  void panel.offsetWidth;

  // 第8步：恢复 panel + 子元素 transition
  panel.style.transition = '';
  sidebarView.style.transition = '';
  fullscreenView.style.transition = '';

  // 第9步：下一帧清除内联 transform + fullscreenView.opacity，让 CSS 值生效
  // CSS transform 是 translateX(calc(100%-780px))（dual-column）或 translateX(calc(100%-480px))
  // 从 translateX(100%) 过渡到目标值，触发滑入动画
  requestAnimationFrame(() => {
    panel.style.transform = '';
    fullscreenView.style.opacity = '';
    debugLog('debug', `  rAF 后 panel.transform(计算值) = ${getComputedStyle(panel).transform}`);
    debugLog('debug', `  rAF 后 fullscreenView.opacity(计算值) = ${getComputedStyle(fullscreenView).opacity}`);
  });
}

function renderDetailSidebar(p) {
  const body = document.getElementById('detail-body-sidebar');
  const hasContent = p.agentsContent || p.statusContent || p.readmeContent;
  const hasPlugins = p.plugins && p.plugins.length > 0;
  const hasModules = p.modules && p.modules.length > 0;
  const hasSubItems = hasPlugins || hasModules;
  const isCollection = p.projectType === '项目集' && hasPlugins;

  // 项目集模式：双栏布局（左栏全部子项目卡片列表，右栏项目级信息）
  // 点击子项目卡片 → 扩展全屏查看详情（openSubProjectFullscreen）
  if (isCollection) {
    body.innerHTML = `
      <div class="detail-dual-body">
        <!-- 左栏：全部子项目卡片列表（名称+状态+版本+描述） -->
        <div class="detail-sub-column">
          <div class="detail-section-title">${t('project.subprojectCount', p.plugins.length)}</div>
          <div class="sub-project-list">
            ${p.plugins.map((item, i) => `
              <div class="sub-project-card" onclick="openSubProjectFullscreen(${i})">
                <div class="sub-project-card-header">
                  <span class="sub-tab-status ${item.status}"></span>
                  <span class="sub-project-card-name">${item.name}</span>
                </div>
                <div class="sub-project-card-meta">
                  <span class="meta-tag">${item.version || '-'}</span>
                  <span class="meta-tag">${item.author || '-'}</span>
                </div>
                <div class="sub-project-card-desc">${item.desc || ''}</div>
              </div>
            `).join('')}
          </div>
        </div>
        <!-- 右栏：项目级信息 -->
        <div class="detail-main-column">
          <div class="detail-section">
            <div class="detail-section-title">${t('project.description')}</div>
            <div class="detail-section-body">${p.desc}</div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">${t('project.basicInfo')}</div>
            <div class="detail-info-grid">
              <div class="detail-info-item"><span class="info-label">${t('project.type')}</span><span class="info-value">${p.type}</span></div>
              <div class="detail-info-item"><span class="info-label">${t('project.createdAt')}</span><span class="info-value">${p.createdAt}</span></div>
              <div class="detail-info-item"><span class="info-label">${t('project.path')}</span><span class="info-value">${p.path}</span></div>
              <div class="detail-info-item"><span class="info-label">${t('project.status')}</span><span class="info-value">${p.status}</span></div>
              <div class="detail-info-item"><span class="info-label">${t('project.projectType')}</span><span class="info-value">${p.projectType || '-'}</span></div>
            </div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">${t('project.techStack')}</div>
            <div class="detail-tags">${p.techStack.map(t => `<span class="tech-tag">${t}</span>`).join('')}</div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">${t('project.fileIntegrity')}</div>
            <div class="detail-files">
              <span class="file-status ${p.hasAgents ? 'ok' : 'missing'}">${p.hasAgents ? '✓' : '✗'} AGENTS.md</span>
              <span class="file-status ${p.hasReadme ? 'ok' : 'missing'}">${p.hasReadme ? '✓' : '✗'} README.md</span>
              <span class="file-status ${p.hasStatus ? 'ok' : 'missing'}">${p.hasStatus ? '✓' : '✗'} STATUS.md</span>
            </div>
          </div>
          ${hasContent ? `
          <div class="detail-hint">
            <span class="hint-icon">⛶</span>
            <span>${t('project.expandHint')}</span>
          </div>
          ` : `
          <div class="detail-hint">
            <span class="hint-icon">›</span>
            <span>${t('project.expandHintSingle')}</span>
          </div>
          `}
        </div>
      </div>
    `;
    return;
  }

  // 单一项目模式：单栏布局（含模块内联切换）
  body.innerHTML = `
    <div class="detail-section">
      <div class="detail-section-title">${t('project.description')}</div>
      <div class="detail-section-body">${p.desc}</div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">${t('project.basicInfo')}</div>
      <div class="detail-info-grid">
        <div class="detail-info-item"><span class="info-label">${t('project.type')}</span><span class="info-value">${p.type}</span></div>
        <div class="detail-info-item"><span class="info-label">${t('project.createdAt')}</span><span class="info-value">${p.createdAt}</span></div>
        <div class="detail-info-item"><span class="info-label">${t('project.path')}</span><span class="info-value">${p.path}</span></div>
        <div class="detail-info-item"><span class="info-label">${t('project.status')}</span><span class="info-value">${p.status}</span></div>
        <div class="detail-info-item"><span class="info-label">${t('project.projectType')}</span><span class="info-value">${p.projectType || '-'}</span></div>
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">${t('project.techStack')}</div>
      <div class="detail-tags">${p.techStack.map(t => `<span class="tech-tag">${t}</span>`).join('')}</div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">${t('project.fileIntegrity')}</div>
      <div class="detail-files">
        <span class="file-status ${p.hasAgents ? 'ok' : 'missing'}">${p.hasAgents ? '✓' : '✗'} AGENTS.md</span>
        <span class="file-status ${p.hasReadme ? 'ok' : 'missing'}">${p.hasReadme ? '✓' : '✗'} README.md</span>
        <span class="file-status ${p.hasStatus ? 'ok' : 'missing'}">${p.hasStatus ? '✓' : '✗'} STATUS.md</span>
      </div>
    </div>
    ${hasSubItems ? `
    <div class="detail-section">
      <div class="detail-section-title">${hasPlugins ? t('project.subprojectCount', p.plugins.length) : t('project.moduleCount', p.modules.length)}</div>
      <div class="sub-project-switcher" id="sub-project-switcher">
        ${(hasPlugins ? p.plugins : p.modules).map((item, i) => `
          <div class="sub-project-tab ${i === 0 ? 'active' : ''}" data-idx="${i}" onclick="switchSubProjectInSidebar(${currentProjectIndex}, ${i})">
            ${hasPlugins ? `<span class="sub-tab-status ${item.status}"></span>` : ''}
            <span class="sub-project-tab-name">${hasPlugins ? item.name : item.name + '/'}</span>
          </div>
        `).join('')}
      </div>
      <div id="sub-project-content" class="sub-project-content"></div>
    </div>
    ` : ''}
    ${hasContent ? `
    <div class="detail-hint">
      <span class="hint-icon">⛶</span>
      <span>${t('project.expandHintSimple')}</span>
    </div>
    ` : ''}
  `;

  // 如果有子项目/模块，默认显示第一个
  if (hasSubItems) {
    switchSubProjectInSidebar(currentProjectIndex, 0);
  }
}

// 侧滑面板内子项目/模块切换（无需跳转 L3）
function switchSubProjectInSidebar(projectIndex, subIndex) {
  const p = AOS_DATA.projects[projectIndex];
  const items = p.plugins || p.modules;
  const item = items[subIndex];
  if (!item) return;

  // 更新标签页激活状态
  document.querySelectorAll('.sub-project-tab').forEach(tab => tab.classList.remove('active'));
  const targetTab = document.querySelector(`.sub-project-tab[data-idx="${subIndex}"]`);
  if (targetTab) targetTab.classList.add('active');

  // 渲染子项目/模块详情
  const content = document.getElementById('sub-project-content');
  if (p.plugins) {
    content.innerHTML = renderPluginInSidebar(item, p);
  } else {
    content.innerHTML = renderModuleInSidebar(item, p);
  }
}

function renderPluginInSidebar(plugin, project) {
  const detail = (typeof SUBPROJECT_DATA !== 'undefined') ? SUBPROJECT_DATA[plugin.name] : null;
  return `
    <div class="sub-detail-info">
      <div class="sub-detail-row"><span class="info-label">名称</span><span class="info-value">${plugin.name}</span></div>
      <div class="sub-detail-row"><span class="info-label">版本</span><span class="info-value">${plugin.version || '-'}</span></div>
      <div class="sub-detail-row"><span class="info-label">作者</span><span class="info-value">${plugin.author || '-'}</span></div>
      <div class="sub-detail-row"><span class="info-label">状态</span><span class="info-value">${plugin.status}</span></div>
      <div class="sub-detail-row"><span class="info-label">路径</span><span class="info-value">${project.path}src/${plugin.name}/</span></div>
    </div>
    <div class="sub-detail-desc">${plugin.desc || ''}</div>
    ${detail ? `
      ${detail.metadata ? `
      <div class="sub-detail-section">
        <div class="sub-detail-section-title">metadata.yaml</div>
        <pre class="md-code md-code-compact"><code>${escapeHtml(detail.metadata)}</code></pre>
      </div>
      ` : ''}
      ${detail.readme ? `
      <div class="sub-detail-section">
        <div class="sub-detail-section-title">README.md</div>
        <div class="md-preview-compact">${renderMarkdownPreview(detail.readme)}</div>
      </div>
      ` : ''}
      ${detail.structure ? `
      <div class="sub-detail-section">
        <div class="sub-detail-section-title">文件结构</div>
        <pre class="md-code md-code-compact"><code>${escapeHtml(detail.structure)}</code></pre>
      </div>
      ` : ''}
    ` : `
      <div class="detail-hint warning" style="margin-top:8px">
        <span class="hint-icon">⚠</span>
        <span>详细数据（metadata.yaml / README.md / 文件结构）待建模</span>
      </div>
    `}
  `;
}

function renderModuleInSidebar(mod, project) {
  return `
    <div class="sub-detail-info">
      <div class="sub-detail-row"><span class="info-label">名称</span><span class="info-value">${mod.name}/</span></div>
      <div class="sub-detail-row"><span class="info-label">路径</span><span class="info-value">${project.path}src/${mod.name}/</span></div>
    </div>
    <div class="sub-detail-desc">${mod.desc || ''}</div>
    <div class="sub-detail-section">
      <div class="sub-detail-section-title">文件列表</div>
      <div class="detail-tags">${mod.files.map(f => `<span class="structure-tag">${f}</span>`).join('')}</div>
    </div>
  `;
}

// 向左扩展/收起（统一交互范式：左侧把手控制）
// 新方案：panel 始终 width 100%，用 transform 控制可见区域，内容用 opacity 切换
// 扩展：先渲染全屏视图（opacity:0 不可见），下一帧添加 expanded（opacity 0→1 淡入 + transform 滑动）
// 收起：只移除 expanded（opacity 1→0 淡出 + transform 滑动）
function toggleExpandDetail() {
  if (currentProjectIndex < 0) return;
  const p = AOS_DATA.projects[currentProjectIndex];
  const panel = document.getElementById('project-detail-panel');
  const handle = document.getElementById('detail-expand-handle');
  const isExpanded = panel.classList.contains('expanded');

  debugLog('info', `▶ toggleExpandDetail() 被调用，isExpanded=${isExpanded}`);

  // 更新把手提示文字
  handle.title = isExpanded ? '向左扩展' : '向右收起';

  if (isExpanded) {
    // 收起：移除 expanded，transform 从 translateX(0) → translateX(calc(100% - 780/480px))
    // 同时全屏视图 opacity 1→0，侧滑视图 opacity 0→1（CSS 自动过渡）
    detailIsFullscreen = false;
    panel.classList.remove('expanded', 'fullscreen');
    debugLog('debug', `  收起后 panel.classList = "${panel.className}"`);
  } else {
    // 扩展：先渲染全屏视图（此时 opacity:0 不可见，innerHTML 替换无闪烁）
    renderDetailFullscreen(p);
    debugLog('debug', `  renderDetailFullscreen 完成，fullscreenView.innerHTML.length = ${document.getElementById('detail-body-fullscreen').innerHTML.length}`);
    // 下一帧添加 expanded，触发 transform 滑动 + opacity 淡入
    requestAnimationFrame(() => {
      panel.classList.add('expanded', 'fullscreen');
      debugLog('debug', `  rAF 添加 expanded 后 panel.classList = "${panel.className}"`);
    });
    detailIsFullscreen = true;
  }
}

// 点击子项目卡片 → 扩展全屏 + 切换到对应子项目 tab
// 用于项目集模式侧滑状态下的子项目卡片点击交互
function openSubProjectFullscreen(subIndex) {
  if (currentProjectIndex < 0) return;
  const p = AOS_DATA.projects[currentProjectIndex];
  const panel = document.getElementById('project-detail-panel');
  const handle = document.getElementById('detail-expand-handle');
  const isExpanded = panel.classList.contains('expanded');

  debugLog('info', `▶ openSubProjectFullscreen(${subIndex}) 项目: ${p.title}`);

  if (!isExpanded) {
    // 未扩展 → 先渲染全屏视图并扩展
    renderDetailFullscreen(p);
    requestAnimationFrame(() => {
      panel.classList.add('expanded', 'fullscreen');
      // 扩展完成后切换到指定子项目 tab
      switchProjectTab('plugin-' + subIndex);
    });
    detailIsFullscreen = true;
    handle.title = '向右收起';
  } else {
    // 已扩展 → 直接切换到指定子项目 tab
    switchProjectTab('plugin-' + subIndex);
  }
}

function renderDetailFullscreen(p) {
  const body = document.getElementById('detail-body-fullscreen');
  const hasAgents = !!p.agentsContent;
  const hasStatus = !!p.statusContent;
  const hasReadme = !!p.readmeContent;
  const isCollection = p.projectType === '项目集' && p.plugins && p.plugins.length > 0;
  const hasModules = p.modules && p.modules.length > 0;

  // 全屏模式：左侧标签栏 + 右侧内容区（交互逻辑统一在左侧）
  body.innerHTML = `
    <div class="detail-expanded-layout">
      <!-- 左侧标签栏 -->
      <div class="detail-sidebar-tabs">
        <div class="tab-group">
          <div class="tab-group-label">项目级</div>
          <div class="tab-item active" data-tab="overview" onclick="switchProjectTab('overview')">概览</div>
          <div class="tab-item ${hasAgents ? '' : 'disabled'}" data-tab="agents" onclick="switchProjectTab('agents')">AGENTS.md</div>
          <div class="tab-item ${hasStatus ? '' : 'disabled'}" data-tab="status" onclick="switchProjectTab('status')">STATUS.md</div>
          <div class="tab-item ${hasReadme ? '' : 'disabled'}" data-tab="readme" onclick="switchProjectTab('readme')">README.md</div>
        </div>
        ${isCollection ? `
        <div class="tab-group">
          <div class="tab-group-label">子项目（${p.plugins.length}）</div>
          ${p.plugins.map((pl, i) => `
            <div class="tab-item tab-item-sub" data-tab="plugin-${i}" onclick="switchProjectTab('plugin-${i}')">
              <span class="sub-tab-status ${pl.status}"></span>
              <span class="tab-item-name">${pl.name}</span>
            </div>
          `).join('')}
        </div>
        ` : ''}
        ${hasModules ? `
        <div class="tab-group">
          <div class="tab-group-label">源码模块（${p.modules.length}）</div>
          ${p.modules.map((m, i) => `
            <div class="tab-item tab-item-sub" data-tab="module-${i}" onclick="switchProjectTab('module-${i}')">
              <span class="tab-item-name">${m.name}/</span>
            </div>
          `).join('')}
        </div>
        ` : ''}
      </div>
      <!-- 右侧内容区 -->
      <div class="detail-content-area" id="detail-tab-content"></div>
    </div>
  `;
  switchProjectTab('overview');
}

function switchProjectTab(tabName) {
  if (currentProjectIndex < 0) return;
  const p = AOS_DATA.projects[currentProjectIndex];
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  const targetTab = document.querySelector(`.tab-item[data-tab="${tabName}"]`);
  if (targetTab) targetTab.classList.add('active');
  const content = document.getElementById('detail-tab-content');

  if (tabName === 'overview') {
    content.innerHTML = getOverviewHTML(p);
  } else if (tabName === 'agents') {
    content.innerHTML = p.agentsContent ? renderMarkdownPreview(p.agentsContent) : getEmptyFileHTML('AGENTS.md');
  } else if (tabName === 'status') {
    content.innerHTML = p.statusContent ? renderMarkdownPreview(p.statusContent) : getEmptyFileHTML('STATUS.md');
  } else if (tabName === 'readme') {
    content.innerHTML = p.readmeContent ? renderMarkdownPreview(p.readmeContent) : getEmptyFileHTML('README.md');
  } else if (tabName.startsWith('plugin-')) {
    const pluginIndex = parseInt(tabName.split('-')[1]);
    content.innerHTML = getPluginOverviewHTML(p, pluginIndex);
  } else if (tabName.startsWith('module-')) {
    const moduleIndex = parseInt(tabName.split('-')[1]);
    content.innerHTML = getModuleDetailHTML(p, moduleIndex);
  }
}

// 模块详情（全屏模式左侧标签栏切换）
function getModuleDetailHTML(p, moduleIndex) {
  const mod = p.modules[moduleIndex];
  return `
    <div class="detail-section">
      <div class="detail-section-title">模块详情</div>
      <div class="detail-info-grid">
        <div class="detail-info-item"><span class="info-label">名称</span><span class="info-value">${mod.name}/</span></div>
        <div class="detail-info-item"><span class="info-label">路径</span><span class="info-value">${p.path}src/${mod.name}/</span></div>
      </div>
      <div class="detail-section-body" style="margin-top:12px">${mod.desc || ''}</div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">文件列表</div>
      <div class="detail-tags">${mod.files.map(f => `<span class="structure-tag">${f}</span>`).join('')}</div>
    </div>
  `;
}

// 子项目标签页详情（全屏模式直接显示完整内容，无需二次跳转）
function getPluginOverviewHTML(p, pluginIndex) {
  const plugin = p.plugins[pluginIndex];
  const detail = (typeof SUBPROJECT_DATA !== 'undefined') ? SUBPROJECT_DATA[plugin.name] : null;
  return `
    <div class="detail-section">
      <div class="detail-section-title">插件详情</div>
      <div class="detail-info-grid">
        <div class="detail-info-item"><span class="info-label">名称</span><span class="info-value">${plugin.name}</span></div>
        <div class="detail-info-item"><span class="info-label">版本</span><span class="info-value">${plugin.version || '-'}</span></div>
        <div class="detail-info-item"><span class="info-label">作者</span><span class="info-value">${plugin.author || '-'}</span></div>
        <div class="detail-info-item"><span class="info-label">状态</span><span class="info-value">${plugin.status}</span></div>
        <div class="detail-info-item"><span class="info-label">路径</span><span class="info-value">${p.path}src/${plugin.name}/</span></div>
      </div>
      <div class="detail-section-body" style="margin-top:12px">${plugin.desc || ''}</div>
    </div>
    ${detail ? `
      ${detail.metadata ? `
      <div class="detail-section">
        <div class="detail-section-title">metadata.yaml</div>
        <pre class="md-code"><code>${escapeHtml(detail.metadata)}</code></pre>
      </div>
      ` : ''}
      ${detail.readme ? `
      <div class="detail-section">
        <div class="detail-section-title">README.md</div>
        <div class="md-preview">${renderMarkdownPreview(detail.readme)}</div>
      </div>
      ` : ''}
      ${detail.structure ? `
      <div class="detail-section">
        <div class="detail-section-title">文件结构</div>
        <pre class="md-code"><code>${escapeHtml(detail.structure)}</code></pre>
      </div>
      ` : ''}
    ` : `
      <div class="detail-hint warning">
        <span class="hint-icon">⚠</span>
        <span>详细数据（metadata.yaml / README.md / 文件结构）待建模</span>
      </div>
    `}
  `;
}

function getOverviewHTML(p) {
  return `
    <div class="detail-section">
      <div class="detail-section-title">项目描述</div>
      <div class="detail-section-body">${p.desc}</div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">基本信息</div>
      <div class="detail-info-grid">
        <div class="detail-info-item"><span class="info-label">类型</span><span class="info-value">${p.type}</span></div>
        <div class="detail-info-item"><span class="info-label">创建时间</span><span class="info-value">${p.createdAt}</span></div>
        <div class="detail-info-item"><span class="info-label">路径</span><span class="info-value">${p.path}</span></div>
        <div class="detail-info-item"><span class="info-label">状态</span><span class="info-value">${p.status}</span></div>
        <div class="detail-info-item"><span class="info-label">项目类型</span><span class="info-value">${p.projectType || '-'}</span></div>
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">技术栈</div>
      <div class="detail-tags">${p.techStack.map(t => `<span class="tech-tag">${t}</span>`).join('')}</div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">文件完整性</div>
      <div class="detail-files">
        <span class="file-status ${p.hasAgents ? 'ok' : 'missing'}">${p.hasAgents ? '✓' : '✗'} AGENTS.md</span>
        <span class="file-status ${p.hasReadme ? 'ok' : 'missing'}">${p.hasReadme ? '✓' : '✗'} README.md</span>
        <span class="file-status ${p.hasStatus ? 'ok' : 'missing'}">${p.hasStatus ? '✓' : '✗'} STATUS.md</span>
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">项目结构</div>
      <div class="detail-tags">${p.structure.map(s => `<span class="structure-tag">${s}</span>`).join('')}</div>
    </div>
    ${p.plugins ? `
    <div class="detail-section">
      <div class="detail-section-title">子项目统计</div>
      <div class="detail-info-grid">
        <div class="detail-info-item"><span class="info-label">总数</span><span class="info-value">${p.plugins.length} 个</span></div>
        <div class="detail-info-item"><span class="info-label">活跃</span><span class="info-value">${p.plugins.filter(pl => pl.status === 'active').length} 个</span></div>
        <div class="detail-info-item"><span class="info-label">归档</span><span class="info-value">${p.plugins.filter(pl => pl.status === 'archived').length} 个</span></div>
      </div>
      <div class="detail-hint" style="margin-top:12px">
        <span class="hint-icon">ℹ</span>
        <span>点击左侧子项目标签可查看每个插件的详情</span>
      </div>
    </div>
    ` : ''}
    ${p.modules ? `
    <div class="detail-section">
      <div class="detail-section-title">源码模块（${p.modules.length}）</div>
      <div class="module-grid">
        ${p.modules.map((m, i) => `
          <div class="module-card" onclick="switchProjectTab('module-${i}')">
            <div class="module-card-header">
              <span class="module-card-name">${m.name}/</span>
              <span class="module-card-arrow">›</span>
            </div>
            <div class="module-card-desc">${m.desc}</div>
            <div class="module-card-files">${m.files.length} 个文件</div>
          </div>
        `).join('')}
      </div>
    </div>
    ` : ''}
  `;
}

function getEmptyFileHTML(filename) {
  return `
    <div class="empty-state">
      <div class="empty-icon">📄</div>
      <div class="empty-title">${filename} 暂不可用</div>
      <div class="empty-desc">项目目录待创建，文件内容将在项目初始化后可用</div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════
// 右侧侧边栏 Markdown 阅读器（记忆/知识库全文预览）
// 交互：点击卡片→滑入侧边栏 / 点击空白→收起 / 点击其他卡片→切换内容
// ═══════════════════════════════════════════════════════
function openMdReader(title, content) {
  const overlay = document.getElementById('md-reader-overlay');
  const titleEl = document.getElementById('md-reader-title');
  const bodyEl = document.getElementById('md-reader-body');
  titleEl.textContent = title;
  if (content) {
    bodyEl.innerHTML = renderMarkdownPreview(content);
  } else {
    bodyEl.innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><div class="empty-title">内容待填充</div><div class="empty-desc">该文件的完整内容尚未录入数据层</div></div>';
  }
  // 已打开则直接替换内容（不关闭再打开，避免闪烁）
  // 未打开则滑入侧边栏
  overlay.classList.remove('md-reader-hidden');
  overlay.classList.add('md-reader-visible');
}

function closeMdReader() {
  const overlay = document.getElementById('md-reader-overlay');
  overlay.classList.remove('md-reader-visible');
  overlay.classList.add('md-reader-hidden');
}

// 点击侧边栏外部空白处收起（在 initGlobalClick 中调用）
// 同时收起所有展开的记忆/知识库卡片，保持状态同步
function initMdReaderOutsideClick() {
  document.addEventListener('click', (e) => {
    const overlay = document.getElementById('md-reader-overlay');
    if (!overlay.classList.contains('md-reader-visible')) return;
    // 点击侧边栏内部不处理
    if (overlay.contains(e.target)) return;
    // 点击卡片（记忆/知识库）不处理 —— 由卡片 onclick 负责切换内容
    if (e.target.closest('.memory-item') || e.target.closest('.ref-card')) return;
    // 点击其他按钮（如 dock、设置）也不处理，由各自逻辑负责
    if (e.target.closest('button') || e.target.closest('.dock-item') || e.target.closest('#settings-btn')) return;
    // 其余空白处 → 收起侧边栏 + 同步收起所有展开的卡片
    closeMdReader();
    collapseAllExpandedCards();
  });
}

// 收起所有展开的记忆/知识库卡片（侧边栏关闭时同步调用）
function collapseAllExpandedCards() {
  document.querySelectorAll('.memory-item.expanded').forEach(el => {
    el.classList.remove('expanded');
    const hint = el.querySelector('.memory-toggle-hint');
    if (hint) {
      const hasContent = el.classList.contains('has-content');
      hint.textContent = hasContent ? '点击阅读全文 / 展开详情 ›' : '点击展开详情 ›';
    }
  });
  document.querySelectorAll('.ref-card.expanded').forEach(el => {
    el.classList.remove('expanded');
    const hint = el.querySelector('.ref-toggle-hint');
    if (hint) {
      const hasContent = el.classList.contains('has-content');
      hint.textContent = hasContent ? '点击阅读全文 / 展开详情 ›' : '点击展开详情 ›';
    }
  });
}

// 拖拽调整侧边栏宽度
// 限制：最小 400px，最大 75vw（页面 3/4）
function initMdReaderResize() {
  const handle = document.getElementById('md-reader-resize-handle');
  const overlay = document.getElementById('md-reader-overlay');
  let isDragging = false;
  let startX = 0;
  let startWidth = 0;

  // 从 localStorage 恢复上次宽度
  const savedWidth = localStorage.getItem('md_reader_width');
  if (savedWidth) {
    overlay.style.width = savedWidth + 'px';
  }

  handle.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX;
    startWidth = overlay.offsetWidth;
    handle.classList.add('dragging');
    document.body.classList.add('md-reader-resizing');
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    // 向左拖拽 → 增加宽度（clientX 减小，宽度增大）
    const delta = startX - e.clientX;
    let newWidth = startWidth + delta;
    const maxWidth = window.innerWidth * 0.75;  // 最宽 75vw
    const minWidth = 400;
    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    overlay.style.width = newWidth + 'px';
  });

  document.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    handle.classList.remove('dragging');
    document.body.classList.remove('md-reader-resizing');
    // 保存宽度到 localStorage
    localStorage.setItem('md_reader_width', overlay.offsetWidth);
  });
}

// 简易 Markdown 预览（保留换行和缩进，渲染表格和代码块）
function renderMarkdownPreview(md) {
  const lines = md.split('\n');
  let html = '';
  let inCodeBlock = false;
  let inTable = false;
  let tableRows = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // 代码块
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        html += '</code></pre>';
        inCodeBlock = false;
      } else {
        html += '<pre class="md-code"><code>';
        inCodeBlock = true;
      }
      continue;
    }
    if (inCodeBlock) {
      html += escapeHtml(line) + '\n';
      continue;
    }
    // 表格
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      if (line.trim().match(/^\|[\s-:|]+\|$/)) continue; // 分隔行
      tableRows.push(line);
      const nextLine = lines[i + 1] || '';
      if (!nextLine.trim().startsWith('|')) {
        html += renderMdTable(tableRows);
        tableRows = [];
      }
      continue;
    }
    // 标题
    if (line.startsWith('# ')) { html += `<h1 class="md-h1">${escapeHtml(line.slice(2))}</h1>`; continue; }
    if (line.startsWith('## ')) { html += `<h2 class="md-h2">${escapeHtml(line.slice(3))}</h2>`; continue; }
    if (line.startsWith('### ')) { html += `<h3 class="md-h3">${escapeHtml(line.slice(4))}</h3>`; continue; }
    // 引用
    if (line.startsWith('> ')) { html += `<blockquote class="md-quote">${escapeHtml(line.slice(2))}</blockquote>`; continue; }
    // 列表
    if (line.startsWith('- ')) { html += `<div class="md-list-item">• ${escapeHtml(line.slice(2))}</div>`; continue; }
    // 空行
    if (line.trim() === '') { html += '<div class="md-spacer"></div>'; continue; }
    // 普通文本
    html += `<div class="md-text">${escapeHtml(line)}</div>`;
  }
  if (inCodeBlock) html += '</code></pre>';
  return html;
}

function renderMdTable(rows) {
  if (rows.length === 0) return '';
  const parseRow = (row) => row.trim().slice(1, -1).split('|').map(c => c.trim());
  const headers = parseRow(rows[0]);
  let html = '<table class="md-table"><thead><tr>';
  headers.forEach(h => html += `<th>${escapeHtml(h)}</th>`);
  html += '</tr></thead><tbody>';
  for (let i = 1; i < rows.length; i++) {
    const cells = parseRow(rows[i]);
    html += '<tr>';
    cells.forEach(c => html += `<td>${escapeHtml(c)}</td>`);
    html += '</tr>';
  }
  html += '</tbody></table>';
  return html;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function closeProjectDetail() {
  const panel = document.getElementById('project-detail-panel');
  debugLog('info', `▶ closeProjectDetail() 被调用`);
  debugLog('debug', `  关闭前 panel.classList = "${panel.className}"`);
  panel.classList.remove('visible', 'fullscreen', 'expanded', 'dual-column');
  // 清除可能残留的内联样式（防止 openProjectDetail 的内联 transform/transition 残留）
  panel.style.transform = '';
  panel.style.visibility = '';
  panel.style.transition = '';
  debugLog('debug', `  关闭后 panel.classList = "${panel.className}"`);
  currentProjectIndex = -1;
  detailIsFullscreen = false;
}

// ═══════════════════════════════════════════════════════
// 调试面板（类似 F12 Console）
// debugEnabled 和 debugLogs 已在文件顶部声明
// ═══════════════════════════════════════════════════════

// 记录调试日志（debugEnabled 为 false 时静默跳过，零开销）
function debugLog(level, msg) {
  if (!debugEnabled) return;
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}.${String(now.getMilliseconds()).padStart(3,'0')}`;
  debugLogs.push({ time: timeStr, level, msg });
  if (debugLogs.length > 300) debugLogs.shift();
  renderDebugLog();
}

// 渲染日志列表
function renderDebugLog() {
  const logEl = document.getElementById('debug-log');
  if (!logEl) return;
  logEl.innerHTML = debugLogs.map(l => `
    <div class="debug-log-line">
      <span class="log-time">${l.time}</span>
      <span class="log-level log-level-${l.level}">[${l.level.toUpperCase()}]</span>
      <span class="log-msg">${escapeHtml(l.msg)}</span>
    </div>
  `).join('');
  logEl.scrollTop = logEl.scrollHeight;
}

// 刷新 DOM 状态快照
function updateDebugState() {
  const stateEl = document.getElementById('debug-state');
  if (!stateEl) return;
  const panel = document.getElementById('project-detail-panel');
  const sidebarView = document.getElementById('detail-body-sidebar');
  const fullscreenView = document.getElementById('detail-body-fullscreen');
  const cs = getComputedStyle(panel);
  const csSidebar = getComputedStyle(sidebarView);
  const csFull = getComputedStyle(fullscreenView);

  const lines = [
    `currentProjectIndex = ${currentProjectIndex}`,
    `detailIsFullscreen  = ${detailIsFullscreen}`,
    ``,
    `── #project-detail-panel ──`,
    `  classList          = "${panel.className}"`,
    `  inline.transform   = "${panel.style.transform}"`,
    `  inline.visibility  = "${panel.style.visibility}"`,
    `  inline.transition  = "${panel.style.transition}"`,
    `  computed.transform = ${cs.transform}`,
    `  computed.visibility= ${cs.visibility}`,
    ``,
    `── #detail-body-sidebar ──`,
    `  inline.transition  = "${sidebarView.style.transition}"`,
    `  computed.opacity   = ${csSidebar.opacity}`,
    `  innerHTML.length   = ${sidebarView.innerHTML.length}`,
    ``,
    `── #detail-body-fullscreen ──`,
    `  inline.transition  = "${fullscreenView.style.transition}"`,
    `  inline.opacity     = "${fullscreenView.style.opacity}"`,
    `  computed.opacity   = ${csFull.opacity}`,
    `  innerHTML.length   = ${fullscreenView.innerHTML.length}`,
  ];
  stateEl.textContent = lines.join('\n');
}

// 初始化调试面板事件
function initDebugPanel() {
  document.getElementById('debug-clear').addEventListener('click', () => {
    debugLogs.length = 0;
    renderDebugLog();
  });
  document.getElementById('debug-refresh').addEventListener('click', () => {
    updateDebugState();
  });
  document.getElementById('debug-export').addEventListener('click', () => {
    exportDebugLog();
  });
  // ✕ 关闭按钮：只收起面板（不关闭 debugEnabled），可通过把手重新展开
  document.getElementById('debug-close').addEventListener('click', () => {
    collapseDebugPanel();
  });
  // 把手点击：切换面板展开/收起
  document.getElementById('debug-toggle-handle').addEventListener('click', () => {
    const handle = document.getElementById('debug-toggle-handle');
    if (handle.classList.contains('collapsed')) {
      expandDebugPanel();
    } else {
      collapseDebugPanel();
    }
  });
}

// 展开调试面板（从屏幕左侧滑入）
function expandDebugPanel() {
  const debugPanel = document.getElementById('debug-panel');
  const handle = document.getElementById('debug-toggle-handle');
  debugPanel.classList.add('visible');
  handle.classList.remove('collapsed');
  handle.title = '收起调试面板';
  handle.querySelector('.debug-handle-arrow').textContent = '‹';
  updateDebugState();
  debugLog('info', '调试面板已展开');
}

// 收起调试面板（滑到屏幕左侧外，把手保留在屏幕左边缘）
function collapseDebugPanel() {
  const debugPanel = document.getElementById('debug-panel');
  const handle = document.getElementById('debug-toggle-handle');
  debugPanel.classList.remove('visible');
  handle.classList.add('collapsed');
  handle.title = '展开调试面板';
  handle.querySelector('.debug-handle-arrow').textContent = '›';
  debugLog('info', '调试面板已收起');
}

// 导出调试日志到本地文件（通过 Blob 下载）
function exportDebugLog() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const ts = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;

  // 同时导出日志和 DOM 状态快照
  let stateText = '';
  const stateEl = document.getElementById('debug-state');
  if (stateEl) stateText = stateEl.textContent;

  const lines = debugLogs.map(l => `${l.time} [${l.level.toUpperCase()}] ${l.msg}`);
  const content = `═══ AOS Debug Log Export ═══
导出时间: ${now.toLocaleString('zh-CN')}
日志条数: ${debugLogs.length}

─── DOM 状态快照 ───
${stateText}

─── 调用日志 ───
${lines.join('\n')}
`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `aos_debug_${ts}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  debugLog('info', `日志已导出: aos_debug_${ts}.txt`);
}

// ═══════════════════════════════════════════════════════
// 旧 L3 代码已移除（统一为向左扩展式交互）
// ═══════════════════════════════════════════════════════

function initProjectDetail() {
  document.getElementById('detail-close').addEventListener('click', closeProjectDetail);
  // expand handle 的点击/拖拽由 initPanelResizer 统一处理（双功能：点击展开 + 拖拽调整宽度）

  // 点击侧边栏外部空白区域关闭侧边栏（仅侧滑状态，非全屏）
  document.addEventListener('click', (e) => {
    const panel = document.getElementById('project-detail-panel');
    if (!panel.classList.contains('visible')) return;  // 不可见时不处理
    if (panel.classList.contains('expanded')) return;  // 全屏状态不处理（全屏无空白区域）
    if (panel.contains(e.target)) return;  // 点击 panel 内部不关闭
    if (e.target.closest('.project-card')) return;  // 点击项目卡片不关闭（会打开新项目）
    if (e.target.closest('.dock-item')) return;  // 点击 Dock 栏不关闭（会切换模块，switchModule 已处理）
    closeProjectDetail();
  });

  // ESC 关闭：扩展状态先收起，否则关闭
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const panel = document.getElementById('project-detail-panel');
      if (panel.classList.contains('visible')) {
        if (panel.classList.contains('expanded')) {
          toggleExpandDetail();
        } else {
          closeProjectDetail();
        }
      }
    }
  });
}

// ═══════════════════════════════════════════════════════
// 模块④：记忆中心
// ═══════════════════════════════════════════════════════
let currentMemoryCat = 'user';

function renderMemory() {
  // 更新计数
  document.getElementById('mem-user-count').textContent = AOS_DATA.memories.user.length;
  document.getElementById('mem-feedback-count').textContent = AOS_DATA.memories.feedback.length;
  document.getElementById('mem-reference-count').textContent = AOS_DATA.memories.reference.length;
  document.getElementById('mem-project-count').textContent = AOS_DATA.memories.project.length;
  renderMemoryList(currentMemoryCat);
}

function renderMemoryList(cat) {
  const list = document.getElementById('memory-list');
  const items = AOS_DATA.memories[cat] || [];
  if (items.length === 0) {
    list.innerHTML = `<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-title">${t('memory.empty')}</div></div>`;
    return;
  }
  list.innerHTML = items.map((m, i) => `
    <div class="memory-item ${m.content ? 'has-content' : ''}" onclick="onMemoryCardClick(event, '${cat}', ${i})">
      <div class="memory-header">
        <div class="memory-title">${m.title}</div>
        <span class="memory-type ${m.type === '记录型' ? 'record' : 'state'}">${m.type}</span>
      </div>
      <div class="memory-hook">${m.hook}</div>
      <div class="memory-detail-collapse">
        <div class="memory-path">📁 ${m.path}</div>
        <div class="memory-path-hint">${t('memory.pathHint', m.path)}</div>
        ${m.content ? `<div class="md-reader-btn-disabled">${t('memory.readFull')}</div>` : `<div class="md-reader-btn-disabled">${t('memory.noContent')}</div>`}
      </div>
      <div class="memory-toggle-hint">${m.content ? t('memory.toggleHint') : t('memory.toggleHintNoContent')}</div>
    </div>
  `).join('');
}

// 记忆卡片点击逻辑：
// - 有 content：点击卡片→始终打开/切换右侧侧边栏 MD 阅读（不收起卡片）
// - 无 content：点击卡片→仅展开/收起详情
// - 点击展开区域内部（路径信息）：仅切换展开，不触发阅读
function onMemoryCardClick(event, cat, index) {
  const m = AOS_DATA.memories[cat][index];
  const card = event.currentTarget;
  // 如果点击的是展开详情区域内部，仅切换展开状态
  if (event.target.closest('.memory-detail-collapse')) {
    toggleMemoryDetail(card);
    return;
  }
  // 有 content → 始终打开侧边栏阅读（不管卡片是否已展开，都不收起）
  if (m.content) {
    openMdReader(m.title, m.content);
    // 确保卡片展开显示路径信息（已展开则保持）
    if (!card.classList.contains('expanded')) {
      toggleMemoryDetail(card);
    }
  } else {
    // 无 content → 仅展开/收起
    toggleMemoryDetail(card);
  }
}

function toggleMemoryDetail(el) {
  const isExpanded = el.classList.toggle('expanded');
  const hint = el.querySelector('.memory-toggle-hint');
  if (hint) {
    // 有 content 时显示"收起/阅读全文"，无 content 时显示"收起/展开详情"
    const hasContent = el.classList.contains('has-content');
    hint.textContent = isExpanded ? t('memory.collapse') : (hasContent ? t('memory.toggleHint') : t('memory.toggleHintNoContent'));
  }
}

function initMemoryTabs() {
  document.querySelectorAll('.memory-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.memory-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentMemoryCat = tab.dataset.cat;
      renderMemoryList(currentMemoryCat);
    });
  });
}

// ═══════════════════════════════════════════════════════
// 模块⑤：知识库
// ═══════════════════════════════════════════════════════
let currentRefCat = 'all';

function renderReference() {
  const all = AOS_DATA.references;
  const systemCount = all.filter(r => r.category === 'system').length;
  const webCount = all.filter(r => r.category === 'web').length;
  document.getElementById('ref-all-count').textContent = all.length;
  document.getElementById('ref-system-count').textContent = systemCount;
  document.getElementById('ref-web-count').textContent = webCount;
  renderRefList(currentRefCat);
}

function renderRefList(cat) {
  const grid = document.getElementById('ref-grid');
  const items = cat === 'all' ? AOS_DATA.references : AOS_DATA.references.filter(r => r.category === cat);
  grid.innerHTML = items.map((r, i) => `
    <div class="ref-card ${r.content ? 'has-content' : ''}" onclick="onRefCardClick(event, '${r.slug}')">
      <div class="ref-header">
        <div class="ref-title">${r.title}</div>
        <span class="ref-cat ${r.category}">${r.category}</span>
      </div>
      <div class="ref-tags">
        ${r.tags.map(t => `<span class="ref-tag">${t}</span>`).join('')}
      </div>
      <div class="ref-source">🔗 ${r.source}</div>
      <div class="ref-confidence">
        <span class="confidence-label">${t('ref.confidence')}</span>
        <div class="confidence-bar">
          <div class="confidence-fill" style="width:${r.confidence * 100}%"></div>
        </div>
        <span class="confidence-value">${(r.confidence * 100).toFixed(0)}%</span>
      </div>
      <div class="ref-detail-collapse">
        <div class="ref-slug">slug: ${r.slug}</div>
        <div class="ref-path-hint">${t('ref.pathHint', r.category, r.slug)}</div>
        <div class="ref-source-link">${r.source.startsWith('http') ? `<a href="${r.source}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${t('ref.sourceLink')}</a>` : t('ref.source', r.source)}</div>
        ${r.content ? `<div class="md-reader-btn-disabled">${t('ref.readFull')}</div>` : `<div class="md-reader-btn-disabled">${t('ref.noContent')}</div>`}
      </div>
      <div class="ref-toggle-hint">${r.content ? t('ref.toggleHint') : t('ref.toggleHintNoContent')}</div>
    </div>
  `).join('');
}

// 知识库卡片点击逻辑（与记忆卡片对称）：
// - 有 content：点击卡片→始终打开/切换右侧侧边栏 MD 阅读（不收起卡片）
// - 无 content：点击卡片→仅展开/收起详情
// - 点击展开区域内部：仅切换展开，不触发阅读
function onRefCardClick(event, slug) {
  const r = AOS_DATA.references.find(x => x.slug === slug);
  if (!r) return;
  const card = event.currentTarget;
  // 点击展开详情区域内部，仅切换展开
  if (event.target.closest('.ref-detail-collapse')) {
    toggleRefDetail(card);
    return;
  }
  // 有 content → 始终打开侧边栏阅读（不管卡片是否已展开，都不收起）
  if (r.content) {
    openMdReader(r.title, r.content);
    if (!card.classList.contains('expanded')) {
      toggleRefDetail(card);
    }
  } else {
    toggleRefDetail(card);
  }
}

function toggleRefDetail(el) {
  const isExpanded = el.classList.toggle('expanded');
  const hint = el.querySelector('.ref-toggle-hint');
  if (hint) {
    const hasContent = el.classList.contains('has-content');
    hint.textContent = isExpanded ? t('ref.collapse') : (hasContent ? t('ref.toggleHint') : t('ref.toggleHintNoContent'));
  }
}

function initRefFilter() {
  document.querySelectorAll('.ref-filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.ref-filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentRefCat = tab.dataset.cat;
      renderRefList(currentRefCat);
    });
  });
}

// ═══════════════════════════════════════════════════════
// 模块⑥：Loop 监控
// ═══════════════════════════════════════════════════════
function renderLoops() {
  const container = document.getElementById('loop-types');
  container.innerHTML = AOS_DATA.loops.types.map(l => `
    <div class="loop-type-card unavailable">
      <div class="loop-type-header">
        <div class="loop-type-name">${l.name}</div>
        <span class="status-tag ready" title="${t('loop.unavailable.title')}">${t('loop.unavailable')}</span>
      </div>
      <div class="loop-type-desc">${l.desc}</div>
      <div class="loop-type-meta">${t('loop.activeMeta', l.active)}</div>
    </div>
  `).join('');
}

// ═══════════════════════════════════════════════════════
// 模块⑦：Agent 任务池
// ═══════════════════════════════════════════════════════
function renderAgents() {
  const modesContainer = document.getElementById('agent-modes');
  modesContainer.innerHTML = AOS_DATA.agents.modes.map(m => `
    <div class="agent-mode-card unavailable">
      <div class="agent-mode-header">
        <div class="agent-mode-name">${m.name}</div>
        <span class="status-tag ready" title="${t('agent.unavailable.title')}">${t('agent.unavailable')}</span>
      </div>
      <div class="agent-mode-desc">${m.desc}</div>
      <div class="agent-mode-trigger">${t('agent.trigger', m.trigger)}</div>
    </div>
  `).join('');

  const protocolsContainer = document.getElementById('agent-protocols');
  protocolsContainer.innerHTML = AOS_DATA.agents.protocols.map(p => `
    <div class="protocol-item">
      <span class="protocol-icon">⚙</span>
      <span class="protocol-text">${p}</span>
    </div>
  `).join('');
}

// ═══════════════════════════════════════════════════════
// 模块⑧：日志查看器
// ═══════════════════════════════════════════════════════
let currentLogLevel = 'all';
let currentLogSearch = '';

function renderLogs() {
  renderLogList();
  initLogFilter();
  initLogSearch();
}

function renderLogList() {
  const list = document.getElementById('log-list');
  // data.js 事件字段为 {time, type, desc}，需映射为日志查看器期望的 {time, level, source, message}
  // 事件 type → 日志 level 映射规则
  const typeToLevel = (type) => {
    const t = (type || 'info').toLowerCase();
    // 成功类操作（创建/注册/执行/发布）
    if (/^(skill_|tool_|project_|system_(patch|refactor|release))/.test(t) || t === 'system_init') {
      return 'SUCCESS';
    }
    // 警告类（归档/暂停/错误）
    if (/^(archive|pause|error|warn)/.test(t)) {
      return 'WARN';
    }
    return 'INFO';
  };
  // 事件 type → source 映射（提取前缀作为来源）
  const typeToSource = (type) => {
    const t = (type || 'system').toLowerCase();
    if (t.startsWith('skill_')) return 'SKILL';
    if (t.startsWith('tool_')) return 'TOOL';
    if (t.startsWith('project_')) return 'PROJECT';
    if (t.startsWith('system_')) return 'SYSTEM';
    if (t.startsWith('archive')) return 'ARCHIVE';
    return 'SYSTEM';
  };

  let items = (AOS_DATA.logs?.systemEvents || []).map(e => ({
    time: e.time || '',
    level: typeToLevel(e.type),
    source: typeToSource(e.type),
    message: e.desc || ''
  }));
  // 级别筛选
  if (currentLogLevel !== 'all') {
    items = items.filter(log => log.level === currentLogLevel);
  }
  // 搜索筛选
  if (currentLogSearch) {
    const q = currentLogSearch.toLowerCase();
    items = items.filter(log =>
      log.message.toLowerCase().includes(q) ||
      log.source.toLowerCase().includes(q) ||
      log.time.toLowerCase().includes(q)
    );
  }
  // 渲染
  if (items.length === 0) {
    list.innerHTML = `<div class="log-header"><span>${t('logs.col.time')}</span><span>${t('logs.col.level')}</span><span>${t('logs.col.source')}</span><span>${t('logs.col.message')}</span></div><div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-title">${t('logs.empty')}</div></div>`;
  } else {
    // 保留表头 + 日志行
    const header = `<div class="log-header"><span>${t('logs.col.time')}</span><span>${t('logs.col.level')}</span><span>${t('logs.col.source')}</span><span>${t('logs.col.message')}</span></div>`;
    list.innerHTML = header + items.map((log, idx) => `
      <div class="log-row" data-idx="${idx}" onclick="toggleLogDetail(this, ${idx})">
        <span class="log-time">${log.time}</span>
        <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
        <span class="log-source">${log.source}</span>
        <span class="log-message">${escapeHtml(log.message)}</span>
      </div>
    `).join('');
    // 存储当前日志数据供详情展开使用
    list._logItems = items;
  }
  document.getElementById('log-count').textContent = items.length;
}

// 日志行点击展开/收起详情
function toggleLogDetail(row, idx) {
  const existing = row.querySelector('.log-detail');
  if (existing) {
    // 收起
    existing.remove();
    row.classList.remove('expanded');
  } else {
    // 展开
    const items = row.parentElement._logItems || [];
    const log = items[idx];
    if (!log) return;
    const detail = document.createElement('div');
    detail.className = 'log-detail';
    detail.textContent = `${t('logs.detail.time')}: ${log.time}\n${t('logs.detail.level')}: ${log.level}\n${t('logs.detail.source')}: ${log.source}\n${t('logs.detail.message')}: ${log.message}`;
    row.appendChild(detail);
    row.classList.add('expanded');
  }
}

function initLogFilter() {
  document.querySelectorAll('.log-filter-tab').forEach(tab => {
    if (tab.dataset.initialized) return;
    tab.dataset.initialized = 'true';
    tab.addEventListener('click', () => {
      document.querySelectorAll('.log-filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentLogLevel = tab.dataset.level;
      renderLogList();
    });
  });
}

function initLogSearch() {
  const input = document.getElementById('log-search');
  if (!input || input.dataset.initialized) return;
  input.dataset.initialized = 'true';
  input.addEventListener('input', (e) => {
    currentLogSearch = e.target.value.trim();
    renderLogList();
  });
}

// ─── 数字滚动动画 ───
function animateNumber(el) {
  const target = parseInt(el.dataset.target);
  const delay = parseInt(el.dataset.delay) || 0;
  const duration = 800;
  setTimeout(() => {
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      el.textContent = Math.round(target * eased);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, delay);
}

// ═══════════════════════════════════════════════════════
// Dock 鱼眼效果
// ═══════════════════════════════════════════════════════
function initDockFisheye() {
  const dock = document.getElementById('dock');
  const items = dock.querySelectorAll('.dock-item');
  const maxScale = 1.5;

  dock.addEventListener('mousemove', (e) => {
    // 动效关闭时跳过鱼眼效果，保持静态
    if (document.body.classList.contains('no-animations')) {
      items.forEach(item => item.style.setProperty('--scale', '1'));
      return;
    }
    items.forEach(item => {
      const rect = item.getBoundingClientRect();
      const center = rect.left + rect.width / 2;
      const dist = Math.abs(e.clientX - center);
      const range = 120; // 影响范围
      if (dist < range) {
        const scale = 1 + (maxScale - 1) * (1 - dist / range);
        item.style.setProperty('--scale', scale.toFixed(3));
      } else {
        item.style.setProperty('--scale', '1');
      }
    });
  });

  dock.addEventListener('mouseleave', () => {
    items.forEach(item => item.style.setProperty('--scale', '1'));
  });

  // Dock 点击切换模块
  items.forEach(item => {
    item.addEventListener('click', () => {
      const target = item.dataset.module;
      // 所有 9 个模块均可切换
      const validModules = ['dashboard', 'skills', 'projects', 'memory', 'reference', 'loop', 'agent', 'logs', 'console'];
      if (validModules.includes(target)) {
        switchModule(target);
      } else {
        flashDockItem(item);
      }
    });
  });
}

function flashDockItem(item) {
  item.style.animation = 'none';
  setTimeout(() => { item.style.animation = 'shake 0.4s ease'; }, 10);
  setTimeout(() => { item.style.animation = ''; }, 450);
  const label = item.querySelector('.dock-label').textContent;
  showNotification(`${label} 模块`, '该模块正在开发中，敬请期待');
}

// ═══════════════════════════════════════════════════════
// Spotlight 搜索
// ═══════════════════════════════════════════════════════
// 构建 Spotlight 搜索索引（模块 + 脚本 + Skill + 项目 + 记忆 + 知识库）
function buildSearchIndex() {
  const index = [
    { icon: '📊', title: t('module.dashboard'), desc: t('search.desc.dashboard'), type: t('search.type.module'), action: () => switchModule('dashboard') },
    { icon: '⚙', title: t('module.skills'), desc: t('search.desc.skills'), type: t('search.type.module'), action: () => switchModule('skills') },
    { icon: '📁', title: t('module.projects'), desc: t('search.desc.projects'), type: t('search.type.module'), action: () => switchModule('projects') },
    { icon: '🧠', title: t('module.memory'), desc: t('search.desc.memory'), type: t('search.type.module'), action: () => switchModule('memory') },
    { icon: '📚', title: t('module.reference'), desc: t('search.desc.reference'), type: t('search.type.module'), action: () => switchModule('reference') },
    { icon: '🔄', title: t('module.loop'), desc: t('search.desc.loop'), type: t('search.type.module'), action: () => switchModule('loop') },
    { icon: '👥', title: t('module.agent'), desc: t('search.desc.agent'), type: t('search.type.module'), action: () => switchModule('agent') },
    { icon: '📋', title: t('module.logs'), desc: t('search.desc.logs'), type: t('search.type.module'), action: () => switchModule('logs') },
    { icon: '🖥', title: t('module.console'), desc: t('search.desc.console'), type: t('search.type.module'), action: () => switchModule('console') },
    { icon: '🔧', title: t('menu.tools.check'), desc: 'aos_check.py', type: t('search.type.script'), action: () => { switchModule('console'); setTimeout(() => runScript('check'), 300); } },
    { icon: '📥', title: t('menu.tools.migrate'), desc: 'aos_migrate_collect.py', type: t('search.type.script'), action: () => { switchModule('console'); setTimeout(() => runScript('migrate'), 300); } },
  ];

  // Skill 条目
  if (AOS_DATA.skills && Array.isArray(AOS_DATA.skills)) {
    AOS_DATA.skills.forEach(s => {
      index.push({
        icon: '⚙',
        title: s.name,
        desc: s.trigger || s.id,
        type: 'Skill',
        action: () => switchModule('skills')
      });
    });
  }

  // 项目条目（点击跳转并打开详情）
  if (AOS_DATA.projects && Array.isArray(AOS_DATA.projects)) {
    AOS_DATA.projects.forEach((p, i) => {
      // 项目级 MD：合并 agentsContent + readmeContent
      const projContent = [p.agentsContent || '', p.readmeContent || ''].join('\n');
      index.push({
        icon: '📁',
        title: p.title || p.name,
        desc: p.desc || p.path,
        type: t('search.type.project'),
        content: projContent,
        action: () => { switchModule('projects'); setTimeout(() => openProjectDetail(i), 350); }
      });
      // 项目集模式：子项目（plugins）也加入索引
      if (p.projectType === '项目集' && Array.isArray(p.plugins)) {
        p.plugins.forEach((sub, subIdx) => {
          // 子项目详细 MD 在 SUBPROJECT_DATA 中（readme + metadata）
          const subData = (typeof SUBPROJECT_DATA !== 'undefined' && SUBPROJECT_DATA[sub.name]) || {};
          const subContent = [subData.readme || '', subData.metadata || ''].join('\n');
          index.push({
            icon: '🔌',
            title: sub.name,
            desc: sub.desc || `${sub.version || ''} · ${sub.author || ''}`,
            type: t('search.type.subproject', p.name),
            content: subContent,
            action: () => {
              switchModule('projects');
              setTimeout(() => {
                openProjectDetail(i);
                // 等面板渲染完成后，打开子项目全屏视图
                setTimeout(() => openSubProjectFullscreen(subIdx), 600);
              }, 350);
            }
          });
        });
      }
    });
  }

  // 记忆条目（4 个分类，点击自动切换到对应分类）
  if (AOS_DATA.memories && typeof AOS_DATA.memories === 'object') {
    const memCatKeys = { user: 'memory.user', feedback: 'memory.feedback', reference: 'memory.reference', project: 'memory.project' };
    Object.keys(AOS_DATA.memories).forEach(cat => {
      const items = AOS_DATA.memories[cat];
      if (Array.isArray(items)) {
        items.forEach(m => {
          index.push({
            icon: '🧠',
            title: m.title,
            desc: m.hook || m.path,
            type: t('search.type.memory', t(memCatKeys[cat] || cat)),
            content: m.content || '',
            action: () => {
              switchModule('memory');
              setTimeout(() => {
                const tab = document.querySelector(`.memory-tab[data-cat="${cat}"]`);
                if (tab) tab.click();
              }, 350);
            }
          });
        });
      }
    });
  }

  // 知识库条目（点击自动切换到对应分类）
  if (AOS_DATA.references && Array.isArray(AOS_DATA.references)) {
    AOS_DATA.references.forEach(r => {
      index.push({
        icon: '📚',
        title: r.title,
        desc: r.tags ? r.tags.join(', ') : r.slug,
        type: t('search.type.reference', r.category || 'web'),
        content: r.content || '',
        action: () => {
          switchModule('reference');
          setTimeout(() => {
            const cat = r.category || 'web';
            const tab = document.querySelector(`.ref-filter-tab[data-cat="${cat}"]`);
            if (tab) tab.click();
          }, 350);
        }
      });
    });
  }

  return index;
}

// 高亮搜索关键词（5 秒后自动消失）
function highlightSearchTerm(term) {
  if (!term || term.length < 2) return;
  // 先清除之前的高亮
  clearSearchHighlight();

  // 确定搜索范围：项目详情面板（如果可见）或当前活跃模块
  let scope = document.getElementById('project-detail-panel');
  if (!scope || !scope.classList.contains('visible')) {
    scope = document.querySelector('.module.active') || document.getElementById('content');
  }
  if (!scope) return;

  const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');

  // 遍历文本节点
  const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => {
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      const parent = node.parentElement;
      if (!parent) return NodeFilter.FILTER_REJECT;
      // 排除 script/style/mark 等
      if (parent.closest('script, style, mark.search-highlight, .spotlight-hint')) return NodeFilter.FILTER_REJECT;
      return regex.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });

  const nodes = [];
  let node;
  while (node = walker.nextNode()) nodes.push(node);

  let highlightCount = 0;
  nodes.forEach(n => {
    const text = n.nodeValue;
    const span = document.createElement('span');
    span.innerHTML = text.replace(regex, '<mark class="search-highlight">$1</mark>');
    n.parentNode.replaceChild(span, n);
    highlightCount++;
  });

  debugLog('info', `[Highlight] 高亮 "${term}" — ${highlightCount} 处`);

  // 滚动到第一个高亮位置
  const firstMark = document.querySelector('mark.search-highlight');
  if (firstMark) {
    firstMark.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // 6 秒后自动移除高亮
  setTimeout(() => clearSearchHighlight(), 6000);
}

// 清除搜索高亮
function clearSearchHighlight() {
  document.querySelectorAll('mark.search-highlight').forEach(mark => {
    const parent = mark.parentNode;
    parent.replaceChild(document.createTextNode(mark.textContent), mark);
    parent.normalize();
  });
}

// 转义正则特殊字符
function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 调试：打印搜索索引构建情况
function logSearchIndexDebug(index) {
  if (!debugEnabled) return;
  debugLog('info', `[SearchIndex] 构建完成，共 ${index.length} 条`);
  // 统计有 content 的条目
  const withContent = index.filter(i => i.content && i.content.length > 0);
  debugLog('debug', `[SearchIndex] 含 content 的条目: ${withContent.length} 条`);
  withContent.forEach(item => {
    debugLog('debug', `  - ${item.title} (${item.type}) | content: ${item.content.length} 字符`);
  });
}

function initSpotlight() {
  const spotlight = document.getElementById('spotlight');
  const input = document.getElementById('spotlight-input');
  const results = document.getElementById('spotlight-results');
  const closeBtn = document.getElementById('spotlight-close');

  // 搜索数据源（动态构建）
  const searchIndex = buildSearchIndex();
  // 调试：打印索引构建情况
  logSearchIndexDebug(searchIndex);

  // Ctrl+Space / Cmd+Space 唤起
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.code === 'Space') {
      e.preventDefault();
      openSpotlight();
    }
    if (e.code === 'Escape' && spotlight.classList.contains('visible')) {
      closeSpotlight();
    }
  });

  // 关闭按钮
  closeBtn.addEventListener('click', closeSpotlight);

  // 实时搜索（带防抖）
  let searchTimer = null;
  input.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => doSearch(), 200);
  });

  function doSearch() {
    const query = input.value.trim().toLowerCase();
    if (!query) { results.innerHTML = ''; return; }
    const prefs = loadPrefs();
    const mdOn = !!prefs.mdSearch;

    debugLog('info', `[Spotlight] 搜索: "${query}" | MD搜索: ${mdOn ? 'ON' : 'OFF'} | 索引总数: ${searchIndex.length}`);

    const matched = searchIndex.filter(item => {
      if (item.title.toLowerCase().includes(query)) return true;
      if (item.desc.toLowerCase().includes(query)) return true;
      if (item.type.toLowerCase().includes(query)) return true;
      // MD 正文搜索
      if (mdOn && item.content && item.content.toLowerCase().includes(query)) return true;
      return false;
    });

    // 调试：记录匹配详情
    debugLog('debug', `[Spotlight] 匹配 ${matched.length} 条:`);
    matched.forEach((m, i) => {
      const contentLen = m.content ? m.content.length : 0;
      debugLog('debug', `  [${i}] ${m.title} (${m.type}) | content长度: ${contentLen}`);
    });

    results.innerHTML = matched.map((item, i) => {
      // 生成显示描述：如果 MD 搜索开启且匹配到 content，显示匹配片段
      let displayDesc = item.desc;
      if (mdOn && item.content) {
        const lowerContent = item.content.toLowerCase();
        const idx = lowerContent.indexOf(query);
        if (idx >= 0) {
          const start = Math.max(0, idx - 40);
          const end = Math.min(item.content.length, idx + query.length + 40);
          const snippet = (start > 0 ? '…' : '') + item.content.slice(start, end).replace(/\n/g, ' ') + (end < item.content.length ? '…' : '');
          displayDesc = snippet;
        }
      }
      return `
        <div class="spotlight-result ${i === 0 ? 'selected' : ''}" data-idx="${i}">
          <span class="spotlight-result-icon">${item.icon}</span>
          <div class="spotlight-result-info">
            <div class="spotlight-result-title">${item.title}</div>
            <div class="spotlight-result-desc">${displayDesc}</div>
          </div>
          <span class="spotlight-result-type">${item.type}</span>
        </div>
      `;
    }).join('');

    // 点击结果
    results.querySelectorAll('.spotlight-result').forEach((el, i) => {
      el.addEventListener('click', () => {
        const query = input.value.trim();
        matched[i].action();
        // 等待页面跳转和渲染完成后高亮关键词
        setTimeout(() => highlightSearchTerm(query), 1200);
        closeSpotlight();
      });
    });
  }

  // Enter 执行第一个结果
  input.addEventListener('keydown', (e) => {
    if (e.code === 'Enter') {
      const first = results.querySelector('.spotlight-result');
      if (first) first.click();
    }
  });
}

function switchModule(name) {
  closeAllOverlays();
  // 切换模块时自动收起项目详情面板（无论扩展或侧滑状态）
  closeProjectDetail();
  document.querySelectorAll('.dock-item').forEach(d => {
    d.classList.toggle('active', d.dataset.module === name);
  });
  document.querySelectorAll('.module').forEach(m => m.classList.remove('active'));
  const targetModule = document.getElementById(`m-${name}`);
  if (targetModule) targetModule.classList.add('active');
  // 日志模块特殊处理：添加 logs-active 类，CSS flex 自动适配高度
  const content = document.getElementById('content');
  if (name === 'logs') {
    content.classList.add('logs-active');
  } else {
    content.classList.remove('logs-active');
  }
  // dashboard 模块重新触发数字动画
  if (name === 'dashboard') {
    setTimeout(() => {
      document.querySelectorAll('.stat-value').forEach(el => {
        el.textContent = '0';
        animateNumber(el);
      });
    }, 100);
  }
}

function flashDockByName(name) {
  const item = document.querySelector(`.dock-item[data-module="${name}"]`);
  if (item) flashDockItem(item);
}

// ═══════════════════════════════════════════════════════
// 右键菜单
// ═══════════════════════════════════════════════════════
function initContextMenu() {
  const menu = document.getElementById('context-menu');

  document.addEventListener('contextmenu', (e) => {
    // 检测当前是否有选中文字（在任何区域都先检测，用于决定是否全局允许右键）
    const sel = window.getSelection();
    const selectedText = sel ? sel.toString().trim() : '';

    // 有选中文字时，全局允许右键菜单（仅显示复制/搜索）
    // 无选中文字时，仅在桌面和 Dock 上显示完整右键菜单
    const isDesktop = e.target.closest('#desktop, #dock');
    if (!isDesktop && !selectedText) return;

    // 有选中文字时不排除任何浮层（允许在 MD reader、项目详情等侧边栏区域复制文字）
    // 无选中文字时，排除浮层区域
    if (!selectedText) {
      if (e.target.closest('#spotlight, #settings-panel, #context-menu, #notification, #md-reader-overlay')) return;
      const pdp = document.getElementById('project-detail-panel');
      if (pdp && pdp.classList.contains('visible') && pdp.contains(e.target)) return;
      const dbg = document.getElementById('debug-panel');
      if (dbg && dbg.classList.contains('visible') && dbg.contains(e.target)) return;
    }
    e.preventDefault();

    const isEvent = e.target.closest('.event-row');

    let items = [];
    // 有选中文字时，在菜单顶部添加复制和搜索选项（全局有效）
    if (selectedText) {
      items.push({ icon: '📋', label: t('ctx.copySelection'), shortcut: 'Ctrl+C', action: 'copy-selection' });
      items.push({ icon: '🔍', label: t('ctx.searchSelection'), shortcut: '', action: 'search-selection' });
    }

    // 仅在桌面/Dock区域显示完整功能菜单
    if (isDesktop) {
      if (selectedText) items.push({ divider: true });
      if (isEvent) {
        // 事件行右键菜单：仅提供复制功能（真正调用 clipboard API）
        items.push({ icon: '📋', label: t('ctx.copyEvent'), shortcut: 'Ctrl+C', action: 'copy-event' });
        items.push({ divider: true });
        items.push({ icon: '🔄', label: t('ctx.refreshLog'), shortcut: 'F5', action: 'refresh' });
      } else {
        // 桌面右键菜单：快捷操作入口
        items.push({ icon: '🔄', label: t('ctx.refresh'), shortcut: 'F5', action: 'refresh' });
        items.push({ icon: '🔍', label: t('ctx.spotlight'), shortcut: 'Ctrl+Space', action: 'spotlight' });
        items.push({ divider: true });
        items.push({ icon: '📊', label: t('ctx.dashboard'), shortcut: '', action: 'goto-dashboard' });
        items.push({ icon: '🖥', label: t('ctx.console'), shortcut: '', action: 'goto-console' });
        items.push({ divider: true });
        items.push({ icon: '⚙', label: t('ctx.settings'), shortcut: 'Ctrl+,', action: 'settings' });
      }
    }

    if (items.length === 0) return;

    menu.innerHTML = items.map(item => {
      if (item.divider) return '<div class="ctx-divider"></div>';
      return `<div class="ctx-item">
        <span class="ctx-icon">${item.icon}</span>
        <span>${item.label}</span>
        ${item.shortcut ? `<span class="ctx-shortcut">${item.shortcut}</span>` : ''}
      </div>`;
    }).join('');

    // 定位
    menu.style.left = Math.min(e.clientX, window.innerWidth - 200) + 'px';
    menu.style.top = Math.min(e.clientY, window.innerHeight - 300) + 'px';
    menu.classList.add('visible');

    // 菜单项点击 — 传递 selectedText 缓存值（点击菜单项时选区可能已清除）
    const realItems = items.filter(it => !it.divider);
    menu.querySelectorAll('.ctx-item').forEach((el, i) => {
      el.addEventListener('click', () => {
        const action = realItems[i];
        handleContextAction(action, isEvent ? e.target.closest('.event-row') : null, selectedText);
        closeContextMenu();
      });
    });
  });

  // ESC 关闭
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Escape' && menu.classList.contains('visible')) {
      closeContextMenu();
    }
  });
}

// 右键菜单动作处理
// action: { icon, label, shortcut, action }
// eventRow: 如果是事件行右键，传入 .event-row 元素用于提取文本
// cachedSelection: contextmenu 触发时缓存的选中文字（点击菜单项时选区可能已清除）
function handleContextAction(item, eventRow, cachedSelection) {
  switch (item.action) {
    case 'refresh':
      renderDashboard();
      showNotification(t('notif.refresh'), t('notif.refreshDesc'));
      break;
    case 'spotlight':
      openSpotlight();
      break;
    case 'goto-dashboard':
      switchModule('dashboard');
      break;
    case 'goto-console':
      switchModule('console');
      break;
    case 'settings':
      openSettings();
      break;
    case 'copy-event':
      if (eventRow) {
        const text = eventRow.innerText || eventRow.textContent;
        copyToClipboard(text);
      }
      break;
    case 'copy-selection': {
      // 使用 contextmenu 事件触发时缓存的选中文字（点击菜单项时选区可能已清除）
      const text = cachedSelection || '';
      if (text) {
        copyToClipboard(text);
        const sel = window.getSelection();
        if (sel) sel.removeAllRanges();
      }
      break;
    }
    case 'search-selection': {
      // 使用 contextmenu 事件触发时缓存的选中文字
      const text = cachedSelection || '';
      if (text) {
        const sel = window.getSelection();
        if (sel) sel.removeAllRanges();
        openSpotlight(text);
      }
      break;
    }
  }
}

// 真正复制文本到剪贴板（使用 Clipboard API，带降级方案）
function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showNotification(t('notif.copied'), t('notif.copiedDesc'));
    }).catch(() => {
      fallbackCopyToClipboard(text);
    });
  } else {
    fallbackCopyToClipboard(text);
  }
}

// 降级复制方案（兼容旧浏览器/非 HTTPS 环境）
function fallbackCopyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    showNotification(t('notif.copied'), t('notif.copiedDesc'));
  } catch (err) {
    showNotification(t('notif.copyFail'), t('notif.copyFailDesc'));
  }
  document.body.removeChild(textarea);
}

// ═══════════════════════════════════════════════════════
// 通知气泡
// ═══════════════════════════════════════════════════════
let notifTimer = null;
function showNotification(title, desc) {
  const notif = document.getElementById('notification');
  document.getElementById('notif-title').textContent = title;
  document.getElementById('notif-desc').textContent = desc;
  notif.classList.add('visible');
  clearTimeout(notifTimer);
  notifTimer = setTimeout(() => closeNotification(), 3000);
}

// ═══════════════════════════════════════════════════════
// 控制台脚本执行
// ═══════════════════════════════════════════════════════
document.querySelectorAll('.glass-btn').forEach(btn => {
  btn.addEventListener('click', () => runScript(btn.dataset.script));
});

function runScript(script) {
  const output = SCRIPT_OUTPUTS[script];
  if (!output) return;
  const body = document.getElementById('terminal-body');
  // 清空之前的 prompt
  body.querySelectorAll('.term-prompt').forEach(p => p.remove());

  let i = 0;
  const typeNext = () => {
    if (i >= output.length) {
      const prompt = document.createElement('div');
      prompt.className = 'term-line term-prompt';
      prompt.innerHTML = 'AOS:~$ <span class="cursor"></span>';
      body.appendChild(prompt);
      body.scrollTop = body.scrollHeight;
      return;
    }
    const line = output[i];
    const div = document.createElement('div');
    div.className = `term-line term-${line.type}`;
    div.textContent = line.text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    i++;
    setTimeout(typeNext, 100 + Math.random() * 60);
  };
  typeNext();
}

// ═══════════════════════════════════════════════════════
// 顶部菜单栏（下拉菜单 + 单按钮入口）
// ═══════════════════════════════════════════════════════
function initMenuBar() {
  const menuItems = document.querySelectorAll('.menu-item');

  menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
      // 阻止冒泡到 document 的全局点击（避免立即收起）
      e.stopPropagation();
      const menu = item.dataset.menu;

      // 下拉菜单：切换展开状态
      const isOpen = item.classList.contains('open');
      closeAllDropdowns();
      if (!isOpen) {
        item.classList.add('open');
        // 同步当前主题选中态
        syncDropdownChecks();
      }
    });
  });

  // 下拉菜单项点击
  document.querySelectorAll('.dropdown-item').forEach(dd => {
    dd.addEventListener('click', (e) => {
      e.stopPropagation();
      const action = dd.dataset.action;
      handleMenuAction(action, dd);
      closeAllDropdowns();
    });
  });

  // 点击外部收起
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-item')) {
      closeAllDropdowns();
    }
  });

  // ESC 收起
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Escape') {
      closeAllDropdowns();
    }
  });

  // 首次同步选中态
  syncDropdownChecks();

  // 桌面模式检测与窗口控制
  initDesktopMode();
}

function initDesktopMode() {
  // 检测是否在 PyWebView 桌面模式下运行
  const isDesktop = !!(window.pywebview && window.pywebview.api);

  if (isDesktop) {
    document.body.classList.add('desktop-mode');
    document.body.classList.add('frameless');

    // 窗口控制按钮
    document.getElementById('win-minimize')?.addEventListener('click', () => {
      window.pywebview.api.minimize();
    });
    document.getElementById('win-maximize')?.addEventListener('click', () => {
      window.pywebview.api.toggle_maximize();
    });
    document.getElementById('win-close')?.addEventListener('click', () => {
      window.pywebview.api.close();
    });

    // 自定义菜单栏拖拽（easy_drag=False，避免 PyWebView 全局拖拽阻止文字选中）
    // 方案：绝对位置追踪 — mousedown 时 drag_start 记录初始位置，mousemove 时 drag_move 计算绝对目标位置
    // 优势：基于初始窗口位置 + 鼠标偏移量计算，避免依赖过时的 self._window.x/y
    const menuBarDrag = document.getElementById('menu-bar');

    // 拖拽状态（闭包内，避免全局污染）
    let isDragging = false;
    let dragRafId = null;
    let lastMoveEvent = null;

    menuBarDrag?.addEventListener('mousedown', (e) => {
      // 只在非交互元素上启动拖拽
      if (e.target.closest('.menu-item, .menu-settings, .win-btn, .dropdown-item, .menu-dropdown')) return;
      if (e.button !== 0) return;  // 只响应左键
      // 调用 Python 端记录初始窗口位置和鼠标屏幕坐标
      window.pywebview.api.drag_start(e.screenX, e.screenY);
      isDragging = true;
      document.body.classList.add('window-dragging');
      e.preventDefault();
    });

    // 拖拽移动：使用 requestAnimationFrame 批处理，每帧最多 1 次 drag_move 调用
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      lastMoveEvent = e;
      if (dragRafId !== null) return;  // 已有待执行帧，跳过
      dragRafId = requestAnimationFrame(() => {
        dragRafId = null;
        if (!isDragging || !lastMoveEvent) return;
        window.pywebview.api.drag_move(lastMoveEvent.screenX, lastMoveEvent.screenY);
      });
    });

    // 拖拽结束清理
    document.addEventListener('mouseup', () => {
      isDragging = false;
      if (dragRafId !== null) {
        cancelAnimationFrame(dragRafId);
        dragRafId = null;
      }
      document.body.classList.remove('window-dragging');
    });

    // 拖拽中离开窗口也要清理（防止状态卡死）
    document.addEventListener('mouseleave', () => {
      if (isDragging) {
        isDragging = false;
        if (dragRafId !== null) {
          cancelAnimationFrame(dragRafId);
          dragRafId = null;
        }
        document.body.classList.remove('window-dragging');
      }
    });

    // 双击菜单栏空白区域切换最大化
    const menuBar = document.getElementById('menu-bar');
    menuBar?.addEventListener('dblclick', (e) => {
      // 只在空白区域双击（排除交互元素）
      if (e.target.closest('.menu-item, .menu-settings, .win-btn, .dropdown-item, .menu-dropdown')) return;
      window.pywebview.api.toggle_maximize();
    });

    debugLog('info', '桌面模式已激活（frameless + 自定义标题栏 + 菜单栏拖拽限制 + 双击最大化）');
  }
}

function closeAllDropdowns() {
  document.querySelectorAll('.menu-item.has-dropdown.open').forEach(el => {
    el.classList.remove('open');
  });
}

// 同步下拉菜单的选中标记（主题、当前模块）
function syncDropdownChecks() {
  const prefs = loadPrefs();
  // 主题选中
  document.querySelectorAll('.dropdown-item[data-action="theme"]').forEach(el => {
    el.classList.toggle('checked', el.dataset.theme === prefs.theme);
  });
  // 当前模块选中
  const activeModule = document.querySelector('.dock-item.active');
  const activeName = activeModule ? activeModule.dataset.module : 'dashboard';
  document.querySelectorAll('.dropdown-item[data-action="switch"]').forEach(el => {
    el.classList.toggle('checked', el.dataset.module === activeName);
  });
}

// 菜单动作分发
function handleMenuAction(action, el) {
  switch (action) {
    case 'refresh':
      if (dataLoadMode === 'api') {
        refreshApiData();
      } else {
        renderDashboard();
        showNotification(t('notif.refresh'), t('notif.refreshDesc'));
      }
      break;
    case 'export-json':
      exportAOSJson();
      break;
    case 'close-panel':
      closeAllOverlays();
      closeProjectDetail && closeProjectDetail();
      showNotification(t('notif.closed'), t('notif.closedDesc'));
      break;
    case 'switch':
      switchModule(el.dataset.module);
      syncDropdownChecks();
      break;
    case 'theme':
      setTheme(el.dataset.theme);
      syncDropdownChecks();
      break;
    case 'zoom-in':
      setScale(Math.min(1.4, (loadPrefs().scale || 1) + 0.1));
      break;
    case 'zoom-out':
      setScale(Math.max(0.8, (loadPrefs().scale || 1) - 0.1));
      break;
    case 'zoom-reset':
      setScale(1);
      break;
    case 'about':
      showAboutDialog();
      break;
    case 'shortcuts':
      showShortcutsDialog();
      break;
    case 'spotlight':
      openSpotlight();
      break;
    case 'run-check':
      switchModule('console');
      setTimeout(() => runScript('check'), 300);
      break;
    case 'run-migrate':
      switchModule('console');
      setTimeout(() => runScript('migrate'), 300);
      break;
    case 'settings':
      openSettings();
      break;
  }
}

// 设置主题（同步偏好）
function setTheme(theme) {
  const prefs = loadPrefs();
  prefs.theme = theme;
  applyPrefs(prefs);
  savePrefs(prefs);
  // 同步设置面板 UI
  if (typeof updateSettingsUI === 'function') updateSettingsUI(prefs);
  const themeKeys = { dark: 'theme.dark', light: 'theme.light', minimal: 'theme.minimal' };
  showNotification(t('notif.themeChanged'), t('notif.themeChangedDesc', t(themeKeys[theme] || theme)));
}

// 设置缩放（同步偏好）
function setScale(scale) {
  const prefs = loadPrefs();
  prefs.scale = scale;
  applyPrefs(prefs);
  savePrefs(prefs);
  if (typeof updateSettingsUI === 'function') updateSettingsUI(prefs);
  showNotification(t('notif.scaleChanged'), t('notif.scaleChangedDesc', Math.round(scale * 100)));
}

// 导出 AOS 数据为 JSON
function exportAOSJson() {
  try {
    const data = JSON.stringify(AOS_DATA, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aos_data_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showNotification(t('notif.exportSuccess'), t('notif.exportSuccessDesc'));
  } catch (err) {
    showNotification(t('notif.exportFail'), t('notif.exportFailDesc', err.message || t('common.unknown')));
  }
}

// 关于 AOS — 跳转官网
function showAboutDialog() {
  const officialSite = 'https://magicalyuyu.github.io/agent-operating-system/';
  window.open(officialSite, '_blank');
  showNotification(t('notif.redirecting'), t('notif.redirectingDesc'));
}

// 快捷键说明
function showShortcutsDialog() {
  showNotification(
    t('shortcuts.title'),
    t('shortcuts.desc')
  );
}

// ═══════════════════════════════════════════════════════
// 全局快捷键
// ═══════════════════════════════════════════════════════
document.addEventListener('keydown', (e) => {
  // F5 刷新
  if (e.code === 'F5') {
    e.preventDefault();
    renderDashboard();
    showNotification(t('notif.refresh'), t('notif.refreshDesc'));
  }
  // Ctrl+1/2 切换模块
  if (e.ctrlKey && e.code === 'Digit1') {
    e.preventDefault();
    switchModule('dashboard');
  }
  if (e.ctrlKey && e.code === 'Digit2') {
    e.preventDefault();
    switchModule('console');
  }
  // Ctrl+, 打开偏好设置
  if (e.ctrlKey && e.code === 'Comma') {
    e.preventDefault();
    openSettings();
  }
});

// ═══════════════════════════════════════════════════════
// 偏好设置面板
// ═══════════════════════════════════════════════════════
function initSettings() {
  const settingsBtn = document.getElementById('settings-btn');
  const settingsClose = document.getElementById('settings-close');
  const overlay = document.getElementById('overlay');
  let prefs = loadPrefs();

  // 应用已保存的偏好
  applyPrefs(prefs);
  updateSettingsUI(prefs);

  settingsBtn.addEventListener('click', (e) => {
    e.stopPropagation();  // 阻止冒泡到 document，避免 initGlobalClick 干扰
    openSettings();
  });
  settingsClose.addEventListener('click', closeSettings);
  overlay.addEventListener('click', closeSettings);

  // 主题切换
  document.querySelectorAll('.theme-option').forEach(opt => {
    opt.addEventListener('click', () => {
      prefs.theme = opt.dataset.theme;
      applyPrefs(prefs);
      savePrefs(prefs);
      updateSettingsUI(prefs);
    });
  });

  // 动效开关
  const toggleAnim = document.getElementById('toggle-animations');
  toggleAnim.addEventListener('click', () => {
    prefs.animations = !prefs.animations;
    applyPrefs(prefs);
    savePrefs(prefs);
    updateSettingsUI(prefs);
  });

  // 缩放滑块
  const sliderScale = document.getElementById('slider-scale');
  const scaleValue = document.getElementById('scale-value');
  sliderScale.addEventListener('input', () => {
    prefs.scale = parseFloat(sliderScale.value);
    applyPrefs(prefs);
    savePrefs(prefs);
    scaleValue.textContent = Math.round(prefs.scale * 100) + '%';
  });

  // 玻璃强度
  document.querySelectorAll('.glass-option').forEach(opt => {
    opt.addEventListener('click', () => {
      prefs.glass = opt.dataset.glass;
      applyPrefs(prefs);
      savePrefs(prefs);
      updateSettingsUI(prefs);
    });
  });

  // 调试面板开关
  const toggleDebug = document.getElementById('toggle-debug');
  if (toggleDebug) {
    toggleDebug.addEventListener('click', () => {
      prefs.debug = !prefs.debug;
      savePrefs(prefs);
      updateSettingsUI(prefs);
      debugEnabled = prefs.debug;
      const debugPanel = document.getElementById('debug-panel');
      const handle = document.getElementById('debug-toggle-handle');
      if (prefs.debug) {
        // 开启：面板展示 + 把手显示在展开位置
        debugPanel.classList.add('visible');
        handle.classList.add('visible');
        handle.classList.remove('collapsed');
        handle.title = '收起调试面板';
        handle.querySelector('.debug-handle-arrow').textContent = '‹';
        updateDebugState();
        debugLog('info', '调试面板已开启');
      } else {
        // 关闭：面板隐藏 + 把手隐藏
        debugPanel.classList.remove('visible');
        handle.classList.remove('visible', 'collapsed');
      }
    });
  }

  // MD 正文搜索开关
  const toggleMdSearch = document.getElementById('toggle-md-search');
  if (toggleMdSearch) {
    toggleMdSearch.addEventListener('click', () => {
      prefs.mdSearch = !prefs.mdSearch;
      savePrefs(prefs);
      updateSettingsUI(prefs);
      updateSpotlightHint();
    });
  }

  // 语言切换
  document.querySelectorAll('.lang-option').forEach(opt => {
    opt.addEventListener('click', () => {
      const lang = opt.dataset.lang;
      if (lang === _currentLang) return;
      setLang(lang);
      // 更新选中态
      document.querySelectorAll('.lang-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      // 重新渲染所有动态模块（更新动态文本）
      renderDashboard();
      renderSkills();
      renderProjects();
      renderMemory();
      renderReference();
      renderLoops();
      renderAgents();
      renderLogs();
      // 重建搜索索引（描述文本已翻译）
      buildSearchIndex();
      // 更新 Spotlight 提示
      updateSpotlightHint();
      // 更新数据源指示器
      updateDataSourceIndicator();
    });
  });

  // ESC 关闭
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Escape' && document.getElementById('settings-panel').classList.contains('visible')) {
      closeSettings();
    }
  });
}

function updateSettingsUI(prefs) {
  // 主题选中态
  document.querySelectorAll('.theme-option').forEach(opt => {
    opt.classList.toggle('selected', opt.dataset.theme === prefs.theme);
  });
  // 动效开关
  document.getElementById('toggle-animations').classList.toggle('on', prefs.animations);
  // 缩放
  document.getElementById('slider-scale').value = prefs.scale;
  document.getElementById('scale-value').textContent = Math.round(prefs.scale * 100) + '%';
  // 玻璃强度
  document.querySelectorAll('.glass-option').forEach(opt => {
    opt.classList.toggle('selected', opt.dataset.glass === prefs.glass);
  });
  // 调试面板开关
  const toggleDebug = document.getElementById('toggle-debug');
  if (toggleDebug) toggleDebug.classList.toggle('on', prefs.debug);
  // MD 正文搜索开关
  const toggleMdSearch = document.getElementById('toggle-md-search');
  if (toggleMdSearch) toggleMdSearch.classList.toggle('on', prefs.mdSearch);
  // 语言选中态
  document.querySelectorAll('.lang-option').forEach(opt => {
    opt.classList.toggle('selected', opt.dataset.lang === (prefs.lang || 'zh-CN'));
  });
}

// ═══════════════════════════════════════════════════════
// 项目详情面板 expand handle 点击功能
// TODO: 侧边栏拖拽调整宽度（PyWebView 环境下 mousedown 事件异常，暂搁置）
// ═══════════════════════════════════════════════════════
function initPanelResizer() {
  const expandHandle = document.getElementById('detail-expand-handle');
  if (!expandHandle) return;
  // 点击展开/收起（恢复原有功能）
  expandHandle.addEventListener('click', toggleExpandDetail);
}
