#!/usr/bin/env python3
"""
Excel 测试用例转换为 XMind 思维导图脚本

功能：
1. 读取 Excel 格式的测试用例文件
2. 按"所属模块"层级结构组织用例
3. 生成 XMind 思维导图文件

使用方法：
python xlsx_to_xmind.py <excel文件路径> [输出文件路径]

示例：
python xlsx_to_xmind.py output/test.xlsx
python xlsx_to_xmind.py output/test.xlsx output/test.xmind
"""
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import xmind
from xmind.core.topic import TopicElement


class TestCaseTreeBuilder:
    """测试用例树形结构构建器"""

    def __init__(self):
        self.tree = {}

    def add_testcase(self, module_path: str, testcase: Dict[str, Any]):
        """添加测试用例到树形结构"""
        # 处理空值或非字符串的情况
        if pd.isna(module_path) or not isinstance(module_path, str):
            module_path = '/未分类'

        # 分割模块路径
        parts = [p.strip() for p in module_path.split('/') if p.strip()]

        if not parts:
            parts = ['未分类']

        # 构建树形结构
        current = self.tree
        for part in parts:
            if part not in current:
                current[part] = {'_children': {}, '_testcases': []}
            current = current[part]['_children']

        # 将测试用例添加到叶子节点
        # 回退到最后一个模块节点
        current = self.tree
        for part in parts[:-1]:
            current = current[part]['_children']

        if parts:
            current[parts[-1]]['_testcases'].append(testcase)

    def get_tree(self) -> Dict:
        """获取构建的树形结构"""
        return self.tree


class XMindConverter:
    """XMind 转换器"""

    def __init__(self, excel_file: Path):
        self.excel_file = excel_file
        self.workbook = None
        self.sheet = None
        self.root_topic = None

    def read_excel(self) -> pd.DataFrame:
        """读取 Excel 文件"""
        print(f"📄 读取 Excel 文件: {self.excel_file.name}")
        df = pd.DataFrame()

        try:
            # 尝试读取第一个sheet
            df = pd.read_excel(self.excel_file, sheet_name=0)

            # **先标记**哪些行是新用例的开始（在填充之前）
            # 用例名称不为空的行是新用例的开始
            df['_is_new_case'] = df['用例名称'].notna()

            # 处理合并单元格：对非步骤/预期结果的列进行前向填充
            # 这些列在Excel中被合并了，pandas读取时只有第一个单元格有值
            cols_to_fill = ['用例名称', '所属模块', '用例等级', '责任人', '标签', '备注', '前置条件']
            for col in cols_to_fill:
                if col in df.columns:
                    df[col] = df[col].ffill()

            print(f"   找到 {len(df)} 行数据")
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            raise

        return df

    def build_tree(self, df: pd.DataFrame) -> TestCaseTreeBuilder:
        """构建树形结构"""
        print(f"🌲 构建模块树形结构...")

        tree_builder = TestCaseTreeBuilder()

        # 由于Excel中步骤和预期结果被展开成多行，需要按用例名称分组合并
        # 使用之前标记的 _is_new_case 来识别新用例
        grouped_data = []
        current_case = None

        for _, row in df.iterrows():
            # 使用标记判断是否是新用例
            is_new = row.get('_is_new_case', False)

            if is_new:
                # 如果有之前的用例，先保存
                if current_case is not None:
                    grouped_data.append(current_case)

                # 开始新用例
                current_case = {
                    '用例名称': row.get('用例名称', ''),
                    '所属模块': row.get('所属模块', ''),
                    '用例等级': row.get('用例等级', ''),
                    '责任人': row.get('责任人', ''),
                    '标签': row.get('标签', ''),
                    '备注': row.get('备注', ''),
                    '前置条件': row.get('前置条件', ''),
                    '步骤描述': str(row.get('步骤描述', '')) if pd.notna(row.get('步骤描述')) else '',
                    '预期结果': str(row.get('预期结果', '')) if pd.notna(row.get('预期结果')) else '',
                }
            else:
                # 这是同一用例的后续步骤行，追加步骤和预期结果
                if current_case is not None:
                    step = row.get('步骤描述', '')
                    result = row.get('预期结果', '')
                    if pd.notna(step) and step:
                        current_case['步骤描述'] += '\n' + str(step)
                    if pd.notna(result) and result:
                        current_case['预期结果'] += '\n' + str(result)

        # 保存最后一个用例
        if current_case is not None:
            grouped_data.append(current_case)

        print(f"   识别出 {len(grouped_data)} 条独立用例")

        # 构建树
        for testcase in grouped_data:
            module_path = testcase.get('所属模块', '')
            tree_builder.add_testcase(module_path, testcase)

        return tree_builder

    def create_xmind(self, tree_builder: TestCaseTreeBuilder, output_file: Path):
        """创建 XMind 思维导图"""
        print(f"🎨 生成 XMind 思维导图...")

        # 创建工作簿和画布
        self.workbook = xmind.load(str(output_file))
        self.sheet = self.workbook.getPrimarySheet()

        # 设置根节点标题（使用文件名去掉扩展名）
        root_title = self.excel_file.stem.replace('_功能测试用例', '')
        self.sheet.setTitle(root_title)
        self.root_topic = self.sheet.getRootTopic()
        self.root_topic.setTitle(root_title)

        # 递归构建思维导图
        tree = tree_builder.get_tree()
        self._build_subtopics(self.root_topic, tree)

        # 保存文件
        xmind.save(self.workbook, str(output_file))

        # 修复XMind文件：添加缺失的manifest.xml
        self._add_manifest(output_file)

        print(f"✅ XMind 生成成功！")
        print(f"   输出文件: {output_file}")

    def _add_manifest(self, xmind_file: Path):
        """添加META-INF/manifest.xml到XMind文件"""
        import zipfile
        import tempfile
        import shutil

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 解压现有文件
            with zipfile.ZipFile(xmind_file, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # 创建META-INF目录和manifest.xml
            meta_inf = temp_path / 'META-INF'
            meta_inf.mkdir(exist_ok=True)

            manifest_content = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
    <file-entry full-path="content.xml" media-type="text/xml"/>
    <file-entry full-path="META-INF/" media-type=""/>
    <file-entry full-path="meta.xml" media-type="text/xml"/>
    <file-entry full-path="styles.xml" media-type="text/xml"/>
</manifest>'''

            (meta_inf / 'manifest.xml').write_text(manifest_content, encoding='utf-8')

            # 如果缺少meta.xml，创建一个基本的
            if not (temp_path / 'meta.xml').exists():
                meta_content = '''<?xml version="1.0" encoding="UTF-8"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"></meta>'''
                (temp_path / 'meta.xml').write_text(meta_content, encoding='utf-8')

            # 重新打包
            with zipfile.ZipFile(xmind_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zip_ref.write(file_path, arcname)

    def _build_subtopics(self, parent_topic: TopicElement, tree_node: Dict):
        """递归构建子主题"""
        # 保持模块在Excel中出现的顺序（字典插入顺序）
        module_keys = [k for k in tree_node.keys() if not k.startswith('_')]

        for module_name in module_keys:
            node = tree_node[module_name]

            # 创建模块节点
            module_topic = parent_topic.addSubTopic()

            # 统计该模块下的用例数量（包括子模块）
            total_cases = self._count_testcases(node)
            module_title = f"{module_name} ({total_cases}条)"
            module_topic.setTitle(module_title)

            # 如果有测试用例，添加用例节点
            testcases = node.get('_testcases', [])
            if testcases:
                # 按用例等级排序（P0 > P1 > P2 > P3）
                priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
                sorted_testcases = sorted(
                    testcases,
                    key=lambda x: priority_order.get(x.get('用例等级', 'P3'), 99)
                )

                for testcase in sorted_testcases:
                    self._add_testcase_topic(module_topic, testcase)

            # 递归处理子模块
            children = node.get('_children', {})
            if children:
                self._build_subtopics(module_topic, children)

    def _add_testcase_topic(self, parent_topic: TopicElement, testcase: Dict):
        """添加测试用例节点"""
        case_topic = parent_topic.addSubTopic()

        # 用例标题：[P0] 用例名称
        priority = testcase.get('用例等级', '')
        case_name = testcase.get('用例名称', '')
        case_title = f"[{priority}] {case_name}" if priority else case_name
        case_topic.setTitle(case_title)

        # 添加标签
        tags = testcase.get('标签', '')
        if tags:
            # 移除"AI,"前缀
            clean_tags = tags.replace('AI,', '').replace('AI', '').strip(',').strip()
            if clean_tags:
                case_topic.addLabel(clean_tags)

        # 添加备注（详细信息）
        note_parts = []

        # 责任人
        if testcase.get('责任人'):
            note_parts.append(f"👤 责任人: {testcase['责任人']}")

        # 备注
        if testcase.get('备注'):
            note_parts.append(f"📝 备注: {testcase['备注']}")

        # 前置条件
        if testcase.get('前置条件'):
            note_parts.append(f"\n📋 前置条件:\n{testcase['前置条件']}")

        # 步骤描述
        if testcase.get('步骤描述'):
            note_parts.append(f"\n🔧 步骤描述:\n{testcase['步骤描述']}")

        # 预期结果
        if testcase.get('预期结果'):
            note_parts.append(f"\n✅ 预期结果:\n{testcase['预期结果']}")

        if note_parts:
            note_content = '\n\n'.join(note_parts)
            case_topic.setPlainNotes(note_content)

        # 根据用例等级设置图标
        if priority == 'P0':
            case_topic.addMarker('priority-1')  # 最高优先级
        elif priority == 'P1':
            case_topic.addMarker('priority-2')
        elif priority == 'P2':
            case_topic.addMarker('priority-3')
        elif priority == 'P3':
            case_topic.addMarker('priority-4')

    def _count_testcases(self, node: Dict) -> int:
        """统计节点及其子节点下的用例总数"""
        count = len(node.get('_testcases', []))

        # 递归统计子节点
        children = node.get('_children', {})
        for child_node in children.values():
            count += self._count_testcases(child_node)

        return count


def convert_xlsx_to_xmind(excel_file: Path, output_file: Path = None):
    """转换 Excel 到 XMind"""
    if output_file is None:
        output_file = excel_file.parent / excel_file.name.replace('.xlsx', '.xmind')

    converter = XMindConverter(excel_file)

    # 读取 Excel
    df = converter.read_excel()

    if df.empty:
        print("⚠️  警告: Excel 文件为空")
        return

    # 检查必需的列
    required_columns = ['用例名称', '所属模块']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ 错误: Excel 缺少必需的列: {', '.join(missing_columns)}")
        return

    # 构建树形结构
    tree_builder = converter.build_tree(df)

    # 创建 XMind
    converter.create_xmind(tree_builder, output_file)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python xlsx_to_xmind.py <excel文件路径> [输出文件路径]")
        print("\n示例:")
        print("  python xlsx_to_xmind.py output/test.xlsx")
        print("  python xlsx_to_xmind.py output/test.xlsx output/test.xmind")
        sys.exit(1)

    excel_file = Path(sys.argv[1])

    if not excel_file.exists():
        print(f"❌ 错误: 文件不存在: {excel_file}")
        sys.exit(1)

    if excel_file.suffix not in ['.xlsx', '.xls']:
        print(f"❌ 错误: 不是 Excel 文件: {excel_file}")
        sys.exit(1)

    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        convert_xlsx_to_xmind(excel_file, output_file)
        print(f"\n🎉 转换完成！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
