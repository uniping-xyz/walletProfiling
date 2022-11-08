# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------


from sanic.response import json
from sanic import Blueprint
from sanic.exceptions import SanicException
from loguru import logger


ERRORS_BP = Blueprint('errors')
DEFAULT_MSGS = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    406: "Not Acceptable",
    501: 'Not Implemented',
    503: 'Internal Error'
}


def add_status_code(code):
    def class_decorator(cls):
        cls.status_code = code
        return cls
    return class_decorator



class ApiException(SanicException):
    def __init__(self, message=None, status_code=None, data= None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if message is None:
            self.message = DEFAULT_MSGS[self.status_code]
        else:
            self.message = message
        self.data = data
        logger.error(message)

@ERRORS_BP.exception(ApiException)
def ApiJsonError(request, exception):
    return json({
        'message': exception.message,
        'error': True,
        'success': False,
        'data': exception.data
    }, status=exception.status_code)





@add_status_code(400)
class CustomError(ApiException):
    def __init__(self, message="This is a custom error", status_code=None):
        super().__init__(message, status_code)

@add_status_code(400)
class SubscriptionRequiredError(ApiException):
    def __init__(self, message="subscription is required", status_code=None):
        super().__init__(message, status_code)
