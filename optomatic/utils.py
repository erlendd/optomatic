import yaml


def yread(fpath):
    with open(fpath, 'r') as f:
        dat = yaml.load(f)
    return dat


def ywrite(dat, fpath):
    with open(fpath, 'w') as f:
        yaml.dump(dat, f, default_flow_style=False)
