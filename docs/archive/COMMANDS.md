# 🎯 常用命令速查表

## 快速开始（三步走）

```bash
# 1️⃣ 配置小说
python3 configure_novel.py

# 2️⃣ 验证系统
./quick_check.sh

# 3️⃣ 生成小说
./run_novel.sh
```

---

## 📋 配置相关

```bash
# 创建新配置（交互式）
python3 configure_novel.py

# 查看当前配置
cat bible/novel_config_latest.yaml

# 编辑配置
vim bible/novel_config_latest.yaml
# 或
nano bible/novel_config_latest.yaml

# 列出所有配置文件
ls -lh bible/*.yaml
```

---

## 🔍 验证和测试

```bash
# 快速系统检查
./quick_check.sh

# 验证节点配置
./verify_config.sh

# 测试 API 连接
./test_api.sh

# Python 导入测试
source venv/bin/activate && python3 -c "
from src.nodes.planner import planner_node
from src.nodes.writer import writer_node
print('✅ 节点导入成功')
"
```

---

## 🚀 生成小说

```bash
# 生成小说（使用当前配置）
./run_novel.sh

# 或使用 Python 直接运行
source venv/bin/activate
python3 src/main.py

# 后台运行（不推荐）
nohup ./run_novel.sh > output.log 2>&1 &
```

---

## 📁 查看结果

```bash
# 列出生成的小说
ls manuscript/

# 查看某个小说的所有章节
ls manuscript/[小说名]/

# 读取第一章
cat manuscript/[小说名]/chapter_001.md

# 查看世界状态
cat bible/[小说名]_world_state.json

# 查看世界状态（格式化）
cat bible/[小说名]_world_state.json | python3 -m json.tool
```

---

## 🧹 清理和重置

```bash
# 清除状态数据库（重新开始）
rm -f novel_state.db*

# 删除某个小说的章节
rm -rf manuscript/[小说名]/

# 清除所有生成的内容
rm -rf manuscript/*/

# 删除旧配置（保留最新）
cd bible
ls -t novel_config*.yaml | tail -n +2 | xargs rm
cd ..
```

---

## 🔧 环境管理

```bash
# 激活虚拟环境
source venv/bin/activate

# 退出虚拟环境
deactivate

# 安装/更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 查看已安装的包
pip list

# 检查 Python 版本
python3 --version
```

---

## 📊 查看状态

```bash
# 查看数据库内容
sqlite3 novel_state.db "SELECT * FROM checkpoints LIMIT 5;"

# 查看数据库大小
ls -lh novel_state.db*

# 查看日志文件
ls -lh logs/

# 统计生成的章节数
find manuscript/ -name "chapter_*.md" | wc -l

# 统计总字数（近似）
cat manuscript/[小说名]/chapter_*.md | wc -m
```

---

## 🎨 调整配置参数

```bash
# 仅生成 1 章（测试用）
# 编辑 bible/novel_config_latest.yaml
# 修改: target_chapters: 1

# 快速编辑章节数
sed -i 's/target_chapters: .*/target_chapters: 1/' bible/novel_config_latest.yaml

# 提高随机性
# 编辑 bible/novel_config_latest.yaml
# 修改: randomness_level: high
# 修改: writer_temp: 0.9
```

---

## 🐛 故障排除

```bash
# 检查 API Key
cat .env | grep ANTHROPIC_API_KEY

# 测试 API 连接（详细输出）
./test_api.sh

# 检查节点配置
./verify_config.sh

# 查看最近的错误
tail -50 logs/*.log

# 检查 Python 路径
which python3

# 检查虚拟环境
ls -la venv/bin/
```

---

## 📚 文档查看

```bash
# 查看所有文档
ls -lh *.md

# 快速预览
head -30 README.md

# 在终端查看 Markdown（如果安装了 glow）
glow README.md

# 或使用 cat
cat QUICKSTART_NEW.md
```

---

## 💡 高级用法

```bash
# 批量生成不同版本
for i in {1..3}; do
    echo "生成第 $i 版本..."
    ./run_novel.sh
    mv manuscript/[小说名] manuscript/[小说名]_v$i
    rm novel_state.db*
done

# 监控生成进度（另一个终端）
watch -n 5 'ls -lh manuscript/[小说名]/'

# 导出配置为 JSON
cat bible/novel_config_latest.yaml | python3 -c "
import sys, yaml, json
print(json.dumps(yaml.safe_load(sys.stdin), indent=2))
"

# 合并所有章节为一个文件
cat manuscript/[小说名]/chapter_*.md > full_novel.md
```

---

## 🔄 Git 操作（如果使用版本控制）

```bash
# 初始化 Git（如果还没有）
git init

# 添加 .gitignore
echo "venv/" >> .gitignore
echo "novel_state.db*" >> .gitignore
echo ".env" >> .gitignore
echo "manuscript/" >> .gitignore

# 提交配置
git add bible/*.yaml
git commit -m "Add novel configuration"

# 查看状态
git status

# 查看修改
git diff
```

---

## 📦 备份和恢复

```bash
# 备份整个项目
tar -czf novel_backup_$(date +%Y%m%d).tar.gz \
    bible/ manuscript/ .env

# 仅备份生成的内容
tar -czf chapters_$(date +%Y%m%d).tar.gz manuscript/

# 恢复备份
tar -xzf novel_backup_20260204.tar.gz

# 列出备份内容
tar -tzf novel_backup_20260204.tar.gz
```

---

## 🎬 一键操作脚本

```bash
# 创建快速重启脚本
cat > restart.sh << 'SCRIPT'
#!/bin/bash
echo "🔄 重启生成..."
rm -f novel_state.db*
./run_novel.sh
SCRIPT
chmod +x restart.sh

# 使用
./restart.sh
```

---

## 📈 性能监控

```bash
# 监控系统资源
top -p $(pgrep -f "python3 src/main.py")

# 查看内存使用
ps aux | grep "python3 src/main.py"

# 监控网络（API 请求）
netstat -an | grep ESTABLISHED | grep 443
```

---

## 🎯 常见任务组合

### 首次使用

```bash
python3 configure_novel.py
./quick_check.sh
./verify_config.sh
./test_api.sh
./run_novel.sh
```

### 重新生成

```bash
rm novel_state.db*
./run_novel.sh
```

### 完整验证

```bash
./quick_check.sh
./verify_config.sh
./test_api.sh
echo "✅ 验证完成"
```

### 查看最新结果

```bash
novel=$(ls -t bible/*.yaml | head -1 | sed 's/.*novel_config_//' | sed 's/_[0-9]*.yaml//')
ls -lh manuscript/$novel/
cat manuscript/$novel/chapter_001.md | head -50
```

---

## 🆘 紧急情况

```bash
# 系统卡住 - 找到并终止进程
ps aux | grep python3 | grep main.py
kill -9 <PID>

# 数据库损坏 - 删除并重新开始
rm -f novel_state.db*
./run_novel.sh

# API 配置错误 - 重新配置
cp .env.example .env
vim .env  # 填入正确的 API Key
./test_api.sh
```

---

**提示**: 复制这些命令到终端直接运行！

**文档版本**: 2.0  
**最后更新**: 2026-02-04
