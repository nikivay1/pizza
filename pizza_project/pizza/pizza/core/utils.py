import binascii
import hashlib
import os
import random
import uuid

import requests
from django.conf import settings
from django.utils import timezone


def generate_token(length=16):
    """
    Генерирует токен длиною length
    
    :param length: int Длина токена
    :return: str
    """

    return hashlib.sha256(os.urandom(length)).hexdigest()


def uuid_replacer_handler(instance, filename, path=''):
    """
    Замена имени файла на uuid

    :param instance: models.Model subclass
    :param filename: str Имя фалй
    :param path: str Путь для сохранения
    :return: str Результирующий путь к файлу
    """

    ext = filename.split('.')[-1]
    new_filename = os.path.join(path, '{}.{}'.format(uuid.uuid4(), ext).lower())
    return new_filename


def upload_path_handler(instance, filename):
    """
    Загрузка файла в указанную папку с заменой имени на uuid
    
    :param instance: object
    :param filename: str Оригинальное имя файла
    :return: str Новый путь файла
    """

    path = instance.IMAGE_PATH
    return uuid_replacer_handler(instance, filename, path=path)


def generate_key(length=25):
    return binascii.hexlify(os.urandom(length)).decode()


def generate_number_code(length=6):
    code_chars = []
    for i in range(length):
        char = random.randint(0, 9)
        code_chars.append(str(char))

    return ''.join(code_chars)


def get_status_sb_order(remote_order_id):
    param = {
        'language': settings.SBERBANK['LANGUAGE'],
        'password': settings.SBERBANK['PASSWORD'],
        'userName': settings.SBERBANK['USERNAME'],
        'orderId': remote_order_id
    }

    response = requests.post(settings.SBERBANK['ORDER_STATUS_URL'], data=param)

    if response.status_code == 200:
        response_data = response.json()
        if 'orderStatus' in response_data:
            return response_data['orderStatus']


def create_sb_order(order, request):
    param = {
        'amount': int(order.get_total_price()) * 100,
        'language': settings.SBERBANK['LANGUAGE'],
        'orderNumber': order.sb_internal_id,
        'password': settings.SBERBANK['PASSWORD'],
        'returnUrl': request.build_absolute_uri(order.get_absolute_url()),
        'userName': settings.SBERBANK['USERNAME'],
        'pageView': settings.SBERBANK['PAGE_VIEW']
    }
    response = requests.post(settings.SBERBANK['ORDER_REGISTER_URL'], data=param)

    if response.status_code == 200:
        response_data = response.json()
        if 'errorCode' not in response_data:
            return response_data['orderId'], response_data['formUrl']
    return None, None


def update_sb_order_status(order):

    from cart.models import Order

    if order.online_status != Order.TRANSACTION_STATUS.SUCCESS:
        status = get_status_sb_order(order.sb_remote_id)

        if status is not None:
            order.online_status = status

            if status == Order.TRANSACTION_STATUS.SUCCESS:
                order.status = Order.STATUS_CHOICES.CONFIRMED
                order.started_at = timezone.now()
            elif status != Order.TRANSACTION_STATUS.REGISTERED:
                order.status = Order.STATUS_CHOICES.FAILED

            order.save()


def get_or_create_sb_link(order, request):

    status = get_status_sb_order(order.sb_remote_id)

    if status == order.TRANSACTION_STATUS.SUCCESS:
        return 1, None

    if status == order.TRANSACTION_STATUS.REGISTERED:
        return 0, order.sb_form_url

    order.set_internal_id()
    order_id, form_url = create_sb_order(order, request)

    if order_id and form_url:
        order.online_status = order.TRANSACTION_STATUS.REGISTERED
        order.status = order.STATUS_CHOICES.WAIT
        order.sb_remote_id = order_id
        order.sb_form_url = form_url
        order.save()
        return 0, form_url
    return -1, None
