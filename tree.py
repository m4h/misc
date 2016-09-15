import os
import sys
from optparse import OptionParser

'''
structure:
    {
     '.vimrc':None,
     'docs':{
              'README':None,
              'mans': {}
             }
    }
'''

class RGB:
    '''
    ANSI color codes
    '''
    red = '\033[91m'
    grn = '\033[92m'
    blu = '\033[94m'
    rst = '\033[0m'

def display(path, content):
    '''
    path    - directory to display
    content - object describing files and  directories
    return  -
    '''
    text = render(content)
    print text

def render(content, mark=''):
    '''
    content - object describing files and  directories
    mark    - characters used to indent deeper objects
    return  - rendered text

    dictionary objects save keys in un-ordered manner (not like list or tuples)
    thus directory tree will be displayed not in same order as it been originaly listed
    '''
    text = ''
    # key - name of file or dir
    # val - None for file; dict for directory
    for key, val in content.iteritems():
        if val is None:
            file_name = '%s%s\n' % (mark, key)
            text += file_name
        else:
            dir_name = '%s%s%s%s/\n' % (mark, RGB.blu, key, RGB.rst)
            text += dir_name
            dir_content = content[key]
            new_mark = '  %s' % mark
            new_text = render(dir_content, new_mark)
            text += new_text
    return text

def list_dir(path, depth):
    '''
    path    - directory to list
    depth   - how deep to walk down from path
    return  - hierarchical object

    recusively will walk path until it hit negative depth
    '''
    content = {}
    if depth < 0:
        return content
    files = os.listdir(path)
    for _file in files:
        file_path = os.path.join(path, _file)
        if os.path.isdir(file_path):
            depth -= 1
            obj = list_dir(file_path, depth)
            content[_file] = obj
        else:
            content[_file] = None
    return content

if __name__ == '__main__':
    usage = '[usage]: %prog -d PATH'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--depth', dest='depth', type=int, help='maximum depth to go for (minimum is 0)')
    opts, args = parser.parse_args()
    # required only one path in args
    # depth is required as well
    if (len(args) != 1) or opts.depth is None:
        parser.print_help()
        sys.exit(1)
    depth = opts.depth
    path = args[0]
    # exit with error if directory doesn't exists
    if not os.path.isdir(path):
        print '[ERROR]: directory %s do not exists' % path
        sys.exit(2)
    content = list_dir(path, depth)
    display(path, content)
    sys.exit(0)
