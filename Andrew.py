import os
def create_field(text, name) :
    file = open(f'{name}.kbs', 'w')
    file.write(text)
    file.close()
    command = f'python -m at_krl atkrl-xml -i {name}.kbs -o {name}_TKB.xml -a {name}_Allen.xml'
    os.system(command)