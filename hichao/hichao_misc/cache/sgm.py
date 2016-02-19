def sgm(cache, keys, miss_fn, prefix='', time=0, stale=False, found_fn=None, _update=False, post_missing_fn=None, post_fn=None):
    if not keys:return None
    ret = {}

    # map the string versions of the keys to the real version. we only
    # need this to interprate the cache's response and turn it back
    # into the version they asked for
    s_keys = {}
    for key in keys:
        s_keys[prefix+str(key)] = key


    if _update:
        cached = {}
    else:
        #todo use our custom cache chain
        if stale:
            cached = [None for i in s_keys]
        else:
            cached = cache.mget(s_keys.keys())
        
        for k, v in zip(s_keys.keys(), cached):
            ret[s_keys[k]] = v

    still_need = dict((k,v) for k,v in ret.iteritems() if v is None)
    ret = dict((k,v) for k,v in ret.iteritems() if v)

    if found_fn is not None:
        # give the caller an opportunity to reject some of the cache
        # hits if they aren't good enough. it's expected to use the
        # mutability of the cached dict and still_need set to modify
        # them as appropriate
        found_fn(ret, still_need)


    if miss_fn and still_need:
        # if we didn't get all of the keys from the cache, go to the
        # miss_fn with the keys they asked for minus the ones that we
        # found
        calculated = miss_fn(still_need)
        ret.update(calculated)

        calculated_to_cache = {}
        for k, v in calculated.iteritems():
            calculated_to_cache[prefix+str(k)] = post_missing_fn(k, v)
        # Todo expire for multi key!!!!
        cache.mset_with_expire(calculated_to_cache, expire=time)

    if post_fn:
        for k, v in ret.iteritems():
            post_fn(k, v)
    return ret
