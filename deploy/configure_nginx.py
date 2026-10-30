"""Run once as root after a successful initial build, on the existing myserver."""
from pathlib import Path
import shutil
import subprocess

CONFIG = Path("/etc/nginx/sites-available/default")
BACKUP = CONFIG.with_name("default.before-deep-learning")
INCLUDE = "    include /etc/nginx/snippets/deep-learning.conf;"
ANCHOR = "    server_name glance02.xyz www.glance02.xyz; # managed by Certbot"


def main():
    original = CONFIG.read_text()
    if INCLUDE in original:
        print("Deep learning route already configured")
        return
    if original.count(ANCHOR) != 1:
        raise RuntimeError("Expected HTTPS server block was not found uniquely")
    if not BACKUP.exists():
        shutil.copy2(CONFIG, BACKUP)
    CONFIG.write_text(original.replace(ANCHOR, ANCHOR + "\n" + INCLUDE, 1))
    try:
        subprocess.run(["nginx", "-t"], check=True)
    except BaseException:
        CONFIG.write_text(original)
        raise
    subprocess.run(["systemctl", "reload", "nginx"], check=True)
    print(f"Route enabled; original config backed up at {BACKUP}")


if __name__ == "__main__":
    main()
