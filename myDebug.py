def debug(func):
    import time

    def nf(*args, **kwargs):
        try:
            prompt = 'Function {} called'.format(func.__name__)
            if args:
                prompt += ' with arguments {}'.format(args)
            if kwargs:
                if args:
                    prompt += ' and keyword arguments '
                else:
                    prompt += ' with keyword arguments '
                prompt += '({})'.format(
                    ', '.join(['{}={}'.format(k, kwargs[k]) for k in kwargs]))
            print(prompt)
            t0 = time.time()
            result = func(*args, **kwargs)
            t = time.time()
            prompt = 'Function {} ends'
            if t-t0 >= 0.001:
                prompt += 'time taken: {:.1f}ms'.format((t-t0)*1000)
            if t-t0 >= 0.3:
                prompt += 'time taken: {:.3f}s'.format(t-t0)
            print(prompt)
            return result
        except SystemExit:
            print('SystemExit')
            exit(0)
        except:
            import traceback
            traceback.print_exc()
            return None
    return nf
