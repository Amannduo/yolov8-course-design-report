#!/usr/bin/env python3
"""
YOLOv8 推理模块
支持命令行调用和API调用
"""

import argparse
from pathlib import Path
import cv2
import time
import threading
import logging
from ultralytics import YOLO

# 全局模型实例和锁
_model = None
_model_lock = threading.Lock()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model(weights: Path = Path("weights/yolov8n.pt")):
    """
    线程安全的模型加载函数
    Args:
        weights: 模型权重文件路径
    Returns:
        YOLO模型实例
    """
    global _model

    with _model_lock:
        if _model is None:
            try:
                if not weights.exists():
                    raise FileNotFoundError(f"模型权重文件不存在: {weights}")

                logger.info(f"正在加载模型: {weights}")
                _model = YOLO(str(weights))
                logger.info("模型加载成功")

            except Exception as e:
                logger.error(f"模型加载失败: {str(e)}")
                raise

    return _model


def run_inference(img_path: Path,
                  weights: Path = Path("weights/yolov8n.pt"),
                  save_dir: Path = Path("runs/local_test")) -> dict:
    """
    执行目标检测推理
    Args:
        img_path: 输入图像路径
        weights: 模型权重文件路径
        save_dir: 结果保存目录
    Returns:
        推理结果字典
    """
    try:
        # 检查输入文件
        if not img_path.exists():
            raise FileNotFoundError(f"输入图像不存在: {img_path}")

        # 创建保存目录
        save_dir.mkdir(parents=True, exist_ok=True)

        # 记录开始时间
        start_time = time.time()

        # 加载模型
        model = load_model(weights)

        # 执行推理
        logger.info(f"开始推理: {img_path.name}")
        results = model(str(img_path))

        if not results:
            raise RuntimeError("推理返回空结果")

        result = results[0]

        # 生成可视化图像
        try:
            annotated_img = result.plot()
            if annotated_img is None:
                raise RuntimeError("无法生成可视化图像")

            # 保存可视化结果
            vis_filename = f"vis_{img_path.stem}_{int(time.time())}{img_path.suffix}"
            vis_path = save_dir / vis_filename

            success = cv2.imwrite(str(vis_path), annotated_img)
            if not success:
                raise RuntimeError(f"保存可视化图像失败: {vis_path}")

            logger.info(f"可视化图像保存成功: {vis_path}")

        except Exception as e:
            logger.error(f"生成可视化图像失败: {str(e)}")
            vis_path = None

        # 解析检测结果
        detections = []
        best_detection = None

        if result.boxes is not None and len(result.boxes.conf) > 0:
            # 获取所有检测结果
            for i in range(len(result.boxes.conf)):
                detection = {
                    "class_id": int(result.boxes.cls[i]),
                    "class_name": model.names[int(result.boxes.cls[i])],
                    "confidence": float(result.boxes.conf[i]),
                    "bbox": result.boxes.xyxy[i].tolist() if result.boxes.xyxy is not None else None
                }
                detections.append(detection)

            # 获取置信度最高的检测结果
            best_idx = result.boxes.conf.argmax()
            best_detection = {
                "class_id": int(result.boxes.cls[best_idx]),
                "class_name": model.names[int(result.boxes.cls[best_idx])],
                "confidence": float(result.boxes.conf[best_idx]),
                "bbox": result.boxes.xyxy[best_idx].tolist() if result.boxes.xyxy is not None else None
            }

        # 计算推理时间
        inference_time = time.time() - start_time

        # 构建返回结果
        inference_result = {
            "image": img_path.name,
            "image_path": str(img_path),
            "vis_path": str(vis_path) if vis_path else None,
            "inference_time_seconds": round(inference_time, 3),
            "model_name": str(weights.name),
            "detection_count": len(detections),
            "detections": detections,
            "best_detection": best_detection,
            "success": True
        }

        # 兼容原有接口格式
        if best_detection:
            inference_result.update({
                "class_id": best_detection["class_id"],
                "score": best_detection["confidence"]
            })
        else:
            inference_result.update({
                "class_id": None,
                "score": None
            })

        logger.info(f"推理完成: {img_path.name}, 耗时: {inference_time:.3f}s, 检测到 {len(detections)} 个对象")
        return inference_result

    except Exception as e:
        logger.error(f"推理失败: {str(e)}")
        return {
            "image": img_path.name if img_path else "unknown",
            "image_path": str(img_path) if img_path else None,
            "vis_path": None,
            "inference_time_seconds": 0,
            "model_name": str(weights.name) if weights else "unknown",
            "detection_count": 0,
            "detections": [],
            "best_detection": None,
            "success": False,
            "error": str(e),
            "class_id": None,
            "score": None
        }


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="YOLOv8 目标检测推理")
    parser.add_argument("-s", "--source", required=True, help="输入图像路径")
    parser.add_argument("-w", "--weights", default="weights/yolov8n.pt", help="模型权重文件路径")
    parser.add_argument("-o", "--out", default="runs/local_test", help="输出目录")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 检查输入参数
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"错误: 输入文件不存在: {source_path}")
            return 1

        weights_path = Path(args.weights)
        if not weights_path.exists():
            print(f"错误: 权重文件不存在: {weights_path}")
            return 1

        output_path = Path(args.out)

        # 执行推理
        print(f"开始推理...")
        print(f"输入图像: {source_path}")
        print(f"模型权重: {weights_path}")
        print(f"输出目录: {output_path}")
        print("-" * 50)

        result = run_inference(source_path, weights_path, output_path)

        # 打印结果
        if result["success"]:
            print("推理成功!")
            print(f"图像: {result['image']}")
            print(f"推理时间: {result['inference_time_seconds']}s")
            print(f"检测到 {result['detection_count']} 个对象")

            if result["best_detection"]:
                best = result["best_detection"]
                print(f"最佳检测: {best['class_name']} (ID: {best['class_id']}, 置信度: {best['confidence']:.3f})")
            else:
                print("未检测到任何对象")

            if result["vis_path"]:
                print(f"可视化结果: {result['vis_path']}")

            if args.verbose:
                print("\n所有检测结果:")
                for i, det in enumerate(result["detections"]):
                    print(f"  {i + 1}. {det['class_name']} - 置信度: {det['confidence']:.3f}")
        else:
            print("推理失败!")
            print(f"错误: {result.get('error', '未知错误')}")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1
    except Exception as e:
        print(f"程序异常: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())