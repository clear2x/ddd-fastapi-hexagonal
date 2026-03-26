# 贡献说明

## 分支约定

当前建议的长期工作分支：
- `feat/domain-core`
- `feat/http-api`
- `feat/tests-docs-ci`

## 规则

- Domain 层不要引入 FastAPI、SQLAlchemy 等框架依赖
- Application 层扩展后，尽量保持一个文件一个用例
- 任何行为变更，都应同步补测试或更新测试
- README 与 docs 要和真实 API、真实结构保持一致
- **所有文档与代码注释统一使用中文**
- 类名、函数名、模块名、API 路径保持英文，便于开源协作与 Python 项目习惯对齐

## 提交 PR 前

- 跑测试
- 检查 API 示例是否仍然正确
- 检查架构边界是否仍然清晰
- 检查新增文档与注释是否使用中文
