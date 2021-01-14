#!/usr/bin/env python
import requests
import json

import logging

log = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()
REQUEST_TIMEOUT = 5

class DiscourseApi():
    def __init__(self, host, username, api_key):
        self.host = host
        self.username = username
        self.api_key = api_key

    # Use discourse API to create topic
    def create_topic(self, title, raw, category_id):
        data_dict = {
            'title': title,
            'raw': raw,
            'category': category_id
        }
        return self.make_request('POST', '/posts.json', data_dict)

    # Use discourse API to update a post
    def update_post(self, post_id, raw):
        data_dict = {
            'post[raw]': raw,
        }
        return self.make_request('PUT', '/posts/{0}.json'.format(post_id), data_dict)

    # Use discourse API to get list of topics in a category
    def get_topic_list(self, category_id):
        topics = []
        page = 0
        while True:
            category = self.make_request('GET', '/c/{0}.json?page={1}'.format(category_id, page))
            if category.get('topic_list', {}).get('topics'):
                topics.extend(category.get('topic_list', {}).get('topics'))
            else:
                break
            page += 1
        return topics

    # Use discourse API to get list of posts in a topic
    def get_topic_posts(self, topic_id):
        post_stream = self.make_request('GET', '/t/{0}.json'.format(topic_id))
        return post_stream.get('post_stream', {}).get('posts', [])

    # Make request and return json response
    def make_request(self, method, path, data_dict={}):
        if method not in ['GET', 'POST', 'PUT']:
            log.error('Invalid HTTP request methods used')
            return

        url = self.host + path

        headers = {
            'Content-Type': 'multipart/form-data;',
            'Api-Key': self.api_key,
            'Api-Username': self.username
        }
        json_response = {}
        try:
            response = requests.request(
                method,
                url,
                data = data_dict,
                headers = headers,
                timeout=REQUEST_TIMEOUT,
                verify = False
            )
            json_response = response.json()
        except requests.exceptions.HTTPError as error:
            log.debug('HTTP error: {}'.format(error))
        except requests.exceptions.Timeout:
            log.warn('URL time out for {0} after {1}s'.format(category_url, REQUEST_TIMEOUT))
        except Exception as e:
            log.error(e)

        return json_response
