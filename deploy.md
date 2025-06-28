# 📚 YOLOv8课程设计报告部署指南

本文档详细介绍如何将这个Docsify报告部署到GitHub Pages，实现在线访问。

## 🚀 部署到GitHub Pages

### 步骤1：创建GitHub仓库

1. **登录GitHub**
   - 访问 [GitHub.com](https://github.com)
   - 登录你的GitHub账户

2. **创建新仓库**
   - 点击右上角的 `+` 按钮
   - 选择 `New repository`
   - 仓库名称建议：`yolov8-course-design-report`
   - 描述：`YOLOv8目标检测课程设计报告 - 基于PyTorch和Flask的完整实现`
   - 设置为 **Public**（这样才能使用GitHub Pages）
   - **不要**勾选 "Add a README file"（我们已经有了）
   - 点击 `Create repository`

### 步骤2：推送代码到GitHub

在你的本地终端中执行以下命令：

```bash
# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/yolov8-course-design-report.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

### 步骤3：启用GitHub Pages

1. **进入仓库设置**
   - 在你的GitHub仓库页面，点击 `Settings` 标签

2. **配置GitHub Pages**
   - 在左侧菜单中找到 `Pages`
   - 在 "Source" 部分选择 `Deploy from a branch`
   - Branch选择 `main`
   - Folder选择 `/ (root)`
   - 点击 `Save`

3. **等待部署**
   - GitHub会自动部署你的站点
   - 通常需要几分钟时间
   - 部署完成后会显示访问链接

### 步骤4：访问在线报告

部署完成后，你的报告将在以下地址可访问：
```
https://YOUR_USERNAME.github.io/yolov8-course-design-report/
```

## 🔧 本地开发和预览

### 本地预览方法1：使用Python内置服务器

```bash
# 在项目目录下运行
python -m http.server 3000

# 然后访问 http://localhost:3000
```

### 本地预览方法2：使用docsify-cli

```bash
# 安装docsify-cli
npm install -g docsify-cli

# 启动本地服务器
docsify serve .

# 默认访问 http://localhost:3000
```

### 本地预览方法3：使用Live Server (VS Code)

1. 在VS Code中安装 `Live Server` 扩展
2. 右键点击 `index.html`
3. 选择 `Open with Live Server`

## 📝 更新文档

### 更新内容

当你需要更新文档内容时：

1. **修改Markdown文件**
   - 编辑 `chapter*.md` 文件
   - 修改 `README.md` 或 `_sidebar.md`

2. **提交更改**
   ```bash
   git add .
   git commit -m "更新：具体的修改内容描述"
   git push origin main
   ```

3. **自动部署**
   - GitHub Pages会自动检测到更改
   - 几分钟后更新就会生效

### 添加新章节

1. **创建新的Markdown文件**
   ```bash
   # 例如添加第七章
   touch chapter7.md
   ```

2. **更新侧边栏**
   - 编辑 `_sidebar.md`
   - 添加新章节的链接

3. **提交并推送**
   ```bash
   git add .
   git commit -m "添加第七章：新内容"
   git push origin main
   ```

## 🎨 自定义配置

### 修改主题样式

1. **编辑index.html**
   - 修改 `index.html` 中的主题配置
   - 更改颜色、字体等样式

2. **添加自定义CSS**
   ```html
   <!-- 在index.html的<head>中添加 -->
   <style>
   .sidebar {
     /* 自定义侧边栏样式 */
   }
   </style>
   ```

### 修改Docsify配置

在 `index.html` 中修改 `window.$docsify` 配置：

```javascript
window.$docsify = {
  name: '你的项目名称',
  repo: 'https://github.com/YOUR_USERNAME/your-repo-name',
  // 其他配置...
}
```

## 🔍 SEO优化

### 添加元信息

在 `index.html` 的 `<head>` 中添加：

```html
<meta name="description" content="YOLOv8目标检测课程设计报告，详细介绍了基于PyTorch和Flask的完整实现过程">
<meta name="keywords" content="YOLOv8,目标检测,PyTorch,Flask,课程设计,深度学习">
<meta name="author" content="你的姓名">

<!-- Open Graph标签 -->
<meta property="og:title" content="YOLOv8课程设计报告">
<meta property="og:description" content="基于PyTorch和Flask的YOLOv8目标检测系统完整实现">
<meta property="og:type" content="website">
<meta property="og:url" content="https://YOUR_USERNAME.github.io/yolov8-course-design-report/">
```

## 📊 访问统计

### 添加Google Analytics

1. **创建Google Analytics账户**
2. **获取跟踪ID**
3. **在index.html中添加跟踪代码**

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

## 🚨 常见问题解决

### 问题1：GitHub Pages显示404

**解决方案**：
- 确保仓库是Public
- 检查GitHub Pages设置
- 确认index.html在根目录

### 问题2：Mermaid图表不显示

**解决方案**：
- 检查网络连接
- 确认Mermaid插件配置正确
- 尝试刷新浏览器缓存

### 问题3：中文字符显示异常

**解决方案**：
- 确保所有文件都是UTF-8编码
- 检查index.html中的charset设置

### 问题4：侧边栏链接跳转失败

**解决方案**：
- 检查_sidebar.md中的链接格式
- 确认文件名和章节标题匹配

## 📞 技术支持

如果遇到其他问题，可以：

1. **查看GitHub Pages文档**：https://docs.github.com/en/pages
2. **查看Docsify文档**：https://docsify.js.org/
3. **检查仓库的Actions标签页**：查看部署日志

---

🎉 **恭喜！你的YOLOv8课程设计报告现在可以在线访问了！**

记得在报告中包含这个在线链接，让老师和同学们都能方便地查看你的完整报告。 