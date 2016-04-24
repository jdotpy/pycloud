import sys
import os
import subprocess

EDITOR_FALLBACK = 'vim'
def user_edit(tmp_file, initial_content='', editor=None):
    if editor is None:
        try:
            env_editor = os.environ['EDITOR']
        except KeyError:
            editor = None
        else:
            if env_editor:
                editor = env_editor
    if editor is None:
        editor = EDITOR_FALLBACK

    with open(tmp_file, 'w') as f:
        f.write(initial_content)
    subprocess.call([editor, tmp_file], stdout=sys.stdout, stderr=sys.stderr)
    with open(tmp_file, 'r') as f:
        new_contents = f.read()
    os.remove(tmp_file)
    return new_contents

if __name__ == '__main__':
    """ Usage """
    path = '/tmp/file.txt'
    initial_content = 'hiya'
    new_content = user_edit(path, initial_content)
    print('You wrote:\n', new_content)
