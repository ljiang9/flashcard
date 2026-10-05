"""flashcard - 终端抽认卡测验。纯标准库，纯本地。

牌组是 JSON 文件：{"cards": [{"front": ..., "back": ..., "streak": 0, "seen": 0}]}。
学习进度（streak/seen）直接写在牌组文件里，没有额外的 sidecar——
简单、可备份、可手改。README 有说明。
"""
import argparse
import json
import os
import random
import sys

VERSION = "0.1.0"


def load_deck(path):
    if not os.path.exists(path):
        return {"cards": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"error: 牌组文件不是合法 JSON：{path}（第 {e.lineno} 行）\n")
        sys.exit(2)
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        sys.stderr.write(f"error: 牌组文件格式不对：{path}（需要 {{\"cards\": [...]}}）\n")
        sys.exit(2)
    for c in data["cards"]:
        c.setdefault("streak", 0)
        c.setdefault("seen", 0)
    return data


def save_deck(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def cmd_add(args):
    data = load_deck(args.deck)
    data["cards"].append({"front": args.front, "back": args.back, "streak": 0, "seen": 0})
    save_deck(args.deck, data)
    print(f"已添加卡片 #{len(data['cards'])}：{args.front} → {args.back}")


def order_cards(cards, seed=None):
    """测验顺序：streak 越低越优先（简单间隔重复）；同 streak 内随机打乱。"""
    rng = random.Random(seed)
    idx = list(range(len(cards)))
    rng.shuffle(idx)
    idx.sort(key=lambda i: cards[i].get("streak", 0))
    return idx


def cmd_quiz(args):
    data = load_deck(args.deck)
    cards = data["cards"]
    if not cards:
        sys.stderr.write(f"error: 牌组是空的：{args.deck}（先用 add 添加卡片）\n")
        sys.exit(1)
    order = order_cards(cards, args.seed)
    correct = 0
    total = 0
    script = args.script
    for n, i in enumerate(order, 1):
        card = cards[i]
        print(f"\n【{n}/{len(order)}】{card['front']}")
        if not script:
            try:
                input("  按回车看答案…")
            except EOFError:
                print("\n已中断。")
                break
        print(f"  答案：{card['back']}")
        if script:
            line = sys.stdin.readline()
            ans = line.strip().lower() if line else ""
        else:
            try:
                ans = input("  答对了吗？(y/n) ").strip().lower()
            except EOFError:
                print("\n已中断。")
                break
        ok = ans in ("y", "yes", "Y", "是", "对")
        card["seen"] = card.get("seen", 0) + 1
        if ok:
            card["streak"] = card.get("streak", 0) + 1
            correct += 1
        else:
            card["streak"] = 0
        total += 1
    save_deck(args.deck, data)
    print(f"\n本次：{correct}/{total} 答对。进度已保存。")


def cmd_stats(args):
    data = load_deck(args.deck)
    cards = data["cards"]
    if not cards:
        print("牌组是空的。")
        return
    print(f"===== 学习统计：{args.deck}（{len(cards)} 张）=====\n")
    for i, c in enumerate(cards, 1):
        bar = "█" * min(c.get("streak", 0), 20)
        print(f"  #{i} {c['front']} → {c['back']}")
        print(f"      连对 {c.get('streak', 0)} {bar}　已测 {c.get('seen', 0)} 次")


def build_parser():
    p = argparse.ArgumentParser(prog="flashcard", description="终端抽认卡测验（纯本地）")
    p.add_argument("--version", action="version", version=f"flashcard {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="添加一张卡片")
    a.add_argument("deck", help="牌组 JSON 文件")
    a.add_argument("--front", required=True, help="卡片正面")
    a.add_argument("--back", required=True, help="卡片背面")
    a.set_defaults(func=cmd_add)

    q = sub.add_parser("quiz", help="开始测验")
    q.add_argument("deck", help="牌组 JSON 文件")
    q.add_argument("--script", action="store_true", help="从 stdin 读 y/n 答案（测试/脚本用）")
    q.add_argument("--seed", type=int, default=None, help="随机种子（可复现顺序）")
    q.set_defaults(func=cmd_quiz)

    s = sub.add_parser("stats", help="查看每张卡片的连对/已测次数")
    s.add_argument("deck", help="牌组 JSON 文件")
    s.set_defaults(func=cmd_stats)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
