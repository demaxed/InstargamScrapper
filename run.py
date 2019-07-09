import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup

user_agents = 'Chrome/70.0.3538.77'

count_of_post = 3

'''
There are all data instagram post may content:

    '__typename',
    'id',
    'edge_media_to_caption': {edges: [node: {text: __}],
    'shortcode',
    'edge_media_to_comment',
    'comments_disabled',
    'taken_at_timestamp',
    'dimensions',
    'display_url',
    'edge_liked_by',
    'edge_media_preview_like',
    'location',
    'gating_info',
    'media_preview',
    'owner':{id: _, username: _},
    'thumbnail_src',
    'thumbnail_resources',
    'is_video',
    'accessibility_caption'])
'''


def response_template(
        username, user_id, url, text, likes, accessibility_caption):

    template = {
        'Username': username,
        'User_id': user_id,
        'Posts': {
            'image_url': url,
            'text': text,
            'likes': likes
        },
        'Accessibility_caption': accessibility_caption
    }

    return template


def request_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': user_agents})
        response.raise_for_status()
    except requests.HTTPError:
        raise requests.HTTPError('Received non 200 status code from Instagram')
    except requests.RequestException:
        raise requests.RequestException
    else:
        return response.text


def extract_json_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('body')
    script_tag = body.find('script')
    raw_string = script_tag.text.strip().replace('window._sharedData =', '') \
        .replace(';', '')
    return json.loads(raw_string)


def profile_page_recent_posts(json_data, count=None):
    results = []
    try:
        metrics = json_data['entry_data']['ProfilePage'][0]['graphql'] \
            ['user']['edge_owner_to_timeline_media']["edges"]
    except Exception as e:
        raise e
    else:
        if count is None:
            pass
        else:
            i = 0
            for node in metrics:
                node = node.get('node', None)
                media = node.get('edge_media_to_caption').get('edges')
                if media:
                    media = media[0]
                    text = media.get('node').get('text')
                else:
                    text = ''
                likes = node.get('edge_liked_by').get('count')
                url = node.get('display_url')
                username = node.get('owner').get('username')
                user_id = node.get('owner').get('id')
                accessibility_caption = node.get('accessibility_caption')
                results.append(
                    response_template(
                        username, user_id, url,
                        text, likes, accessibility_caption
                ))

                i += 1
                if i == count:
                    return json.dumps(results, ensure_ascii=False)

    return json.dumps(results, ensure_ascii=False)


if __name__ == '__main__':
    username = input('Input username: ')
    url = f'https://www.instagram.com/{username}'

    html = request_url(url)
    json_data = extract_json_data(html)

    data = profile_page_recent_posts(json_data, count_of_post)
    print(f'Posts display: {count_of_post}')
    pprint(data)
