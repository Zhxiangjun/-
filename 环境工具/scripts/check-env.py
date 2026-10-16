# -*- coding: utf-8 -*-
"""
智慧园区平台 · 环境自检脚本（Windows 开发机 / 云服务器 / 现场服务器通用）
文件：环境配置/scripts/check-env.py

用法：
    python check-env.py                # 全量自检并输出报告
    python check-env.py --json         # 以 JSON 输出（便于机房批量收集）
    python check-env.py --role dev     # 指定角色：dev / server / client / cloud

退出码：0 = 全部通过；1 = 存在缺失项（便于 CI 或批量脚本判定）

依赖：仅使用 Python 标准库；如安装了 requests 会额外做 HTTP 探测。
"""

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime

# ---------------------------------------------------------------- 常量
PORTS = [
    (5432, "PostgreSQL", "dev/server/cloud"),
    (6379, "Redis", "dev/server/cloud"),
    (1883, "EMQX MQTT", "dev/server/cloud"),
    (8083, "EMQX WebSocket", "dev/server"),
    (18083, "EMQX Dashboard", "dev/server"),
    (9000, "MinIO API", "dev/server/cloud"),
    (9001, "MinIO Console", "dev/server"),
    (6041, "TDengine REST", "server"),
    (8000, "后端 API", "all"),
    (5173, "前端 Vite", "dev"),
]

CMDS = [
    ("git", ["--version"], "全部"),
    ("python", ["--version"], "全部"),
    ("node", ["-v"], "全部"),
    ("pnpm", ["-v"], "全部"),
    ("uv", ["--version"], "dev/server"),
    ("docker", ["--version"], "dev/server"),
    ("ffmpeg", ["-version"], "dev"),
    ("nvidia-smi", ["--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], "dev"),
]


def run(cmd, timeout=15):
    """执行命令并返回 (成功, 输出)。"""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        out = (p.stdout or p.stderr or "").strip().splitlines()
        return (p.returncode == 0, out[0] if out else "")
    except Exception as e:  # noqa: BLE001
        return (False, str(e))


def port_open(host, port, timeout=1.0):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:  # noqa: BLE001
        return False
    finally:
        s.close()


def check_system():
    rows = []
    rows.append(("操作系统", platform.platform(), True))
    rows.append(("Python 版本", sys.version.split()[0], sys.version_info >= (3, 11)))
    rows.append(("编码环境", f"UTF8={os.environ.get('PYTHONUTF8', '未设置')}", os.environ.get("PYTHONUTF8") == "1"))
    rows.append(("磁盘可用", disk_info(), True))
    if os.name == "nt":
        ok = run("wsl -l -v")[0]
        rows.append(("WSL2 发行版", "已安装" if ok else "未检测到", ok))
    return rows


def disk_info():
    parts = []
    for letter in ("C", "D"):
        path = f"{letter}:\\" if os.name == "nt" else "/"
        try:
            total, used, free = shutil.disk_usage(path)
            parts.append(f"{letter}: 可用 {free / 1024 ** 3:.1f} GB / 共 {total / 1024 ** 3:.1f} GB")
        except Exception:  # noqa: BLE001
            continue
    return "；".join(parts) if parts else "未知"


def check_commands(role):
    rows = []
    for cmd, args, scope in CMDS:
        if role == "client" and scope == "dev":
            continue
        if role == "cloud" and scope in ("dev", "server"):
            continue
        arg = " ".join(args)
        ok, out = run(f"{cmd} {arg}")
        if not ok:
            ok2, out2 = run(cmd)
            ok, out = ok2, out2
        rows.append((f"命令 {cmd}", out if out else "未安装", ok))
    return rows


def check_ports(role):
    rows = []
    for port, name, scope in PORTS:
        if role == "client":
            continue
        if role == "cloud" and scope not in ("cloud", "all"):
            continue
        if role == "server" and scope == "dev" and port == 5173:
            pass
        opened = port_open("127.0.0.1", port)
        rows.append((f"端口 {port} {name}", "开放" if opened else "未监听", opened))
    return rows


def check_python_libs():
    rows = []
    libs = [
        ("fastapi", "FastAPI"), ("uvicorn", "Uvicorn"), ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"), ("redis", "redis-py"), ("paho.mqtt", "paho-mqtt"),
        ("torch", "PyTorch"), ("ultralytics", "Ultralytics"), ("onnxruntime", "ONNX Runtime"),
        ("cv2", "OpenCV"), ("numpy", "NumPy"), ("minio", "MinIO SDK"),
    ]
    for mod, name in libs:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "已安装")
            rows.append((f"Python 库 {name}", str(ver), True))
        except Exception:  # noqa: BLE001
            rows.append((f"Python 库 {name}", "未安装", False))
    # CUDA 可用性
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            rows.append(("CUDA 可用", f"是，{torch.cuda.get_device_name(0)}，CUDA {torch.version.cuda}", True))
        else:
            rows.append(("CUDA 可用", "否（仅 CPU）", False))
    except Exception:  # noqa: BLE001
        rows.append(("CUDA 可用", "未安装 PyTorch", False))
    return rows


def check_node_project():
    rows = []
    for d in ("web-admin", "frontend", "web"):
        if os.path.isdir(d):
            rows.append((f"前端工程 {d}", os.path.abspath(d), True))
            break
    else:
        rows.append(("前端工程目录", "未找到 web-admin（尚未创建）", False))
    return rows


def main():
    ap = argparse.ArgumentParser(description="智慧园区平台环境自检")
    ap.add_argument("--role", default="dev", choices=["dev", "server", "client", "cloud"])
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    ap.add_argument("--host", default="127.0.0.1", help="探测依赖服务的主机地址")
    args = ap.parse_args()

    sections = [
        ("一、系统与运行环境", check_system()),
        ("二、命令行工具", check_commands(args.role)),
        ("三、依赖服务端口", check_ports(args.role)),
        ("四、Python 依赖与 GPU", check_python_libs() if args.role in ("dev",) else []),
        ("五、工程目录", check_node_project()),
    ]

    total = passed = 0
    report = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "host": platform.node(), "role": args.role, "sections": []}

    if not args.json:
        print("=" * 74)
        print(f" 智慧园区平台 环境自检报告   角色={args.role}   主机={platform.node()}")
        print(f" 时间：{report['time']}")
        print("=" * 74)
    for title, rows in sections:
        if not rows:
            continue
        if not args.json:
            print(f"\n{title}")
        sec = {"title": title, "items": []}
        for name, value, ok in rows:
            total += 1
            passed += 1 if ok else 0
            sec["items"].append({"name": name, "value": value, "pass": bool(ok)})
            if not args.json:
                flag = "[ OK ]" if ok else "[FAIL]"
                print(f"  {flag} {name:<26} {value}")
        report["sections"].append(sec)

    report["summary"] = {"total": total, "passed": passed,
                         "failed": total - passed,
                         "rate": round(passed / total * 100, 1) if total else 0}

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n" + "-" * 74)
        print(f" 合计 {total} 项，通过 {passed} 项，未通过 {total - passed} 项，通过率 {report['summary']['rate']}%")
        if total - passed:
            print(" 未通过项请对照《电脑环境配置详细方案》对应章节处理。")
        print("-" * 74)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
