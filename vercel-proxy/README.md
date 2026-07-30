# 写代理部署指南

## 问题
浏览器无法直接访问 `api.github.com`（被墙），导致数据无法写入 GitHub。

## 解决方案
部署一个云端代理，转发浏览器的写入请求到 GitHub API。

## Vercel 部署（免费，推荐）

### 步骤 1：注册 Vercel
1. 打开 https://vercel.com
2. 点击 "Sign Up" → 用 GitHub 账号登录（同一账号）
3. 授权 Vercel 访问你的 GitHub

### 步骤 2：导入项目
1. 在 Vercel 控制台点 "Add New" → "Project"
2. 选择你的 GitHub 仓库 `yangwenhui-ywh/-`
3. **Root Directory** 设为 `vercel-proxy`
4. **Framework Preset** 选 "Other"
5. 点 "Deploy"

### 步骤 3：设置环境变量
1. 部署完成后，进入项目 Settings → Environment Variables
2. 添加变量：
   - Name: `GITHUB_TOKEN`
   - Value: （填入你的 GitHub Personal Access Token，需 repo 权限）
3. 点 "Save"
4. 回到 Deployments，点最新部署旁的 "..." → "Redeploy"

### 步骤 4：获取代理地址
部署成功后，Vercel 会给你一个地址，类似：
```
https://xxx-xxx.vercel.app
```

### 步骤 5：配置看板
1. 打开看板：https://yangwenhui-ywh.github.io/-/
2. 在顶部设置区域，找到"代理地址"输入框
3. 输入：`https://xxx-xxx.vercel.app/api/write`
4. 点击"保存"
5. 看到"代理已连接"提示即成功

## 其他平台

### Render.com
1. 注册 https://render.com
2. New → Web Service → 连接 GitHub 仓库
3. Build Command: 留空
4. Start Command: `python proxy/proxy.py`
5. 环境变量: `GITHUB_TOKEN=ghp_xxx`
6. 部署后获取 `https://xxx.onrender.com/api/write`

### Railway.app
1. 注册 https://railway.app
2. New Project → Deploy from GitHub repo
3. 添加环境变量 `GITHUB_TOKEN`
4. Start command: `python proxy/proxy.py`
5. 获取公网 URL

## 代理 API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/write` | 写入数据到 GitHub |
| POST | `/api/github-proxy` | 同上（别名） |
| OPTIONS | `*` | CORS 预检 |

### 请求格式
```json
{
  "modules": { ... },
  "updatedBy": "用户名",
  "work段": "工段名",
  "班组": "班组名",
  "confirmed": { ... }
}
```

### 响应格式
```json
{ "ok": true, "sha": "abc123..." }
```
