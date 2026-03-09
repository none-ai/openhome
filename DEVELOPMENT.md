# OpenHome 开发规范

## 陛下旨意

> **所有代码必须使用 Claude Code 进行代码编写**

根据陛下旨意，本项目的所有代码编写工作必须使用 Claude Code (claude) 进行，禁止使用其他 AI 代码生成工具。

> **所有项目开发时都必须进行测试，不能写完就提交**

根据陛下旨意，每次代码提交前都必须进行测试验证，确保代码质量。

## 开发要求

1. **代码编写**：所有新增代码必须通过 Claude Code 生成
2. **代码审查**：使用 Claude Code 进行代码审查和优化
3. **问题修复**：使用 Claude Code 诊断和修复问题
4. **测试验证**：所有代码提交前必须进行测试验证，禁止写完就提交

## 测试要求

### 测试原则
- **先测试后提交**：每次代码修改完成后，必须运行测试验证通过后方可提交
- **测试覆盖率**：新增功能必须包含对应的单元测试或集成测试
- **回归测试**：修改代码后应运行现有测试确保没有引入新问题

### 测试执行流程

```bash
# 1. 开发完成后，运行测试
pytest

# 2. 如果有测试覆盖检查，运行覆盖率
pytest --cov

# 3. 测试全部通过后，方可提交代码
git add .
git commit -m "描述你的修改"
git push
```

### 测试文件命名规范
- 单元测试：`tests/test_*.py` 或 `tests/*_test.py`
- 集成测试：`tests/integration/test_*.py`
- 测试文件名应与被测试模块对应

### 提交前检查清单
- [ ] 所有单元测试通过
- [ ] 新增功能有对应的测试用例
- [ ] 运行 `pytest` 无报错
- [ ] 代码符合项目规范

## 使用 Claude Code

### 基本命令

```bash
# 启动 Claude Code 交互式会话
claude

# 使用 Claude Code 执行特定任务
claude -p "请帮我写一个函数..."

# 使用 Claude Code 读取和分析代码
claude -p "请分析 app.py 的代码结构"
```

### 在本项目中使用

```bash
cd /home/stlin-claw/.openclaw/workspace-taizi/openhome

# 启动 Claude Code
claude

# 或者直接让 Claude Code 读取和修改文件
claude -p "请阅读 app.py 并添加一个新功能..."
```

## 注意事项

- 保持代码高质量和一致性
- 遵循项目现有的代码风格
- 确保代码有适当的注释和文档

---

**旨意日期**：2026-03-09
