#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os
import sys
import time

import transaction

from hichao.forum.models.db import dbsession_generator
from hichao.forum.models.forum import Forum
from hichao.forum.models.thread import Thread
from hichao.forum.models.tag import Tag

def do_work():
    cache = {}
    session = dbsession_generator()
    print(session.bind)
    count = 0
    skip = 0
    while True:
        cache = {}
        print('%d...' % count)

        try:
            threads = session.query(Thread).filter(
                Thread.tags == ''
            ).offset(skip).limit(1000).all()
            for thread in threads:
                cat_id = thread.category_id
                if cat_id not in cache:
                    cat = session.query(Forum).filter(
                        Forum.category_id == cat_id,
                        Forum.review != 2,
                    ).order_by(Forum.id.desc()).limit(1).scalar()
                    cache[cat_id] = cat
                else:
                    cat = cache[cat_id]
                if cat is None:
                    skip += 1
                    continue
                tags = session.query(Tag).filter(
                    Tag.tag == cat.name).limit(1).all()
                if tags:
                    tag_id = tags[0].id
                else:
                    tag = Tag(
                        tag = cat.name,
                        description = cat.description,
                        review = cat.review,
                    )
                    session.add(tag)
                    session.flush()
                    tag_id = tag.id
                thread.tags = str(tag_id)

            transaction.commit()

            if len(threads) < 1000:
                break
            count += 1000
        except:
            transaction.abort()
            raise
        finally:
            session.close()

        pass

if __name__ == '__main__':
    if 'thrift_stage' not in os.environ:
        sys.exit('Please set thrift_stage environment variable.')
    do_work()
