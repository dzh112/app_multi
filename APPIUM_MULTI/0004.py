import yaml

with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

print(data['testcase'])