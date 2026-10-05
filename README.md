# flashcard

终端抽认卡测验：正面出题、回车看答案、自己判对错。纯标准库，纯本地。

## 快速开始

```bash
# 添加卡片（牌组是普通 JSON 文件）
python -m flashcard add words.json --front "apple" --back "苹果"

# 开始测验：显示正面 → 回车看答案 → y/n 自评
python -m flashcard quiz words.json

# 看每张卡片的连对/已测次数
python -m flashcard stats words.json
```

`examples/words.json` 自带 10 组英中单词，可直接拿来测。

## 测验顺序（简单间隔重复）

测验按**连对次数（streak）从低到高**出牌：越不熟的卡越先出现；streak
相同的卡片随机打乱。答对 streak+1，答错清零。`--seed` 可固定顺序：

```bash
python -m flashcard quiz words.json --seed 42
```

## 数据格式

牌组就是一个 JSON 文件，学习进度直接写在卡片上（没有额外的 sidecar 文件）：

```json
{"cards": [{"front": "apple", "back": "苹果", "streak": 2, "seen": 3}]}
```

想备份、想手改、想用 git 管版本，都很方便。

## 脚本模式（测试用）

```bash
printf 'y\ny\nn\n' | python -m flashcard quiz deck.json --script --seed 1
```

`--script` 从 stdin 读 `y/n` 答案，不等待回车，方便写自动化测试。

## 诚实说明

- **自评制**：对错由你自己按 `y/n` 判定，工具不做语义判断——别骗自己。
- 排序是"streak 越低越优先"的简单启发式，**不是真正的 SM-2 算法**（没有
  easiness factor、没有间隔天数计算）。
- 牌组文件是明文 JSON；别把密码当卡片背。
- 需要真正的间隔重复算法（Anki 那套）时，请用 Anki。
