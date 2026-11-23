#!/usr/bin/env python3
"""Pinned, copy-only Claude Code skill setup. No upstream programs are executed."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent

def load_sources():
    return json.loads((ROOT / 'sources.lock.json').read_text())['sources']

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def source_dir(cache, source):
    return cache / (source['id'] + '-' + source['commit'])

def digest_tree(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if '.git' in p.relative_to(root).parts:
            continue
        if p.is_symlink():
            raise ValueError('Symlinks are not accepted: ' + str(p))
        if p.is_file():
            result[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result

def fetch(cache, sources):
    cache.mkdir(parents=True, exist_ok=True)
    for source in sources:
        dest = source_dir(cache, source)
        stamp = cache / (dest.name + '.sha256.json')
        if dest.exists():
            if not stamp.exists() or digest_tree(dest) != json.loads(stamp.read_text()):
                raise ValueError('Cache changed or incomplete. Keep it for inspection, then move it aside: ' + str(dest))
            print('Verified cached source:', source['id'])
            continue
        with tempfile.TemporaryDirectory(dir=cache) as temp:
            temp = Path(temp)
            git = temp / 'git'
            run('git', 'init', '--quiet', str(git))
            run('git', '-C', str(git), 'remote', 'add', 'origin', source['url'])
            run('git', '-c', 'core.hooksPath=/dev/null', '-C', str(git), 'fetch', '--quiet', '--depth=1', 'origin', source['commit'])
            actual = subprocess.check_output(['git','-C',str(git),'rev-parse','FETCH_HEAD'], text=True).strip()
            if actual != source['commit']:
                raise ValueError('Commit mismatch')
            archive = subprocess.check_output(['git','-C',str(git),'archive','--format=tar',actual])
            content = temp / 'content'
            content.mkdir()
            with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
                members = tf.getmembers()
                for member in members:
                    parts = Path(member.name).parts
                    if member.name.startswith('/') or '..' in parts or not (member.isfile() or member.isdir()):
                        raise ValueError('Unsafe archive member: ' + member.name)
                tf.extractall(content, members=members, filter='data')
            # The stamp checks later local drift; it is not an upstream signature.
            stamp_data = digest_tree(content)
            content.rename(dest)
            stamp.write_text(json.dumps(stamp_data, indent=2) + '\n')
        print('Fetched pinned source:', source['id'])

def entries(cache, sources):
    result = []
    for source in sources:
        base = source_dir(cache, source)
        if not base.is_dir():
            raise ValueError('Source missing. Run fetch first: ' + str(base))
        stamp = cache / (base.name + '.sha256.json')
        if not stamp.exists() or digest_tree(base) != json.loads(stamp.read_text()):
            raise ValueError('Cached source changed: ' + str(base))
        skill = base / source['skill_path']
        if source['id'] == 'design':
            styles = sorted(p for p in skill.iterdir() if (p/'SKILL.md').is_file())
            if len(styles) != 67:
                raise ValueError('Expected exactly 67 design styles')
            result.extend(('design-' + p.name, p, source) for p in styles)
        else:
            names = {'taste':'design-taste-frontend','impeccable':'impeccable','img2threejs':'img2threejs','playwright':'playwright-cli'}
            if not (skill/'SKILL.md').is_file():
                raise ValueError('Missing SKILL.md: ' + str(skill))
            result.append((names[source['id']], skill, source))
    return result

def transform(text, name, source_id):
    if not text.startswith('---\n'):
        raise ValueError('Missing YAML frontmatter')
    split = text.find('\n---\n', 4)
    if split < 0:
        raise ValueError('Unclosed YAML frontmatter')
    front, body = text[4:split], text[split+5:]
    if source_id == 'taste':
        # At this exact pin hooks is the final frontmatter property.
        front = re.sub(r'^hooks:\n.*\Z', '', front, flags=re.M | re.S).rstrip()
    front, count = re.subn(r'^name:.*$', 'name: ' + name, front, count=1, flags=re.M)
    if count != 1:
        raise ValueError('Missing name')
    return '---\n' + front + '\n---\n' + body

def state_path(target):
    return target / '.ui-skills-kit-state.json'

def copy_skill(src, dest, name, source):
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns('.git'))
    skill = dest/'SKILL.md'
    skill.write_text(transform(skill.read_text(), name, source['id']))
    base = src
    while not (base/'LICENSE').is_file() and base.parent != base:
        base = base.parent
    if (base/'LICENSE').is_file():
        shutil.copy2(base/'LICENSE', dest/'UPSTREAM-LICENSE.txt')
    for notice in ['NOTICE', 'NOTICE.md']:
        if (base/notice).is_file():
            shutil.copy2(base/notice, dest/'UPSTREAM-NOTICE.txt')
    (dest/'KIT-PROVENANCE.json').write_text(json.dumps(source, indent=2)+'\n')

def install(target, cache, sources, apply):
    items = entries(cache, sources)
    if state_path(target).exists():
        raise ValueError('A kit install is already tracked here. Verify it, then follow UPDATING.md.')
    collisions = [str(target/name) for name, _, _ in items if os.path.lexists(target/name)]
    if collisions:
        raise ValueError('No files changed. Existing destinations:\n'+'\n'.join(collisions))
    # Reject symlinks even in subdirectories before writing anything.
    for _, src, _ in items:
        digest_tree(src)
    print('Plan:',len(items),'folders ->',target)
    print('Taste skill-local hook removed; design frontmatter names namespaced. settings.json untouched.')
    if not apply:
        print('Preview only. Add --apply to install.')
        return
    target.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        with tempfile.TemporaryDirectory(prefix='.ui-kit-stage-', dir=target) as stage:
            stage = Path(stage)
            records = {}
            for name, src, source in items:
                copy_skill(src,stage/name,name,source)
                records[name] = digest_tree(stage/name)
            for name, _, _ in items:
                if os.path.lexists(target/name):
                    raise ValueError('Destination appeared during install: ' + name)
                (stage/name).rename(target/name)
                created.append(target/name)
            state_path(target).write_text(json.dumps({'format':1,'sources':sources,'files':records},indent=2)+'\n')
    except Exception:
        for p in reversed(created):
            shutil.rmtree(p)
        raise
    print('Installed',len(created),'folders. Restart Claude Code when ready; no Claude process was launched.')

def inspect(target, remove=False, apply=False):
    state = json.loads(state_path(target).read_text())
    changed = []
    if len(state['files']) != 71 or any(not re.fullmatch(r'[a-z0-9][a-z0-9-]*', n) for n in state['files']):
        raise ValueError('Unexpected state manifest; inspect it manually')
    for name, expected in state['files'].items():
        p = target/name
        try:
            good = p.is_dir() and not p.is_symlink() and digest_tree(p)==expected
        except ValueError:
            good = False
        if not good:
            changed.append(name)
    if changed:
        raise ValueError('Missing or modified folders; nothing removed: '+', '.join(changed))
    print('Verified',len(state['files']),'installed folder hashes, including support files.')
    if remove:
        if not apply:
            print('Uninstall preview only. Add --apply to remove only these tracked folders.')
            return
        for name in state['files']:
            shutil.rmtree(target/name)
        state_path(target).unlink()
        print('Removed tracked folders. Unrelated skills and settings were not touched.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['fetch','install','verify','uninstall'])
    p.add_argument('--skills-dir',type=Path,default=Path.home()/'.claude/skills')
    p.add_argument('--cache-dir',type=Path,default=Path.home()/'.cache/claude-ui-skills-kit')
    p.add_argument('--apply',action='store_true',help='Required for install/uninstall writes; fetch always downloads')
    a=p.parse_args()
    if a.skills_dir.is_symlink():
        p.error('Choose a real skills directory, not a symlink')
    target=a.skills_dir.expanduser().absolute()
    cache=a.cache_dir.expanduser().absolute()
    try:
        if a.action=='fetch': fetch(cache,load_sources())
        elif a.action=='install': install(target,cache,load_sources(),a.apply)
        else: inspect(target,remove=a.action=='uninstall',apply=a.apply)
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        p.exit(1,str(e)+'\n')

if __name__=='__main__':
    main()
