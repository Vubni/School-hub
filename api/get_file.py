from aiohttp import web
import os, mimetypes

async def handle_get_file(request):
    path = request.match_info.get('path', '')
    
    if path.endswith('.py'):
        return web.Response(status=404, text='404 Not Found: File not found')

    file_path = os.path.join(os.getcwd(), path.lstrip('/'))
    
    if os.path.isdir(file_path):
        index_path = os.path.join(file_path, 'index.html')
        if os.path.isfile(index_path):
            file_path = index_path
        else:
            return web.Response(status=404, text='404 Not Found: Directory index not found')

    if os.path.isfile(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type or 'application/octet-stream'
        
        charset = 'utf-8' if content_type.startswith('text/') else None

        with open(file_path, 'rb') as f:
            return web.Response(
                body=f.read(),
                content_type=content_type,
                charset=charset  # Отдельный параметр для кодировки
            )
    else:
        return web.Response(status=404, text='404 Not Found: File not found')