"""
病理图像炎症区域检测和标注工具
Pathology Image Inflammation Detection and Annotation Tool
"""

import cv2
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt


class PathologyAnalyzer:
    def __init__(self, input_folder="input_images", output_folder="output_images"):
        """
        初始化病理分析器

        Args:
            input_folder: 输入图像文件夹路径
            output_folder: 输出图像文件夹路径
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

    def detect_inflammation_regions(self, image):
        """
        检测炎症区域
        基于颜色和纹理特征识别可能的炎症损伤区域

        病理学特征：
        - 炎症区域通常呈现深紫色/紫红色（细胞密集）
        - 组织结构破坏、细胞浸润
        - 核密度增加

        Args:
            image: BGR格式的输入图像

        Returns:
            mask: 二值化的炎症区域掩码
            intensity_map: 炎症强度热图
        """
        # 转换到HSV色彩空间，更好地分析颜色
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 定义紫色/紫红色范围（炎症细胞密集区域）
        # 调整这些参数可以优化检测效果
        lower_purple1 = np.array([120, 30, 30])
        upper_purple1 = np.array([160, 255, 255])

        lower_purple2 = np.array([140, 50, 50])
        upper_purple2 = np.array([180, 255, 200])

        # 创建紫色区域掩码
        mask1 = cv2.inRange(hsv, lower_purple1, upper_purple1)
        mask2 = cv2.inRange(hsv, lower_purple2, upper_purple2)
        purple_mask = cv2.bitwise_or(mask1, mask2)

        # 转换到灰度图，分析密度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 检测暗色区域（高密度细胞区域）
        _, dark_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

        # 结合颜色和密度信息
        combined_mask = cv2.bitwise_and(purple_mask, dark_mask)

        # 形态学操作去除噪声
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

        # 计算炎症强度（基于颜色深度和区域大小）
        intensity_map = cv2.GaussianBlur(combined_mask.astype(np.float32), (21, 21), 0)

        return combined_mask, intensity_map

    def find_severe_regions(self, mask, intensity_map, min_area=500):
        """
        找出严重炎症区域的中心点

        Args:
            mask: 炎症区域掩码
            intensity_map: 炎症强度图
            min_area: 最小区域面积阈值

        Returns:
            centers: 严重炎症区域的中心点列表 [(x, y, severity), ...]
        """
        # 查找连通区域
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        centers = []
        for i in range(1, num_labels):  # 跳过背景（标签0）
            area = stats[i, cv2.CC_STAT_AREA]

            if area > min_area:
                x, y = int(centroids[i][0]), int(centroids[i][1])

                # 计算该区域的平均炎症强度
                region_mask = (labels == i).astype(np.uint8)
                severity = cv2.mean(intensity_map, mask=region_mask)[0]

                centers.append((x, y, severity, area))

        # 按严重程度排序
        centers.sort(key=lambda x: x[2] * x[3], reverse=True)

        return centers

    def draw_custom_arrow(self, image, start_point, end_point, color, thickness=2):
        """
        绘制自定义的医学风格箭头（类似病理图中的标注箭头）

        Args:
            image: 图像
            start_point: 箭头起点 (x, y)
            end_point: 箭头终点 (x, y)
            color: 颜色 BGR
            thickness: 线条粗细
        """
        # 计算箭头方向
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        angle = np.arctan2(dy, dx)

        # 箭头长度
        arrow_length = np.sqrt(dx**2 + dy**2)

        # 绘制箭头主干（实心线）
        cv2.line(image, start_point, end_point, color, thickness, cv2.LINE_AA)

        # 箭头头部参数
        arrow_head_length = min(20, arrow_length * 0.3)  # 箭头头部长度
        arrow_head_width = 12  # 箭头头部宽度

        # 计算箭头头部的三个顶点
        # 箭头尖端就是终点
        tip = end_point

        # 左侧点
        left_x = int(end_point[0] - arrow_head_length * np.cos(angle) - arrow_head_width/2 * np.sin(angle))
        left_y = int(end_point[1] - arrow_head_length * np.sin(angle) + arrow_head_width/2 * np.cos(angle))

        # 右侧点
        right_x = int(end_point[0] - arrow_head_length * np.cos(angle) + arrow_head_width/2 * np.sin(angle))
        right_y = int(end_point[1] - arrow_head_length * np.sin(angle) - arrow_head_width/2 * np.cos(angle))

        # 绘制实心三角形箭头头部
        arrow_head_points = np.array([tip, (left_x, left_y), (right_x, right_y)], dtype=np.int32)
        cv2.fillPoly(image, [arrow_head_points], color, cv2.LINE_AA)

    def draw_arrows(self, image, centers, max_arrows=5):
        """
        在图像上绘制指向炎症区域的红色箭头（医学病理图风格）

        Args:
            image: 原始图像
            centers: 炎症中心点列表
            max_arrows: 最多绘制的箭头数量

        Returns:
            annotated_image: 标注后的图像
        """
        annotated = image.copy()
        h, w = image.shape[:2]

        # 只标注最严重的几个区域
        for idx, (x, y, severity, area) in enumerate(centers[:max_arrows]):
            # 计算箭头起点（紧凑型，短箭头，靠近目标）
            # 根据区域位置选择合适的箭头方向
            arrow_distance = 60  # 箭头长度（从起点到终点的距离）

            if x < w // 3:
                # 左侧区域，箭头从左指向右
                start_x, start_y = x - arrow_distance, y
            elif x > 2 * w // 3:
                # 右侧区域，箭头从右指向左
                start_x, start_y = x + arrow_distance, y
            elif y < h // 3:
                # 上方区域，箭头从上指向下
                start_x, start_y = x, y - arrow_distance
            else:
                # 下方区域，箭头从下指向上
                start_x, start_y = x, y + arrow_distance

            # 确保起点在图像范围内
            start_x = max(20, min(w - 20, start_x))
            start_y = max(20, min(h - 20, start_y))

            # 箭头颜色
            arrow_color = (0, 0, 0)  # 黑色箭头（更接近医学图像风格）
            outline_color = (255, 255, 255)  # 白色轮廓
            circle_color = (0, 0, 255)  # 红色圆圈 BGR

            # 先绘制红色圆圈标记（在箭头终点）
            circle_radius = 25  # 圆圈半径
            circle_thickness = 3  # 圆圈线条粗细

            # 绘制白色外圈（增强对比度）
            cv2.circle(annotated, (x, y), circle_radius + 1, outline_color, circle_thickness + 2, cv2.LINE_AA)

            # 绘制红色圆圈
            cv2.circle(annotated, (x, y), circle_radius, circle_color, circle_thickness, cv2.LINE_AA)

            # 绘制白色轮廓箭头（增强可见性）
            self.draw_custom_arrow(annotated, (start_x, start_y), (x, y), outline_color, thickness=4)

            # 绘制黑色箭头主体
            self.draw_custom_arrow(annotated, (start_x, start_y), (x, y), arrow_color, thickness=2)

        return annotated

    def process_image(self, image_path, max_arrows=5, show_debug=False):
        """
        处理单张图像

        Args:
            image_path: 图像文件路径
            max_arrows: 最多标注的箭头数量
            show_debug: 是否显示调试信息

        Returns:
            annotated_image: 标注后的图像
        """
        # 读取图像
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"无法读取图像: {image_path}")
            return None

        print(f"处理图像: {image_path.name}")

        # 检测炎症区域
        mask, intensity_map = self.detect_inflammation_regions(image)

        # 查找严重区域
        centers = self.find_severe_regions(mask, intensity_map)
        print(f"  检测到 {len(centers)} 个可能的炎症区域")

        # 绘制箭头
        annotated = self.draw_arrows(image, centers, max_arrows)

        # 保存结果
        output_path = self.output_folder / f"annotated_{image_path.name}"
        cv2.imwrite(str(output_path), annotated)
        print(f"  已保存到: {output_path}")

        # 调试模式：显示中间结果
        if show_debug:
            debug_output = self.output_folder / f"debug_{image_path.name}"
            fig, axes = plt.subplots(2, 2, figsize=(15, 15))

            axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            axes[0, 0].set_title('Original Image')
            axes[0, 0].axis('off')

            axes[0, 1].imshow(mask, cmap='gray')
            axes[0, 1].set_title('Inflammation Mask')
            axes[0, 1].axis('off')

            axes[1, 0].imshow(intensity_map, cmap='hot')
            axes[1, 0].set_title('Intensity Map')
            axes[1, 0].axis('off')

            axes[1, 1].imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
            axes[1, 1].set_title('Annotated Result')
            axes[1, 1].axis('off')

            plt.tight_layout()
            plt.savefig(debug_output)
            plt.close()
            print(f"  调试图已保存到: {debug_output}")

        return annotated

    def process_all_images(self, max_arrows=5, show_debug=False):
        """
        处理输入文件夹中的所有图像

        Args:
            max_arrows: 每张图像最多标注的箭头数量
            show_debug: 是否生成调试图像
        """
        # 支持的图像格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

        image_files = []
        for ext in image_extensions:
            image_files.extend(self.input_folder.glob(f'*{ext}'))
            image_files.extend(self.input_folder.glob(f'*{ext.upper()}'))

        if not image_files:
            print(f"在 {self.input_folder} 中没有找到图像文件")
            print(f"支持的格式: {', '.join(image_extensions)}")
            return

        print(f"找到 {len(image_files)} 张图像，开始处理...\n")

        for image_path in image_files:
            self.process_image(image_path, max_arrows, show_debug)
            print()

        print("=" * 50)
        print("处理完成！")
        print(f"标注后的图像已保存到: {self.output_folder}")


def main():
    """主函数"""
    print("=" * 50)
    print("病理图像炎症区域检测和标注工具")
    print("Pathology Inflammation Detection Tool")
    print("=" * 50)
    print()

    # 创建分析器实例
    analyzer = PathologyAnalyzer(
        input_folder="input_images",
        output_folder="output_images"
    )

    # 处理所有图像
    # max_arrows: 每张图最多标注几个区域
    # show_debug: 是否生成包含中间步骤的调试图
    analyzer.process_all_images(max_arrows=5, show_debug=True)


if __name__ == "__main__":
    main()
