#!/usr/bin/env python3
"""
简单的网络连通性测试服务器
用于验证宿主机是否能访问虚拟机服务
"""

from flask import Flask, jsonify
import socket
import time

app = Flask(__name__)


@app.route('/test')
def test():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return jsonify({
        "status": "success",
        "message": "网络连通正常！",
        "server_info": {
            "hostname": hostname,
            "local_ip": local_ip,
            "time": time.strftime('%Y-%m-%d %H:%M:%S')
        },
        "access_info": {
            "message": "如果你在宿主机看到这个消息，说明网络配置成功！",
            "test_url": f"http://{local_ip}:5000/test"
        }
    })


@app.route('/')
def index():
    return """
    <h1>🎉 网络测试成功！</h1>
    <p>如果你在宿主机浏览器中看到这个页面，说明虚拟机网络配置正确。</p>
    <p>现在可以访问你的主要Flask应用了！</p>
    <a href="/test">JSON测试接口</a>
    """


if __name__ == "__main__":
    print("🚀 启动网络测试服务器...")
    print("=" * 50)

    # 获取本机IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print(f"服务器信息:")
    print(f"  主机名: {hostname}")
    print(f"  本地IP: {local_ip}")
    print(f"  监听地址: 0.0.0.0:5000")
    print()
    print(f"访问地址:")
    print(f"  虚拟机内访问: http://localhost:5000/")
    print(f"  宿主机访问: http://{local_ip}:5000/")
    print()
    print("如果宿主机无法访问，请检查:")
    print("1. Ubuntu防火墙设置")
    print("2. VMware网络配置")
    print("3. Flask绑定地址")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)