import json
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.hset("status","name",json.dumps([1,2,3,4,5]))
print(type(json.loads(r.hget("status","name"))))