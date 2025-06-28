#!/usr/bin/env python3
"""
Flask API wrapper around run_inference() from predict.py
启动:  python app.py
默认端口: http://0.0.0.0:5000
访问页面: http://localhost:5000/
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import time
import logging
import os

# 复用你刚才写好的函数
from predict import run_inference

# 配置
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "tiff"}
SAVE_ROOT = Path("runs/api_test")  # 结果统一放这里
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_FILES_COUNT = 10  # 最大上传文件数

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
CORS(app)  # 启用跨域支持

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def make_response(ok: bool, msg: str, data=None, code=200):
    """统一返回格式"""
    return jsonify({
        "ok": ok,
        "msg": msg,
        "data": data,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }), code


def is_valid_extension(filename: str) -> bool:
    """检查文件扩展名是否有效"""
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


def check_file_content(file_path: Path) -> bool:
    """简单检查文件内容是否为图像文件"""
    try:
        import cv2
        img = cv2.imread(str(file_path))
        return img is not None
    except Exception:
        return False


@app.route("/")
def index():
    """主页面，返回上传界面"""
    return send_from_directory("static", "upload.html")


@app.route("/test", methods=["GET"])
def healthcheck():
    """健康检查接口"""
    try:
        # 检查模型权重文件是否存在
        weights_path = Path("weights/yolov8n.pt")
        model_status = "loaded" if weights_path.exists() else "not found"

        data = {
            "server_status": "running",
            "model_status": model_status,
            "save_directory": str(SAVE_ROOT),
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
        }

        logger.info("健康检查请求成功")
        return make_response(True, "服务器运行正常", data)

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return make_response(False, f"服务器异常: {str(e)}", code=500)


@app.route("/upload/<category>/single", methods=["POST"])
def upload_single(category):
    """单文件上传推理接口"""
    try:
        # 检查文件是否存在
        if "file" not in request.files:
            return make_response(False, "请求中未包含文件", code=400)

        file = request.files["file"]
        if file.filename == "":
            return make_response(False, "未选择文件", code=400)

        if not is_valid_extension(file.filename):
            return make_response(False, f"不支持的文件类型，支持的格式: {', '.join(ALLOWED_EXTENSIONS)}", code=415)

        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"

        upload_dir = SAVE_ROOT / "uploads" / category
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / unique_filename

        file.save(file_path)
        logger.info(f"文件保存成功: {file_path}")

        # 检查文件内容
        if not check_file_content(file_path):
            file_path.unlink()  # 删除无效文件
            return make_response(False, "文件损坏或不是有效的图像文件", code=400)

        # 执行推理
        vis_dir = SAVE_ROOT / "visualizations" / category
        result = run_inference(file_path, save_dir=vis_dir)

        # 添加额外信息
        result.update({
            "category": category,
            "original_filename": filename,
            "upload_path": str(file_path),
            "inference_time": time.strftime('%Y-%m-%d %H:%M:%S')
        })

        logger.info(f"推理完成: {filename}, 类别ID: {result.get('class_id')}")
        return make_response(True, "推理完成", result)

    except Exception as e:
        logger.error(f"单文件上传推理失败: {str(e)}")
        return make_response(False, f"推理失败: {str(e)}", code=500)


@app.route("/upload/<category>/multiple", methods=["POST"])
def upload_multiple(category):
    """多文件上传推理接口"""
    try:
        files = request.files.getlist("files")
        if not files:
            return make_response(False, "请求中未包含文件", code=400)

        if len(files) > MAX_FILES_COUNT:
            return make_response(False, f"文件数量超过限制，最大支持 {MAX_FILES_COUNT} 个文件", code=400)

        results = []
        success_count = 0

        for i, file in enumerate(files):
            file_result = {
                "index": i + 1,
                "filename": file.filename,
                "ok": False,
                "msg": "",
                "data": None
            }

            try:
                # 检查文件
                if file.filename == "":
                    raise ValueError("文件名为空")

                if not is_valid_extension(file.filename):
                    raise ValueError(f"不支持的文件类型")

                # 保存文件
                filename = secure_filename(file.filename)
                timestamp = int(time.time())
                unique_filename = f"{timestamp}_{i + 1}_{filename}"

                upload_dir = SAVE_ROOT / "uploads" / category
                upload_dir.mkdir(parents=True, exist_ok=True)
                file_path = upload_dir / unique_filename

                file.save(file_path)

                # 检查文件内容
                if not check_file_content(file_path):
                    file_path.unlink()
                    raise ValueError("文件损坏或不是有效的图像文件")

                # 执行推理
                vis_dir = SAVE_ROOT / "visualizations" / category
                inference_result = run_inference(file_path, save_dir=vis_dir)

                # 添加额外信息
                inference_result.update({
                    "category": category,
                    "original_filename": filename,
                    "upload_path": str(file_path)
                })

                file_result.update({
                    "ok": True,
                    "msg": "推理成功",
                    "data": inference_result
                })
                success_count += 1

            except Exception as e:
                file_result["msg"] = str(e)
                logger.error(f"文件 {file.filename} 处理失败: {str(e)}")

            results.append(file_result)

        summary = {
            "total_files": len(files),
            "success_count": success_count,
            "failed_count": len(files) - success_count,
            "results": results
        }

        logger.info(f"批量推理完成: {success_count}/{len(files)} 成功")
        return make_response(True, f"批量推理完成，成功 {success_count}/{len(files)} 个文件", summary)

    except Exception as e:
        logger.error(f"批量推理失败: {str(e)}")
        return make_response(False, f"批量推理失败: {str(e)}", code=500)


@app.errorhandler(413)
def file_too_large(e):
    """文件过大错误处理"""
    return make_response(False, f"文件大小超过限制 ({MAX_FILE_SIZE // (1024 * 1024)}MB)", code=413)


@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return make_response(False, "请求的资源不存在", code=404)


@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(e)}")
    return make_response(False, "内部服务器错误", code=500)


@app.route("/results", methods=["GET"])
def list_results():
    """获取所有推理结果列表"""
    try:
        results = []

        # 遍历所有类别目录
        if SAVE_ROOT.exists():
            upload_dir = SAVE_ROOT / "uploads"
            vis_dir = SAVE_ROOT / "visualizations"

            categories = set()
            if upload_dir.exists():
                categories.update([d.name for d in upload_dir.iterdir() if d.is_dir()])
            if vis_dir.exists():
                categories.update([d.name for d in vis_dir.iterdir() if d.is_dir()])

            for category in categories:
                cat_upload_dir = upload_dir / category
                cat_vis_dir = vis_dir / category

                # 获取上传的文件
                uploaded_files = {}
                if cat_upload_dir.exists():
                    for file_path in cat_upload_dir.iterdir():
                        if file_path.is_file():
                            # 提取时间戳和原始文件名
                            name_parts = file_path.name.split('_', 1)
                            if len(name_parts) >= 2:
                                timestamp = name_parts[0]
                                original_name = '_'.join(name_parts[1:])
                            else:
                                timestamp = str(int(file_path.stat().st_mtime))
                                original_name = file_path.name

                            uploaded_files[timestamp] = {
                                "original_name": original_name,
                                "upload_path": str(file_path),
                                "upload_size": file_path.stat().st_size,
                                "upload_time": time.strftime('%Y-%m-%d %H:%M:%S',
                                                             time.localtime(file_path.stat().st_mtime))
                            }

                # 获取可视化文件
                vis_files = {}
                if cat_vis_dir.exists():
                    for file_path in cat_vis_dir.iterdir():
                        if file_path.is_file() and file_path.name.startswith('vis_'):
                            # 提取时间戳
                            name_parts = file_path.stem.split('_')
                            timestamp = name_parts[-1] if name_parts else str(int(file_path.stat().st_mtime))

                            vis_files[timestamp] = {
                                "vis_path": str(file_path),
                                "vis_size": file_path.stat().st_size,
                                "vis_time": time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.localtime(file_path.stat().st_mtime))
                            }

                # 合并结果
                all_timestamps = set(uploaded_files.keys()) | set(vis_files.keys())
                for timestamp in all_timestamps:
                    result_item = {
                        "id": f"{category}_{timestamp}",
                        "category": category,
                        "timestamp": timestamp,
                        "upload_info": uploaded_files.get(timestamp),
                        "visualization_info": vis_files.get(timestamp)
                    }
                    results.append(result_item)

        # 按时间排序（最新的在前）
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        summary = {
            "total_results": len(results),
            "categories": list(set(r["category"] for r in results)),
            "total_upload_size": sum(r["upload_info"]["upload_size"] for r in results if r["upload_info"]),
            "total_vis_size": sum(r["visualization_info"]["vis_size"] for r in results if r["visualization_info"])
        }

        data = {
            "summary": summary,
            "results": results
        }

        logger.info(f"获取结果列表成功，共 {len(results)} 条记录")
        return make_response(True, f"获取到 {len(results)} 条推理结果", data)

    except Exception as e:
        logger.error(f"获取结果列表失败: {str(e)}")
        return make_response(False, f"获取结果列表失败: {str(e)}", code=500)


@app.route("/results/download", methods=["GET"])
def download_all_results():
    """打包下载所有推理结果"""
    try:
        import zipfile
        import tempfile
        from flask import send_file

        # 创建临时ZIP文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0

            # 添加上传的原始文件
            upload_dir = SAVE_ROOT / "uploads"
            if upload_dir.exists():
                for file_path in upload_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = f"uploads/{file_path.relative_to(upload_dir)}"
                        zipf.write(file_path, arcname)
                        file_count += 1

            # 添加可视化结果文件
            vis_dir = SAVE_ROOT / "visualizations"
            if vis_dir.exists():
                for file_path in vis_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = f"visualizations/{file_path.relative_to(vis_dir)}"
                        zipf.write(file_path, arcname)
                        file_count += 1

            # 创建结果摘要文件
            summary_content = f"""推理结果摘要
===================
打包时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
文件总数: {file_count}
打包路径: {SAVE_ROOT}

目录结构:
- uploads/     : 用户上传的原始图像文件
- visualizations/ : 推理结果可视化图像文件

使用说明:
1. uploads/ 目录包含所有上传的原始图像
2. visualizations/ 目录包含带检测框的结果图像
3. 文件名中的时间戳可以用来关联原图和结果图
"""
            zipf.writestr("README.txt", summary_content)

        # 生成下载文件名
        download_filename = f"inference_results_{time.strftime('%Y%m%d_%H%M%S')}.zip"

        logger.info(f"生成结果打包文件: {download_filename}, 包含 {file_count} 个文件")

        def remove_file():
            """下载完成后删除临时文件"""
            try:
                Path(zip_path).unlink()
            except:
                pass

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        logger.error(f"打包下载失败: {str(e)}")
        return make_response(False, f"打包下载失败: {str(e)}", code=500)


@app.route("/results/download/<category>", methods=["GET"])
def download_category_results(category):
    """按类别下载推理结果"""
    try:
        import zipfile
        import tempfile
        from flask import send_file

        # 检查类别是否存在
        cat_upload_dir = SAVE_ROOT / "uploads" / category
        cat_vis_dir = SAVE_ROOT / "visualizations" / category

        if not (cat_upload_dir.exists() or cat_vis_dir.exists()):
            return make_response(False, f"类别 '{category}' 不存在", code=404)

        # 创建临时ZIP文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0

            # 添加该类别的上传文件
            if cat_upload_dir.exists():
                for file_path in cat_upload_dir.iterdir():
                    if file_path.is_file():
                        zipf.write(file_path, f"uploads/{file_path.name}")
                        file_count += 1

            # 添加该类别的可视化文件
            if cat_vis_dir.exists():
                for file_path in cat_vis_dir.iterdir():
                    if file_path.is_file():
                        zipf.write(file_path, f"visualizations/{file_path.name}")
                        file_count += 1

            if file_count == 0:
                return make_response(False, f"类别 '{category}' 下没有文件", code=404)

            # 创建类别摘要文件
            summary_content = f"""类别推理结果摘要
===================
类别: {category}
打包时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
文件总数: {file_count}

目录结构:
- uploads/     : 该类别的原始图像文件
- visualizations/ : 该类别的结果可视化图像文件
"""
            zipf.writestr("README.txt", summary_content)

        # 生成下载文件名
        download_filename = f"inference_results_{category}_{time.strftime('%Y%m%d_%H%M%S')}.zip"

        logger.info(f"生成类别打包文件: {download_filename}, 包含 {file_count} 个文件")

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        logger.error(f"按类别打包下载失败: {str(e)}")
        return make_response(False, f"按类别打包下载失败: {str(e)}", code=500)


@app.route("/results/clean", methods=["DELETE"])
def clean_results():
    """清理所有推理结果"""
    try:
        import shutil

        deleted_files = 0
        deleted_dirs = 0

        if SAVE_ROOT.exists():
            for item in SAVE_ROOT.iterdir():
                if item.is_file():
                    item.unlink()
                    deleted_files += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_dirs += 1

        # 重新创建必要的目录
        (SAVE_ROOT / "uploads").mkdir(parents=True, exist_ok=True)
        (SAVE_ROOT / "visualizations").mkdir(parents=True, exist_ok=True)

        logger.info(f"清理完成: 删除 {deleted_files} 个文件, {deleted_dirs} 个目录")
        return make_response(True, f"清理完成，删除了 {deleted_files} 个文件和 {deleted_dirs} 个目录")

    except Exception as e:
        logger.error(f"清理失败: {str(e)}")
        return make_response(False, f"清理失败: {str(e)}", code=500)


@app.route("/results/clean/<category>", methods=["DELETE"])
def clean_category_results(category):
    """清理指定类别的推理结果"""
    try:
        import shutil

        deleted_files = 0

        # 清理上传文件
        cat_upload_dir = SAVE_ROOT / "uploads" / category
        if cat_upload_dir.exists():
            for file_path in cat_upload_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_files += 1
            # 如果目录为空则删除
            try:
                cat_upload_dir.rmdir()
            except OSError:
                pass

        # 清理可视化文件
        cat_vis_dir = SAVE_ROOT / "visualizations" / category
        if cat_vis_dir.exists():
            for file_path in cat_vis_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_files += 1
            # 如果目录为空则删除
            try:
                cat_vis_dir.rmdir()
            except OSError:
                pass

        if deleted_files == 0:
            return make_response(False, f"类别 '{category}' 不存在或已为空", code=404)

        logger.info(f"清理类别 {category} 完成: 删除 {deleted_files} 个文件")
        return make_response(True, f"清理类别 '{category}' 完成，删除了 {deleted_files} 个文件")

    except Exception as e:
        logger.error(f"清理类别失败: {str(e)}")
        return make_response(False, f"清理类别失败: {str(e)}", code=500)


if __name__ == "__main__":
    # 创建必要的目录
    SAVE_ROOT.mkdir(parents=True, exist_ok=True)
    (SAVE_ROOT / "uploads").mkdir(parents=True, exist_ok=True)
    (SAVE_ROOT / "visualizations").mkdir(parents=True, exist_ok=True)

    # 检查静态文件目录
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)

    logger.info("Flask 服务器启动中...")
    logger.info(f"访问地址: http://localhost:5000/")
    logger.info(f"结果保存目录: {SAVE_ROOT}")

    app.run(host="0.0.0.0", port=5000, debug=True)