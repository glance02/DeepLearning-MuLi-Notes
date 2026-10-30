# 学习网站部署与更新

入口：<https://glance02.xyz/deep-learning/>，首页跳转至手边册。

## 发布内容

构建保留 `lessons/` 和 `reference/` 中的 HTML，转换斋藤笔记目录中的 Markdown，并沿用手边册样式。笔记内公式使用本地托管的 MathJax 3.2.2 SVG 渲染器；表格、代码块和章节目录由固定版本的 Python-Markdown 与 PyMdown Extensions 生成。

仅在输出目录中把已发布 Markdown 的链接改成 HTML。引用的 PDF、Python 源码、Notebook 和图片复制到相同相对位置；指向未发布内容或目录的链接转到 GitHub。Markdown 源文件不变，李沐笔记、Git 元数据、Obsidian 状态及无关数据文件不发布。Notebook 仅供下载。

MathJax 来源：`https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js`；许可证与脚本一起保存在 `assets/vendor/mathjax/`，浏览器不依赖外部 CDN。

## 本地构建

```powershell
python -m venv .site-venv
.site-venv/Scripts/python.exe -m pip install -r deploy/requirements.txt
.site-venv/Scripts/python.exe scripts/build_site.py --output dist/preview
.site-venv/Scripts/python.exe tests/test_site.py -v
```

输出必须使用空目录。构建完成后自动检查站内文件链接、锚点和资源，`build.json` 记录对应提交与检查结果。虚拟环境、测试目录和构建结果均已忽略。

## myserver 目录与首次安装

- `/srv/deep-learning/repo`：只读使用的 `main` 分支工作区，禁止在服务器直接修改已跟踪文件。
- `/srv/deep-learning/venv`：独立 Python 环境。
- `/srv/deep-learning/releases`：生成结果；`current`、`previous` 分别指向当前和上一版。
- `/var/www/myhtml/deep-learning`：固定链接到 `/srv/deep-learning/current`。

站点运行在现有 Ubuntu 24.04、Nginx HTTPS 入口上，不增加监听端口。以下操作由管理员逐条执行；首次安装前应确认用户名和目标路径尚未使用。

```bash
useradd --system --user-group --home-dir /srv/deep-learning --shell /usr/sbin/nologin deep-learning
install -d -o deep-learning -g deep-learning -m 755 /srv/deep-learning
runuser -u deep-learning -- git -c http.proxy=http://127.0.0.1:7890 clone --depth 1 --single-branch --branch main https://github.com/glance02/DeepLearning-MuLi-Notes.git /srv/deep-learning/repo
runuser -u deep-learning -- git -C /srv/deep-learning/repo config http.proxy http://127.0.0.1:7890
runuser -u deep-learning -- python3 -m venv /srv/deep-learning/venv
runuser -u deep-learning -- env HTTPS_PROXY=http://127.0.0.1:7890 /srv/deep-learning/venv/bin/python -m pip install -r /srv/deep-learning/repo/deploy/requirements.txt
install -m 644 /srv/deep-learning/repo/deploy/deep-learning-update.service /etc/systemd/system/deep-learning-update.service
install -m 644 /srv/deep-learning/repo/deploy/deep-learning-update.timer /etc/systemd/system/deep-learning-update.timer
systemctl daemon-reload
systemctl start deep-learning-update.service
ln -s /srv/deep-learning/current /var/www/myhtml/deep-learning
install -m 644 /srv/deep-learning/repo/deploy/nginx-deep-learning.conf /etc/nginx/snippets/deep-learning.conf
python3 /srv/deep-learning/repo/deploy/configure_nginx.py
systemctl enable --now deep-learning-update.timer
```

仓库目前无需 GitHub 登录即可通过 HTTPS 拉取。服务器直连 GitHub 曾超时，因此仅在该仓库与该更新任务中使用现有本机代理，不改全局 Git 或代理配置。Git 拉取及 Python 包安装依赖代理服务可用。

`configure_nginx.py` 只在已核实的域名 HTTPS server 块插入 include，并备份原配置；`nginx -t` 失败会恢复原配置，不 reload。现有域名证书、其他站点和 HTTP 到 HTTPS 跳转沿用。

## 后续更新与维护

本地修改后需 **commit 并 push 到 GitHub main**。服务器每天北京时间 **04:00** 快进拉取，无新提交则跳过构建。服务器错过运行时间时，systemd 会在恢复后补跑。新结果通过文件及锚点检查后才原子切换软链接；失败保留当前网站。网页使用 `no-cache`，刷新时向服务器核实新版本。

手动更新、查看任务和日志：

```bash
sudo systemctl start deep-learning-update.service
systemctl list-timers deep-learning-update.timer
journalctl -u deep-learning-update.service -n 60 --no-pager
```

强制重新构建同一提交：

```bash
sudo -u deep-learning /srv/deep-learning/venv/bin/python /srv/deep-learning/repo/scripts/update_site.py --force
```

回退到上一版（再次执行可切回；下一次正常更新仍会发布 main）：

```bash
sudo -u deep-learning /srv/deep-learning/venv/bin/python /srv/deep-learning/repo/scripts/update_site.py --rollback
```

自动更新失败时先查日志：网络失败恢复代理后重试；工作区有改动时先检查和保存改动，不执行强制覆盖；构建报告断链时修复源文件并 push。普通内容变更不需 reload Nginx。修改 systemd 或 Nginx 的部署配置后，需要由管理员重新安装相应配置并验证后启用。

Linux 上可运行全部测试（包含软链接切换和仅保留两版的验证）：

```bash
sudo -u deep-learning /srv/deep-learning/venv/bin/python /srv/deep-learning/repo/tests/test_site.py -v
```
