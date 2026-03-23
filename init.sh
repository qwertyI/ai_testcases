cp -r skills/requirement-to-features ~/.claude/skills/requirement-to-features
cp -r skills/gen-functional-testcase ~/.claude/skills/gen-functional-testcase
cp -r skills/update-workflow ~/.claude/skills/update-workflow

conda create -n ai_testcases python=3.11
conda init
source ~/.zshrc
conda activate ai_testcases
pip install -r requirements.txt




