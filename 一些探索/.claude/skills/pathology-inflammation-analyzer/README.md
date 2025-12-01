# Pathology Inflammation Analyzer Skill

这是一个 Claude Code 技能包，用于自动分析病理图像中的炎症区域。

## 安装方法

### 方法 1: 项目级别（推荐用于团队协作）

将此技能添加到您的项目中：

```bash
# 如果已有 .claude/skills 目录，直接复制
cp -r .claude/skills/pathology-inflammation-analyzer /path/to/your/project/.claude/skills/

# 提交到版本控制
git add .claude/skills/pathology-inflammation-analyzer
git commit -m "Add pathology inflammation analyzer skill"
git push
```

团队成员拉取代码后，此技能会自动可用。

### 方法 2: 全局个人级别（跨所有项目使用）

将此技能复制到您的个人配置目录：

**Windows**:
```bash
mkdir -p %USERPROFILE%\.claude\skills
xcopy /E /I .claude\skills\pathology-inflammation-analyzer %USERPROFILE%\.claude\skills\pathology-inflammation-analyzer
```

**macOS/Linux**:
```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/pathology-inflammation-analyzer ~/.claude/skills/
```

安装后，此技能将在您的所有项目中可用。

## 使用方法

安装后，只需向 Claude Code 发送相关请求，技能会自动激活：

```
"请分析这张病理图像"
"标注炎症区域"
"检测病理切片中的炎症损伤"
```

无需手动调用，Claude 会根据您的需求自动使用该技能。

## 验证安装

检查技能是否已安装：

1. 在 Claude Code 中询问：
   ```
   What skills are available?
   ```

2. 您应该看到 `pathology-inflammation-analyzer` 出现在列表中

## 技能内容

此技能包含以下文件：

- `SKILL.md` - 主要技能定义和使用说明
- `reference.md` - 技术参考文档（HE 染色、色彩空间、OpenCV 函数）
- `examples.md` - 详细使用示例和场景
- `README.md` - 安装和快速开始指南（本文件）

## 功能特性

- ✅ 自动检测病理切片中的炎症区域
- ✅ 基于颜色和细胞密度的智能分析
- ✅ 医学标准的箭头和圆圈标注
- ✅ 批量处理多张图像
- ✅ 生成详细的调试信息
- ✅ 可调节的检测参数

## 系统要求

- Python 3.8+
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0

依赖会在首次使用时自动安装。

## 快速开始示例

```
用户: 请帮我分析这张病理切片图像
[上传图像]

Claude: 我会使用病理图像分析工具来检测炎症区域...
[自动创建项目结构]
[保存图像]
[运行分析]
[展示结果]
```

## 自定义配置

如果需要修改默认参数，可以编辑技能中的代码建议：

- 标注数量：`max_arrows=5` (改为 3-10)
- 检测灵敏度：`min_area=500` (减小检测更多小区域)
- 箭头样式：`circle_radius=25`, `arrow_distance=60`

## 故障排除

### 问题：技能没有自动激活

**解决方案**：
1. 确认文件已正确复制到 `.claude/skills/` 目录
2. 检查 `SKILL.md` 文件中的 YAML frontmatter 格式
3. 重启 Claude Code

### 问题：找不到 Python 或依赖库

**解决方案**：
```bash
# 安装 Python（如果未安装）
# Windows: 从 python.org 下载
# macOS: brew install python
# Linux: sudo apt install python3

# 安装依赖
pip install opencv-python numpy matplotlib
```

### 问题：检测效果不理想

**解决方案**：
1. 查看生成的 debug 图像了解检测过程
2. 根据 `reference.md` 调整参数
3. 确认图像是 HE 染色
4. 参考 `examples.md` 中的调优建议

## 更新日志

### v1.0 (2025-12-01)
- 初始版本发布
- 支持 HE 染色图像分析
- 自动检测和标注炎症区域
- 医学风格的箭头和圆圈标记
- 完整的文档和示例

## 贡献

欢迎提出改进建议！如果您：
- 发现了 bug
- 有新功能建议
- 想要分享优化参数
- 需要支持其他染色方法

请通过 Claude Code 向我反馈。

## 许可

此技能供研究和教育使用。

⚠️ **重要**: 本工具不能用于临床诊断。所有结果需要专业病理医生审核。

## 联系方式

- 技术支持：通过 Claude Code 对话获取帮助
- 文档：查看 `SKILL.md` 获取完整说明
- 示例：查看 `examples.md` 获取使用案例

---

**创建时间**: 2025-12-01
**作者**: Claude Code AI Assistant
**版本**: 1.0
