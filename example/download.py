from gohlkegrabber import GohlkeGrabber

gg = GohlkeGrabber(cached='../work/cache.html')
print(list(gg.packages))

fn, metadata = gg.retrieve('../output', 'numpy', python='2.7', platform='win32', version='<1.17')
print(fn, metadata)
