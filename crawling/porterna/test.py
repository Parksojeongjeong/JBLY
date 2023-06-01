import ray

ray.init()

@ray.remote
def add_numbers(a, b):
    a = a+2
    return a + b

result_ref = add_numbers.remote(3, 4)
result = ray.get(result_ref)
print(result)