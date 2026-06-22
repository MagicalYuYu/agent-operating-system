# 网页模板规范文档

> 本文档永久留存 AOS 与灵犀两个项目网站的开发经验、可视化技巧和模板规范，供后续开发更多网页时复用。
>
> - **AOS 网站**（`d:\AOS\docs\index.html`）：蓝紫科技风，纯文件系统 Agent 框架官网
> - **灵犀网站**（`d:\AOS\05_CACHE\smart_wakeup_repo\docs\index.html`）：翡翠绿暖色调，AstrBot 智能唤醒插件官网
>
> 维护规则：本文档为状态型参考知识，新增动效或配色方案时覆盖旧值并保留变更注释。

---

## 1. 设计模式总结

### 1.1 AOS 蓝紫科技风配色方案

适用于：技术框架、开发者工具、AI/Agent 类项目。营造冷峻、未来感、专业感。

```css
:root {
  /* 背景层（深空黑紫） */
  --bg-primary: #08080d;          /* 主背景 */
  --bg-secondary: #0f0f18;        /* 次背景 */
  --bg-card: rgba(21, 21, 34, 0.55);   /* 卡片半透明背景 */
  --bg-card-solid: #151522;       /* 卡片实色背景 */
  --bg-card-hover: rgba(28, 28, 48, 0.65);

  /* 主色调（蓝紫青科技色） */
  --accent-blue: #4f8fff;         /* 主蓝 */
  --accent-cyan: #00d4ff;         /* 青色 */
  --accent-purple: #a855f7;       /* 紫色 */
  --accent-pink: #f472b6;         /* 粉色 */

  /* 功能色 */
  --accent-green: #34d399;        /* 成功/正向 */
  --accent-orange: #fb923c;       /* 警告/强调 */
  --accent-red: #f87171;          /* 错误/负向 */
  --accent-yellow: #fbbf24;       /* 高亮 */

  /* 文字 */
  --text-primary: #eeeef2;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;

  /* 边框 */
  --border-color: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(79, 143, 255, 0.35);
  --glass-border: rgba(255, 255, 255, 0.12);

  /* 光晕 */
  --glow-blue: 0 0 60px rgba(79, 143, 255, 0.18);
  --glow-purple: 0 0 60px rgba(168, 85, 247, 0.18);
  --glow-cyan: 0 0 60px rgba(0, 212, 255, 0.18);
  --glow-green: 0 0 60px rgba(52, 211, 153, 0.18);

  /* 圆角 */
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 24px;

  /* 缓动函数 */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 1.2 灵犀翡翠暖色调配色方案

适用于：社交类、生活类、Bot/聊天机器人项目。营造温暖、亲切、有呼吸感的氛围。

```css
:root {
  /* 背景层（深墨绿/深青黑） */
  --bg-primary: #08110f;
  --bg-secondary: #0a1612;
  --bg-card: #0f1d18;
  --bg-card-hover: #14271f;
  --bg-glass: rgba(15, 29, 24, 0.65);

  /* 主色调：翡翠绿 + 琥珀金 + 珊瑚橙 */
  --emerald: #34d399;
  --emerald-deep: #10b981;
  --emerald-soft: #6ee7b7;
  --amber: #fbbf24;
  --amber-deep: #f59e0b;
  --amber-soft: #fcd34d;
  --coral: #fb923c;
  --coral-deep: #f97316;
  --coral-soft: #fdba74;

  /* 辅助色 */
  --mint: #2dd4bf;
  --warm-amber: #f59e0b;
  --rose: #fb7185;
  --cream: #fef3c7;

  /* 文字（带绿色色调） */
  --text-primary: #ecfdf5;
  --text-secondary: #a7f3d0;
  --text-muted: #6ee7b7;
  --text-dim: #4b6358;

  /* 渐变（核心三色暖渐变） */
  --grad-warm: linear-gradient(135deg, #34d399 0%, #fbbf24 50%, #fb923c 100%);
  --grad-emerald: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  --grad-amber: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  --grad-coral: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
  --grad-mint: linear-gradient(135deg, #2dd4bf 0%, #34d399 100%);

  /* 光晕 */
  --glow-emerald: 0 0 40px rgba(52, 211, 153, 0.35);
  --glow-amber: 0 0 40px rgba(251, 191, 36, 0.35);
  --glow-coral: 0 0 40px rgba(251, 146, 60, 0.35);
  --glow-warm: 0 0 60px rgba(251, 191, 36, 0.25);

  /* 阴影 */
  --shadow-soft: 0 10px 40px rgba(0, 0, 0, 0.4);
  --shadow-warm: 0 12px 48px rgba(251, 146, 60, 0.18);
  --shadow-emerald: 0 12px 48px rgba(52, 211, 153, 0.18);

  /* 圆角（比 AOS 更大，更柔和） */
  --radius-sm: 12px;
  --radius-md: 20px;
  --radius-lg: 28px;
  --radius-xl: 36px;
  --radius-full: 999px;
}
```

### 1.3 配色选择原则

| 项目特性 | 推荐配色 | 理由 |
|---------|---------|------|
| 技术框架/开发者工具/AI Agent | 蓝紫科技风 | 冷色调传达专业、未来感，高对比度适合代码展示 |
| 社交/聊天/生活类 Bot | 翡翠暖色调 | 暖色渐变营造亲切感，三色渐变（绿→金→橙）模拟自然光线 |
| 数据/金融类 | 深蓝 + 青色 | 蓝色传达信任，青色用于数据高亮 |
| 创意/设计类 | 紫粉 + 珊瑚 | 高饱和度激发创意感 |
| 教育/儿童类 | 多彩明亮 | 高对比 + 高饱和吸引注意力 |

**核心原则**：
1. **背景永远深色**（#08~#0f 区间），保证内容前景对比度
2. **主色不超过 3 个**，通过明度变化（deep/normal/soft）扩展层次
3. **渐变方向统一**（135deg），形成视觉一致性
4. **文字色带主题色调**（AOS 灰白；灵犀带绿调），强化品牌识别
5. **光晕色与主色同源**，仅降低透明度

### 1.4 字体方案

两个项目共用同一套 Google Fonts 组合：

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+SC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
```

| 字体 | 用途 | 权重范围 |
|------|------|---------|
| `Noto Sans SC` | 中文正文（主字体） | 300/400/500/700/900 |
| `Inter` | 英文/数字（标题、统计数字） | 300/400/500/600/700/800/900 |
| `JetBrains Mono` | 代码、目录名、配置项 | 400/500/600/700 |

```css
body {
  font-family: 'Noto Sans SC', 'Inter', -apple-system, sans-serif;
}
.stat-number, .hero-stat-num {
  font-family: 'Inter', sans-serif;  /* 数字用 Inter */
}
.dir-card-name, .install-code, .config-num {
  font-family: 'JetBrains Mono', monospace;  /* 代码用等宽 */
}
```

---

## 2. 动效技术清单

### 2.1 Aurora 流动背景

**实现方式**：CSS @keyframes + 多个 radial-gradient blob

**核心代码**：
```css
.aurora {
  position: absolute;
  inset: -20%;
  z-index: 0;
  overflow: hidden;
}

.aurora-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.55;
  mix-blend-mode: screen;  /* 关键：混合模式让颜色叠加 */
  will-change: transform;
}

.aurora-blob.b1 {
  width: 50vw; height: 50vw;
  background: radial-gradient(circle, var(--accent-blue), transparent 70%);
  top: 10%; left: 5%;
  animation: aurora-1 18s ease-in-out infinite;
}

@keyframes aurora-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20vw, 10vh) scale(1.15); }
  66% { transform: translate(-10vw, 20vh) scale(0.9); }
}
```

**适用场景**：Hero 区背景，营造流动光晕氛围。需配合 `mix-blend-mode: screen` 让多个 blob 颜色叠加。

### 2.2 Glassmorphism 玻璃拟态

**实现方式**：CSS backdrop-filter

**核心代码**：
```css
.glass-card {
  background: var(--bg-card);  /* 半透明背景 */
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);  /* Safari 必需 */
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

nav {
  background: rgba(8, 8, 13, 0.55);
  backdrop-filter: blur(24px) saturate(180%);
}
```

**适用场景**：导航栏、卡片、徽章、聊天气泡。注意必须加 `-webkit-` 前缀兼容 Safari。

### 2.3 Scroll Reveal 滚动入场

**实现方式**：JS IntersectionObserver + CSS transition

**核心代码**：
```css
.reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s var(--ease-out), transform 0.8s var(--ease-out);
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* 错峰入场（灵犀版，带 scale） */
.reveal {
  opacity: 0;
  transform: translateY(40px) scale(0.96);
  transition: opacity 0.8s ease, transform 0.8s ease;
}
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }
```

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);  // AOS 版：触发后取消观察
    }
  });
}, {
  threshold: 0.12,
  rootMargin: '0px 0px -60px 0px'  /* 提前 60px 触发 */
});

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

**适用场景**：所有 section、卡片、标题的入场动画。`threshold: 0.12` + `rootMargin: -60px` 是经验值，保证元素进入视口 12% 时触发，且提前 60px。

### 2.4 Magnetic Hover 磁吸悬停

**实现方式**：JS mousemove + CSS perspective + rotateX/rotateY

**核心代码**：
```css
.dir-card {
  transform-style: preserve-3d;
  will-change: transform;
  transition: transform 0.3s var(--ease-out);
}
```

```javascript
document.querySelectorAll('[data-magnetic-item]').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    // 计算 rotate 角度（最大 ±6deg）
    const rotateX = ((y - centerY) / centerY) * -6;
    const rotateY = ((x - centerX) / centerX) * 6;
    card.style.transform = 
      `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    // 同时更新光斑位置
    card.style.setProperty('--mx', (x / rect.width * 100) + '%');
    card.style.setProperty('--my', (y / rect.height * 100) + '%');
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});
```

**适用场景**：目录卡片、能力卡片等需要交互感的元素。`perspective(800px)` 是经验值，太小畸变大，太大无立体感。

### 2.5 Number Counter 数字滚动

**实现方式**：JS requestAnimationFrame + easeOutExpo 缓动

**核心代码**：
```html
<div class="stat-number" data-target="30" data-suffix="+">0</div>
```

```javascript
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.target);
      const suffix = el.dataset.suffix || '';
      const duration = 1800;  // 动画时长 ms
      const startTime = performance.now();

      const animate = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // easeOutExpo：开始快，结束慢
        const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const current = Math.round(target * eased);
        el.textContent = current + suffix;
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          el.textContent = target + suffix;  // 确保最终值精确
        }
      };
      requestAnimationFrame(animate);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number').forEach(c => counterObserver.observe(c));
```

**适用场景**：Hero 区统计数据、成就数字。AOS 版额外支持 `data-static="true"` 处理 `∞` 等非数字值。

### 2.6 Cursor Glow 鼠标跟随光晕

**实现方式**：JS requestAnimationFrame + lerp 缓动

**核心代码**：
```css
.cursor-glow {
  position: fixed;
  width: 480px; height: 480px;
  border-radius: 50%;
  background: radial-gradient(circle, 
    rgba(79, 143, 255, 0.12) 0%, 
    rgba(168, 85, 247, 0.06) 35%, 
    transparent 65%);
  pointer-events: none;
  z-index: 1;
  transform: translate(-50%, -50%);
  mix-blend-mode: screen;
  filter: blur(20px);
  will-change: transform;
}

.cursor-dot {
  position: fixed;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
  pointer-events: none;
  z-index: 9999;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.6);
}

/* 触摸设备隐藏 */
@media (hover: none) { 
  .cursor-glow, .cursor-dot { display: none; } 
  body { cursor: auto; }
}
```

```javascript
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let glowX = mouseX, glowY = mouseY;  // 光晕位置（慢）
let dotX = mouseX, dotY = mouseY;    // 小点位置（快）

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

function animateCursor() {
  // lerp 缓动：光晕 0.12（慢），小点 0.35（快）
  glowX += (mouseX - glowX) * 0.12;
  glowY += (mouseY - glowY) * 0.12;
  cursorGlow.style.transform = 
    `translate(${glowX}px, ${glowY}px) translate(-50%, -50%)`;
  
  dotX += (mouseX - dotX) * 0.35;
  dotY += (mouseY - dotY) * 0.35;
  cursorDot.style.transform = 
    `translate(${dotX}px, ${dotY}px) translate(-50%, -50%)`;
  
  requestAnimationFrame(animateCursor);
}
animateCursor();

// 悬停可交互元素时小点放大
document.querySelectorAll('a, button, .dir-card').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursorDot.style.transform += ' scale(2.5)';
  });
});
```

**适用场景**：桌面端全站自定义光标。注意触摸设备必须隐藏，否则影响交互。

### 2.7 渐变文字流动

**实现方式**：CSS background-clip: text + @keyframes background-position

**核心代码**：
```css
.gradient-text {
  background: linear-gradient(135deg, 
    var(--accent-blue) 0%, 
    var(--accent-cyan) 35%, 
    var(--accent-purple) 70%, 
    var(--accent-pink) 100%);
  background-size: 300% 300%;  /* 关键：放大背景才能流动 */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-flow 6s ease infinite;
}

@keyframes gradient-flow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

**适用场景**：Hero 标题、Logo、统计数字、Footer Logo。`background-size: 300% 300%` 是关键，否则无法流动。

### 2.8 横向无限滚动卡片

**实现方式**：CSS @keyframes translateX + 复制一份内容 + mask 渐隐边缘

**核心代码**：
```css
.features-scroll {
  position: relative;
  overflow: hidden;
  mask-image: linear-gradient(90deg, transparent 0%, #000 8%, #000 92%, transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, #000 8%, #000 92%, transparent 100%);
}

.features-track {
  display: flex;
  gap: 24px;
  width: max-content;  /* 关键：让 track 宽度撑开 */
  animation: scrollX 50s linear infinite;
}

.features-scroll:hover .features-track {
  animation-play-state: paused;  /* 悬停暂停 */
}

@keyframes scrollX {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }  /* 关键：移动 -50% */
}
```

```html
<!-- 必须复制一份内容实现无缝循环 -->
<div class="features-track">
  <div class="feature-card">...</div>
  <!-- 第一组卡片 -->
  <div class="feature-card">...</div>
  <!-- 第二组（完全复制第一组） -->
  <div class="feature-card">...</div>
</div>
```

**适用场景**：功能亮点展示、痛点列表。AOS 版因有 gap，用 `translateX(calc(-50% - 9px))` 修正间隙；灵犀版直接 `-50%`。

### 2.9 呼吸感浮动

**实现方式**：CSS @keyframes translateY

**核心代码**：
```css
/* 对比板块呼吸 */
.comparison-col {
  animation: breathe 6s ease-in-out infinite;
}
.comparison-col.after {
  animation-delay: 3s;  /* 错峰，避免同步 */
}

@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 聊天气泡浮动 */
.chat-bubble {
  animation: bubbleFloat 5s ease-in-out infinite;
}

@keyframes bubbleFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 标题呼吸（灵犀版，用 filter） */
.hero-title {
  animation: titleBreath 4s ease-in-out infinite;
}

@keyframes titleBreath {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 30px rgba(251, 191, 36, 0.3)); }
  50% { filter: brightness(1.15) drop-shadow(0 0 50px rgba(251, 146, 60, 0.5)); }
}
```

**适用场景**：对比板块、聊天气泡、标题。多元素同时浮动时必须错峰 `animation-delay`。

### 2.10 SVG 波浪动画

**实现方式**：CSS @keyframes translateX + SVG path + JS 动态变形 path d

**核心代码**：
```css
.hero-wave {
  position: absolute;
  left: 0;
  width: 200%;  /* 关键：宽度 200% 才能平移 -50% */
  height: 120px;
  opacity: 0.5;
}

.hero-wave-1 {
  top: 15%;
  animation: waveMove 20s linear infinite;
}

.hero-wave-2 {
  top: 35%;
  animation: waveMove 28s linear infinite reverse;  /* 反向 */
  opacity: 0.3;
}

@keyframes waveMove {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```

```html
<svg viewBox="0 0 1200 120" preserveAspectRatio="none">
  <!-- path 需要画两倍长度（2400）才能无缝循环 -->
  <path d="M0,60 C150,100 350,20 600,60 C850,100 1050,20 1200,60 
           L2400,60 C2250,100 2050,20 1800,60 C1550,100 1350,20 1200,60 Z" 
        fill="none" stroke="url(#waveGrad1)" stroke-width="2"/>
  <defs>
    <linearGradient id="waveGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="50%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#fb923c"/>
    </linearGradient>
  </defs>
</svg>
```

```javascript
// JS 动态变形 path（让波浪更生动）
const wavePaths = document.querySelectorAll('.hero-wave path');
let waveTime = 0;

function animateWaves() {
  waveTime += 0.005;
  wavePaths.forEach((path, idx) => {
    const offset = idx * 1.5;
    const a = Math.sin(waveTime + offset) * 20;
    const b = Math.cos(waveTime * 0.8 + offset) * 15;
    const d = `M0,60 C${150+a},${100+b} ${350+a},${20-b} 600,60 C${850+a},${100+b} ${1050+a},${20-b} 1200,60 L2400,60 C${2250+a},${100+b} ${2050+a},${20-b} 1800,60 C${1550+a},${100+b} ${1350+a},${20-b} 1200,60 Z`;
    if (idx === 0) path.setAttribute('d', d);  // 仅第一条变形，避免性能问题
  });
  requestAnimationFrame(animateWaves);
}
animateWaves();
```

**适用场景**：Hero 区背景装饰、波浪分隔线。`preserveAspectRatio="none"` 让 SVG 拉伸填满。

### 2.11 心流状态机交互演示

**实现方式**：JS setInterval + class toggle

**核心代码**：
```css
.fsm-state {
  padding: 14px 24px;
  border-radius: var(--radius-full);
  background: rgba(52, 211, 153, 0.08);
  border: 1px solid rgba(52, 211, 153, 0.2);
  transition: all 0.5s ease;
}

.fsm-state.active {
  background: var(--grad-warm);
  color: #08110f;
  border-color: transparent;
  transform: scale(1.08);  /* 激活时放大 */
  box-shadow: var(--glow-amber);
}

.fsm-state.active .fsm-state-dot {
  animation: dotBlink 1s ease-in-out infinite;
}
```

```javascript
const fsmStates = document.querySelectorAll('.fsm-state');
const fsmDesc = document.getElementById('fsmDesc');
const fsmDescriptions = [
  '休眠状态：精力不足，Bot 静默观察，等待唤醒信号',
  '倾听状态：检测到潜在话题，Bot 开始关注对话走向',
  '活跃状态：话题匹配兴趣，Bot 自然介入并参与讨论',
  '兴奋状态：被点名或话题高度契合，Bot 全力响应',
  '疲倦状态：精力接近耗尽，Bot 减少发言，准备休息'
];
let fsmIndex = 0;

function updateFsm() {
  fsmStates.forEach((s, i) => {
    s.classList.toggle('active', i === fsmIndex);
  });
  fsmDesc.textContent = fsmDescriptions[fsmIndex];
  fsmIndex = (fsmIndex + 1) % fsmStates.length;
}

updateFsm();
setInterval(updateFsm, 2800);  /* 2.8s 切换一次 */
```

**适用场景**：状态机演示、流程循环展示、产品特性轮播。

### 2.12 悬浮弹窗（Tooltip）

**实现方式**：CSS tooltip + JS 控制位置（光斑跟随变体）

**核心代码**：
```css
/* 卡片光斑跟随（伪 Tooltip 效果） */
.pain-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at var(--mx, 50%) var(--my, 50%), 
    rgba(248, 113, 113, 0.08), transparent 50%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.pain-card:hover::after { opacity: 1; }
```

```javascript
document.querySelectorAll('.pain-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    card.style.setProperty('--mx', ((e.clientX - rect.left) / rect.width * 100) + '%');
    card.style.setProperty('--my', ((e.clientY - rect.top) / rect.height * 100) + '%');
  });
});
```

**适用场景**：卡片悬停光斑、目录卡片磁吸光斑。通过 CSS 变量 `--mx`/`--my` 传递鼠标位置。

### 2.13 其他辅助动效

#### 铃铛摇摆（灵犀）
```css
@keyframes bellRing {
  0%, 90%, 100% { transform: rotate(0deg); }
  92% { transform: rotate(-12deg); }
  94% { transform: rotate(12deg); }
  96% { transform: rotate(-8deg); }
  98% { transform: rotate(8deg); }
}
```

#### 徽章脉冲（灵犀）
```css
@keyframes badgePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
  50% { box-shadow: 0 0 0 12px rgba(52, 211, 153, 0); }
}
```

#### 聊天气泡入场（灵犀）
```css
@keyframes bubbleIn {
  0% { opacity: 0; transform: translateY(15px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

.chat-bubble:nth-child(1) { animation-delay: 0.2s; }
.chat-bubble:nth-child(2) { animation-delay: 0.5s; }
.chat-bubble:nth-child(3) { animation-delay: 0.8s; }
```

#### 滚动提示箭头（AOS）
```css
@keyframes scroll-arrow {
  0%, 100% { transform: scaleY(1); opacity: 0.5; }
  50% { transform: scaleY(1.5); opacity: 1; }
}
```

#### 有机光晕浮动（灵犀 body::before/after）
```css
body::before {
  content: '';
  position: fixed;
  top: -20%; left: -10%;
  width: 60%; height: 60%;
  background: radial-gradient(circle, rgba(52, 211, 153, 0.12) 0%, transparent 70%);
  filter: blur(80px);
  animation: floatGlow 18s ease-in-out infinite;
}

@keyframes floatGlow {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -30px) scale(1.1); }
  66% { transform: translate(-30px, 40px) scale(0.95); }
}
```

---

## 3. 可直接套用的模板规范

### 3.1 HTML 骨架结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>项目名 — 一句话标语</title>
  <meta name="description" content="项目描述">
  <meta property="og:title" content="项目名">
  <meta property="og:description" content="项目描述">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://...">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>">
  <style>
    /* @import 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+SC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
    /* :root 变量 */
    /* * reset */
    /* body */
    /* 各组件样式 */
  </style>
</head>
<body>
  <!-- 鼠标光晕（可选，仅桌面） -->
  <div class="cursor-glow" id="cursorGlow"></div>
  <div class="cursor-dot" id="cursorDot"></div>

  <!-- 导航栏 -->
  <nav id="nav">...</nav>

  <!-- Hero 区 -->
  <section class="hero">
    <div class="aurora">...</div>  <!-- 或 hero-waves -->
    <div class="hero-content">...</div>
  </section>

  <!-- 分隔线 -->
  <div class="divider"><div class="divider-line"></div></div>

  <!-- 各 Section -->
  <section class="section" id="xxx">
    <div class="section-label reveal">...</div>
    <h2 class="section-title reveal">...</h2>
    <p class="section-desc reveal">...</p>
    <div class="xxx-grid reveal-stagger">...</div>
  </section>

  <!-- Footer -->
  <footer>...</footer>

  <script>
    /* 鼠标光晕、滚动入场、数字滚动、磁吸、平滑滚动等 */
  </script>
</body>
</html>
```

### 3.2 CSS 变量定义模板

见 **1.1** 和 **1.2** 节，直接复制对应配色方案的 `:root` 块即可。

### 3.3 JavaScript 工具函数模板

#### 完整工具函数集合
```javascript
(function () {
  'use strict';

  // ===== 1. 鼠标光晕跟随（lerp 缓动） =====
  const cursorGlow = document.getElementById('cursorGlow');
  const cursorDot = document.getElementById('cursorDot');
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let glowX = mouseX, glowY = mouseY;
  let dotX = mouseX, dotY = mouseY;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animateCursor() {
    glowX += (mouseX - glowX) * 0.12;
    glowY += (mouseY - glowY) * 0.12;
    cursorGlow.style.transform = 
      `translate(${glowX}px, ${glowY}px) translate(-50%, -50%)`;
    dotX += (mouseX - dotX) * 0.35;
    dotY += (mouseY - dotY) * 0.35;
    cursorDot.style.transform = 
      `translate(${dotX}px, ${dotY}px) translate(-50%, -50%)`;
    requestAnimationFrame(animateCursor);
  }
  if (cursorGlow) animateCursor();

  // ===== 2. 导航栏滚动效果 =====
  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });

  // ===== 3. IntersectionObserver 滚动入场 =====
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

  document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => {
    revealObserver.observe(el);
  });

  // ===== 4. 数字滚动（easeOutExpo） =====
  const numberObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        if (el.dataset.static === 'true') {
          el.textContent = el.dataset.count;
          numberObserver.unobserve(el);
          return;
        }
        const target = parseFloat(el.dataset.target || el.dataset.count);
        const suffix = el.dataset.suffix || '';
        if (isNaN(target)) {
          el.textContent = el.dataset.target || el.dataset.count;
          numberObserver.unobserve(el);
          return;
        }
        const duration = 1800;
        const startTime = performance.now();
        function tick(now) {
          const progress = Math.min((now - startTime) / duration, 1);
          const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
          el.textContent = Math.round(target * eased) + suffix;
          if (progress < 1) {
            requestAnimationFrame(tick);
          } else {
            el.textContent = target + suffix;
          }
        }
        requestAnimationFrame(tick);
        numberObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.stat-number, .hero-stat-num').forEach(el => {
    numberObserver.observe(el);
  });

  // ===== 5. 磁吸悬停 =====
  document.querySelectorAll('[data-magnetic-item]').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -6;
      const rotateY = ((x - centerX) / centerX) * 6;
      card.style.transform = 
        `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
      card.style.setProperty('--mx', (x / rect.width * 100) + '%');
      card.style.setProperty('--my', (y / rect.height * 100) + '%');
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });

  // ===== 6. 光斑跟随（卡片） =====
  document.querySelectorAll('[data-spotlight]').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - rect.left) / rect.width * 100) + '%');
      card.style.setProperty('--my', ((e.clientY - rect.top) / rect.height * 100) + '%');
    });
  });

  // ===== 7. 平滑滚动导航（修正导航栏偏移） =====
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId.length < 2) return;
      const target = document.querySelector(targetId);
      if (!target) return;
      e.preventDefault();
      const navHeight = 64;  /* 导航栏高度 */
      const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 10;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ===== 8. 触摸设备隐藏自定义光标 =====
  if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
    if (cursorGlow) cursorGlow.style.display = 'none';
    if (cursorDot) cursorDot.style.display = 'none';
    document.body.style.cursor = 'auto';
  }

  // ===== 9. 移动端导航菜单（灵犀版） =====
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });
  }
})();
```

### 3.4 响应式断点规范

```css
/* ===== 三档断点（灵犀版，更完整） ===== */

/* 平板（≤1024px）：4列→2列，3列→2列 */
@media (max-width: 1024px) {
  .flow-container { grid-template-columns: repeat(2, 1fr); }
  .flow-arrow { display: none; }
  .capabilities-grid { grid-template-columns: repeat(2, 1fr); }
  .install-steps { grid-template-columns: 1fr; gap: 48px; }
  .install-step-num::after { display: none; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
}

/* 手机（≤768px）：2列→1列，显示移动菜单 */
@media (max-width: 768px) {
  .nav-links { display: none; }
  .nav-mobile-toggle { display: block; }
  .nav-links.open {
    display: flex;
    position: absolute;
    top: 100%; left: 0; right: 0;
    flex-direction: column;
    background: rgba(8, 17, 15, 0.95);
    backdrop-filter: blur(20px);
    padding: 20px;
  }
  .hero { padding: 100px 20px 60px; }
  .hero-stats { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-card { padding: 18px 12px; }
  .stat-number { font-size: 28px; }
  .section { padding: 60px 20px; }
  .compare-grid { grid-template-columns: 1fr; }
  .flow-container { grid-template-columns: 1fr; }
  .capabilities-grid { grid-template-columns: 1fr; }
  .platforms { grid-template-columns: 1fr; }
  .config-grid { grid-template-columns: 1fr; }
  .footer-grid { grid-template-columns: 1fr; gap: 32px; }
  .fsm-state { padding: 10px 16px; font-size: 12px; }
}

/* 小手机（≤640px）：AOS 版额外断点 */
@media (max-width: 640px) {
  .nav-links { display: none; }
  .hero-stats { gap: 1.5rem; }
  .hero-stat:not(:last-child)::after { display: none; }
  .section { padding: 4rem 1.5rem; }
  .floating-emoji { display: none; }
  .flow-container { padding: 2rem 1.5rem; }
}

/* 触摸设备（无 hover） */
@media (hover: none) {
  body { cursor: auto; }
  .cursor-glow, .cursor-dot { display: none; }
}
```

---

## 4. 可视化实操技巧

### 4.1 如何实现无缝循环滚动

**核心原理**：复制一份内容 + `translateX(-50%)`

**步骤**：
1. 容器 `overflow: hidden` + `mask-image` 渐隐边缘
2. track 设置 `width: max-content` 撑开宽度
3. **复制一份**所有卡片，让总数翻倍
4. 动画从 `translateX(0)` 到 `translateX(-50%)`，正好移动一半（即第一份的宽度）

**关键代码**：
```css
.features-track {
  display: flex;
  gap: 24px;
  width: max-content;
  animation: scrollX 50s linear infinite;
}

@keyframes scrollX {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```

**坑点**：如果有 `gap`，AOS 版用 `translateX(calc(-50% - 9px))` 修正（9px = gap/2）；灵犀版直接 `-50%` 也可接受（视觉差异极小）。

### 4.2 如何实现玻璃拟态效果

**核心属性**：`backdrop-filter: blur() saturate()`

**注意事项**：
1. **必须加 `-webkit-` 前缀**，否则 Safari 不生效
2. **背景必须半透明**（`rgba` 或 `hsla`），否则看不到模糊效果
3. **`saturate(180%)` 提升饱和度**，让玻璃后的颜色更鲜艳
4. **性能消耗大**，不要全站使用，仅用于导航栏、卡片、徽章

```css
.glass {
  background: rgba(15, 29, 24, 0.65);  /* 半透明 */
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);  /* Safari */
  border: 1px solid rgba(255, 255, 255, 0.12);  /* 玻璃边框 */
}
```

### 4.3 如何实现鼠标跟随光晕

**核心原理**：`requestAnimationFrame` + lerp 线性插值缓动

**lerp 公式**：`current += (target - current) * factor`
- factor 越小，跟随越慢（拖尾感）
- factor 越大，跟随越快（紧跟）

**双元素策略**：
- 大光晕（480px）：factor = 0.12，慢速跟随，营造拖尾
- 小圆点（8px）：factor = 0.35，快速跟随，精准定位

```javascript
function animateCursor() {
  glowX += (mouseX - glowX) * 0.12;  // 慢
  dotX += (mouseX - dotX) * 0.35;    // 快
  requestAnimationFrame(animateCursor);
}
```

**性能优化**：`will-change: transform` 提示浏览器优化合成层。

### 4.4 如何实现数字滚动动画

**核心缓动函数**：`easeOutExpo = 1 - 2^(-10 * progress)`

**特点**：开始快速冲值，结束缓慢逼近，符合视觉预期。

```javascript
const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
const current = Math.round(target * eased);
```

**注意事项**：
1. 动画结束必须强制设置最终值 `el.textContent = target + suffix`，避免浮点误差
2. 用 `performance.now()` 而非 `Date.now()`，精度更高
3. 用 IntersectionObserver 触发，避免页面加载就执行
4. 处理 `∞` 等非数字值：`data-static="true"` 直接显示

### 4.5 如何实现磁吸悬停

**核心计算**：
```javascript
const rotateX = ((y - centerY) / centerY) * -6;  // 鼠标在上→正仰角
const rotateY = ((x - centerX) / centerX) * 6;   // 鼠标在右→正转角
```

**关键点**：
1. `perspective(800px)` 必须写在 transform 字符串里，不能只在父元素
2. `transform-style: preserve-3d` 让子元素保持 3D 空间
3. `rotateX` 取反（`-6`），否则方向反了
4. 最大角度 ±6deg，太大畸变，太小无感
5. `mouseleave` 时清空 transform，让 CSS transition 平滑回弹

### 4.6 如何实现 SVG 波浪动画

**两种方案**：

**方案一：CSS 平移（推荐，性能好）**
- SVG path 画两倍长度（2400）
- 容器 `width: 200%`
- `@keyframes waveMove { translateX(0) → translateX(-50%) }`

**方案二：JS 动态变形 path d（更生动，耗性能）**
```javascript
const a = Math.sin(waveTime) * 20;
const b = Math.cos(waveTime * 0.8) * 15;
const d = `M0,60 C${150+a},${100+b} ${350+a},${20-b} 600,60 ...`;
path.setAttribute('d', d);
```

**波浪分隔线模板**：
```html
<div class="wave-divider">
  <svg viewBox="0 0 1200 80" preserveAspectRatio="none">
    <path d="M0,40 C300,80 600,0 900,40 C1050,60 1150,20 1200,40 L1200,80 L0,80 Z" 
          fill="rgba(52, 211, 153, 0.04)"/>
    <path d="M0,40 C300,80 600,0 900,40 C1050,60 1150,20 1200,40" 
          fill="none" stroke="rgba(251, 191, 36, 0.2)" stroke-width="1"/>
  </svg>
</div>
```

### 4.7 如何实现悬浮弹窗（Tooltip）

**CSS 变量传递鼠标位置**：
```css
.card::after {
  background: radial-gradient(
    circle at var(--mx, 50%) var(--my, 50%), 
    rgba(79, 143, 255, 0.12), 
    transparent 50%
  );
}
```

```javascript
card.addEventListener('mousemove', (e) => {
  const rect = card.getBoundingClientRect();
  card.style.setProperty('--mx', ((e.clientX - rect.left) / rect.width * 100) + '%');
  card.style.setProperty('--my', ((e.clientY - rect.top) / rect.height * 100) + '%');
});
```

**优势**：纯 CSS 渲染光斑，JS 只更新变量，性能极佳。

### 4.8 性能优化注意事项

| 优化项 | 做法 | 原因 |
|-------|------|------|
| `will-change` | 对动画元素加 `will-change: transform` | 提示浏览器创建合成层 |
| `transform` 代替 `top/left` | 所有位移动画用 `transform` | 不触发重排，仅合成 |
| `requestAnimationFrame` | 数字滚动、光晕跟随必用 | 同步刷新率，避免丢帧 |
| `unobserve` | IntersectionObserver 触发后取消观察 | 避免重复触发 |
| 限制 JS 动态变形 | 灵犀波浪仅对第一条 path 变形 | 多 path 变形性能差 |
| `mix-blend-mode: screen` | Aurora blob 叠加 | 比多个 opacity 更高效 |
| `pointer-events: none` | 装饰元素必加 | 避免拦截鼠标事件 |
| 触摸设备降级 | `@media (hover: none)` 隐藏自定义光标 | 移动端无需光晕 |
| `backdrop-filter` 慎用 | 仅用于导航栏、卡片 | 大面积使用导致卡顿 |
| `filter: blur()` 慎用 | Aurora blob 用 80px blur | 大半径 blur 耗 GPU |

---

## 5. 布局组件库

### 5.1 Hero 区模板

```html
<section class="hero">
  <!-- 背景：AOS 用 aurora，灵犀用 hero-waves -->
  <div class="aurora">
    <div class="aurora-blob b1"></div>
    <div class="aurora-blob b2"></div>
    <div class="aurora-blob b3"></div>
    <div class="aurora-blob b4"></div>
  </div>
  <div class="hero-grid"></div>  <!-- 网格背景 -->
  <div class="hero-noise"></div>  <!-- 噪点纹理 -->

  <!-- 浮动装饰 -->
  <span class="floating-emoji e1">🧠</span>

  <div class="hero-content">
    <div class="hero-badge">
      <span class="dot"></span>
      v1.0.0 已发布
    </div>
    <h1 class="hero-title">
      主标题<br><span class="gradient-text">渐变高亮部分</span>
    </h1>
    <p class="hero-subtitle">
      副标题描述，<strong>关键词加粗</strong>
    </p>
    <div class="hero-actions">
      <a href="#start" class="btn btn-primary">主按钮</a>
      <a href="#" class="btn btn-secondary">次按钮</a>
    </div>
    <div class="hero-stats">
      <div class="hero-stat">
        <div class="hero-stat-num" data-count="10">0</div>
        <div class="hero-stat-label">标签</div>
      </div>
    </div>
  </div>

  <div class="scroll-hint">Scroll<span class="arrow"></span></div>
</section>
```

### 5.2 导航栏模板

**AOS 版（简洁，无移动菜单）**：
```html
<nav id="nav">
  <a href="#" class="nav-logo">
    <span class="logo-orb"></span>
    <span class="g">LOGO</span>
  </a>
  <ul class="nav-links">
    <li><a href="#xxx">导航项</a></li>
    <li><a href="#" class="nav-cta">CTA 按钮</a></li>
  </ul>
</nav>
```

**灵犀版（带移动菜单）**：
```html
<nav class="nav" id="nav">
  <div class="nav-inner">
    <a href="#" class="nav-logo">
      <span class="nav-logo-icon">🔔</span>
      <span class="nav-logo-text">灵犀</span>
    </a>
    <div class="nav-links" id="navLinks">
      <a href="#features" class="nav-link">功能</a>
      <a href="#" class="nav-cta">GitHub</a>
    </div>
    <button class="nav-mobile-toggle" id="navToggle">☰</button>
  </div>
</nav>
```

### 5.3 卡片网格模板

```html
<div class="ability-grid reveal-stagger">
  <div class="ability-card">
    <div class="ability-icon">🧠</div>
    <div class="ability-title">卡片标题</div>
    <div class="ability-analogy">→ 类比说明</div>
    <div class="ability-desc">卡片描述文字</div>
  </div>
  <!-- 更多卡片 -->
</div>
```

```css
.ability-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
@media (max-width: 768px) { .ability-grid { grid-template-columns: 1fr; } }

.ability-card {
  background: var(--bg-card);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 2.5rem 1.8rem;
  transition: transform 0.4s var(--ease-spring);
}
.ability-card:hover { transform: translateY(-8px); }
```

### 5.4 横向滚动模板

```html
<div class="features-scroll">
  <div class="features-track">
    <!-- 第一组 -->
    <div class="feature-card">
      <div class="feature-icon">🎯</div>
      <h3 class="feature-title">标题</h3>
      <p class="feature-desc">描述</p>
    </div>
    <!-- ...更多卡片... -->
    <!-- 第二组（完全复制第一组，实现无缝循环） -->
    <div class="feature-card">...</div>
  </div>
</div>
```

### 5.5 对比板块模板

```html
<div class="compare-grid">
  <div class="compare-col before reveal">
    <div class="compare-header">
      <span class="compare-emoji">😐</span>
      <h3 class="compare-title">没有 XXX</h3>
    </div>
    <div class="chat-bubble user">
      <div class="chat-meta">用户 · 14:02</div>
      消息内容
    </div>
    <div class="chat-bubble bot-cold">
      <div class="chat-meta">Bot · 14:02</div>
      （无响应）
    </div>
  </div>

  <div class="compare-col after reveal reveal-delay-1">
    <div class="compare-header">
      <span class="compare-emoji">✨</span>
      <h3 class="compare-title">有了 XXX</h3>
    </div>
    <div class="chat-bubble bot">
      <div class="chat-meta">灵犀 · 14:02</div>
      响应内容
    </div>
  </div>
</div>
```

### 5.6 流程图模板

**AOS 版（纵向时间线）**：
```html
<div class="flow-container reveal">
  <div class="flow-steps">
    <div class="flow-step">
      <div class="flow-step-indicator">
        <div class="flow-step-num" style="background:linear-gradient(135deg,#4f8fff,#3b82f6);">1</div>
        <div class="flow-step-line"></div>
      </div>
      <div class="flow-step-content">
        <div class="flow-step-title">🔍 步骤标题</div>
        <div class="flow-step-desc">步骤描述</div>
        <span class="flow-step-tag" style="background:rgba(79,143,255,0.12);color:var(--accent-blue);">标签</span>
      </div>
    </div>
  </div>
</div>
```

**灵犀版（横向卡片 + 箭头）**：
```html
<div class="flow-container">
  <div class="flow-step reveal">
    <div class="flow-num">1</div>
    <div class="flow-icon">📨</div>
    <h3 class="flow-title">消息到达</h3>
    <p class="flow-desc">描述</p>
    <div class="flow-arrow">→</div>
  </div>
</div>
```

### 5.7 表格模板

```html
<table class="compare-table reveal">
  <thead>
    <tr>
      <th>对比维度</th>
      <th>AOS</th>
      <th>传统方案</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>技术依赖</td>
      <td>纯文件系统</td>
      <td>需要安装框架</td>
    </tr>
  </tbody>
</table>
```

```css
.compare-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--bg-card);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.compare-table thead th {
  background: rgba(255, 255, 255, 0.03);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  border-bottom: 1px solid var(--border-color);
}
.compare-table tbody td {
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}
.compare-table tbody tr:hover td {
  background: rgba(79, 143, 255, 0.03);
}
.compare-table tbody tr:last-child td { border-bottom: none; }
```

### 5.8 Footer 模板

**AOS 版（简洁居中）**：
```html
<footer>
  <div class="footer-logo"><span class="g">AOS</span></div>
  <div class="footer-desc">一句话描述</div>
  <div class="footer-links">
    <a href="#">GitHub</a>
    <a href="#">文档</a>
    <a href="#">协议</a>
  </div>
</footer>
```

**灵犀版（多列网格 + 波浪顶部）**：
```html
<footer class="footer">
  <div class="footer-wave">
    <svg viewBox="0 0 1200 60" preserveAspectRatio="none">
      <path d="M0,30 C300,60 600,0 900,30 C1050,45 1150,15 1200,30 L1200,60 L0,60 Z" 
            fill="var(--bg-secondary)"/>
    </svg>
  </div>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="footer-logo">...</div>
        <p class="footer-desc">...</p>
        <span class="footer-license">MIT License</span>
      </div>
      <div>
        <h4 class="footer-col-title">文档</h4>
        <ul class="footer-links">...</ul>
      </div>
      <div>
        <h4 class="footer-col-title">资源</h4>
        <ul class="footer-links">...</ul>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copy">© 2026 项目名</div>
      <div class="footer-social">...</div>
    </div>
  </div>
</footer>
```

---

## 6. 经验教训

### 6.1 常见坑点

| 坑点 | 现象 | 解决方案 |
|------|------|---------|
| `backdrop-filter` Safari 不生效 | 玻璃拟态在 Safari 失效 | 必须加 `-webkit-backdrop-filter` 前缀 |
| `background-clip: text` 渐变不流动 | 文字渐变静止不动 | `background-size: 300% 300%` + `@keyframes background-position` |
| 横向滚动有缝隙 | 卡片间出现闪烁白缝 | 有 gap 时用 `translateX(calc(-50% - gap/2))` 修正 |
| 磁吸方向反了 | 鼠标向上，卡片却向下仰 | `rotateX` 取反：`((y - centerY) / centerY) * -6` |
| 数字滚动浮点误差 | 最终值不是整数 | 动画结束强制 `el.textContent = target + suffix` |
| IntersectionObserver 重复触发 | 元素反复出入视口时动画重播 | 触发后 `observer.unobserve(el)` |
| 自定义光标挡点击 | 光标元素拦截鼠标事件 | `pointer-events: none` 必加 |
| 移动端光标残留 | 触摸设备显示自定义光标 | `@media (hover: none)` 隐藏 + JS 检测 `ontouchstart` |
| SVG 波浪不拉伸 | 波浪两端有空白 | `preserveAspectRatio="none"` + path 画两倍长度 |
| `mix-blend-mode` 失效 | Aurora 颜色不叠加 | 父元素不能有 `opacity`，否则混合模式失效 |

### 6.2 浏览器兼容性注意

| 特性 | Chrome | Firefox | Safari | Edge | 兼容方案 |
|------|--------|---------|--------|------|---------|
| `backdrop-filter` | ✅ 76+ | ✅ 103+ | ✅（需 `-webkit-`） | ✅ | 加 `-webkit-` 前缀 |
| `background-clip: text` | ✅（需 `-webkit-`） | ✅ 49+ | ✅（需 `-webkit-`） | ✅ | 加 `-webkit-` 前缀 |
| `mix-blend-mode` | ✅ | ✅ | ✅ | ✅ | 父元素避免 `opacity` |
| `mask-image` | ✅（需 `-webkit-`） | ✅ 53+ | ✅（需 `-webkit-`） | ✅ | 加 `-webkit-` 前缀 |
| IntersectionObserver | ✅ | ✅ | ✅ | ✅ | IE 不支持，需 polyfill |
| `clamp()` | ✅ 79+ | ✅ 75+ | ✅ 13.1+ | ✅ | 旧浏览器用 `@media` 替代 |
| CSS 变量 | ✅ 49+ | ✅ 31+ | ✅ 9.1+ | ✅ | IE 不支持 |

### 6.3 移动端适配要点

1. **断点策略**：1024px（平板）→ 768px（手机）→ 640px（小手机）
2. **网格降列**：4列→2列→1列，3列→2列→1列
3. **导航栏**：768px 以下隐藏链接，显示汉堡菜单
4. **自定义光标**：`@media (hover: none)` 隐藏，恢复 `cursor: auto`
5. **浮动装饰**：640px 以下隐藏 `floating-emoji`，避免遮挡内容
6. **Hero 区**：减小 padding（`100px 20px 60px`），缩小统计数字（`28px`）
7. **流程图箭头**：768px 以下隐藏 `flow-arrow`
8. **触摸交互**：磁吸悬停在触摸设备无意义，但不必特意禁用（不触发 mousemove）
9. **视口设置**：`<meta name="viewport" content="width=device-width, initial-scale=1.0">`
10. **字号下限**：正文不小于 12px，标题用 `clamp()` 自适应

### 6.4 性能优化建议

1. **动画优先级**：`transform` > `opacity` > `filter` > `top/left`
2. **合成层提示**：动画元素加 `will-change: transform`
3. **观察者清理**：IntersectionObserver 触发后 `unobserve`
4. **限制 JS 变形**：灵犀波浪仅对第一条 path 动态变形，其余用 CSS 平移
5. **图片优化**：用 SVG 代替 PNG，矢量且小
6. **字体优化**：`@import` 只加载需要的权重，不加载全量
7. **避免大面积 blur**：`backdrop-filter` 仅用于导航栏和卡片，不全站使用
8. **`requestAnimationFrame`**：所有 JS 动画必用，同步刷新率
9. **触摸设备降级**：隐藏光晕、禁用磁吸，减少 GPU 负担
10. **CSS 动画 > JS 动画**：能用 `@keyframes` 就不用 JS，浏览器可优化

---

## 附录：两个项目网站对照表

| 维度 | AOS 网站 | 灵犀网站 |
|------|---------|---------|
| 配色风格 | 蓝紫科技风（冷色） | 翡翠暖色调（暖色） |
| 主背景 | `#08080d`（深空黑） | `#08110f`（深墨绿） |
| 主色 | 蓝 `#4f8fff` + 紫 `#a855f7` | 翡翠 `#34d399` + 琥珀 `#fbbf24` + 珊瑚 `#fb923c` |
| Hero 背景 | Aurora 流动 blob | SVG 波浪 + 有机光晕 |
| 自定义光标 | ✅ 双层（光晕+小点） | ❌ 原生光标 |
| 磁吸悬停 | ✅ 目录卡片 | ❌ 无 |
| 横向滚动 | ✅ 痛点卡片 | ✅ 功能亮点 |
| 数字滚动 | ✅ easeOutExpo | ✅ easeOutExpo |
| 心流状态机 | ❌ 无 | ✅ setInterval 循环 |
| SVG 波浪 | ❌ 无 | ✅ 三层波浪 + 动态变形 |
| 玻璃拟态 | ✅ 大量使用 | ✅ 大量使用 |
| 移动端菜单 | ❌ 直接隐藏链接 | ✅ 汉堡菜单展开 |
| Footer | 简洁居中 | 多列网格 + 波浪顶部 |
| 圆角 | 10/14/20/24px | 12/20/28/36px（更大更柔） |
| 缓动函数 | `cubic-bezier(0.16, 1, 0.3, 1)` | `ease` |

---

**文档版本**：v1.0  
**创建日期**：2026-06-22  
**维护规则**：新增动效或配色方案时，在对应章节追加并更新版本号；删除时保留变更注释  
**引用路径**：本文档为唯一参考源，其他文档引用请使用路径 `09_REFERENCE/web/web-template-specification.md`
