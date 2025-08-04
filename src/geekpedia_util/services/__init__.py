import datetime
import httpx
import nltk

import nanoid
from newspaper import Article, Config
from readability import Document

HTTPX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

META_TEMPLATE = {
    "pinakes_id": "",
    "pinakes_version": 1,
    "pinakes_type": "",
    "pinakes_created": "",
    "pinakes_updated": "",
    "pinakes_status": "new", 
    "pinakes_opt_etag": "",
    "pinakes_opt_last_modified": "",
    "pinakes_opt_mime_type": "",
    "cite_type": "",
    "cite_title": "",
    "cite_authors": [],
    "cite_publisher": "",
    "cite_publish_date": "",
    "cite_opt_event": "",
    "cite_opt_source_url": "",
    "cite_opt_img_text": "",
    "user_tags": [],
    "user_topics": [],
    "user_highlights": [],
    "user_summary": "",
}

def get_new_item(uri):
    time_stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    resp = httpx.get(uri, headers=HTTPX_HEADERS)
    resp.raise_for_status()
    
    nltk.download('punkt_tab')
    article = Article(uri)
    article.set_html(resp.text)
    article.parse()
    article.nlp()
    
    meta = META_TEMPLATE.copy()
    meta['pinakes_id'] = nanoid.generate(size=10)
    meta['pinakes_type'] = 'article-web'
    meta['pinakes_created'] = time_stamp
    meta['pinakes_updated'] = time_stamp
    meta['pinakes_opt_etag'] = resp.headers.get('ETag', '')
    meta['pinakes_opt_last_modified'] = resp.headers.get('Last-Modified', '')
    meta['pinakes_opt_mime_type'] = resp.headers.get('Content-Type', '')

    meta['cite_type'] = 'article-web'
    meta['cite_title'] = article.title or "Untitled"
    meta['cite_authors'] = []
    meta['cite_publisher'] = article.source_url or "Unknown Publisher"
    meta['cite_opt_source_url'] = uri

    meta['nlp_0_opt_tool'] = "newspaper"
    meta['nlp_0_opt_authors'] = article.authors or []
    meta['nlp_0_opt_date_published'] = article.publish_date.isoformat() if article.publish_date else ""
    meta['nlp_0_opt_keywords'] = article.keywords or []
    meta['nlp_0_opt_topics'] = []
    meta['nlp_0_opt_summary'] = article.summary or ""

    return (meta, article.text)
