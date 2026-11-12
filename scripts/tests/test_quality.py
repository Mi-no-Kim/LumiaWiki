"""Quality contracts: boundaries, staged inputs, hooks and CI decisions."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[2]
MODULES = (PROJECT / 'scripts/quality').as_uri()


class QualityTests(unittest.TestCase):
    def setUp(self):
        parent = PROJECT / '.tmp/task-42-004/fixtures'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True, encoding='utf-8').strip()

    def node(self, code):
        script = (f"const root={json.dumps(str(self.root))};\n"
                  f"const paths=await import('{MODULES}/paths.mjs');\n"
                  f"const format=await import('{MODULES}/format.mjs');\n"
                  f"const hook=await import('{MODULES}/post-edit.mjs');\n"
                  f"const ci=await import('{MODULES}/changes.mjs');\n"
                  "const fs=await import('node:fs/promises');\n"
                  "const path=await import('node:path');\n"
                  "const attempt=async(fn)=>{try{return {value:await fn()};}catch(e){return {error:e.message};}};\n"
                  + code)
        result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=PROJECT,
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def formatter_project(self):
        for name in ('package.json', 'package-lock.json', '.prettierrc.json'):
            self.write(name, (PROJECT / name).read_text(encoding='utf-8'))
        self.write('package.json', json.dumps({'devDependencies': {'prettier': '3.10.0'}}, indent=2) + '\n')
        for name in ('format', 'paths', 'process'):
            self.write('scripts/quality/' + name + '.mjs', (PROJECT / 'scripts/quality' / (name + '.mjs')).read_text(encoding='utf-8'))

    def test_normalization_rejects_escape_and_windows_ambiguity(self):
        result = self.node("""
const good=paths.normalize('docs\\\\sub/example.md');
const bad=['../x.md','docs/../x.md','C:\\\\private.md','/absolute.md','docs/a:stream','docs/a.','docs/a ','docs/*.md','docs/zero\\0.md'];
console.log(JSON.stringify({good,bad:await Promise.all(bad.map(x=>attempt(()=>paths.normalize(x))))}));
""")
        self.assertEqual(result['good'], 'docs/sub/example.md')
        self.assertTrue(all('error' in item for item in result['bad']))

    def test_allowlist_and_preservation_before_collection(self):
        names = ['README.md', 'docs/current.md', 'work/records/task.md', '.github/workflows/quality.yml',
                 'frontend/src/App.tsx', 'backend/src/main/java/Example.java', 'scripts/quality/paths.mjs',
                 'harness-design/no-read.md', '.HARNESS-STATE/no-read.json', 'work/records/artifacts/proof.md',
                 'db/migration/V1.sql', 'package-lock.json', 'scripts/a.py', 'frontend/node_modules/a.js',
                 '.env', 'other/new.ts']
        result = self.node(f'console.log(JSON.stringify({json.dumps(names)}.map(paths.formatKind)));')
        self.assertEqual(result, ['prettier'] * 5 + ['java', 'prettier'] + ['skip'] * 8 + ['unknown'])
        self.write('docs/current.md', '# Current\n')
        self.write('work/records/artifacts/proof.md', '  immutable evidence  ')
        self.write('backend/src/main/java/Example.java', 'class Example {}')
        result = self.node('console.log(JSON.stringify(await paths.collectFiles(root)));')
        self.assertEqual(sorted(result or []), ['backend/src/main/java/Example.java', 'docs/current.md'])
        self.assertEqual((self.root / 'work/records/artifacts/proof.md').read_text(), '  immutable evidence  ')

    def test_symlink_is_rejected_before_following(self):
        self.write('outside/value.md', '# Outside\n')
        (self.root / 'docs').mkdir()
        try:
            os.symlink(self.root / 'outside', self.root / 'docs/link', target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                raise
            subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(self.root / 'docs/link'), str(self.root / 'outside')],
                           check=True, capture_output=True, timeout=5)
        result = self.node("console.log(JSON.stringify(await attempt(()=>paths.safeFile(root,'docs/link/value.md'))));")
        self.assertIn('error', result)

    def test_ci_areas_and_unknown_paths_fail_safe(self):
        cases = [['frontend/src/App.tsx'], ['backend/src/main/X.java', 'db/migration/V1.sql'],
                 ['work/records/task.md'], ['scripts/quality/paths.mjs'],
                 ['harness-design/no-read.md', '.harness-state/no-read.json'], ['new-area/file'],
                 ['package-lock.json'], ['../ambiguous']]
        result = self.node(f'console.log(JSON.stringify({json.dumps(cases)}.map(paths.classifyChanges)));')
        no = dict.fromkeys(['tools', 'docs', 'frontend', 'backend'], False)
        all_areas = dict.fromkeys(no, True)
        self.assertEqual(result, [{**no, 'frontend': True}, {**no, 'backend': True},
                                  {**no, 'docs': True}, all_areas, no, all_areas, all_areas, all_areas])

    def test_ci_rename_delete_and_missing_baseline(self):
        self.git('init', '-q')
        self.git('config', 'user.name', 'Quality fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.write('docs/old.md', '# Moved\n')
        self.git('add', 'docs/old.md')
        self.git('-c', 'core.hooksPath=', 'commit', '-qm', 'fixture input')
        base = self.git('rev-parse', 'HEAD')
        self.write('frontend/src/moved.ts', '# Moved\n')
        (self.root / 'docs/old.md').unlink()
        self.git('add', 'docs', 'frontend')
        self.git('-c', 'core.hooksPath=', 'commit', '-qm', 'fixture rename')
        head = self.git('rev-parse', 'HEAD')
        result = self.node(f"console.log(JSON.stringify([await ci.changes(root,{{QUALITY_EVENT:'push',QUALITY_BASE:'{base}',QUALITY_HEAD:'{head}'}}),await ci.changes(root,{{QUALITY_EVENT:'push'}})]));")
        self.assertEqual(result, [dict(tools=False, docs=True, frontend=True, backend=False),
                                  dict.fromkeys(['tools', 'docs', 'frontend', 'backend'], True)])

    def test_ci_aggregate_rejects_failure_cancel_and_unintended_skip(self):
        result = self.node("""
const good={changes:{result:'success',outputs:{tools:'false',docs:'true',frontend:'false',backend:'false'}},tools:{result:'skipped'},docs:{result:'success'},frontend:{result:'skipped'},backend:{result:'skipped'}};
const cases=[good,...['failure','cancelled','skipped'].map(result=>({...good,docs:{result}})),{...good,changes:{result:'failure'}},{...good,changes:{result:'success',outputs:{}}}];
console.log(JSON.stringify(cases.map(ci.aggregate)));
""")
        self.assertEqual(result, [True, False, False, False, False, False])

    def test_patch_paths_and_invalid_input(self):
        patch = '*** Begin Patch\n*** Update File: docs/a.md\n*** Move to: docs/b.md\n@@\n-old\n+new\n*** Delete File: docs/deleted.md\n*** End Patch'
        result = self.node(f"console.log(JSON.stringify([hook.patchPaths({json.dumps(patch)}),await attempt(()=>hook.patchPaths('unreadable'))]));")
        self.assertEqual(result[0], ['docs/a.md', 'docs/b.md', 'docs/deleted.md'])
        self.assertIn('error', result[1])

    def test_prettier_check_is_read_only_and_write_is_idempotent(self):
        self.formatter_project()
        self.write('docs/example.json', '{"answer":42}')
        result = self.node("""
const before=await fs.readFile(path.join(root,'docs/example.json'),'utf8');
const checked=await attempt(()=>format.formatFiles(root,['docs/example.json'],{write:false}));
const after=await fs.readFile(path.join(root,'docs/example.json'),'utf8');
await format.formatFiles(root,['docs/example.json'],{write:true});
const first=await fs.readFile(path.join(root,'docs/example.json'),'utf8');
await format.formatFiles(root,['docs/example.json'],{write:true});
console.log(JSON.stringify({checked,before,after,first,second:await fs.readFile(path.join(root,'docs/example.json'),'utf8')}));
""")
        self.assertIn('error', result['checked'])
        self.assertEqual(result['before'], result['after'])
        self.assertEqual(result['first'], '{ "answer": 42 }\n')
        self.assertEqual(result['first'], result['second'])

    def test_index_uses_staged_content_and_configuration(self):
        self.formatter_project()
        self.git('init', '-q')
        self.write('.prettierrc.json', '{ "singleQuote": true }\n')
        self.write('frontend/src/example.ts', "const value = 'staged';\n")
        self.git('add', 'package.json', 'package-lock.json', '.prettierrc.json', 'frontend/src/example.ts', 'scripts/quality')
        self.write('.prettierrc.json', '{"singleQuote":false}\n')
        self.write('frontend/src/example.ts', "const value='working'\n")
        result = self.node("console.log(JSON.stringify(await attempt(()=>format.checkIndex(root))));")
        self.assertNotIn('error', result)
        self.assertEqual((self.root / 'frontend/src/example.ts').read_text(), "const value='working'\n")
        self.write('docs/bad.json', '{"unformatted":true}')
        self.git('add', 'docs/bad.json')
        result = self.node("console.log(JSON.stringify(await attempt(()=>format.checkIndex(root))));")
        self.assertIn('error', result)

    def test_hook_duplicate_and_reentry_preserve_existing_edits(self):
        self.write('docs/edit.json', '{"x":1}')
        result = self.node("""
const event={tool_name:'apply_patch',tool_use_id:'same-call',tool_input:{command:'*** Begin Patch\\n*** Update File: docs/edit.json\\n@@\\n-a\\n+b\\n*** End Patch'}};
let calls=0;
const formatter=async()=>{calls++;};
await hook.postEdit(root,event,{formatter});
await hook.postEdit(root,event,{formatter});
await fs.writeFile(path.join(root,'docs/edit.json'),'{"x":2}');
await hook.postEdit(root,event,{formatter});
let nested;
await hook.postEdit(root,{...event,tool_use_id:'outer'},{formatter:async()=>{nested=await attempt(()=>hook.postEdit(root,{...event,tool_use_id:'inner'},{formatter}));}});
console.log(JSON.stringify({calls,nested,content:await fs.readFile(path.join(root,'docs/edit.json'),'utf8')}));
""")
        self.assertEqual(result['calls'], 2)
        self.assertIn('error', result['nested'])
        self.assertEqual(result['content'], '{"x":2}')

    def test_index_uses_staged_formatter_policy(self):
        self.formatter_project()
        self.git('init', '-q')
        original = (self.root / 'scripts/quality/paths.mjs').read_text(encoding='utf-8')
        changed = original.replace('export function formatKind(input) {', "export function formatKind(input) {\n  if (input === 'docs/new.ts') return 'prettier';")
        self.write('scripts/quality/paths.mjs', changed)
        self.write('docs/new.ts', 'export const value=1')
        self.git('add', 'package.json', 'package-lock.json', '.prettierrc.json', 'scripts/quality', 'docs/new.ts')
        self.write('scripts/quality/paths.mjs', original)
        result = self.node('console.log(JSON.stringify(await attempt(()=>format.checkIndex(root))));')
        self.assertIn('error', result)

    def test_new_unclassified_index_path_requires_review_without_hook_state(self):
        self.formatter_project()
        self.git('init', '-q')
        self.write('new-area/new.ts', 'export const value = 1;\n')
        self.git('add', 'package.json', 'package-lock.json', '.prettierrc.json', 'scripts/quality', 'new-area/new.ts')
        result = self.node('console.log(JSON.stringify(await attempt(()=>format.checkIndex(root))));')
        self.assertIn('unclassified', result.get('error', '').lower())

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive pathname contract')
    def test_windows_path_case_cannot_bypass_file_lock(self):
        self.write('docs/edit.json', '{"x":1}')
        result = self.node("""
const event={tool_name:'apply_patch',tool_use_id:'lower',tool_input:{command:'*** Begin Patch\\n*** Update File: docs/edit.json\\n@@\\n-a\\n+b\\n*** End Patch'}};
let calls=0,nested;
await hook.postEdit(root,event,{formatter:async()=>{calls++;nested=await attempt(()=>hook.postEdit(root,{...event,tool_use_id:'upper',tool_input:{command:event.tool_input.command.replace('docs/edit.json','docs/EDIT.json')}},{formatter:async()=>{calls++;}}));}});
console.log(JSON.stringify({calls,nested}));
""")
        self.assertEqual(result['calls'], 1)
        self.assertIn('error', result['nested'])

    def test_absolute_patch_inside_workspace_is_supported(self):
        self.write('docs/edit.json', '{"x":1}')
        patch = f'*** Begin Patch\n*** Update File: {(self.root / "docs/edit.json").as_posix()}\n@@\n-a\n+b\n*** End Patch'
        result = self.node(f"let calls=0;const outcome=await attempt(()=>hook.postEdit(root,{{tool_name:'apply_patch',tool_use_id:'absolute',cwd:root,tool_input:{{command:{json.dumps(patch)}}}}},{{formatter:async()=>{{calls++;}}}}));console.log(JSON.stringify({{calls,outcome}}));")
        self.assertEqual(result['calls'], 1)
        self.assertNotIn('error', result['outcome'])

    def test_full_format_preserves_unclassified_failure(self):
        self.formatter_project()
        self.git('init', '-q')
        self.write('new-area/new.ts', 'export const value=1')
        result = self.node(f"""
const proc=await import('{MODULES}/process.mjs');
const event={{tool_name:'apply_patch',tool_use_id:'unclassified',tool_input:{{command:'*** Begin Patch\\n*** Update File: new-area/new.ts\\n@@\\n-a\\n+b\\n*** End Patch'}}}};
const failed=await attempt(()=>hook.postEdit(root,event));
await attempt(()=>proc.run(process.execPath,[path.join(root,'scripts/quality/format.mjs'),'--write'],{{cwd:root,quiet:true}}));
console.log(JSON.stringify({{failed,blocked:await attempt(()=>format.checkIndex(root)),content:await fs.readFile(path.join(root,'new-area/new.ts'),'utf8')}}));
""")
        self.assertIn('error', result['failed'])
        self.assertIn('error', result['blocked'])
        self.assertEqual(result['content'], 'export const value=1')

    def test_hook_failure_blocks_submission_and_allows_recovery(self):
        self.write('docs/edit.json', '{"x":1}')
        result = self.node("""
const event={tool_name:'apply_patch',tool_use_id:'failed',tool_input:{command:'*** Begin Patch\\n*** Update File: docs/edit.json\\n@@\\n-a\\n+b\\n*** End Patch'}};
const failed=await attempt(()=>hook.postEdit(root,event,{formatter:async()=>{throw Error('controlled timeout');}}));
const blocked=await attempt(()=>format.checkIndex(root));
await hook.postEdit(root,event,{formatter:async()=>{}});
console.log(JSON.stringify({failed,blocked,content:await fs.readFile(path.join(root,'docs/edit.json'),'utf8')}));
""")
        self.assertIn('error', result['failed'])
        self.assertIn('error', result['blocked'])
        self.assertEqual(result['content'], '{"x":1}')

    def test_java_hook_is_one_offline_targeted_invocation(self):
        self.formatter_project()
        self.write('backend/src/main/java/Edited.java', 'class Edited{}')
        self.write('backend/src/main/java/Untouched.java', 'class Untouched{}')
        result = self.node("""
const calls=[];
await format.formatFiles(root,['backend/src/main/java/Edited.java'],{write:true,offline:true,runGradle:async(r,args)=>calls.push(args)});
console.log(JSON.stringify(calls));
""")
        self.assertEqual(len(result), 1)
        self.assertIn('--offline', result[0])
        self.assertIn('spotlessApply', result[0])
        self.assertTrue(any(part.startswith('-PspotlessIdeHook=') for part in result[0]))
        self.assertTrue(any('Edited' in part and 'Untouched' not in part for part in result[0]))

    def test_real_hook_formats_only_the_edited_file_silently(self):
        self.formatter_project()
        self.git('init', '-q')
        for source in (PROJECT / 'scripts/quality').glob('*.mjs'):
            self.write('scripts/quality/' + source.name, source.read_text(encoding='utf-8'))
        self.write('docs/edited.json', '{"x":1}')
        self.write('docs/untouched.json', '{"x":2}')
        result = self.node("""
const event={tool_name:'apply_patch',tool_use_id:'real-call',cwd:root,tool_input:{command:'*** Begin Patch\\n*** Update File: docs/edited.json\\n@@\\n-a\\n+b\\n*** End Patch'}};
const outcome=await attempt(()=>hook.postEdit(root,event));
console.log(JSON.stringify({outcome,edited:await fs.readFile(path.join(root,'docs/edited.json'),'utf8'),untouched:await fs.readFile(path.join(root,'docs/untouched.json'),'utf8')}));
""")
        self.assertNotIn('error', result['outcome'])
        self.assertEqual(result['edited'], '{ "x": 1 }\n')
        self.assertEqual(result['untouched'], '{"x":2}')

    def test_process_timeout_is_failure(self):
        result = self.node(f"const proc=await import('{MODULES}/process.mjs');const start=performance.now();const outcome=await attempt(()=>proc.run(process.execPath,['-e','setTimeout(()=>{{}},10000)'],{{cwd:root,timeout:40,quiet:true}}));console.log(JSON.stringify({{outcome,elapsed:performance.now()-start}}));")
        self.assertIn('error', result['outcome'])
        self.assertLess(result['elapsed'], 2000)

    def test_unprepared_offline_java_does_not_start_wrapper(self):
        self.formatter_project()
        self.write('backend/src/main/java/Example.java', 'class Example{int value=1;}')
        self.write('backend/gradlew.bat', '@echo off\r\ntype nul > "..\\wrapper-called"\r\nexit /b 0\r\n')
        self.write('backend/gradlew', '#!/bin/sh\n: > ../wrapper-called\nexit 0\n')
        result = self.node("console.log(JSON.stringify(await attempt(()=>format.formatFiles(root,['backend/src/main/java/Example.java'],{write:true,offline:true,quiet:true}))));")
        self.assertIn('error', result)
        self.assertFalse((self.root / 'wrapper-called').exists())

    def test_failure_state_file_cannot_follow_symlink(self):
        self.write('docs/edit.json', '{"x":1}')
        self.write('outside/proof.json', 'immutable')
        result = self.node("""
const dir=path.join(root,'.tmp/quality/failures');await fs.mkdir(dir,{recursive:true});
const target=path.join(dir,format.fingerprint('docs/edit.json')+'.json');
let unavailable=false;
try{await fs.symlink(path.join(root,'outside/proof.json'),target);}catch(e){if(e.code==='EPERM')unavailable=true;else throw e;}
if(unavailable)console.log(JSON.stringify({unavailable:true}));else{
const event={tool_name:'apply_patch',tool_use_id:'link',tool_input:{command:'*** Begin Patch\\n*** Update File: docs/edit.json\\n@@\\n-a\\n+b\\n*** End Patch'}};
const outcome=await attempt(()=>hook.postEdit(root,event,{formatter:async()=>{throw Error('controlled failure');}}));
console.log(JSON.stringify({outcome,content:await fs.readFile(path.join(root,'outside/proof.json'),'utf8')}));}
""")
        if result.get('unavailable'):
            self.skipTest('file symlink creation unavailable; exercised on Linux CI')
        self.assertEqual(result['content'], 'immutable')
        self.assertIn('error', result['outcome'])


if __name__ == '__main__':
    unittest.main()
