# 病理图像分析技术参考

## HE 染色特征

### Hematoxylin（苏木精）- 蓝紫色
- 染色对象：细胞核、钙盐、细菌
- 颜色：蓝色到紫色
- 用途：显示细胞核的形态和分布

### Eosin（伊红）- 粉红色
- 染色对象：细胞质、胶原纤维、红细胞
- 颜色：粉红色到红色
- 用途：显示细胞质和纤维结构

## 炎症的病理学特征

### 急性炎症
- 血管扩张和充血
- 中性粒细胞浸润（主要）
- 组织水肿
- 颜色特征：深紫色（细胞密集）+ 粉红色（水肿）

### 慢性炎症
- 淋巴细胞和巨噬细胞浸润
- 纤维组织增生
- 血管新生
- 颜色特征：紫色细胞聚集 + 粉色纤维化

### 肉芽肿性炎症
- 上皮样细胞聚集
- 多核巨细胞
- 纤维包膜
- 颜色特征：圆形紫色细胞团

## 色彩空间参考

### HSV 色彩空间
- H (Hue): 色调 (0-180 in OpenCV)
- S (Saturation): 饱和度 (0-255)
- V (Value): 明度 (0-255)

### 紫色范围（炎症检测）
```python
# 方案 1: 标准紫色
lower_purple1 = np.array([120, 30, 30])
upper_purple1 = np.array([160, 255, 255])

# 方案 2: 深紫色（高密度细胞）
lower_purple2 = np.array([140, 50, 50])
upper_purple2 = np.array([180, 255, 200])
```

## 细胞密度分析

### 高密度区域特征
- 灰度值：< 180（较暗）
- 细胞核密集排列
- 核间距减小
- 常见于：炎症浸润、肿瘤组织

### 低密度区域特征
- 灰度值：> 200（较亮）
- 细胞稀疏
- 间质丰富
- 常见于：正常结缔组织、水肿

## 形态学操作参考

### 闭运算 (Morphological Closing)
- 作用：填充小孔、连接邻近区域
- 核大小：5x5 或 7x7
- 用途：去除炎症区域内的小空隙

### 开运算 (Morphological Opening)
- 作用：去除小的噪声点
- 核大小：3x3 或 5x5
- 用途：清除误检的小区域

## 区域筛选标准

### 最小区域面积
```python
min_area = 500  # 像素
```
- 太小（< 300）：可能包含噪声
- 适中（500-1000）：平衡准确性和召回率
- 太大（> 2000）：可能遗漏小的炎症灶

### 严重程度评分
```python
severity_score = intensity * area
```
- intensity: 平均颜色强度（0-255）
- area: 区域像素面积
- 综合考虑"程度"和"范围"

## 常见组织类型

### 上皮组织
- 细胞排列整齐
- 细胞间隙小
- 基底膜清晰
- 炎症时：细胞浸润、结构破坏

### 结缔组织
- 细胞稀疏
- 纤维丰富（粉红色）
- 血管分布
- 炎症时：水肿、纤维增生

### 淋巴组织
- 淋巴细胞密集（深紫色）
- 淋巴滤泡结构
- 生发中心
- 炎症时：滤泡增生、浸润扩散

## OpenCV 函数参考

### cv2.inRange()
```python
mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
```
创建颜色范围掩码

### cv2.morphologyEx()
```python
# 闭运算
closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# 开运算
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
```

### cv2.connectedComponentsWithStats()
```python
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
```
查找连通区域及其属性

### cv2.GaussianBlur()
```python
blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
```
高斯模糊，用于生成强度图

## 可视化配色建议

### 标注颜色
- 箭头主体：黑色 (0, 0, 0)
- 箭头轮廓：白色 (255, 255, 255)
- 圆圈标记：红色 (0, 0, 255) BGR
- 背景对比：白色外圈

### 热图配色
- matplotlib.cm.hot：火焰色
- matplotlib.cm.jet：彩虹色
- matplotlib.cm.viridis：蓝绿色（色盲友好）

## 图像质量评估

### 良好图像特征
- 分辨率：≥ 1024x768
- 对焦清晰：边缘锐利
- 曝光适中：无过曝/欠曝
- 染色均匀：色彩一致

### 问题图像特征
- 模糊：运动模糊、失焦
- 色偏：扫描仪颜色不准
- 伪影：气泡、折痕、污染
- 不均：染色不均、厚度不一

## 误差来源

### 技术性误差
- 切片厚度不均
- 染色时间差异
- 扫描参数不同
- 压缩损失（JPEG）

### 生物学变异
- 个体差异
- 取材部位
- 病变阶段
- 组织固定质量

## 性能优化建议

### 计算效率
- 降采样后处理：resize() 到合适大小
- ROI 选择：只处理感兴趣区域
- 批处理：一次处理多张图像

### 内存管理
- 及时释放大图像：del large_image
- 使用生成器处理序列
- 限制并发处理数量

## 参考文献

### 病理学基础
- Robbins Basic Pathology (病理学基础)
- WHO Classification of Tumours (WHO 肿瘤分类)

### 图像处理
- Digital Image Processing (Gonzalez & Woods)
- OpenCV Documentation (opencv.org)

### 医学图像分析
- Medical Image Analysis (Elsevier Journal)
- IEEE Transactions on Medical Imaging
