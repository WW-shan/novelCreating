# 📚 快速参考

## 一键命令

```bash
# 最常用的命令
./novel.sh new       # 创建新小说
./novel.sh generate  # 生成小说
./novel.sh config    # 查看配置
./novel.sh switch    # 切换小说
```

---

## 所有命令

### 主要功能
| 命令 | 简写 | 说明 |
|------|------|------|
| `./novel.sh generate` | `g` | 生成小说 |
| `./novel.sh config` | `c` | 查看当前配置 |
| `./novel.sh new` | `n` | 创建新配置 |
| `./novel.sh switch` | `s` | 切换配置 |

### 测试
| 命令 | 说明 |
|------|------|
| `./novel.sh test` | 运行所有测试 |
| `./novel.sh test-api` | API 连接测试 |
| `./novel.sh test-flow` | 流程测试（生成1章） |

### 维护
| 命令 | 说明 |
|------|------|
| `./novel.sh clean` | 清理生成状态 |
| `./novel.sh status` | 查看系统状态 |
| `./novel.sh help` | 显示帮助 |

---

## 常见场景

### 第一次使用

```bash
# 1. 创建配置
./novel.sh new

# 2. 生成小说
./novel.sh generate

# 3. 查看结果
ls manuscript/
```

### 创建多本小说

```bash
# 创建第一本
./novel.sh new
# 配置完成后...

# 创建第二本
./novel.sh new
# 配置完成后...

# 切换生成
./novel.sh switch     # 选择要生成的
./novel.sh generate   # 开始生成
```

### 中断后重新开始

```bash
./novel.sh clean      # 清除旧状态
./novel.sh generate   # 重新生成
```

---

## 最新更新 (2026-02-04)

### ✅ 已修复
- 核心 Bug 修复: 断点续传、模块导入、环境变量
- 字数控制优化: 2000-2500 字/章
- JSON 解析增强: 95%+ 成功率
- Switch 功能修复: 正确显示所有配置

### 📄 详细文档
- `BUG_FIXES_2026-02-04.md` - 核心 Bug 修复
- `WORD_COUNT_OPTIMIZATION_2026-02-04.md` - 字数控制优化
- `JSON_PARSING_FIX_2026-02-04.md` - JSON 解析修复
- `SYSTEM_STATUS_2026-02-04.md` - 系统总览

---

**记住**: `./novel.sh` 是您唯一需要的命令！
