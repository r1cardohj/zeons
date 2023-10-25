import re

r = r'(?s)(\${.*?}|\$[_A-Za-z][_A-Za-z0-9]*)'

text =  ''' <h1>hello $name</h1>

            <ul>
            ${for p in projects}
                <li>$p.title</li>
            ${endfor}
            </ul>

            ${if i_am_rich}
                <p>hhahaha....</p>
            ${endif}
        '''

result = re.split(r,text)
print(result)