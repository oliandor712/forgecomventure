#!/usr/bin/env python3
"""Agent manager for the Concordia background agents (see .claude/skills/agent-manager/SKILL.md).

    python3 tools/agents/agentctl.py status                      # agents, sessions, triggers, context sync state
    python3 tools/agents/agentctl.py check                       # lint the briefs, registry and shared context
    python3 tools/agents/agentctl.py request <agent|manager|all> "text"   # log a user instruction (dated)
    python3 tools/agents/agentctl.py update "text"               # add a dated line to CONTEXT.md "Recent updates"
    python3 tools/agents/agentctl.py message <agent|all>         # print the context-update message to send
    python3 tools/agents/agentctl.py sent <agent|all>            # record that the current context was sent

The registry (tools/agents/registry.json) keeps each agent's brief, session, folders, triggers and every request the
user made about it. CONTEXT.md is the shared context all agents read first. Messages are sent from the main session
with the remote session tools (send_message); this script only prepares them and keeps the record.
"""
import datetime, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
REG = os.path.join(ROOT, 'tools', 'agents', 'registry.json')
CONTEXT = os.path.join(ROOT, 'tools', 'agents', 'CONTEXT.md')
KEEP_UPDATES = 12  # "Recent updates" lines kept in CONTEXT.md; older ones stay in git history


def load():
    return json.load(open(REG))


def save(reg):
    open(REG, 'w').write(json.dumps(reg, indent=1, ensure_ascii=False) + '\n')


def today():
    return datetime.date.today().isoformat()


def git(*args):
    return subprocess.run(['git', '-C', ROOT] + list(args), capture_output=True, text=True).stdout.strip()


def last_commit(path):
    return git('log', '-1', '--format=%h', '--', path)


def names(reg, who):
    if who == 'all':
        return list(reg['agents'])
    if who not in reg['agents']:
        sys.exit('unknown agent %r (have: %s)' % (who, ', '.join(reg['agents'])))
    return [who]


def files_of(reg, name):
    return [os.path.relpath(CONTEXT, ROOT), reg['agents'][name]['brief']]


def status(reg):
    for name, a in reg['agents'].items():
        sent = reg.get('context_sent', {}).get(name)
        cur = {f: last_commit(f) for f in files_of(reg, name)}
        stale = not sent or any(sent.get(f) != h for f, h in cur.items())
        print('%s  (%s)' % (name, a['model']))
        print('  session  %s' % a['session'])
        print('  brief    %s   folders: %s' % (a['brief'], ', '.join(a['folders'])))
        for t, what in a['triggers'].items():
            print('  trigger  %s  %s' % (t, what))
        print('  requests %d, last: %s' % (len(a['requests']), a['requests'][-1][1][:90] if a['requests'] else '-'))
        print('  context  %s' % ('NOT SENT since the last change' if stale else 'in sync (sent %s)' % sent.get('date')))
    m = reg.get('manager', {})
    print('manager check-in trigger: %s; %d requests' % (m.get('checkin_trigger'), len(m.get('requests', []))))


def check(reg):
    problems = []
    ctx = open(CONTEXT).read()
    for name, a in reg['agents'].items():
        p = os.path.join(ROOT, a['brief'])
        if not os.path.exists(p):
            problems.append('%s: brief %s missing' % (name, a['brief']))
            continue
        s = open(p).read()
        if not s.startswith('---') or 'name: %s' % name not in s.split('---')[1]:
            problems.append('%s: brief has no frontmatter with name: %s' % (name, name))
        if 'tools/agents/CONTEXT.md' not in s:
            problems.append('%s: brief does not tell the agent to read tools/agents/CONTEXT.md' % name)
        if a['session'] not in ctx:
            problems.append('%s: session %s not in CONTEXT.md agents table' % (name, a['session']))
        for f in a['folders']:
            if f not in s:
                problems.append('%s: folder %s not named in the brief' % (name, f))
    for rule in ('Equal life', 'forge-core', 'Pushing', 'setup.sh'):
        if rule not in ctx:
            problems.append('CONTEXT.md lacks the "%s" rule' % rule)
    print('\n'.join(problems) or 'ok')
    return 1 if problems else 0


def update(text):
    s = open(CONTEXT).read()
    head, sep, tail = s.partition('## Recent updates\n')
    if not sep:
        sys.exit('CONTEXT.md has no "## Recent updates" section')
    lines = [l for l in tail.splitlines() if l.strip()]
    items, cur = [], []
    for l in lines:  # items are "- ..." with indented continuation lines
        if l.startswith('- ') and cur:
            items.append(cur); cur = []
        cur.append(l)
    if cur:
        items.append(cur)
    items.insert(0, ['- %s: %s' % (today(), text)])
    out = head + sep + '\n'.join('\n'.join(i) for i in items[:KEEP_UPDATES]) + '\n'
    open(CONTEXT, 'w').write(out)
    print('added to CONTEXT.md: %s' % text)


def message(reg, name):
    a = reg['agents'][name]
    sent = reg.get('context_sent', {}).get(name, {})
    since = min((v for k, v in sent.items() if k != 'date'), default=None)
    changed = []
    for f in files_of(reg, name):
        log = git('log', '--format=%h %s', (since + '..HEAD') if since else '-3', '--', f)
        if log:
            changed.append('%s:\n%s' % (f, '\n'.join('  ' + l for l in log.splitlines()[:6])))
    ups = open(CONTEXT).read().partition('## Recent updates\n')[2].strip()
    print('Context update from the main session (no reply needed). Pull campaign-design, then re-read '
          'tools/agents/CONTEXT.md and %s before your next step; they replace any earlier instructions that conflict.'
          % a['brief'])
    if changed:
        print('\nChanged since your last context update:\n' + '\n'.join(changed))
    print('\nRecent updates (from CONTEXT.md):\n' + ups)
    print('\nYour standing requests from the user, oldest first:')
    for d, r in a['requests']:
        print('- %s: %s' % (d, r))


def sent(reg, name):
    reg.setdefault('context_sent', {})[name] = dict({f: last_commit(f) for f in files_of(reg, name)}, date=today())


def main(argv):
    if not argv:
        print(__doc__); return 2
    reg = load()
    cmd = argv[0]
    if cmd == 'status':
        status(reg)
    elif cmd == 'check':
        return check(reg)
    elif cmd == 'request':
        who, text = argv[1], ' '.join(argv[2:])
        targets = ['manager'] if who == 'manager' else names(reg, who)
        for n in targets:
            (reg['manager'] if n == 'manager' else reg['agents'][n]).setdefault('requests', []).append([today(), text])
        save(reg); print('logged for %s' % ', '.join(targets))
    elif cmd == 'update':
        update(' '.join(argv[1:]))
    elif cmd == 'message':
        for n in names(reg, argv[1]):
            if argv[1] == 'all':
                print('===== %s (%s)' % (n, reg['agents'][n]['session']))
            message(reg, n)
    elif cmd == 'sent':
        for n in names(reg, argv[1]):
            sent(reg, n)
        save(reg); print('recorded')
    else:
        print(__doc__); return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
