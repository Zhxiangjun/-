# ============================================================================
# 智慧园区平台 · 一键基础环境安装脚本（Windows 端，可重复执行）
# 文件：环境配置/scripts/install-base.ps1
# 适用：台式机（主力开发机）、笔记本 1（服务宿主）、笔记本 2（客户端）
# 用法：以【管理员身份】打开 PowerShell 7，执行：
#         Set-ExecutionPolicy -Scope Process Bypass -Force
#         .\install-base.ps1                    # 交互式选择机器角色
#         .\install-base.ps1 -Role dev          # 台式机：全量（含 Docker/Python 双版本）
#         .\install-base.ps1 -Role server       # 笔记本 1：服务宿主
#         .\install-base.ps1 -Role client       # 笔记本 2：客户端
# 说明：脚本只做“可自动化”的部分；WSL2 安装、Docker Desktop 图形设置、
#       NVIDIA 驱动、VS Code 扩展等需按手册对应章节手工完成。
# ============================================================================

[CmdletBinding()]
param(
    [ValidateSet('dev', 'server', 'client')]
    [string]$Role = '',
    [switch]$SkipWinget,       # 跳过软件批量安装（仅做环境变量与配置）
    [switch]$DryRun            # 只打印将要执行的动作，不真正修改系统
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ---------------------------------------------------------------- 工具函数
function Write-Step($msg) { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  [ OK ] $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  [FAIL] $msg" -ForegroundColor Red }

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-Action([string]$desc, [scriptblock]$action) {
    if ($DryRun) { Write-Host "  [DRY ] $desc" -ForegroundColor DarkGray; return }
    try { & $action; Write-Ok $desc }
    catch { Write-Warn2 "$desc —— $($_.Exception.Message)" }
}

# ---------------------------------------------------------------- 前置检查
Write-Host "==============================================================" -ForegroundColor Magenta
Write-Host " 智慧园区平台 · Windows 基础环境安装脚本" -ForegroundColor Magenta
Write-Host " 角色: $(if($Role){$Role}else{'未指定（将交互选择）'})   DryRun: $DryRun" -ForegroundColor Magenta
Write-Host "==============================================================" -ForegroundColor Magenta

if (-not (Test-Admin)) {
    Write-Err '请以管理员身份运行本脚本（右键 PowerShell → 以管理员身份运行）'
    exit 1
}
Write-Ok '管理员权限检查通过'

if (-not $Role) {
    Write-Host "`n请选择本机角色：" -ForegroundColor Yellow
    Write-Host '  1 = dev     台式机（主力：AI 训练 + 全栈开发 + Docker）'
    Write-Host '  2 = server  笔记本 1（服务宿主 / 演示机）'
    Write-Host '  3 = client  笔记本 2（客户端 / 设备联调）'
    $sel = Read-Host '输入 1/2/3'
    $Role = switch ($sel) { '1' { 'dev' } '2' { 'server' } '3' { 'client' } default { 'dev' } }
    Write-Ok "已选择角色：$Role"
}

# 记录关键环境信息，便于归档与排查
$report = [ordered]@{
    '执行时间'   = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    '计算机名'   = $env:COMPUTERNAME
    '角色'       = $Role
    '操作系统'   = (Get-CimInstance Win32_OperatingSystem).Caption
    '系统版本'   = (Get-CimInstance Win32_OperatingSystem).Version
    'CPU'        = (Get-CimInstance Win32_Processor).Name
    '逻辑核心'   = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
    '内存GB'     = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
}

Write-Host "`n---- 本机信息 ----"
$report.GetEnumerator() | ForEach-Object { "  {0,-10}: {1}" -f $_.Key, $_.Value }

# ---------------------------------------------------------------- 1. 虚拟化
Write-Step '1/9 检查 CPU 虚拟化（WSL2 与 Docker 的前置条件）'
$virt = (Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled
if ($virt -eq $true) { Write-Ok 'CPU 虚拟化已在 BIOS/UEFI 中启用' }
else { Write-Warn2 '虚拟化未启用或无法读取：请重启进入 BIOS 开启 Intel VT-x（Intel）或 SVM Mode（AMD）后重新运行本脚本' }

# ---------------------------------------------------------------- 2. winget 与软件安装
Write-Step '2/9 通过 winget 安装基础软件'
$hasWinget = [bool](Get-Command winget -ErrorAction SilentlyContinue)
if (-not $hasWinget) { Write-Warn2 'winget 不可用：请先从 Microsoft Store 安装“应用安装程序”，或到官网手工下载安装包' }
else {
    $common = @(
        'Git.Git', 'Microsoft.VisualStudioCode', 'Microsoft.PowerShell',
        'Microsoft.WindowsTerminal', 'OpenJS.NodeJS.LTS', 'dbeaver.dbeaver',
        'OBSProject.OBSStudio'
    )
    $devOnly = @('Python.Python.3.11', 'Docker.DockerDesktop')
    $list = if ($Role -eq 'client') { $common } else { $common + $devOnly }
    if ($Role -eq 'dev') { $list += 'Python.Python.3.12' }

    if ($SkipWinget) { Write-Warn2 '已指定 -SkipWinget，跳过软件安装' }
    else {
        foreach ($pkg in $list) {
            Invoke-Action "安装 $pkg" {
                winget install --id $pkg -e --silent `
                    --accept-source-agreements --accept-package-agreements | Out-Null
            }
        }
        Write-Warn2 '个别软件（Docker Desktop、Python）安装后需重启或重新登录才会写入 PATH'
    }
}

# ---------------------------------------------------------------- 3. UTF-8 与语言环境
Write-Step '3/9 配置 UTF-8 编码与中文环境（避免乱码与 Python 输出报错）'
Invoke-Action '设置系统区域为 UTF-8（chcp 65001 持久化）' {
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage' `
        -Name 'ACP' -Value '65001' -Force
}
Invoke-Action '设置用户环境变量 PYTHONUTF8=1' {
    [Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
    $env:PYTHONUTF8 = '1'
}
Invoke-Action '设置用户环境变量 PYTHONIOENCODING=utf-8' {
    [Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')
    $env:PYTHONIOENCODING = 'utf-8'
}
Invoke-Action '当前会话切换到 UTF-8 代码页' { chcp 65001 | Out-Null }
Write-Warn2 '区域设置写入注册表后需重启一次才全局生效'

# ---------------------------------------------------------------- 4. 镜像源
Write-Step '4/9 配置国内镜像源（pip / npm / pip 缓存）'
$pipDir = Join-Path $env:APPDATA 'pip'
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $pipDir | Out-Null }
$pipIni = Join-Path $pipDir 'pip.ini'
Invoke-Action '写入 pip 清华镜像配置' {
    @(
        '[global]'
        'index-url = https://pypi.tuna.tsinghua.edu.cn/simple'
        'trusted-host = pypi.tuna.tsinghua.edu.cn'
        'timeout = 60'
        ''
        '[install]'
        'prefer-binary = true'
    ) | Set-Content -Path $pipIni -Encoding UTF8
}
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Invoke-Action '设置 npm 镜像为 npmmirror' {
        npm config set registry https://registry.npmmirror.com | Out-Null
        npm config set fetch-timeout 120000 | Out-Null
    }
} else { Write-Warn2 '未检测到 npm（Node.js 尚未生效），稍后请手工执行：npm config set registry https://registry.npmmirror.com' }

# ---------------------------------------------------------------- 5. 目录规范
Write-Step '5/9 创建标准工作目录（代码放 WSL，样本与数据放数据盘）'
$dirs = @('D:\campus', 'D:\campus\repo', 'D:\campus\data', 'D:\campus\data\dataset',
          'D:\campus\weights', 'D:\campus\backup', 'D:\campus\installers', 'D:\campus\preview')
if ($Role -eq 'client') { $dirs = @('D:\campus', 'D:\campus\repo') }
foreach ($d in $dirs) { Invoke-Action "创建目录 $d" { New-Item -ItemType Directory -Force -Path $d | Out-Null } }

# ---------------------------------------------------------------- 6. Git 全局配置
Write-Step '6/9 Git 全局配置（换行、编码、长路径、大小写）'
if (Get-Command git -ErrorAction SilentlyContinue) {
    Invoke-Action 'git core.autocrlf=false'   { git config --global core.autocrlf false }
    Invoke-Action 'git core.quotepath=false'  { git config --global core.quotepath false }
    Invoke-Action 'git core.longpaths=true'   { git config --global core.longpaths true }
    Invoke-Action 'git core.ignorecase=false' { git config --global core.ignorecase false }
    Invoke-Action 'git pull.rebase=false'     { git config --global pull.rebase false }
    Invoke-Action 'git init.defaultBranch=main' { git config --global init.defaultBranch main }
    Invoke-Action 'git lfs install'           { git lfs install --skip-repo }
    $name = git config --global user.name
    if (-not $name) {
        Write-Warn2 '尚未设置 git user.name / user.email，请执行：'
        Write-Host '         git config --global user.name  "你的姓名"' -ForegroundColor DarkGray
        Write-Host '         git config --global user.email "你的邮箱"' -ForegroundColor DarkGray
    } else { Write-Ok "git 用户已配置：$name" }
} else { Write-Warn2 '未检测到 git，跳过（安装 Git 后请重新运行本脚本）' }

# ---------------------------------------------------------------- 7. Python 环境
Write-Step '7/9 Python 与 uv（包管理与虚拟环境）'
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Ok "python: $(python --version 2>&1)"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Invoke-Action '安装 uv（Python 包与虚拟环境管理器）' {
            powershell -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex" | Out-Null
        }
        Write-Warn2 'uv 安装后需重开终端；若失败可改用：pip install uv'
    } else { Write-Ok "uv 已安装：$(uv --version)" }
} else { Write-Warn2 'python 未就绪，请完成 Python 安装后重新运行本脚本' }

# 检查 py 启动器能否看到 3.11 / 3.12
if (Get-Command py -ErrorAction SilentlyContinue) {
    Write-Host '  已安装的 Python 版本：' -NoNewline
    py -0p 2>$null | ForEach-Object { Write-Host "`n    $_" -NoNewline }
    Write-Host ''
}

# ---------------------------------------------------------------- 8. Node 与 pnpm
Write-Step '8/9 Node.js 与 pnpm'
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Ok "node: $(node -v)"
    Invoke-Action '启用 corepack' { corepack enable 2>$null }
    if ($Role -ne 'client') {
        Invoke-Action '激活 pnpm' { corepack prepare pnpm@latest --activate 2>$null }
    }
    if (Get-Command pnpm -ErrorAction SilentlyContinue) { Write-Ok "pnpm: $(pnpm -v)" }
    else { Write-Warn2 'pnpm 未就绪，可执行：npm install -g pnpm' }
} else { Write-Warn2 'node 未就绪，请完成 Node.js LTS 安装后重新运行本脚本' }

# ---------------------------------------------------------------- 9. 收尾与报告
Write-Step '9/9 生成环境报告与后续待办清单'
$reportPath = 'D:\campus\env-report.txt'
if (-not $DryRun) {
    $lines = @()
    $lines += '===== 智慧园区平台 环境安装报告 ====='
    $report.GetEnumerator() | ForEach-Object { $lines += ('{0,-10}: {1}' -f $_.Key, $_.Value) }
    $lines += ''
    $lines += '----- 组件版本 -----'
    foreach ($c in 'git', 'python', 'node', 'pnpm', 'uv', 'docker') {
        $v = try { (& $c --version 2>&1 | Select-Object -First 1) } catch { '未安装' }
        $lines += ('{0,-8}: {1}' -f $c, $v)
    }
    $lines += ''
    $lines += '----- 待手工完成 -----'
    $lines += '1) BIOS 开启虚拟化（若第 1 步未通过）'
    if ($Role -ne 'client') {
        $lines += '2) wsl --install -d Ubuntu-24.04 并配置 apt 国内源'
        $lines += '3) Docker Desktop：启用 WSL2 后端 + 配置阿里云 ACR 镜像加速 + 限制内存'
        $lines += '4) 克隆仓库并执行 docker compose -f docker-compose.dev.yml up -d'
    }
    if ($Role -eq 'dev') {
        $lines += '5) 安装 NVIDIA 驱动 → PyTorch(cu12x) → Ultralytics → 验证 torch.cuda.is_available()'
        $lines += '6) 运行环境自检：python .\环境工具\scripts\check-env.py'
    }
    $lines += '7) VS Code 扩展：Python/Pylance/Ruff/Vue/Docker/Remote-WSL'
    $lines | Set-Content -Path $reportPath -Encoding UTF8
    Write-Ok "环境报告已写入 $reportPath"
}

Write-Host "`n==============================================================" -ForegroundColor Magenta
Write-Host ' 基础环境安装完成。请按手册继续：WSL2 → Docker → 后端 → AI → 前端' -ForegroundColor Magenta
Write-Host ' 完成后运行 环境工具\scripts\check-env.py 做一次总校验' -ForegroundColor Magenta
Write-Host "==============================================================" -ForegroundColor Magenta
