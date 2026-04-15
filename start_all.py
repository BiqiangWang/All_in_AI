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
        # 停止可能存在的旧容器
        subprocess.run("docker stop all_in_ai_postgres 2>/dev/null; docker rm all_in_ai_postgres 2>/dev/null",
                       shell=True, capture_output=True)

        # 启动 PostgreSQL
        print("[PostgreSQL] 启动数据库...")
        subprocess.run(
            "docker run -d --name all_in_ai_postgres "
            "-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=aegra "
            "-p 5432:5432 postgres:16-alpine",
            shell=True,
        )

        # 等待 PostgreSQL 就绪
        print("[PostgreSQL] 等待数据库就绪...")
        for _ in range(30):
            result = subprocess.run(
                "docker exec all_in_ai_postgres pg_isready -U postgres",
                shell=True,
                capture_output=True,
            )
            if result.returncode == 0:
                print("[PostgreSQL] 数据库已就绪 ✓")
                break
            time.sleep(1)
        else:
            print("[PostgreSQL] 警告: 数据库可能未就绪")

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
        try:
            import httpx
            resp = httpx.get("http://localhost:2026/health", timeout=5)
            if resp.status_code == 200:
                print("[Aegra] 健康检查通过 ✓")
            else:
                print(f"[Aegra] 健康检查异常: {resp.status_code}")
        except Exception as e:
            print(f"[Aegra] 健康检查失败: {e}")

        # 启动前端
        frontend_proc = run_command(
            "npm run dev",
            cwd=os.path.join(project_root, "frontend"),
            name="Frontend"
        )

        print("\n=== 服务已启动 ===")
        print("后端: http://localhost:2026")
        print("前端: http://localhost:3000")
        print("按 Ctrl+C 停止所有服务\n")

        # 同时监控两个进程输出
        def monitor(proc: subprocess.Popen, name: str):
            for line in iter(proc.stdout.readline, ""):
                if line:
                    print(f"[{name}] {line.rstrip()}")

        import threading
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
