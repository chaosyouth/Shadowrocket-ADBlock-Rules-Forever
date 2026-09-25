"""Overlay the active Shadowrocket profile's preferences on upstream rules."""

import json
from pathlib import Path
import sys

REFERENCE_PATH = Path(__file__).resolve().parents[1] / "custom/reference.json"
GROUP = "节点选择"


def overlay_settings(lines, settings):
    """Keep upstream comments and new keys; override matching reference keys."""
    result, seen = [], set()
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in settings:
                line = f"{key} = {settings[key]}"
                seen.add(key)
        result.append(line)
    result.extend(f"{key} = {value}" for key, value in settings.items() if key not in seen)
    return result


def generate(source):
    reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    sections = {"": []}
    section = ""
    for line in source.splitlines():
        if line.startswith("[") and line.endswith("]"):
            section = line
            if section in sections:
                raise ValueError("上游配置存在重复区段，停止发布")
            sections[section] = []
        else:
            sections[section].append(line)
    if "[Rule]" not in sections:
        raise ValueError("上游配置缺少 Rule 区段，停止发布")

    replacements = 0
    for index, line in enumerate(sections["[Rule]"]):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(",")
        policy_index = len(parts) - 1
        while policy_index > 0 and parts[policy_index].strip().lower() in {"no-resolve", "extended-matching"}:
            policy_index -= 1
        if parts[policy_index].strip().upper() == "PROXY":
            parts[policy_index] = GROUP
            sections["[Rule]"][index] = ",".join(parts)
            replacements += 1

    groups = sections.get("[Proxy Group]", [])
    has_groups = any(line.strip() and not line.lstrip().startswith("#") for line in groups)
    use_groups = bool(replacements or has_groups)
    if use_groups:
        # Preserve newly introduced upstream groups, routing generic PROXY via the selector.
        for index, line in enumerate(groups):
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                groups[index] = key + "=" + ",".join(
                    GROUP if part.strip().upper() == "PROXY" else part for part in value.split(",")
                )
        groups = overlay_settings(groups, reference["groups"])

    if "[General]" in sections:
        sections["[General]"] = overlay_settings(sections["[General]"], reference["general"])
        sections["[Host]"] = overlay_settings(sections.get("[Host]", []), reference["hosts"])

    output = ["# 自动生成；个人设置请修改 custom/reference.json。"]
    for name, lines in sections.items():
        if name == "[Proxy Group]" and use_groups:
            lines = groups
        if name == "[Rule]" and use_groups and "[Proxy Group]" not in sections:
            output.extend(["[Proxy Group]", *groups, ""])
        if name:
            output.append(name)
        output.extend(lines)
    return "\n".join(line.rstrip() for line in output).rstrip() + "\n"


def generate_all(source_dir, destination_dir, legacy_path):
    sources = sorted(source_dir.glob("*.conf"))
    if not sources or not (source_dir / "lazy_group.conf").is_file():
        raise ValueError("上游配置集合不完整，停止发布")
    # Validate every input before replacing any published output.
    results = {path.name: generate(path.read_text(encoding="utf-8-sig")) for path in sources}
    destination_dir.mkdir(parents=True, exist_ok=True)
    for name, content in results.items():
        (destination_dir / name).write_text(content, encoding="utf-8")
    for path in destination_dir.glob("*.conf"):
        if path.name not in results:
            path.unlink()
    legacy_path.write_text(results["lazy_group.conf"], encoding="utf-8")
    print(f"Generated {len(results)} custom configurations")


if __name__ == "__main__":
    source, destination, legacy = map(Path, sys.argv[1:])
    generate_all(source, destination, legacy)
