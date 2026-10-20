#!/usr/bin/env python3
"""Shrink a Commander .dck to a smaller main deck, keeping proportions: basics scaled by the same factor, nonbasics
sampled with a fixed seed, `--keep` names always included. Usage: shrink_deck.py in.dck out.dck [--main 29] [--keep A,B]"""
import random, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--main', type=int, default=29); ap.add_argument('--keep', default=''); ap.add_argument('--seed', type=int, default=1)
a = ap.parse_args()
BASIC = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'}
head, main, tail, sec = [], [], [], None
for line in open(a.src).read().split('\n'):
    if line.startswith('['):
        sec = line.strip()
    if sec == '[Main]' and line and not line.startswith('['):
        m = re.match(r'(\d+) ([^|]+)(\|.*)?$', line)
        main.append((int(m.group(1)), m.group(2), m.group(3) or ''))
    elif sec == '[Main]':
        head.append(line)
    elif sec is not None and sec != '[Main]' and head and head[-1] != '__MAIN_DONE__' and False:
        pass
    else:
        (tail if main else head).append(line)
total = sum(n for n, _, _ in main)
keep = [k for k in a.keep.split(',') if k]
basics = [(n, nm, s) for n, nm, s in main if nm in BASIC]
nonb = [(n, nm, s) for n, nm, s in main if nm not in BASIC]
kept = [x for x in nonb if x[1] in keep]
rest = [x for x in nonb if x[1] not in keep]
f = (a.main) / total
b_new = [(max(1, round(n * f)), nm, s) for n, nm, s in basics]
room = a.main - sum(n for n, _, _ in b_new) - sum(n for n, _, _ in kept)
random.Random(a.seed).shuffle(rest)
pick = []
for x in rest:
    if room <= 0: break
    pick.append((1, x[1], x[2])); room -= 1
out = b_new + kept + pick
# trim/pad basics so the total is exact
diff = a.main - sum(n for n, _, _ in out)
if diff and b_new:
    n, nm, s = out[0]; out[0] = (n + diff, nm, s)
open(a.dst, 'w').write('\n'.join(head) + '\n' + '\n'.join(f'{n} {nm}{s}' for n, nm, s in out) + '\n' + '\n'.join(tail))
print(a.dst, 'main', sum(n for n, _, _ in out), 'of', total)
