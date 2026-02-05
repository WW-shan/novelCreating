# ✅ 启动前检查清单

运行小说生成器前，请确保以下项目都已完成：

## 📋 必需项（必须完成）

### 1. 环境配置

- [ ] **Python 版本**: 运行 `python3 --version`，确保 ≥ 3.10
  ```bash
  python3 --version
  # 应显示: Python 3.10.x 或更高
  ```

- [ ] **虚拟环境**: 确认 `venv/` 目录存在
  ```bash
  ls -d venv/
  # 应显示: venv/
  ```

- [ ] **依赖安装**: 运行以下命令确认
  ```bash
  source venv/bin/activate
  python3 -c "import langchain_anthropic; print('✅ 依赖已安装')"
  ```

### 2. API 配置

- [ ] **API Key**: 检查 `.env` 文件存在且配置正确
  ```bash
  cat .env | grep ANTHROPIC_API_KEY
  # 应显示你的 API Key
  ```

- [ ] **API 连接测试**: 运行测试脚本
  ```bash
  ./test_api.sh
  # 应显示成功响应，无错误
  ```

### 3. 小说配置

- [ ] **配置文件**: 确认配置文件存在
  ```bash
  ls bible/novel_config_latest.yaml
  # 应显示文件路径
  ```

- [ ] **如果文件不存在**: 运行配置向导
  ```bash
  python3 configure_novel.py
  # 按提示完成配置
  ```

## 🔧 系统验证（推荐完成）

### 4. 节点配置验证

- [ ] **运行验证脚本**
  ```bash
  ./verify_config.sh
  ```

- [ ] **确认输出包含**:
  ```
  ✅ 所有节点已统一使用 Sonnet 4.5
  ✅ 已添加超时和重试保护
  ```

### 5. 导入测试

- [ ] **测试节点导入**
  ```bash
  source venv/bin/activate
  python3 -c "
  from src.nodes.planner import planner_node
  from src.nodes.writer import writer_node
  from src.nodes.critic import critic_node
  from src.nodes.memory import memory_update_node
  print('✅ 所有节点导入成功')
  "
  ```

## 📁 目录结构检查

- [ ] **核心目录存在**
  ```bash
  ls -d src/ bible/ manuscript/ logs/
  # 应全部显示
  ```

- [ ] **节点文件完整**
  ```bash
  ls src/nodes/*.py
  # 应显示: planner.py writer.py critic.py memory.py
  ```

## ⚡ 可选优化（建议完成）

### 6. 首次测试建议

- [ ] **设置测试章节数**: 编辑配置文件
  ```bash
  # 编辑 bible/novel_config_latest.yaml
  # 将 target_chapters 设为 1
  nano bible/novel_config_latest.yaml
  ```
  
  修改为：
  ```yaml
  novel:
    target_chapters: 1  # 先测试生成 1 章
  ```

### 7. 清理旧数据（如果需要）

- [ ] **删除旧的状态数据库**（可选）
  ```bash
  rm -f novel_state.db*
  # 这会让生成从头开始
  ```

- [ ] **清理旧章节**（可选）
  ```bash
  rm -rf manuscript/*/
  # 删除所有旧的生成结果
  ```

## 🎯 最终检查

完成所有必需项后，运行这个快速检查：

```bash
#!/bin/bash
echo "🔍 最终检查..."
echo ""

# 检查 Python
python3 --version \u003e /dev/null 2\u003e\u00261 \u0026\u0026 echo "✅ Python 已安装" || echo "❌ Python 未安装"

# 检查虚拟环境
[ -d venv ] \u0026\u0026 echo "✅ 虚拟环境存在" || echo "❌ 虚拟环境不存在"

# 检查 .env
[ -f .env ] \u0026\u0026 echo "✅ .env 文件存在" || echo "❌ .env 文件不存在"

# 检查配置
[ -f bible/novel_config_latest.yaml ] \u0026\u0026 echo "✅ 配置文件存在" || echo "❌ 配置文件不存在"

# 检查节点
[ -f src/nodes/writer.py ] \u0026\u0026 echo "✅ 节点文件存在" || echo "❌ 节点文件不存在"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 统计
missing=0
[ ! -d venv ] \u0026\u0026 ((missing++))
[ ! -f .env ] \u0026\u0026 ((missing++))
[ ! -f bible/novel_config_latest.yaml ] \u0026\u0026 ((missing++))

if [ $missing -eq 0 ]; then
    echo "✅ 所有检查通过！可以开始生成"
    echo ""
    echo "运行: ./run_novel.sh"
else
    echo "⚠️  有 $missing 项未完成，请先完成上述步骤"
fi
```

将上面的脚本保存为 `quick_check.sh` 并运行：

```bash
chmod +x quick_check.sh
./quick_check.sh
```

## 🚀 准备就绪？

如果所有必需项都已完成，运行：

```bash
./run_novel.sh
```

享受你的 AI 小说生成之旅！ 🎉

---

## 📚 相关文档

遇到问题？查看这些文档：

- `QUICKSTART_NEW.md` - 快速开始指南
- `SUMMARY.md` - 系统概览
- `WORKFLOW.md` - 详细工作流程
- `FIX_TIMEOUT.md` - 故障排除
- `README.md` - 项目说明

---

**最后更新**: 2026-02-04
