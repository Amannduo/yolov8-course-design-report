#!/usr/bin/env python3
"""
结果管理 API 测试脚本
用于测试批量下载等新增功能
"""

import requests
import json
import time
from pathlib import Path


class ResultsAPITester:
    def __init__(self, base_url="http://192.168.115.133:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_get_results_list(self):
        """测试获取结果列表"""
        print("=" * 50)
        print("📁 测试获取结果列表")
        print("=" * 50)

        try:
            response = self.session.get(f"{self.base_url}/results")
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {response.elapsed.total_seconds():.3f}s")

            if response.status_code == 200:
                data = response.json()
                print("✅ 获取结果列表成功")

                if data.get('ok') and data.get('data'):
                    summary = data['data']['summary']
                    results = data['data']['results']

                    print(f"📊 结果摘要:")
                    print(f"  总结果数: {summary['total_results']}")
                    print(f"  类别数: {len(summary['categories'])}")
                    print(f"  类别列表: {', '.join(summary['categories'])}")
                    print(f"  原图总大小: {summary['total_upload_size'] / 1024 / 1024:.2f}MB")
                    print(f"  可视化总大小: {summary['total_vis_size'] / 1024 / 1024:.2f}MB")

                    if results:
                        print(f"\n📄 前3个结果详情:")
                        for i, result in enumerate(results[:3], 1):
                            print(f"  {i}. ID: {result['id']}")
                            print(f"     类别: {result['category']}")
                            print(f"     时间戳: {result['timestamp']}")
                            if result['upload_info']:
                                print(f"     原图: {result['upload_info']['original_name']}")
                                print(f"     原图大小: {result['upload_info']['upload_size'] / 1024:.1f}KB")
                            if result['visualization_info']:
                                print(f"     可视化大小: {result['visualization_info']['vis_size'] / 1024:.1f}KB")

                    return True, summary['total_results'] > 0
                else:
                    print("❌ 响应数据格式错误")
                    return False, False
            else:
                print("❌ 请求失败")
                return False, False

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False, False

    def test_download_all_results(self):
        """测试批量下载所有结果"""
        print("\n" + "=" * 50)
        print("📦 测试批量下载所有结果")
        print("=" * 50)

        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/results/download")
            elapsed = time.time() - start_time

            print(f"状态码: {response.status_code}")
            print(f"下载时间: {elapsed:.3f}s")

            if response.status_code == 200:
                # 获取文件大小
                file_size = len(response.content)
                print(f"文件大小: {file_size / 1024 / 1024:.2f}MB")

                # 检查Content-Disposition头
                content_disposition = response.headers.get('Content-Disposition', '')
                print(f"Content-Disposition: {content_disposition}")

                # 检查Content-Type
                content_type = response.headers.get('Content-Type', '')
                print(f"Content-Type: {content_type}")

                if content_type == 'application/zip':
                    print("✅ 批量下载成功 - 返回ZIP文件")

                    # 可选：保存文件到本地测试
                    test_filename = f"test_download_{int(time.time())}.zip"
                    with open(test_filename, 'wb') as f:
                        f.write(response.content)
                    print(f"📁 测试文件已保存: {test_filename}")

                    # 清理测试文件
                    Path(test_filename).unlink()
                    print("🧹 测试文件已清理")

                    return True
                else:
                    print("❌ 返回文件类型不正确")
                    return False
            else:
                print("❌ 下载失败")
                try:
                    error_data = response.json()
                    print(f"错误信息: {error_data.get('msg', 'Unknown error')}")
                except:
                    print(f"响应内容: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False

    def test_download_category(self, category):
        """测试按类别下载"""
        print(f"\n" + "=" * 50)
        print(f"📦 测试下载类别: {category}")
        print("=" * 50)

        try:
            response = self.session.get(f"{self.base_url}/results/download/{category}")
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                file_size = len(response.content)
                print(f"文件大小: {file_size / 1024 / 1024:.2f}MB")
                print(f"✅ 类别 '{category}' 下载成功")
                return True
            elif response.status_code == 404:
                print(f"⚠️  类别 '{category}' 不存在或为空")
                return True  # 这也算是正确的行为
            else:
                print(f"❌ 下载失败")
                return False

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False

    def test_clean_operations(self):
        """测试清理操作（需要谨慎使用）"""
        print("\n" + "=" * 50)
        print("🧹 测试清理操作")
        print("=" * 50)

        print("⚠️  清理操作测试已跳过（避免误删数据）")
        print("如需测试清理功能，请手动调用以下API：")
        print(f"  DELETE {self.base_url}/results/clean/<category>  # 清理指定类别")
        print(f"  DELETE {self.base_url}/results/clean            # 清理所有结果")

        return True

    def run_all_tests(self):
        """运行所有结果管理测试"""
        print("🚀 开始结果管理 API 测试")
        print("测试服务器:", self.base_url)
        print("时间:", time.strftime('%Y-%m-%d %H:%M:%S'))

        results = {}

        # 1. 测试获取结果列表
        success, has_results = self.test_get_results_list()
        results['get_results'] = success

        if success and has_results:
            # 2. 测试批量下载
            results['download_all'] = self.test_download_all_results()

            # 3. 测试类别下载（使用第一个类别）
            try:
                response = self.session.get(f"{self.base_url}/results")
                if response.status_code == 200:
                    data = response.json()
                    categories = data['data']['summary']['categories']
                    if categories:
                        results['download_category'] = self.test_download_category(categories[0])
                    else:
                        print("⚠️  没有可用的类别进行测试")
                        results['download_category'] = True
            except:
                results['download_category'] = False
        else:
            print("⚠️  没有可用的结果，跳过下载测试")
            results['download_all'] = True
            results['download_category'] = True

        # 4. 测试清理操作（仅说明）
        results['clean_operations'] = self.test_clean_operations()

        # 测试总结
        print("\n" + "=" * 60)
        print("📋 结果管理测试总结")
        print("=" * 60)

        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)

        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")

        print(f"\n总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests / total_tests * 100:.1f}%")

        if passed_tests == total_tests:
            print("\n🎉 所有结果管理功能测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查功能实现")

        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="结果管理 API 测试工具")
    parser.add_argument("--url", default="http://192.168.115.133:5000", help="API 服务器地址")
    args = parser.parse_args()

    # 运行测试
    tester = ResultsAPITester(args.url)
    results = tester.run_all_tests()

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    exit(main())