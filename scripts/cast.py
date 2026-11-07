"""Offline Liuyao chart CLI. Lines are always bottom to top."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from backend.core.liuyao_engine import LiuyaoEngine


def chart(values, timestamp):
    if len(values) != 6 or any(type(v) is not int or v not in (6, 7, 8, 9) for v in values):
        raise ValueError('Provide exactly six values (6, 7, 8 or 9), bottom to top.')
    moment = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    if moment.tzinfo is None:
        raise ValueError('Timestamp must include UTC offset, e.g. +08:00 or -05:00.')
    local = moment.astimezone(timezone(timedelta(hours=8)))
    engine = LiuyaoEngine()
    bits = [v % 2 for v in values]
    result = engine.paipan(dict(yao_list=bits, changing_yao=[v in (6, 9) for v in values],
        **{k: getattr(local, k) for k in ('year', 'month', 'day', 'hour', 'minute', 'second')}))
    def projection(line):
        return {k: getattr(line, k) for k in ('yin_yang', 'dizhi', 'wuxing', 'liuqin', 'is_kong')}
    return dict(schema_version='yizhan.local.v1', line_values=values,
        timestamp=local.isoformat(), time_convention='UTC+08:00; late Zi keeps civil day (Exact2)',
        base=result.ben_gua_name, changed=result.bian_gua_name or result.ben_gua_name,
        palace=engine._find_gua_by_yao_list(bits)['gong'], shi=result.shi_yao, ying=result.ying_yao,
        calendar=result.gan_zhi, xunkong=list(result.xunkong),
        lines=[dict(projection(y), position=i+1, value=values[i],
                    is_changing=y.is_changing, liushen=y.liushen, changed=projection(y.biangua_info))
               for i, y in enumerate(result.yao_list)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--lines', nargs=6, type=int)
    group.add_argument('--random', action='store_true', help='Explicitly request a simulated three-coin cast')
    parser.add_argument('--timestamp', required=True, help='ISO 8601 with UTC offset')
    args = parser.parse_args()
    values = args.lines if args.lines else [sum(secrets.choice((2, 3)) for _ in range(3)) for _ in range(6)]
    try:
        output = chart(values, args.timestamp)
    except ValueError as error:
        parser.error(str(error))
    output['input_method'] = 'simulated_coins' if args.random else 'manual_lines'
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
