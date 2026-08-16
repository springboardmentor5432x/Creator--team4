from facebook_scraper import get_posts
import json

try:
    posts = []
    # Fetch 7 posts
    for post in get_posts('narendramodi', pages=1, extra_info=True, options={"comments": False}):
        posts.append({
            'post_id': post.get('post_id'),
            'text': post.get('text', '')[:100],
            'time': str(post.get('time')),
            'image': post.get('image'),
            'likes': post.get('likes'),
            'post_url': post.get('post_url')
        })
        if len(posts) >= 7:
            break
            
    print(json.dumps(posts, indent=2))
except Exception as e:
    print("Error:", str(e))
