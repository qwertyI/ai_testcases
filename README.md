# ai_testcases
借助AI生成完整的测试用例

## 快速开始
```shell
cp -r skills/requirement-to-features ~/.claude/skills/requirement-to-features
cp -r skills/gen-functional-testcase ~/.claude/skills/gen-functional-testcase
cp -r skills/update-workflow ~/.claude/skills/update-workflow

conda create -n ai_testcases python=3.11
conda activate ai_testcases
pip install -r requirements.txt

# 激活 claude
claude
# 在claude对话窗口输入
请帮我生成以下文档的测试用例 场次模板配置PRD文档.md
```
1. 执行命令 `sh init.sh`
2. 在当前目录打开 ClaudeCode。
3. 将需求文档放入对话窗口，并告知 claude 你需要生成测试用例


## 配置适合你的内容

1. 在 `knowledge` 中，根据已有的示例内容修改 modules.md 以及新增 `module_knowledge` 的流程知识。


## 效果展示
可以直接打开 `testcases/2026-03-13` 文件夹下面已经生成的一批测试用例。
推荐使用 Sonnet4.5 ，国内模型如Qwen/Kimi等，测试下来效果相对差一些。


## Skill 的核心设计逻辑
1. 解决AI不说人话
    - 常见的AI生成测试用例，经常会面临输出内容夹杂太多专业冗长的表述。这些表述仔细理解，可以看得出其实是非常精准的，但是不适合人来读和理解，容易丢失掌控感，犯困。是经典的副驾陷阱。
    - 在 Skill 中严格规定 AI 输出内容的格式，使其生成的文字与测试用例常见的表达匹配，基本杜绝了这种情况。
2. 解决输出散乱的问题
    - 常见的AI生成测试用例，通常会严格按照输入内容进行梳理，碰到较大型的需求或者产品文档非线性发散的时候，生成的测试用例也经常会东一块，西一块，与人类生成的测试用例的结构有非常巨大的差异。人类因为拥有业务知识，通常会以业务已有的流程对功能点进行归纳整理，然后再根据一些字段限制、业务限制进行补充。而AI没有这块的知识。
    - 利用 `module_knowledge` 模块，补充业务流程知识，可以极大的减少输出散乱的问题。该块内容以模块的具体业务流程为核心，严格让AI以业务流程为输出顺序基准，同时根据前后置数据、流程、依赖信息等内容，将用例分为多个模块，极大的减少了这种散乱感。
3. 关于字段、业务规则限制
    - 大部分类似的限制，在测试用例中的占比极小，除了当次需求会大量用上，后续其他需求用上的概率极小，而当次需求又已经在PRD文档中说明了相关的限制。为了这类小概率事件，在知识文档中永久固化这块内容，即浪费token，又增加幻觉率。当越来越多类似的限制加入到流程知识中时，反而会淹没更加重要的内容。
    - 为了10%的用例，影响90%的用例的构建稳定性，应该不是一个好的设计方式。推荐类似的用例缺失时，都由人来进行补充。
