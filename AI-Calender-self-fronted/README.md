# AI Calendar 前端

基于 React + TypeScript 的智能日历助手前端应用。

## 设计特色

### 🎨 黑白手绘风格
- **极简配色**：纯黑白色调，经典优雅
- **手绘线条**：不规则边框圆角，模拟手绘效果
- **装饰元素**：手绘圆圈、虚线分隔、胶带效果

### 💧 液态玻璃效果
- **流动背景**：缓慢变形的液态 blob 背景动画
- **玻璃模糊**：backdrop-blur 营造磨砂玻璃质感
- **微妙光泽**：内阴影和外阴影叠加创造层次感

### ✨ 交互体验
- **手绘动画**：按钮和卡片有轻微的手绘摇摆效果
- **纸质感**：添加噪点纹理模拟纸张质感
- **堆叠层次**：卡片阴影偏移营造手绘叠加感

## 技术栈

- React 19 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- shadcn/ui
- Lucide React

## 快速开始

```bash
# 安装依赖
npm install

# 配置 API 地址
cp .env.example .env

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 设计风格说明

### 手绘边框 (Sketchy Border)
```css
.sketchy-border {
  border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;
  border: 2px solid currentColor;
}
```

### 液态玻璃 (Liquid Glass)
```css
.liquid-glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### 流动 Blob 动画
```css
@keyframes liquid-flow {
  0%, 100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
  50% { border-radius: 50% 60% 30% 60% / 30% 60% 70% 40%; }
}
```

## 使用指南

### 查看日程
- 左右滑动或点击箭头查看不同日期
- 点击任意日期卡片展开详情

### 创建日程
在底部对话框输入：
- "帮我添加明天下午3点的团队会议"
- "下周二要有一个项目评审"

### 编辑/删除
- 点击卡片进入详情视图
- 悬停事件显示编辑/删除按钮

## API 配置

确保后端服务运行在 http://localhost:8000，或在 `.env` 中修改：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```
