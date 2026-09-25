"""Apply the personal proxy policy without changing upstream routing matches."""

from pathlib import Path
import sys

GROUP = "edgetunnel自动优选"
POLICY = (
    f"{GROUP} = url-test,edgetunnel,use=true,"
    "interval=300,tolerance=50,timeout=5,"
    "url=http://www.gstatic.com/generate_204"
)


def generate(source):
    lines = source.splitlines()
    sections = [line for line in lines if line.startswith("[") and line.endswith("]")]
    if lines.count("[Rule]") != 1 or len(sections) != len(set(sections)):
        raise ValueError("上游配置缺少必要区段或存在重复区段，停止发布")
    if any(line.split("=", 1)[0].strip() == GROUP for line in lines):
        raise ValueError("上游已包含同名策略组，停止发布")
    output = ["# 自动生成，请修改 scripts/generate_edgetunnel.py；订阅备注需为 edgetunnel。"]
    section = ""
    replacements = 0
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            section = line
        if line == "[Proxy Group]":
            output.extend([line, POLICY])
            continue
        if line.strip() and not line.lstrip().startswith("#"):
            if section == "[Proxy Group]" and "=" in line:
                name, value = line.split("=", 1)
                parts = value.split(",")
                for index, part in enumerate(parts):
                    if part.strip().upper() == "PROXY":
                        parts[index] = GROUP
                        replacements += 1
                line = name + "=" + ",".join(parts)
            elif section == "[Rule]":
                # Rule options may follow the policy, e.g. no-resolve.
                parts = line.split(",")
                index = len(parts) - 1
                while index > 0 and parts[index].strip().lower() in {"no-resolve", "extended-matching"}:
                    index -= 1
                if parts[index].strip().upper() == "PROXY":
                    parts[index] = GROUP
                    replacements += 1
                line = ",".join(parts)
        output.append(line)
    if replacements and "[Proxy Group]" not in sections:
        index = output.index("[Rule]")
        output[index:index] = ["[Proxy Group]", POLICY, ""]
    elif not replacements and "[Proxy Group]" in sections:
        output.remove(POLICY)
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
    # Keep the previously published URL working.
    legacy_path.write_text(results["lazy_group.conf"], encoding="utf-8")
    print(f"Generated {len(results)} custom configurations")


if __name__ == "__main__":
    source, destination, legacy = map(Path, sys.argv[1:])
    generate_all(source, destination, legacy)
