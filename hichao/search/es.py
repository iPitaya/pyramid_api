#!/usr/bin/env python
# encoding: utf-8

import itertools
from elasticsearch import Elasticsearch, ThriftConnection
from hc.redis.decorator import cache, pcache, delete_cache
from hichao.cache import get_cache_client
from hichao.util.date_util import (
    MINUTE,
    FIVE_MINUTES,
    TEN_MINUTES,
    HALF_HOUR,
    YEAR,
)
from hichao.util.statsd_client import timeit
from icehole_client.mxyc_search_client import search_skus

from config import NODES, STYLE, CLASSIFY, SKU_TYPE, EXLUDE_CHAR
from icehole_client.coflex_agent_client import CoflexAgentClient
from hichao.cache.cache import deco_cache

# from cache import get_cache_client
# from date_util import MINUTE, FIVE_MINUTES, TEN_MINUTES, HALF_HOUR, FOREVER, YEAR

redis = get_cache_client()

timer = timeit('hichao_backend.m_search_es')


@timer
def es_conn():
    return Elasticsearch(NODES, connection_class=ThriftConnection)


@timer
def search(query_str, offset=0, limit=30, search_type=None):
    res = []
    if not search_type:
        res = hybrid_search(query_str, offset, limit)
    elif search_type == 'star':
        #res = stars(query_str, offset, limit)
        result = CoflexAgentClient().search_star_photo(query_str, 0, offset, limit)
        res = result['star_photos'] if result else []
    elif search_type == 'sku':
        res = skus(query_str, offset, limit, res_type='id')
    elif search_type == 'sku_v2':
        #res = search_skus(query_str, offset, limit, need_total = False)
        res = CoflexAgentClient().search_sku(query_str, 0, offset, limit, need_total = False)
    elif search_type == 'forum':
        res = CoflexAgentClient().search_forum(query_str, offset, limit)
    elif search_type == 'hongren':
        res = CoflexAgentClient().search_iternet_star(query_str, offset, limit)
        if res:
            res = res.get('items',[])
    return res


@timer
# @delete_cache(u'search:hybrid:%s', redis)
@pcache('search:hybrid:%s', redis, count=300, expire=TEN_MINUTES)
def hybrid_search(query_str, offset=0, limit=30):
    if not query_str.strip():
        return []
    query_str = remove_regx_char(query_str)
    hybrid_ids = []
    es = es_conn()
    if u';' in query_str:
        query_str = query_str.replace(';', ' ')
    fields = [
        "title", "desc.part*", "star_name", "nstyle",
        "scene", "shape", "style", "description", "content"]
    body = {
        "query": {
            "multi_match": {
                "query": query_str,
                "fields": fields,
                "operator": "AND",
                "type": "best_fields",
                "tie_breaker": 0.3,
                "minimum_should_match": "70%"
            }
        },
        "sort": [
            {"weight": {"order": "desc"}},
            {"publish_date": {"order": "desc"}}
        ]
    }
    try:
        res = es.search(
            index='sku,star,forum', doc_type='sku,star,threads,topic',
            body=body, from_=offset, size=limit)
        hybrid_ids = build_hybrid_data(res)
        # hybrid_ids_len = len(hybrid_ids)
        # hybrid_total = res["hits"]["total"]
        # if hybrid_ids_len < limit:
        #     vip_limit = limit - hybrid_ids_len
        #     vip_offset = offset - hybrid_total \
        #         if (offset - hybrid_total) > 0 else 0
        #     vip_sku_ids = vip(
        #         query_str, es, vip_offset, vip_limit, search_type='hybrid')
        #     hybrid_ids.extend(vip_sku_ids)
    except Exception as e:
        print "Hybrid search exception: ", str(e)
    return hybrid_ids


@timer
# @delete_cache(u'search:star:%s', redis)
@pcache('search:star:%s', redis, count=360, expire=TEN_MINUTES)
def stars(query_str, offset=0, limit=10):
    if not query_str.strip():
        return []
    query_str = remove_regx_char(query_str)
    es = es_conn()
    star_ids = []
    hot_star_ids = []

    # some stars from editors selection
    if u'@' in query_str:
        side_res = sidebar_handle(query_str, es, limit, offset)
        if side_res:
            is_enough, hot_star_ids, sidebar_len = side_res
            if is_enough:
                return hot_star_ids
            offset = offset - (sidebar_len / limit) * limit

    if query_str in STYLE:
        query_str = STYLE[query_str]
        fields = ["style",  'nstyle', 'scene', 'shape']
    elif u'|' in query_str:
        query_str = query_str.replace(u'|', ' OR ')
        fields = ["desc.part*"]
    elif u'+' in query_str:
        query_str = query_str.replace(u'+', ' AND ')
        fields = ["desc.part*"]
    elif u';' in query_str:
        query_str = ' '.join(query_str.split(';'))
        fields = ["desc.part*", "star_name"]
    else:
        fields = ["desc.part*", 'style', 'nstyle', 'scene', 'shape', "star_name"]
    body = {
        "query": {
            "query_string": {
                "query": query_str,
                "fields": fields,
                "default_operator": "AND",
            }
        }
    }
    try:
        res = es.search(
            index="star", doc_type="star",
            body=body, size=limit, from_=offset, sort="publish_date:desc")
        stars = res["hits"]["hits"]
        if hot_star_ids:
            star_ids = hot_star_ids[:]
            for star in stars:
                star = star["_source"]
                if star['star_id'] not in hot_star_ids:
                    star_ids.append(star['star_id'])
                    if len(star_ids) >= limit:
                        break
        else:
            for star in stars:
                star = star["_source"]
                star_ids.append(star['star_id'])
    except Exception, e:
        print "Star search exception: ", str(e)
    return star_ids


@timer
# @delete_cache(u'search:sku:{query_str}:{res_type}', redis)
@pcache(u'search:sku:{query_str}:{res_type}', redis, expire=FIVE_MINUTES)
def skus(query_str, offset=0, limit=10, res_type='data', index='sku'):
    if not query_str.strip():
        return []
    skus = []
    es = es_conn()
    query_str = remove_regx_char(query_str)
    # if query_str is empty string or sth like whitespaces, return empty result
    filter_tag, query_str = keyword_handler(query_str)
    filter_ = {"match_all": {}}
    if filter_tag:
        if u'女' not in filter_tag:
            filter_ = {"term": {"tags": filter_tag}}
        else:
            query_str = u"{query_str} NOT ({filter_tag})".\
                format(query_str=query_str, filter_tag=filter_tag)
    query = {
        "query_string": {
            "query": query_str,
            "fields": ["title"],
            "default_operator": "AND",
        }
    }
    body = {
        "query": {
            "filtered": {
                "query": query,
                "filter": filter_
            }
        },
        "sort": [
            {'weight': {"order": "desc"}},
            {'publish_date': {"order": "desc"}},
        ]
    }
    try:
        sku_res = es.search(index=index, body=body,
                            from_=offset, size=limit)
        # sku_total = sku_res["hits"]["total"]
        if res_type == 'data':
            for sku in sku_res["hits"]["hits"]:
                sku = sku["_source"]
                sku['f'] = 1
                skus.append(sku)
        else:
            skus = [sku for sku in sku_res['hits']['hits']]
            skus = map(lambda x: str(x["_source"]["sku_id"]), skus)
            # if len(skus) < limit:
            #     sku_len = len(skus)
            #     vip_limit = limit - sku_len
            #     vip_offset = offset - sku_total \
            #         if (offset - sku_total) > 0 else 0
            #     vip_sku_ids = vip(
            #         query_str, es, offset=vip_offset, limit=vip_limit)
            #     skus.extend(vip_sku_ids)
    except Exception as e:
        print "Sku search exception: ", str(e)
    return skus


@timer
@pcache(u'search:vip:%s', redis, count=180, expire=HALF_HOUR)
def vip(query_str, es, offset=0, limit=30, search_type='sku'):
    sku_ids = []
    query_str = remove_regx_char(query_str)
    query = [{
        "multi_match": {
            "query": query_str,
            "fields": ["title", "color"],
            "operator": "AND",
            "type": "best_fields",
            "tie_breaker": 0.3,
        }
    }]
    must_filters = [
        {"term": {"status": 1}},
        {"term": {"is_out": False}},
        {"exists": {"field": "color_url"}},
    ]
    body = {
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "must": query
                    }
                },
                "filter":  {
                    "bool": {
                        "must":  must_filters,
                    }
                }
            }
        },
    }
    try:
        res = es.search(
            'vip', 'vip',
            body=body, from_=offset, size=limit)
        if search_type == 'hybrid':
            sku_ids = [
                {"type": "sku", "id": sku["_id"]}
                for sku in res['hits']['hits']]
        else:
            sku_ids = [sku["_id"] for sku in res["hits"]["hits"]]
    except Exception, e:
        print "Vip search exception: ", str(e)
    return sku_ids


@timer
@pcache(u'search:forum:{query_str}:{doc_type}', redis, expire=MINUTE)
def forum(query_str, offset=0, limit=30, doc_type='threads'):
    if not query_str.strip():
        return []
    ids = []
    es = es_conn()
    query_str = remove_regx_char(query_str)
    if doc_type == 'threads':
        fields = ["title^30", "content^10", "nick_name"]
    else:
        fields = ["title^30", "content^10", "nick_name", "description^30"]
        doc_type = 'threads,topic'

    body = {
        "query": {
            "query_string": {
                "query": query_str,
                "fields": fields,
                "default_operator": "AND"
            }
        }
    }
    try:
        res = es.search(index='forum', doc_type=doc_type, body=body,
                        from_=offset, size=limit)
        if doc_type == "threads":
            ids = [doc["_source"]["id"] for doc in res["hits"]["hits"]]
        else:
            ids = build_hybrid_data(res)
    except Exception, e:
        print "Thread search exception: ", str(e)
    return ids


@timer
def newest_sku(offset, limit):
    skus = []
    es = es_conn()
    body = {
        "query": {
            "match_all": {}
        }
    }
    try:
        res = es.search(
            index='ed_sku', doc_type='ed_sku',
            body=body, from_=offset, size=limit, sort="publish_date:desc")
        for sku in res["hits"]["hits"]:
            sku = sku["_source"]
            sku['f'] = 1
            skus.append(sku)
    except Exception, e:
        print "Newest sku search exception: ", str(e)
    return skus


@timer
#@cache('search:suggester:%s%s', redis, expire=FIVE_MINUTES)
@deco_cache(prefix = 'search_suggester', recycle = FIVE_MINUTES) 
def suggester(query_str, size):
    if not query_str.strip():
        return []
    suggests = []
    es = es_conn()
    query_str = remove_regx_char(query_str)
    body = {
        "suggester": {
            "text": query_str,
            "completion": {
                "field": "search_suggest",
                "size": size,
                "context": {
                    "review": 1,
                }
            }
        }
    }
    try:
        res = es.suggest(body=body, index="suggester_v2")
        suggests = [doc[u"payload"] for doc in res["suggester"][0][u"options"]]
    except Exception, e:
        print 'Search suggester Exception:', str(e)
    return suggests


@timer
# @delete_cache('search:sg_tags:%s%s', redis)
#@cache('search:sg_tags:%s%s', redis, expire=HALF_HOUR)
@deco_cache(prefix = 'search_sg_tags', recycle = HALF_HOUR) 
def sg_tags(query_str, size):
    if not query_str.strip():
        return []
    es = es_conn()
    query_str = remove_regx_char(query_str)
    if u';' in query_str:
        queries = query_str.split(u';')
    else:
        queries = split_str_by_tokenizer(query_str, es)
    filters = [
        {"term": {"tags_comm.name": tag}}
        for tag in queries
    ]
    body = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": filters
                    }
                }
            }
        },
        "sort": [{"weight": {"order": "desc"}}]
    }
    res = es.search(
        index='tags_sg', doc_type='tags_sg', body=body, from_=0, size=size)
    all_tags = [doc['_source']['tags_comm'] for doc in res['hits']['hits']]
    sg_tags = sg_tags_handler(queries, all_tags, size)
    return sg_tags


@timer
#@cache('search:split_str_by_tokenizer:%s', redis, expire=YEAR)
@deco_cache(prefix = 'split_str_by_tokenizer', recycle = HALF_HOUR)
def split_str_by_tokenizer(query_str, es):
    queries = []
    query_str = query_str.upper()
    if u'T恤' in query_str:
        queries.append(u'T恤')
        query_str = u''.join(query_str.split(u'T恤'))
    tokens = es.indices.analyze(
        index='sku', text=query_str, analyzer='ik_smart')['tokens']
    queries.extend([token['token'] for token in tokens])
    return queries


@timer
def sg_tags_handler(queries, all_tags, size):
    type_tags = []
    other_tags = []
    tags_set = set()
    query_str_set = set(queries)
    has_type_tag = bool([tag for tag in queries if tag in SKU_TYPE])
    all_tags = itertools.chain.from_iterable(all_tags)
    for tag in all_tags:
        tag_name = tag.get("name")
        if (tag_name not in query_str_set) and (tag_name not in tags_set):
            if tag_name in SKU_TYPE:
                type_tags.append(tag)
            else:
                other_tags.append(tag)
            tags_set.add(tag_name)
    if has_type_tag:
        other_tags.extend(type_tags)
        sg_tags = other_tags
    else:
        type_tags.extend(other_tags)
        sg_tags = type_tags
    #for tag in sg_tags[0: size]:
    #    print tag.get("name"), tag.get("background")
    return sg_tags[0:size]


def get_phrase_query_arg(query_str, query_type="match_query"):
    if query_type == "match_query":
        arg = {"type": "phrase"}
    else:
        arg = {"auto_generate_phrase_queries": True}
    return arg


@timer
def build_hybrid_data(search_res):
    hybrid_ids = []
    hybrid_ids = [
        {"type": doc["_type"], "id": doc["_id"]}
        for doc in search_res["hits"]["hits"]
    ]
    return hybrid_ids


@timer
def keyword_handler(keyword):
    filter_tag = None
    keyword = keyword

    if ',' in keyword:
        first_tag, second_tag = keyword.split(',', 1)
        if first_tag not in \
                [u'潮男', u'美妆', u'格物', u'裙子', u'最热', u'衣服']:
            filter_tag = CLASSIFY.get(first_tag)
            keyword = second_tag
        else:
            if u'潮男' in keyword:
                filter_tag = u'女 OR BF OR 男朋友 OR 男友'
                if u'男' in second_tag:
                    keyword = second_tag
                else:
                    keyword = CLASSIFY.get(first_tag) + second_tag
            else:
                keyword = second_tag
                filter_tag = None
    elif ';' in keyword:
        keyword = keyword.replace(';', ' ')
    #print 'filter_tag:', filter_tag, 'keyword:', keyword

    return filter_tag, keyword


@timer
def sidebar_handle(query_str, es, limit, offset):
    is_enough = False
    sidebar_body = {
        "query": {
            "query_string": {
                "fields": ["query_str"],
                "query": query_str,
                "minimum_should_match": "100%"
            }
        }
    }
    sidebar_res = es.search(
        index="hot_queries", doc_type="hot_queries", body=sidebar_body)
    if sidebar_res["hits"]["hits"]:
        sidebar_all = sidebar_res["hits"]["hits"][0]["_source"]["star_ids"]
        star_ids = sidebar_all[offset: offset + limit]
        sidebar_len = len(sidebar_all)
        sidebar_num = len(star_ids)
        if sidebar_num >= limit:
            is_enough = True
        return is_enough, star_ids, sidebar_len


def remove_regx_char(query_str):
    return u"".join([char for char in query_str if char not in EXLUDE_CHAR])

if __name__ == '__main__':
    # query_str = raw_input("Please input the query string: ")
    # for item in stars(u'红色细跟高跟鞋', limit=30, offset=0):
    #     print item
    #print stars(u'娇小', limit=30, offset=0)
    # for item in hybrid_search(u'白色细跟高跟鞋', limit=30, offset=0):
    #     print item
    print skus(u'邓紫棋', offset=0, limit=30, res_type='data')
    # print vip(u'红色蕾丝连衣裙', offset=30, limit=30)
    # print forum(u'白色连衣裙', limit=30, offset=30, doc_type='all')
    # print search(u'紫色连衣裙', limit=30, offset=0, search_type='')
    # for i in suggester(u'蓝色', 10):
    #     print i['name']
    #     print i
    # print suggester(u'l', 30)
    # print newest_sku(0, 30)
    # for tag in sg_tags(u'长袖T恤', 10):
    #     print tag.get('name')
