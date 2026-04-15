"""一键启动前后端服务."""
import subprocess
import sys
import os
import time
import signal

def run_command(cmd: str, cwd: str | None = None, name: str = "") -> subprocess.Popen:
    """启动子进程."""
    print(f"[{name}] 启动: {cmd}")
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def stream_output(proc: subprocess.Popen, name: str):
    """实时输出子进程日志."""
    for line in iter(proc.stdout.readline, ""):
        if line:
            print(f"[{name}] {line.rstrip()}")


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_proc = None
    frontend_proc = None

    def cleanup():
        print("\n正在关闭服务...")
        for proc, name in [(backend_proc, "Aegra"), (frontend_proc, "Frontend")]:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"[{name}] 已关闭")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print(f"[{name}] 已强制关闭")

    signal.signal(signal.SIGINT, lambda *_: cleanup())

    try:
        # 启动后端 (Aegra)
        backend_proc = run_command(
            "conda run -n langchain-next aegra dev --no-db-check",
            cwd=os.path.join(project_root, "agents"),
            name="Aegra"
        )

        # 等待后端就绪
        print("[Aegra] 等待服务就绪...")
        time.sleep(8)

        # 检查后端健康状态
        import httpx
        try:
            resp = httpx.get("http://localhost:2026/health", timeout=5)
            if resp.status_code == 200:
                print("[Aegra] 健康检查通过 ✓")
            else:
                print(f"[Aegra] 健康检查异常: {resp.status_code}")
        except Exception as e:
            print(f"[Aegra] 健康检查失败: {e}")

        # 启动前端
        frontend_proc = run_command(
            "pnpm dev",
            cwd=os.path.join(project_root, "frontend"),
            name="Frontend"
        )

        print("\n=== 服务已启动 ===")
        print("后端: http://localhost:2026")
        print("前端: http://localhost:3000")
        print("按 Ctrl+C 停止所有服务\n")

        # 同时监控两个进程输出
        import threading

        def monitor(proc: subprocess.Popen, name: str):
            for line in iter(proc.stdout.readline, ""):
                if line:
                    print(f"[{name}] {line.rstrip()}")

        backend_thread = threading.Thread(target=monitor, args=(backend_proc, "Aegra"), daemon=True)
        frontend_thread = threading.Thread(target=monitor, args=(frontend_proc, "Frontend"), daemon=True)
        backend_thread.start()
        frontend_thread.start()

        # 等待任一进程结束
        while True:
            if backend_proc.poll() is not None:
                print("[Aegra] 进程已退出")
                break
            if frontend_proc.poll() is not None:
                print("[Frontend] 进程已退出")
                break
            time.sleep(0.5)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
