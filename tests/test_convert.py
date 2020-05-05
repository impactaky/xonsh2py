import xonsh2py

def test_function():
    assert xonsh2py.convert(
        "ret=$(ls $HOME/*.txt | grep gcc)"
    ) == 'ret=subprocess.check_output("ls $HOME/*.txt | grep gcc", shell=True).decode()'
    assert xonsh2py.convert("ls") == 'subprocess.call("ls", shell=True)'
    assert xonsh2py.convert(
        "echo '()'") == 'subprocess.call("echo \'()\'", shell=True)'
    assert xonsh2py.convert(
        'result = $(find -name \'*.py\').rstrip()'
    ) == 'result = subprocess.check_output("find -name \'*.py\'", shell=True).decode().rstrip()'
    assert xonsh2py.convert(
        'result = $(find /etc/fonts -name @(\'*.{}\'.format(suffix))).rstrip() + $(find /etc/ld.so.conf.d -name @(\'*.{}\'.format(suffix))).rstrip()'
    ) == 'result = subprocess.check_output("find /etc/fonts -name {}".format(\'*.{}\'.format(suffix)), shell=True).decode().rstrip() + subprocess.check_output("find /etc/ld.so.conf.d -name {}".format(\'*.{}\'.format(suffix)), shell=True).decode().rstrip()'
