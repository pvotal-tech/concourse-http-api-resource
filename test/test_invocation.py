import json
import subprocess

import pytest

from helpers import cmd


def test_out(httpbin):
    """Test out action with minimal input."""

    data = {
        'source': {
            'uri': httpbin + '/status/200',
        },
        'version': {}
    }
    subprocess.check_output('/opt/resource/out', input=json.dumps(data).encode())


def test_out_failure(httpbin):
    """Test action failing if not OK http response."""

    data = {
        'source': {
            'uri': httpbin + '/status/404',
        },
        'version': {}
    }
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_output('/opt/resource/out', input=json.dumps(data).encode())


def test_auth(httpbin):
    """Test basic authentication."""

    data = {
        'source': {
            'uri': 'http://user:password@{0.host}:{0.port}/basic-auth/user/password'.format(httpbin),
        },
    }
    subprocess.check_output('/opt/resource/out', input=json.dumps(data).encode())


def test_json(httpbin):
    """Json should be passed as JSON content."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
        'json': {
            'test': 123,
        },
        'version': {}
    }

    output = cmd('out', source)

    assert output['json']['test'] == 123
    assert output['version'] == {}


def test_json_with_files(httpbin):
    """Json should be passed as JSON content."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
        'json': {
            'test': 123,
            'hostname': '{hostname}',
            'foo': '{foo}',
            'spec': '{spec}'
        },
        'version': {}
    }

    params = {
        'hostname': "file:hostname",
        'foo': "file:test.json",
        'spec': {
          "data": {
            "application": {
              "id": "aa08436a-45c7-4a6c-b6e4-5d38c0da0c49"
            },
            "dockerImage": {
              "tag": "file:hostname"
            }
          },
          "type": "docker-image-pushed"
        }
    }

    output = cmd('out', source, params=params)

    assert output['json']['test'] == 123
    assert output['json']['hostname'] == 'super_hostname'
    assert output['json']['foo'] == {"foo": "bar"}
    assert output['json']['spec']['data']['dockerImage']['tag'] == 'super_hostname'
    assert output['version'] == {}


def test_interpolation(httpbin):
    """Values should be interpolated recursively."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
        'json': {
            'object': {
                'test': '{BUILD_NAME}'
            },
            'array': [
                '{BUILD_NAME}'
            ]
        }
    }

    output = cmd('out', source)

    assert output['json']['object']['test'] == '1'
    assert output['json']['array'][0] == '1'
    assert output['version'] == {}


def test_empty_check(httpbin):
    """Check must return an empty response but not nothing."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
    }

    check = cmd('check', source)

    assert check == []


def test_data_urlencode(httpbin):
    """Test passing URL encoded data."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
        'form_data': {
            'field': {
                'test': 123,
            },
        }
    }

    output = cmd('out', source)

    assert output['form'] == {'field': '{"test": 123}'}
    assert output['version'] == {}


def test_data_ensure_ascii(httpbin):
    """Test form_data json ensure_ascii."""

    source = {
        'uri': httpbin + '/post',
        'method': 'POST',
        'form_data': {
            'field': {
                'test': '日本語',
            },
        },
    }

    output = cmd('out', source)

    assert output['form'] == {'field': '{"test": "日本語"}'}
