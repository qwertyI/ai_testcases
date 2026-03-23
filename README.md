# ai_testcases
借助AI生成完整的测试用例

## 快速开始
1. 将 `gen-functional-testcase` 和 `requirement-to-features` 放入 ClaudeCode skills 目录下面。
2. 启动 ClaudeCode 后，调用 `/requirement-to-features` 同时，将 「场次模板配置PRD文档.md」 放入后开始执行。
3. 等待输出功能文档。
4. 调用 `/gen-functional-testcase` 生成测试用例。


## 配置适合你的内容

1. 新建 `~/testcases` 文件夹，或者修改 `requirement-to-features/Skill.md` 中的测试用例文件夹路径，以适配你自己的需要。
2. 修改 `requirement-to-features/module_knowledge` 中的模块知识，这里只需要你将模块中某些内容的操作流程记录下来即可。
3. 修改 `gen-funcational-testcase/module.md` 中的模块信息，以适配你自身项目的模块层级/路径信息。
4. 将 `gen-functional-testcase` 和 `requirement-to-features` 放入 ClaudeCode skills 目录下面。
5. 启动 ClaudeCode 后，调用 `/requirement-to-features` 同时贴入本次的PRD文档。
6. 等待输出功能文档。
7. 调用 `/gen-functional-testcase` 生成测试用例。


## 效果展示
可以直接打开 `testcases/2026-03-13` 文件夹下面已经生成的一批测试用例。
推荐使用 Sonnet4.5 ，国内模型如Qwen/Kimi等，测试下来效果相对差一些。

