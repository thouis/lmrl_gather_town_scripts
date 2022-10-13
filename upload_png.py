from secrets import SPACE_ID, API_KEY
from PIL import Image
import requests
import io
import json
import sys

# cribbed from https://github.com/shawwn/scrap/blob/b6f5a02aff9734bbf891f91a3980f0fc9245b9e9/data-to-url


def image_to_png(image):
    byte_array = io.BytesIO()
    image.save(byte_array, format="png")
    return byte_array.getvalue()


def data_to_upload_image_args(data):
    if isinstance(data, str):
        try:
            data = data.encode('utf8')
        except:
            data = data.encode('latin1')
    if isinstance(data, bytes):
        data = list(iter(data))
    print(len(data), "len")
    data = {'spaceId': SPACE_ID, 'bytes': {'type': 'Buffer', 'data': data}}
    data = json.dumps(data)
    data = data.encode('utf8')
    return data


def report_error(caught, code=200, **kwds):
    message = str(caught)
    # sys.stderr.write('Failed for {} of data size {}: {}\n'.format(kwds, len(data), message))
    print(json_response(False, message, code=code, **kwds))
    sys.stdout.flush()


def on_err(thunk, *args, handler=report_error, exception=Exception, **kwds):
    try:
        return thunk(*args)
    except exception as e:
        return handler(e, **kwds)


def data_to_url(data, raise_on_error=True):
    data = data_to_upload_image_args(data)
    response = requests.post('https://staging.gather.town/api/uploadImage',
                             headers={'Content-Type': 'application/json'},
                             data=data)
    if response.ok:
        return response.text
    if raise_on_error:
        response.raise_for_status()


def json_response(ok, result, **kwds):
    if 'data' in kwds:
        kwds['size'] = len(kwds.pop('data'))
    if ok:
        if 'path' in kwds:
            path = kwds['path']
            if callable(path):
                path = path()
            key = ':id'
            fqn = path
            kwds[':id'] = fqn
            stub = '&' if '?' in result else '?'
            stub += key + '=' + fqn
            result += stub
    kwds.update({'ok': ok, 'result': result})
    return json.dumps(kwds)


status = data_to_url(image_to_png(Image.open("poster_example.png")))
