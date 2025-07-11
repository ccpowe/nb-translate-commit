# AI-Powered Jupyter Notebook Translator

一个使用LangGraph和多模态LLM的智能Jupyter Notebook翻译器，可以将Jupyter Notebook中的文本翻译成多种语言，并为图片生成描述，为代码添加注释。

## 功能特性

- 🌍 **多语言翻译支持**: 支持中文、英文、西班牙语、法语、德语、日语、韩语、俄语、葡萄牙语、意大利语等
- 📝 **Markdown单元格处理**: 翻译文本内容，保持Markdown格式
- 🖼️ **图片描述生成**: 为图片自动生成目标语言的详细描述 
- 💻 **代码单元格增强**: 添加详细注释，翻译现有注释
- 🔄 **LangGraph工作流**: 使用状态机管理整个翻译流程
- 🤖 **多模态AI**: 通过OpenRouter使用Gemini 2.5 Flash模型

## 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd nb-translate-commit
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下配置：
```env
API_KEY=sk-or-v1-3a6118b505755ea749f953ef5dfbade9b18bf5e7cd1b070
MODEL_NAME=google/gemini-2.5-flash-preview-05-20
MODEL_BASE_URL=https://openrouter.ai/api/v1
```

## 使用方法

### 基本用法

```bash
python main.py notebook.ipynb --target-language Chinese
```

### 命令行选项

```bash
python main.py input.ipynb [选项]

参数:
  input.ipynb              输入的Jupyter Notebook文件路径

选项:
  --target-language, -t    目标翻译语言 (默认: Chinese)
  --check-config, -c       检查配置后退出
  --version, -v            显示版本信息
  --help, -h               显示帮助信息
```

### 使用示例

```bash
# 翻译成中文
python main.py example.ipynb --target-language Chinese

# 翻译成西班牙语
python main.py notebook.ipynb --target-language Spanish

# 翻译成法语
python main.py /path/to/notebook.ipynb --target-language French

# 检查配置
python main.py --check-config
```

## 支持的语言

- Chinese (中文)
- English (英语)
- Spanish (西班牙语)
- French (法语)
- German (德语)
- Japanese (日语)
- Korean (韩语)
- Russian (俄语)
- Portuguese (葡萄牙语)
- Italian (意大利语)

## 输出格式

翻译后的notebook文件将保存为 `原文件名_translated.ipynb`

### Markdown单元格处理示例

**原始内容:**
```markdown
# Data Analysis
This is a sample data analysis notebook.
![Chart](chart.png)
```

**翻译后内容:**
```markdown
# Data Analysis
**翻译：** 数据分析
This is a sample data analysis notebook.
**翻译：** 这是一个示例数据分析笔记本。
![Chart](chart.png)
**图片说明：** 这是一个显示数据趋势的图表，包含了多个数据系列...
```

### 代码单元格处理示例

**原始代码:**
```python
import pandas as pd
df = pd.read_csv('data.csv')
```

**增强后代码:**
```python
# 导入pandas库用于数据处理
import pandas as pd
# 从CSV文件读取数据到DataFrame中
df = pd.read_csv('data.csv')
```

## 项目结构

```
nb-translate-commit/
├── main.py                 # 命令行入口
├── workflow.py             # LangGraph工作流定义
├── state.py                # 状态数据结构
├── config.py               # 配置管理
├── llm_client.py           # OpenRouter API客户端
├── notebook_io.py          # Notebook读写操作
├── cell_processors.py      # 单元格处理逻辑
├── requirements.txt        # 依赖列表
├── development_plan.md     # 开发计划
└── README.md              # 项目说明
```

## 技术架构

- **LangGraph**: 状态机工作流管理
- **OpenRouter**: 统一的LLM API接口
- **Gemini 2.5 Flash**: 多模态AI模型
- **nbformat**: Jupyter Notebook文件处理

## 开发指南

项目使用LangGraph构建状态机工作流：

1. `load_and_parse_notebook`: 加载并解析notebook
2. `route_cell_processing`: 路由到相应的处理节点
3. `process_markdown_cell`: 处理Markdown单元格
4. `process_code_cell`: 处理代码单元格
5. `rebuild_notebook`: 重建并保存notebook

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ❌ Configuration error: API_KEY is required
   ```
   解决方案：检查 `.env` 文件中的API密钥配置

2. **网络连接问题**
   ```
   ❌ Translation failed: Connection error
   ```
   解决方案：检查网络连接和API服务状态

3. **图片加载失败**
   ```
   ⚠️ Could not process image: Image file not found
   ```
   解决方案：确保图片路径正确或图片文件存在

### 调试

使用 `--check-config` 参数检查配置：
```bash
python main.py --check-config
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License 