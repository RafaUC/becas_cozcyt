from .models import CacheVersion

def cache_version(request):    
    version = CacheVersion.get_object()
    return {'cache_version': version.version if version else ''}