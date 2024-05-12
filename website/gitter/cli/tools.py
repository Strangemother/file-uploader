from pathlib import Path
from trim.cli import run as trun

EMPTY = None # '__blank__'
DROP = {}


def pop_first(d, *keys, default=None):
    for k in keys:
        r = d.pop(k, DROP)
        if r is DROP:
            r = None
            continue
        return d,r
    return d, default


class Props(object):

    def prop_C(self, **props):
        CHANGE = {}
        props, v = pop_first(props, 'C', 'cwd', default=CHANGE)
        if v is CHANGE:
            # replace with the git_dir parent if any.
            gd = self.prop_git_dir(**props)
            if gd in (DROP, None):
                # No C
                self.debug('No git-dir')
                return DROP
            self.debug('Using git-dir as C prop')

            parent = Path(gd).parent
            if props.get('absolute_parent', False):
                parent = parent.absolute()
            return parent.as_posix()
        return v

    def prop_git_dir(self, **props):
        props, v = pop_first(props, 'git_dir', 'git-dir', default=DROP)
        return v



def quoted(value):
    return f'"{value}"'


def standard_field(value):
    return str(value)


class Command(Props):
    app = 'git'
    submodule = ''
    prop_args_key = '_run_args'
    options = None
    _execute = True

    def __init__(self, **early):
        self.early = early
        self.args = ()
        self.kwargs = None

    def run(self, *args, **kwargs):
        ss = self.render_command(*args, **kwargs)
        res = self.execute(ss)
        return self.clean(res, neat=False)

    def render_command(self, *args, **kwargs):
        cook = kwargs.pop('cook', None) or False
        if cook:
            self.args = args
            args = ()
            kw = (self.kwargs or {})
            kw.update(kwargs)
            self.kwargs = kw
            kwargs = {}
        props = self.early.copy()
        props.update(kwargs)
        props[self.prop_args_key] = (self.args or ()) + args
        app_props = self.grab_app_props(**props)
        tool_props = self.grab_tool_props(**props)
        ss = self.build_command(app_props, tool_props, props)

        return ss

    def as_string(self,*args, **kwargs):
        return self.render_command(*args, **kwargs)

    def cache_command(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def build_command(self, app_props, tool_props, props):
        app_switches = self.dict_to_switches(app_props)
        tool_switches = self.dict_to_switches(tool_props)
        ss = (self.app,) + app_switches + (self.submodule,) + tool_switches + self.command_tail(**props)
        return ss

    def command_tail(self, **props):
        return ()

    def clean(self, res, **_):
        return res.split('\n')

    def debug(self, *a):
        print(*map(str, a))

    def join_command_list(self, switch_list):
        return ' '.join(switch_list)

    def execute(self, switch_list):
        ss= self.join_command_list(switch_list)
        self.debug(f'executing git command "{ss}"')
        if self._execute:
            func = getattr(self, 'dry_run', trun.read_one_stream_command)
            return func(ss)
        self.debug(self.__class__.__name__, 'run false execute', ss)
        return ""

    def dict_to_switches(self, opts):
        """Covet dict to switches.
        """
        res = ()
        converts = getattr(self, 'convert', {})
        for k,v in opts.items():
            dashes = '-' * (1 + (len(k) > 1))
            ck = k.replace('_', '-')
            s = f'{dashes}{ck}'
            if v is DROP:
                continue
            a = (s,)
            if v != EMPTY:
                c = converts.get(k, standard_field)
                a += (c(v),)
            res += a
        return res

    def grab_app_props(self, **props):
        """Grab python props specific to the git app.

        git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]
            [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
            [-p|--paginate|-P|--no-pager] [--no-replace-objects] [--bare]
            [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
            [--super-prefix=<path>] [--config-env=<name>=<envvar>]
            <command> [<args>]

            -v | --version
            -h | --help
            -C <path>
            -c <name>=<value>
            --exec-path
            --html-path
            --man-path
            --info-path
            -p|--paginate|-P|--no-pager
            --no-replace-objects
            --bare
            --git-dir=<path>
            --work-tree=<path>
            --namespace=<name>
            --super-prefix=<path>
            --config-env=<name>=<envvar>
        """
        props = {
            'git_dir': self.prop_git_dir(**props),
            'C': self.prop_C(**props)
        }

        return props

    def grab_tool_props(self, **props):
        """Return Keys specific to the git status. Found in git status -g
        values of "None" apply a empty switch {'foo': None} == "git status --foo"
        Use `DROP` to drop a key if unpopulated `{foo: DROP}` == `git status`
        """
        f_opts = self.get_forced_props()
        f_opts.update(self.kwargs or {})
        opts = self.grab_drop_options(**props)
        f_opts.update(opts)
        return f_opts

    def grab_drop_options(self, **props):
        res = {}
        MISSING = {}
        o = self.options or ()
        for e in o:
            if isinstance(e, str):
                e = (e,)
            # self.debug('Looking at', e)
            for k in e:
                v = props.get(k, MISSING)
                if v is MISSING:
                    continue
                res[k] = v
                # self.debug('Found', k)
                break
        # self.debug('Returning', len(res), 'options')
        return res

    def get_forced_props(self):
        return {}

    def __str__(self):
        return self.join_command_list(self.render_command())


class GitAdd(Command):
    """
    git add [--verbose | -v] [--dry-run | -n] [--force | -f] [--interactive | -i]
        [--patch | -p] [--edit | -e] [--[no-]all | --[no-]ignore-removal |
        [--update | -u]] [--sparse] [--intent-to-add | -N] [--refresh]
        [--ignore-errors] [--ignore-missing] [--renormalize] [--chmod=(+|-)x]
        [--pathspec-from-file=<file> [--pathspec-file-nul]]
      [--] [<pathspec>…​]
    """
    submodule = 'add'
    prop_args_key = 'pathspec'
    options = (
            ('h', 'help',),
            ('v', 'verbose'),
            ('dry_run', 'n'),
            ('force', 'f'),
            ('interactive', 'i'),
            ('patch', 'p'),
            ('edit', 'e'),
            ('no_all',),
            ('all',),
            ('no_ignore_removal',),
            ('ignore_removal',),
            ('update', 'u',),
            ('sparse',),
            ('intent_to_add', 'N'),
            ('refresh',),
            ('ignore_errors',),
            ('ignore_missing',),
            ('renormalize',),
            ('chmod',),
            ('pathspec_from_file',),
            ('pathspec_file_nul',),
        )

    def command_tail(self, pathspec, **props):
        """return a tuple..
        """
        return pathspec


class GitCommit(GitAdd):
    """
    git commit [-a | --interactive | --patch] [-s] [-v] [-u<mode>] [--amend]
       [--dry-run] [(-c | -C | --squash) <commit> | --fixup [(amend|reword):]<commit>)]
       [-F <file> | -m <msg>] [--reset-author] [--allow-empty]
       [--allow-empty-message] [--no-verify] [-e] [--author=<author>]
       [--date=<date>] [--cleanup=<mode>] [--[no-]status]
       [-i | -o] [--pathspec-from-file=<file> [--pathspec-file-nul]]
       [(--trailer <token>[(=|:)<value>])…​] [-S[<keyid>]]
       [--] [<pathspec>…​]
    """
    submodule = 'commit'

    options = (
            ('h', 'help',),
           ("a", "interactive", "patch",),
           ("s",),
           ("v",),
           ("u",),
           ("amend",),
           ('dry-run',),
           ('c', 'C', 'squash',),
           ('fixup',),
           ('F', 'm',),
           ('reset-author',),
           ('allow-empty',),
           ('allow-empty-message',),
           ('no-verify',),
           ('e',),
           ('author',),
           ('date',),
           ('cleanup',),
           ('no-status',),
           ('status',),
           ('i', 'o', ),
           ('pathspec-from-file',),
           ('pathspec-file-nul',),
           ('trailer',),
           ('S',),
        )

    convert = {
        'm': quoted
    }

    def command_tail(self, pathspec, **props):
        """return a tuple..
        """
        return pathspec


class GitStatus(Command):
    """
    https://git-scm.com/docs/git


    (env)>git status -h
    usage: git status [<options>] [--] <pathspec>...

        -v, --verbose         be verbose
        -s, --short           show status concisely
        -b, --branch          show branch information
        --porcelain           machine-readable output
        --long                show status in long format (default)
        -z, --null            terminate entries with NUL
        -u, --untracked-files[=<mode>]
                              show untracked files, optional modes: all, normal, no. (Default: all)
        --ignored             show ignored files
        --ignore-submodules[=<when>]
                              ignore changes to submodules, optional when: all, dirty, untracked. (Default: all)
        --column[=<style>]    list untracked files in columns

        Using git-dir as C prop
        exeucting git command git --git-dir c:/.../.git -C c:/..us --porcelain
         M django-trim/dev_install.bat
         M django-trim/docs/views/serialized.md
         M django-trim/src/trim/cli/base.py
         M django-trim/src/trim/cli/primary.py
         M django-trim/src/trim/cli/run.py
        ?? django-trim/_dist/


        (('M', 'django-trim/dev_install.bat'),
         ('M', 'django-trim/docs/views/serialized.md'),
         ('M', 'django-trim/src/trim/cli/base.py'),
         ('M', 'django-trim/src/trim/cli/primary.py'),
         ('M', 'django-trim/src/trim/cli/run.py'),
         ('??', 'django-trim/_dist/'))
    """

    submodule = 'status'

    def get_forced_props(self):
        return {
            'porcelain': EMPTY
        }

    def grab_tool_props(self, **props):
        """Return Keys specific to the git status. Found in git status -g
        values of "None" apply a empty switch {'foo': None} == "git status --foo"
        Use `DROP` to drop a key if unpopulated `{foo: DROP}` == `git status`
        """
        res = super().grab_tool_props(**props)
        res.update(branch=self.prop_branch(**props))
        return res

    def prop_branch(self, **props):
        """Return -b --branch or DROP. if DROP, the branch is sthe current
        """
        props, v = pop_first(props, 'b', 'branch', default=DROP)
        return v

    def clean(self, info, neat=True):
        """Given the content from the result, convert to code
            (Pdb) pp(info)
            (' M django-trim/dev_install.bat\n'
             ' M django-trim/docs/views/serialized.md\n'
             ' M django-trim/src/trim/cli/base.py\n'
             ' M django-trim/src/trim/cli/primary.py\n'
             ' M django-trim/src/trim/cli/run.py\n'
             '?? django-trim/_dist/\n')
        """

        res = ()
        states = {
            'M': 'modified',
            '??': 'untracked',
            'D': 'deleted',
        }

        lines = info.split('\n')
        l = len(lines)
        for i, line in enumerate(lines):
            ## skip the last line if its blank
            if (i == l-1) and len(line) == 0: continue

            a = line[0:3].strip()
            state = states.get(a) if neat else a
            entry = state, line[3:]
            res += (entry, )
        return res


class GitPull(Command):
    """
    git push [--all | --mirror | --tags] [--follow-tags] [--atomic] [-n | --dry-run] [--receive-pack=<git-receive-pack>]
       [--repo=<repository>] [-f | --force] [-d | --delete] [--prune] [-v | --verbose]
       [-u | --set-upstream] [-o <string> | --push-option=<string>]
       [--[no-]signed|--signed=(true|false|if-asked)]
       [--force-with-lease[=<refname>[:<expect>]] [--force-if-includes]]
       [--no-verify] [<repository> [<refspec>…​]]


    """
    submodule = 'pull'
    options = (
        ('h', 'help',),
        ('all', 'mirror', 'tags',),
        ('follow-tags',),
        ('atomic',),
        ('n', 'dry-run',),
        ('receive-pack',),
        ('repo',),
        ('f', 'force',),
        ('d', 'delete',),
        ('prune',),
        ('v', 'verbose',),
        ('u', 'set-upstream',),
        ('o', 'push-option',),
        ('no-signed signed',),
        ('force-with-lease',),
        ('force-if-includes',),
        ('no-verify',),
        # ('<repository>',),
        # ('<refspec>',),
    )


class GitPush(GitPull):
    """
    git push [--all | --mirror | --tags] [--follow-tags] [--atomic] [-n | --dry-run] [--receive-pack=<git-receive-pack>]
       [--repo=<repository>] [-f | --force] [-d | --delete] [--prune] [-v | --verbose]
       [-u | --set-upstream] [-o <string> | --push-option=<string>]
       [--[no-]signed|--signed=(true|false|if-asked)]
       [--force-with-lease[=<refname>[:<expect>]] [--force-if-includes]]
       [--no-verify] [<repository> [<refspec>…​]]
    """
    submodule = 'push'



from pprint import pprint as pp

g = GitStatus(git_dir='c:/Users/jay/Documents/projects/django-trim/.git')
r = g.run()
pp(r)

a = GitAdd(dry_run=None).render_command("foo", interactive=None)
e = ('git', 'add', '--dry-run', '--interactive', 'foo')
assert a == e

g = GitAdd(git_dir='path/.git')
g.cache_command(".", '*.py')
r = g.render_command()
e = ('git', '--git-dir', 'path/.git', '-C', 'path', 'add', '.', '*.py')
assert e == r

e = 'git --git-dir path/.git -C path add . *.py'
assert str(g) == e
print(g)
print(e)


g = GitCommit(git_dir='foo/.git')
r = g.render_command(m="Some message", cook=True)
e = 'git --git-dir foo/.git -C foo commit -m "Some message"'
assert str(g) == e




