"""将仓库根目录的 Surge .list 严格转换为 sing-box source JSON。"""
import argparse
import ipaddress
import json
from pathlib import Path

FIELDS = {
    'DOMAIN': 'domain', 'DOMAIN-SUFFIX': 'domain_suffix',
    'DOMAIN-KEYWORD': 'domain_keyword', 'IP-CIDR': 'ip_cidr',
    'IP-CIDR6': 'ip_cidr', 'PROCESS-NAME': 'process_name',
}


def convert(text):
    values = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(('#', '//', ';')):
            continue
        parts = [part.strip() for part in line.split(',')]
        kind = parts[0].upper()
        if kind not in FIELDS or len(parts) < 2 or not parts[1]:
            raise ValueError(f'line {number}: unsupported or invalid rule: {line}')
        # no-resolve 控制 Surge DNS 行为；sing-box headless IP 规则只匹配目标 IP。
        if len(parts) > 2 and not (kind in ('IP-CIDR', 'IP-CIDR6') and parts[2:] == ['no-resolve']):
            raise ValueError(f'line {number}: unsupported options: {line}')
        value = parts[1]
        if kind in ('IP-CIDR', 'IP-CIDR6'):
            network = ipaddress.ip_network(value, strict=False)
            if network.version != (6 if kind == 'IP-CIDR6' else 4):
                raise ValueError(f'line {number}: incorrect IP family')
            value = str(network)
        elif kind.startswith('DOMAIN'):
            value = value.lower().strip('.')
            if not value or any(c.isspace() for c in value):
                raise ValueError(f'line {number}: invalid domain')
        bucket = values.setdefault(FIELDS[kind], [])
        if value not in bucket:
            bucket.append(value)
    if not values:
        raise ValueError('empty rule list')
    # 不同字段在同一 headless rule 中为 AND；分开以保留列表的 OR 语义。
    return {'version': 1, 'rules': [{field: items} for field, items in values.items()]}


def generate(root):
    sources = sorted(root.glob('*.list'))
    if not sources:
        raise ValueError('no .list sources found')
    # 全部解析成功后才写文件，错误源不会发布部分更新。
    outputs = {path.stem + '.json': json.dumps(convert(path.read_text()), ensure_ascii=False, indent=2) + '\n'
               for path in sources}
    target = root / 'sing-box'
    target.mkdir(exist_ok=True)
    for name, text in outputs.items():
        (target / name).write_text(text)
    for stale in target.glob('*.json'):
        if stale.name not in outputs:
            stale.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    generate(parser.parse_args().root)
