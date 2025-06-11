# -*- coding: utf-8 -*-


class BaseMethods:
    login = 'login'


class CustomersMethods:
    get = 'customers.get'
    add = 'customers.add'
    update = 'customers.update'
    add_many = 'customers.addMany'
    update_many = 'customers.updateMany'
    delete = 'customers.delete'


class OrdersMethods:
    get = 'orders.get'
    add = 'orders.add'
    update_many = 'orders.updateMany'
    set_status = 'orders.setStatus'

class GoodsMethods:
    get = 'goods.get'
    add = 'goods.add'
    update = 'goods.update'
    remove = 'goods.remove'


class ManagersMethods:
    get = 'users.get'
