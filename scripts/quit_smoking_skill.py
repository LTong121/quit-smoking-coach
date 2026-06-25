#!/usr/bin/env python3
import argparse
import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: PyYAML. Install with: python3 -m pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "references" / "book_model.yaml"
DEFAULT_STATE_PATH = Path.home() / ".quit-smoking-coach" / "user_state.json"

PUBLIC_STATES = [
    "unaware",
    "questioning",
    "reframing",
    "preparing",
    "quit_day",
    "withdrawal",
    "stable",
    "relapse",
]

DEFAULT_STATE = {
    "profile": {
        "initialized": False,
        "daily_cigarettes": None,
        "years_smoked": None,
        "most_dependent_scenarios": [],
        "quit_history": None,
        "current_willingness": None,
    },
    "current_state": "unaware",
    "identity_stage": "吸烟者",
    "active_false_beliefs": [],
    "transformed_beliefs": [],
    "high_risk_triggers": [],
    "last_cigarette_at": None,
    "experiments": [],
    "relapse_events": [],
    "conversation_count": 0,
}


BELIEF_RULES = [
    ("FB001", ["减压", "压力", "烦", "焦虑", "扛不住", "压不住火", "心烦"]),
    ("FB002", ["放松", "镇定", "缓一缓", "舒服一下", "冷静", "松一口气"]),
    ("FB003", ["集中", "注意力", "提神", "动脑", "写东西", "工作前", "开工"]),
    ("FB004", ["无聊", "没事干", "打发时间", "空落", "闲着"]),
    ("FB005", ["喜欢抽", "享受", "烟味", "乐趣", "快乐", "爽"]),
    ("FB006", ["舍不得", "少了什么", "没乐趣", "被剥夺", "放弃", "牺牲"]),
    ("FB007", ["意志", "毅力", "忍不住", "自控", "控制不住"]),
    ("FB008", ["戒断", "痛苦", "难受", "熬不过", "可怕", "受不了"]),
    ("FB009", ["就一支", "只一支", "一口", "一根", "今天例外", "来一支"]),
    ("FB010", ["少抽", "减量", "慢慢减", "控制数量", "一天几支"]),
    ("FB011", ["糖", "口香糖", "零食", "电子烟", "替代", "顶一下"]),
    ("FB012", ["尼古丁贴", "尼古丁口香糖", "尼古丁替代", "贴片", "先戒动作"]),
    ("FB013", ["我烟瘾太大", "我情况特殊", "我比别人", "特别难戒", "老烟枪"]),
    ("FB014", ["习惯", "手上没东西", "动作", "嘴里没东西", "仪式"]),
    ("FB015", ["忙完", "假期后", "以后再戒", "现在不是时候", "压力小"]),
    ("FB016", ["应酬", "社交", "朋友都抽", "递烟", "聚会", "饭局"]),
    ("FB017", ["饭后", "餐后", "吃完", "饭后一支"]),
    ("FB018", ["怀念", "以后会想", "会想烟", "失去", "再也不能"]),
    ("FB019", ["变胖", "体重", "胖", "吃多", "长肉"]),
    ("FB020", ["留一包", "放着", "备着", "带烟", "有烟安心"]),
    ("FB021", ["失败", "没救", "我太差", "意志薄弱", "废了", "又失败"]),
    ("FB022", ["我愿意", "我自由", "我自己选", "我的选择", "想抽就抽"]),
    ("FB023", ["低谷", "难过", "崩溃", "安慰", "撑过去", "心情不好"]),
    ("FB024", ["戒这么久", "偶尔", "应该没事", "能控制", "不会上瘾"]),
    ("FB025", ["还年轻", "以后再说", "没那么严重", "危害", "身体还好"]),
]

BELIEF_PRIORITY = [
    "FB009",
    "FB024",
    "FB020",
    "FB001",
    "FB017",
    "FB016",
    "FB023",
    "FB008",
    "FB007",
    "FB010",
    "FB011",
    "FB012",
]

TRIGGER_RULES = [
    ("TR001", ["压力", "烦", "焦虑", "吵架", "崩溃"]),
    ("TR003", ["无聊", "没事干", "闲着"]),
    ("TR004", ["集中", "工作", "写", "开工"]),
    ("TR005", ["饭后", "餐后", "吃完"]),
    ("TR007", ["喝酒", "酒", "微醺"]),
    ("TR009", ["聚会", "饭局", "应酬"]),
    ("TR010", ["别人抽", "看到", "闻到烟"]),
    ("TR011", ["递烟", "给我烟", "劝烟"]),
    ("TR017", ["挫败", "搞砸", "工作不顺"]),
    ("TR019", ["孤独", "失落", "难过"]),
    ("TR025", ["感觉很好", "不想了", "证明"]),
    ("TR027", ["身上有烟", "留一包", "买一包"]),
]

INTERVENTION_BY_BELIEF = {
    "FB001": "INT001",
    "FB002": "INT001",
    "FB003": "INT001",
    "FB004": "INT001",
    "FB005": "INT006",
    "FB006": "INT004",
    "FB007": "INT016",
    "FB008": "INT017",
    "FB009": "INT003",
    "FB010": "INT009",
    "FB011": "INT010",
    "FB012": "INT010",
    "FB013": "INT016",
    "FB014": "INT006",
    "FB015": "INT014",
    "FB016": "INT012",
    "FB017": "INT001",
    "FB018": "INT004",
    "FB019": "INT010",
    "FB020": "INT011",
    "FB021": "INT016",
    "FB022": "INT005",
    "FB023": "INT001",
    "FB024": "INT003",
    "FB025": "INT015",
}

EXPERIMENT_BY_BELIEF = {
    "FB001": "EXP003",
    "FB002": "EXP003",
    "FB003": "EXP004",
    "FB004": "EXP007",
    "FB005": "EXP001",
    "FB006": "EXP006",
    "FB007": "EXP004",
    "FB008": "EXP007",
    "FB009": "EXP006",
    "FB010": "EXP005",
    "FB011": "EXP010",
    "FB012": "EXP010",
    "FB013": "EXP004",
    "FB014": "EXP007",
    "FB015": "EXP013",
    "FB016": "EXP008",
    "FB017": "EXP002",
    "FB018": "EXP014",
    "FB019": "EXP010",
    "FB020": "EXP011",
    "FB021": "EXP013",
    "FB022": "EXP006",
    "FB023": "EXP015",
    "FB024": "EXP016",
    "FB025": "EXP006",
}

RESCUE_PATTERNS = re.compile(r"(想抽|忍不住|烟瘾|特别难受|受不了了|买烟|来一支|就一支|一口)")
RELAPSE_PATTERNS = re.compile(r"(我抽了|刚抽|刚刚抽|今天抽|又抽|破戒|复吸|没忍住.*抽|我失败了|这次失败)")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_model():
    with MODEL_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_state(path):
    if not path.exists():
        return copy.deepcopy(DEFAULT_STATE)
    with path.open("r", encoding="utf-8") as f:
        state = json.load(f)
    merged = copy.deepcopy(DEFAULT_STATE)
    deep_update(merged, state)
    return merged


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def deep_update(base, incoming):
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value


def by_id(items):
    return {item["id"]: item for item in items}


def detect_false_beliefs(text):
    hits = []
    for belief_id, keywords in BELIEF_RULES:
        for kw in keywords:
            if kw in text:
                hits.append({"id": belief_id, "keyword": kw})
                break
    priority = {belief_id: idx for idx, belief_id in enumerate(BELIEF_PRIORITY)}
    hits.sort(key=lambda hit: priority.get(hit["id"], 100))
    return hits


def detect_triggers(text):
    hits = []
    for trigger_id, keywords in TRIGGER_RULES:
        for kw in keywords:
            if kw in text:
                hits.append({"id": trigger_id, "keyword": kw})
                break
    return hits


def is_rescue(text):
    return bool(RESCUE_PATTERNS.search(text))


def is_relapse(text):
    if any(marker in text for marker in ["以前", "过去", "曾经", "上次", "之前"]) and not any(
        marker in text for marker in ["刚抽", "刚刚抽", "今天抽", "我抽了", "又抽", "破戒", "复吸", "没忍住"]
    ):
        return False
    return bool(RELAPSE_PATTERNS.search(text))


def update_list_unique(items, new_ids):
    existing = {x["id"] if isinstance(x, dict) else x for x in items}
    for new_id in new_ids:
        if new_id not in existing:
            items.append({"id": new_id, "first_seen_at": now_iso(), "count": 1})
        else:
            for item in items:
                if isinstance(item, dict) and item.get("id") == new_id:
                    item["count"] = item.get("count", 1) + 1
                    item["last_seen_at"] = now_iso()


def classify_state(state, text, beliefs, relapse=False, rescue=False):
    current = state.get("current_state", "unaware")
    if relapse:
        return "relapse"
    if state["profile"].get("initialized") is False:
        return "unaware"
    if state.get("last_cigarette_at") and rescue:
        return "withdrawal"
    if any(hit["id"] in ("FB009", "FB024") for hit in beliefs):
        return current if current in ("withdrawal", "stable", "quit_day") else "questioning"
    if any(hit["id"] in ("FB001", "FB002", "FB003", "FB004", "FB005", "FB017") for hit in beliefs):
        return "questioning"
    if any(hit["id"] in ("FB006", "FB018", "FB022") for hit in beliefs):
        return "reframing"
    if any(hit["id"] in ("FB015", "FB020") for hit in beliefs):
        return "preparing"
    return current if current in PUBLIC_STATES else "unaware"


def intake_response():
    return (
        "先不急着谈戒烟。我得先把你的烟瘾画像搭起来，不然我只会给你泛泛建议。\n\n"
        "按这 5 项直接回答就行：\n\n"
        "1. 你现在平均每天几支？\n"
        "2. 烟龄几年？\n"
        "3. 哪个场景你最离不开烟：压力、饭后、无聊、工作前、社交、喝酒，还是别的？\n"
        "4. 以前戒过吗？通常卡在哪一步？\n"
        "5. 你现在的意愿是：只是看看、想少抽、想彻底戒、还是已经准备停？\n\n"
        "我会根据这 5 个答案判断你现在处在哪个状态，然后先拆你最核心的那个“离不开”的理由。"
    )


def maybe_parse_profile(text, state):
    profile = state["profile"]
    numbers = re.findall(r"\d+", text)
    if numbers and profile.get("daily_cigarettes") is None:
        profile["daily_cigarettes"] = int(numbers[0])
    if len(numbers) >= 2 and profile.get("years_smoked") is None:
        profile["years_smoked"] = int(numbers[1])
    scenarios = []
    for label in ["压力", "饭后", "无聊", "工作", "社交", "喝酒", "应酬", "起床", "睡前"]:
        if label in text:
            scenarios.append(label)
    if scenarios:
        profile["most_dependent_scenarios"] = sorted(set(profile.get("most_dependent_scenarios", []) + scenarios))
    if any(x in text for x in ["戒过", "失败", "复吸", "没戒过", "第一次"]):
        profile["quit_history"] = text[:300]
    if "彻底戒" in text or "准备停" in text:
        profile["current_willingness"] = "ready_to_quit"
    elif "少抽" in text:
        profile["current_willingness"] = "reduce"
    elif "看看" in text:
        profile["current_willingness"] = "curious"
    elif "想戒" in text:
        profile["current_willingness"] = "wants_to_quit"
    if (
        profile.get("daily_cigarettes") is not None
        and profile.get("years_smoked") is not None
        and profile.get("most_dependent_scenarios")
        and profile.get("current_willingness")
    ):
        profile["initialized"] = True


def render_belief_intervention(model, state, text, beliefs):
    false_beliefs = by_id(model["false_beliefs"])
    target_beliefs = by_id(model["target_beliefs"])
    transformations = by_id(model["transformations"])
    interventions = by_id(model["interventions"])
    experiments = by_id(model["experiments"])

    if not beliefs:
        return (
            "我先不硬塞判断。你这句话里还没暴露出一个明确的“离不开烟”的理由。\n\n"
            "我想问一个具体问题：你最怕没有烟之后，哪个场景会先出问题？压力、饭后、无聊、工作，还是社交？"
        )

    belief_id = beliefs[0]["id"]
    fb = false_beliefs[belief_id]
    intervention_id = INTERVENTION_BY_BELIEF.get(belief_id, "INT006")
    intervention = interventions[intervention_id]
    experiment_id = EXPERIMENT_BY_BELIEF.get(belief_id)
    experiment = experiments.get(experiment_id) if experiment_id else None
    transformation = next((t for t in model["transformations"] if t["from_belief"] == belief_id), None)
    target = target_beliefs.get(transformation["to_belief"]) if transformation else None

    lines = []
    lines.append(f"我先抓住你这句话里的核心：{fb['belief']}")
    lines.append("")
    lines.append(f"这里的陷阱是：{fb['description']}")
    lines.append("")
    lines.append(f"我会用的拆法是：{intervention['name']}。")
    for step in intervention["execution_pattern"]:
        lines.append(f"- {step}")
    if target:
        lines.append("")
        lines.append(f"这一轮要转到的新看法是：{target['belief']}")
    if experiment:
        lines.append("")
        lines.append("现在给你一个小实验，不是打卡，是验证这个理由站不站得住：")
        lines.append(f"实验：{experiment['objective']}")
        for step in experiment["procedure"]:
            lines.append(f"- {step}")
        lines.append(f"认知目标：{experiment['expected_realization']}")
        record_experiment(state, experiment_id, belief_id)
    lines.append("")
    lines.append("我问你一个具体问题：刚才你想抽的那一下，更像是真的享受烟，还是想解除某种不舒服？")
    return "\n".join(lines)


def record_experiment(state, experiment_id, belief_id):
    existing = {x.get("id") for x in state.get("experiments", [])}
    if experiment_id and experiment_id not in existing:
        state.setdefault("experiments", []).append({
            "id": experiment_id,
            "linked_belief": belief_id,
            "assigned_at": now_iso(),
            "status": "assigned",
        })


def rescue_response(model, state, text, beliefs, triggers):
    update_list_unique(state.setdefault("active_false_beliefs", []), [hit["id"] for hit in beliefs])
    update_list_unique(state.setdefault("high_risk_triggers", []), [hit["id"] for hit in triggers])
    state["current_state"] = "withdrawal" if state.get("last_cigarette_at") else "questioning"

    trigger_text = "、".join(hit["id"] for hit in triggers) if triggers else "还没确认"
    belief_text = beliefs[0]["id"] if beliefs else "未确认"

    return (
        "先不讲道理。现在这 3 分钟只处理冲动。\n\n"
        "1. 先把这支烟延后 3 分钟。不是永远，只是 3 分钟。\n"
        "2. 立刻离开烟、打火机、卖烟的路径，或者正在抽烟的人。\n"
        "3. 喝一口水，站起来，把手从拿烟动作里断开。\n"
        "4. 给这股感觉命名：它不是“我需要烟”，它是旧依赖在要补给。\n"
        "5. 记住：现在这一支不是一支，它会重新启动下一支。\n\n"
        f"当前识别到的触发器：{trigger_text}\n"
        f"当前最可能的错误信念：{belief_text}\n\n"
        "现在只回答我一个问题：这股想抽最像哪一种，压力、无聊、饭后、看到别人抽、情绪低落，还是突然空了一下？"
    )


def relapse_response(model, state, text, beliefs, triggers):
    event = {
        "occurred_at": now_iso(),
        "raw_report": text,
        "detected_false_beliefs": [hit["id"] for hit in beliefs],
        "detected_triggers": [hit["id"] for hit in triggers],
        "repair_completed": False,
    }
    state.setdefault("relapse_events", []).append(event)
    state["current_state"] = "relapse"
    state["identity_stage"] = "正在摆脱依赖的人"
    update_list_unique(state.setdefault("active_false_beliefs", []), [hit["id"] for hit in beliefs])
    update_list_unique(state.setdefault("high_risk_triggers", []), [hit["id"] for hit in triggers])

    trigger_label = " / ".join(hit["id"] for hit in triggers) or "待确认"
    belief_label = " / ".join(hit["id"] for hit in beliefs) or "待确认"

    return (
        "不责备，也不说空话。我们像分析 Bug 一样分析这次复吸，目标是修掉导致下一支的漏洞。\n\n"
        f"触发器：{trigger_label}\n"
        "↓\n"
        "情绪：你抽之前最强的感觉是什么？压力、烦躁、空、委屈、兴奋、还是“反正就一支”？\n"
        "↓\n"
        "行为：从第一个念头到点上烟，中间发生了什么？谁递的、哪里买的、还是身边本来就有？\n"
        "↓\n"
        "结果：吸完之后，问题真的被解决了吗，还是只是短暂安静了一下？\n"
        "↓\n"
        f"初步定位的错误推理：{belief_label}\n\n"
        "修复方案：\n"
        "1. 现在先阻断下一支，把烟和打火机移出手边。\n"
        "2. 把复吸前那句自我说服写出来，例如“就一支没事”。\n"
        "3. 我们只修这个推理，不评价你这个人。\n"
        "4. 接下来 24 小时按高危处理：不买烟、不留烟、不测试自己。\n\n"
        "现在回答两句就够：触发器是什么？复吸前你对自己说了哪句话？"
    )


def start_response(state):
    if not state["profile"].get("initialized"):
        return intake_response()
    return (
        "你的烟瘾画像已经存在。我们继续从最核心的理由下手。\n\n"
        f"当前状态：{state.get('current_state')}\n"
        f"身份阶段：{state.get('identity_stage')}\n\n"
        "直接告诉我：今天最想抽的是哪个场景？"
    )


def maybe_update_identity(state):
    current = state.get("current_state")
    if current in ("unaware", "questioning"):
        state["identity_stage"] = "吸烟者"
    elif current in ("reframing", "preparing", "withdrawal", "relapse"):
        state["identity_stage"] = "正在摆脱依赖的人"
    elif current in ("quit_day", "stable"):
        state["identity_stage"] = "非吸烟者"


def chat(model, state, text):
    state["conversation_count"] = state.get("conversation_count", 0) + 1
    maybe_parse_profile(text, state)

    beliefs = detect_false_beliefs(text)
    triggers = detect_triggers(text)
    relapse = is_relapse(text)
    rescue = is_rescue(text)

    if relapse:
        return relapse_response(model, state, text, beliefs, triggers)
    if rescue:
        return rescue_response(model, state, text, beliefs, triggers)

    if not state["profile"].get("initialized"):
        if state["conversation_count"] <= 1:
            return intake_response()
        missing = []
        p = state["profile"]
        if p.get("daily_cigarettes") is None:
            missing.append("每天支数")
        if p.get("years_smoked") is None:
            missing.append("烟龄")
        if not p.get("most_dependent_scenarios"):
            missing.append("最依赖场景")
        if not p.get("current_willingness"):
            missing.append("当前意愿")
        if missing:
            return "画像还差这些信息：" + "、".join(missing) + "。\n\n请直接补齐，我再开始第一轮干预。"

    update_list_unique(state.setdefault("active_false_beliefs", []), [hit["id"] for hit in beliefs])
    update_list_unique(state.setdefault("high_risk_triggers", []), [hit["id"] for hit in triggers])
    state["current_state"] = classify_state(state, text, beliefs, relapse=relapse, rescue=rescue)
    maybe_update_identity(state)
    return render_belief_intervention(model, state, text, beliefs)


def print_state(state):
    return json.dumps(state, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="这个Skill能让你戒烟 - local runtime")
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH), help="Path to user state JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("start")
    p_chat = sub.add_parser("chat")
    p_chat.add_argument("message")
    p_rescue = sub.add_parser("rescue")
    p_rescue.add_argument("message")
    p_relapse = sub.add_parser("relapse")
    p_relapse.add_argument("message")
    sub.add_parser("state")
    sub.add_parser("prompt")

    args = parser.parse_args()
    state_path = Path(args.state)
    model = load_model()
    state = load_state(state_path)

    if args.command == "start":
        output = start_response(state)
    elif args.command == "chat":
        output = chat(model, state, args.message)
    elif args.command == "rescue":
        output = rescue_response(model, state, args.message, detect_false_beliefs(args.message), detect_triggers(args.message))
    elif args.command == "relapse":
        output = relapse_response(model, state, args.message, detect_false_beliefs(args.message), detect_triggers(args.message))
    elif args.command == "state":
        output = print_state(state)
    elif args.command == "prompt":
        output = (ROOT / "references" / "system_prompt.md").read_text(encoding="utf-8")
    else:
        raise SystemExit("Unknown command")

    if args.command != "state" and args.command != "prompt":
        save_state(state_path, state)
    print(output)


if __name__ == "__main__":
    main()
