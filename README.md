# Quit Smoking Coach Skill

An open-source Codex skill for interactive smoking-cessation coaching in Chinese.

This skill focuses on cognitive reframing: it helps users identify the beliefs that make cigarettes feel necessary, then responds with short interventions, behavioral experiments, craving rescue flows, relapse repair, and local state tracking.

## What It Does

- Detects common smoking-related beliefs such as "I need cigarettes for stress", "just one is fine", or "I can quit by cutting down".
- Routes conversations through states such as questioning, preparing, withdrawal, stable, and relapse.
- Provides short craving rescue responses when the user says they want to smoke.
- Provides non-shaming relapse repair when the user reports smoking again.
- Includes a local CLI runtime that stores user state on the user's machine.

## Repository Structure

```text
quit-smoking-coach/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── book_model.yaml
│   ├── skill_requirements.md
│   └── system_prompt.md
├── scripts/
│   └── quit_smoking_skill.py
├── state/
│   └── user_state.example.json
├── LICENSE
├── README.md
└── requirements.txt
```

## Use As A Codex Skill

Copy this folder into your Codex skills directory, then restart Codex so the skill metadata can be discovered.

The trigger metadata is in `SKILL.md`.

## Use The Local CLI

Install the only Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

Run from the repository root:

```bash
python3 scripts/quit_smoking_skill.py start
python3 scripts/quit_smoking_skill.py chat "我饭后特别想抽"
python3 scripts/quit_smoking_skill.py rescue "我忍不住了"
python3 scripts/quit_smoking_skill.py relapse "我刚抽了一支"
python3 scripts/quit_smoking_skill.py state
python3 scripts/quit_smoking_skill.py prompt
```

By default, local state is stored at:

```text
~/.quit-smoking-coach/user_state.json
```

You can also pass a custom state file:

```bash
python3 scripts/quit_smoking_skill.py --state ./state/user_state.example.json chat "我想抽烟"
```

## Safety

This project provides cognitive and behavioral support. It is not medical advice, diagnosis, psychotherapy, or a replacement for a smoking-cessation clinic.

If a user reports severe anxiety, depression, self-harm thoughts, complex substance dependence, or a medical emergency, stop ordinary coaching and recommend local professional medical or mental-health support.

## License

MIT License. See `LICENSE`.
