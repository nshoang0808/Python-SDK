from dogpile.cache import make_region

from knurld_sdk.config import Configuration

c = Configuration()
config = c.config
app_root = str(c.app_root)

region = make_region().configure('dogpile.cache.memory',
                                 expiration_time=config['TOKEN_EXPIRES'],
                                 )