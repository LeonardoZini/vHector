def clean_repetitive_commands(path=""):
    header = "\n".join(path.strip().split('\n')[:3])+'\n'
    footer = path.strip().split('\n')[-1]
    paths = path.strip().split('\n')[3:-1]
    res = ""
    for p in paths:
        style, command = p.split('\t')
        commands = command[3:].split(' ')
        clean_commands = [commands[0]]
        for c in commands:
            if c != clean_commands[-1]:
                clean_commands.append(c)

        command = " ".join(clean_commands)
        res += f"{style}\td=\"{command}\n"
    return header + res + footer


