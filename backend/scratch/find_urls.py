import re
with open('c:/infosys/creator_iq/backend/scratch/fb_output.html', 'r', encoding='utf-8') as f:
    text = f.read()

urls2 = re.findall(r'https:\\/\\/www\.facebook\.com\\/[^/]+\\/posts\\/[a-zA-Z0-9_]+', text)
all_urls = list(set([u.replace('\\/', '/') for u in urls2]))
print('Found:', all_urls)
