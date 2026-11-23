#!/usr/bin/env python3
"""Offline behavioral tests. Pass --source-cache pointing at fetched pinned sources."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('kit',ROOT/'skills-kit.py')
kit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)

class KitTests(unittest.TestCase):
    def test_hooks_removed_and_body_preserved(self):
        text='---\nname: old\ndescription: test\nhooks:\n  Stop: []\n---\n# Body\n'
        result=kit.transform(text,'design-taste-frontend','taste')
        self.assertNotIn('hooks:',result)
        self.assertIn('name: design-taste-frontend',result)
        self.assertTrue(result.endswith('# Body\n'))

    def test_namespacing(self):
        self.assertIn('name: design-minimal',kit.transform('---\nname: minimal\n---\nHi','design-minimal','design'))

    def test_missing_frontmatter(self):
        with self.assertRaises(ValueError): kit.transform('no yaml','x','design')

    def test_digest_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'link').symlink_to('/tmp')
            with self.assertRaises(ValueError): kit.digest_tree(p)

    def test_full_lifecycle(self):
        if CACHE is None: self.skipTest('use --source-cache for 71-folder integration test')
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'skills'; target.mkdir()
            (target/'existing').mkdir();(target/'existing'/'keep').write_text('keep')
            sources=kit.load_sources()
            kit.install(target,CACHE,sources,False)
            self.assertEqual(len(list(target.iterdir())),1)
            kit.install(target,CACHE,sources,True)
            self.assertEqual(len(list(target.glob('*/SKILL.md'))),71)
            self.assertIn('name: design-minimal',(target/'design-minimal'/'SKILL.md').read_text())
            self.assertNotIn('\nhooks:',(target/'design-taste-frontend'/'SKILL.md').read_text().split('\n---\n')[0])
            kit.inspect(target)
            with self.assertRaises(ValueError): kit.install(target,CACHE,sources,True)
            changed=target/'impeccable'/'SKILL.md'; original=changed.read_bytes();changed.write_text('edited')
            with self.assertRaises(ValueError):kit.inspect(target,True,True)
            changed.write_bytes(original)
            kit.inspect(target,True,True)
            self.assertEqual((target/'existing'/'keep').read_text(),'keep')
            self.assertEqual(len(list(target.iterdir())),1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-cache',type=Path)
    args,rest=p.parse_known_args();CACHE=args.source_cache
    unittest.main(argv=[sys.argv[0]]+rest)
