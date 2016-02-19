from redis import Redis
from redis.exceptions import RedisError

class IfanRedis(Redis):
    """
    """
    def mset_with_expire(self, items, expire=3600, *args, **kwargs):
        """
        Sets key/values based on a mapping. Mapping can be supplied as a single
        dictionary.
        """
        if args:
            if not isinstance(items, dict):
                raise RedisError('MSET requires a single dict')
        pipe = self.pipeline(False)
        for k, v in items.iteritems():
            pipe.set(k, v, expire)
        return pipe.execute()


