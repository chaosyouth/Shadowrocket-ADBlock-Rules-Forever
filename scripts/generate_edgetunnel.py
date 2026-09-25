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
    required = ["[General]", "[Proxy Group]", "[Rule]"]
    lines = source.splitlines()
    if any(lines.count(section) != 1 for section in required):
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
    if not replacements:
        raise ValueError("上游未发现 PROXY 引用，请检查格式变化")
    return "\n".join(line.rstrip() for line in output) + "\n"


if __name__ == "__main__":
    source, destination = map(Path, sys.argv[1:])
    result = generate(source.read_text(encoding="utf-8-sig"))
    destination.write_text(result, encoding="utf-8")
